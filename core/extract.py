"""
PDForge — core/extract.py
Extract text, images, and tables from PDF files.
"""

from __future__ import annotations
import io
import os
from pathlib import Path
from typing import Callable

from pypdf import PdfReader
import pdfplumber
from PIL import Image


# ── Text extraction ───────────────────────────────────────────────────────────

def extract_text(
    input_path: str,
    output_path: str | None = None,
    pages: str = "all",
    preserve_layout: bool = True,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Extract text from PDF.

    Args:
        output_path:      if given, writes .txt file; else returns text in result
        pages:            "all" or range string
        preserve_layout:  use pdfplumber for layout-aware extraction

    Returns:
        dict with success, text, output_path, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    try:
        if preserve_layout:
            text, num_pages = _extract_text_pdfplumber(input_path, pages, progress_cb)
        else:
            text, num_pages = _extract_text_pypdf(input_path, pages, progress_cb)

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

        return {
            "success": True,
            "text": text,
            "output_path": output_path,
            "char_count": len(text),
            "error": None,
        }

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def _extract_text_pdfplumber(input_path, pages_str, progress_cb):
    with pdfplumber.open(input_path) as pdf:
        total = len(pdf.pages)
        target = _resolve_pages(pages_str, total)
        lines = []
        for i, page in enumerate(pdf.pages):
            if i in target:
                t = page.extract_text(layout=True) or ""
                lines.append(f"--- Page {i + 1} ---\n{t}\n")
            if progress_cb:
                progress_cb(i + 1, total)
    return "\n".join(lines), total


def _extract_text_pypdf(input_path, pages_str, progress_cb):
    reader = PdfReader(input_path)
    total  = len(reader.pages)
    target = _resolve_pages(pages_str, total)
    lines  = []
    for i, page in enumerate(reader.pages):
        if i in target:
            t = page.extract_text() or ""
            lines.append(f"--- Page {i + 1} ---\n{t}\n")
        if progress_cb:
            progress_cb(i + 1, total)
    return "\n".join(lines), total


# ── Image extraction ──────────────────────────────────────────────────────────

def extract_images(
    input_path: str,
    output_dir: str,
    pages: str = "all",
    image_format: str = "PNG",       # "PNG" | "JPEG" | "WEBP"
    min_width: int = 50,
    min_height: int = 50,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Extract all embedded images from a PDF.

    Returns:
        dict with success, output_files, count, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    image_format = image_format.upper()
    if image_format not in ("PNG", "JPEG", "WEBP"):
        return {"success": False, "error": "image_format must be PNG, JPEG, or WEBP."}

    try:
        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        target    = _resolve_pages(pages, num_pages)
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        output_files = []
        img_counter  = 0
        ext          = image_format.lower().replace("jpeg", "jpg")
        stem         = Path(input_path).stem

        for pg_idx in sorted(target):
            page = reader.pages[pg_idx]
            images = _get_page_images(page)

            for raw_data, mode, width, height in images:
                if width < min_width or height < min_height:
                    continue
                try:
                    img      = Image.frombytes(mode, (width, height), raw_data)
                    img_counter += 1
                    out_path = os.path.join(
                        output_dir,
                        f"{stem}_p{pg_idx + 1}_img{img_counter:03d}.{ext}",
                    )
                    if image_format == "JPEG" and img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    img.save(out_path, format=image_format)
                    output_files.append(out_path)
                except Exception:
                    continue

            if progress_cb:
                progress_cb(pg_idx + 1, num_pages)

        return {
            "success": True,
            "output_files": output_files,
            "count": img_counter,
            "error": None,
        }

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def _get_page_images(page) -> list[tuple]:
    """Return list of (raw_bytes, mode, width, height) for page images."""
    results = []
    try:
        resources = page.get("/Resources", {})
        if hasattr(resources, "get_object"):
            resources = resources.get_object()
        xobjects = resources.get("/XObject", {})
        if hasattr(xobjects, "get_object"):
            xobjects = xobjects.get_object()

        for name in xobjects:
            obj = xobjects[name]
            if hasattr(obj, "get_object"):
                obj = obj.get_object()
            if obj.get("/Subtype") != "/Image":
                continue
            try:
                width  = int(obj["/Width"])
                height = int(obj["/Height"])
                cs     = str(obj.get("/ColorSpace", "/DeviceRGB"))
                mode   = "L" if ("Gray" in cs or "Grey" in cs) else "RGB"
                data   = obj.get_data()
                results.append((data, mode, width, height))
            except Exception:
                continue
    except Exception:
        pass
    return results


# ── Table extraction ──────────────────────────────────────────────────────────

def extract_tables(
    input_path: str,
    output_path: str,               # .xlsx or .csv
    pages: str = "all",
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Extract all tables from PDF pages and save to Excel or CSV.

    Returns:
        dict with success, output_path, table_count, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    ext = Path(output_path).suffix.lower()
    if ext not in (".xlsx", ".csv"):
        return {"success": False, "error": "output_path must end with .xlsx or .csv"}

    try:
        import pandas as pd

        all_tables   = []
        table_count  = 0

        with pdfplumber.open(input_path) as pdf:
            total  = len(pdf.pages)
            target = _resolve_pages(pages, total)

            for i, page in enumerate(pdf.pages):
                if i in target:
                    tables = page.extract_tables()
                    for t in tables:
                        if t and len(t) > 1:
                            try:
                                df = pd.DataFrame(t[1:], columns=t[0])
                                df.insert(0, "_page", i + 1)
                                df.insert(1, "_table", table_count + 1)
                                all_tables.append(df)
                                table_count += 1
                            except Exception:
                                continue
                if progress_cb:
                    progress_cb(i + 1, total)

        if not all_tables:
            return {"success": False, "error": "No tables found in the specified pages."}

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if ext == ".xlsx":
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                for idx, df in enumerate(all_tables):
                    sheet = f"Table_{idx + 1}"
                    df.to_excel(writer, sheet_name=sheet, index=False)
        else:
            # CSV: stack all tables vertically
            combined = pd.concat(all_tables, ignore_index=True)
            combined.to_csv(output_path, index=False, encoding="utf-8-sig")

        return {
            "success": True,
            "output_path": output_path,
            "table_count": table_count,
            "error": None,
        }

    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ── Metadata extraction ───────────────────────────────────────────────────────

def extract_metadata(input_path: str) -> dict:
    """Return all PDF metadata fields."""
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}
    try:
        reader = PdfReader(input_path)
        meta   = {}
        if reader.metadata:
            for k, v in reader.metadata.items():
                meta[k.lstrip("/")] = str(v)
        return {
            "success": True,
            "metadata": meta,
            "page_count": len(reader.pages),
            "encrypted": reader.is_encrypted,
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resolve_pages(pages_str: str, total: int) -> set[int]:
    if pages_str.strip().lower() == "all":
        return set(range(total))
    result = set()
    for part in pages_str.split(","):
        part = part.strip().lower()
        if "-" in part:
            a, b  = part.split("-", 1)
            start = 0 if a == "" else int(a) - 1
            end   = total - 1 if b == "last" else int(b) - 1
            result.update(range(max(0, start), min(total - 1, end) + 1))
        elif part == "last":
            result.add(total - 1)
        elif part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < total:
                result.add(idx)
    return result
