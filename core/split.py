"""
PDForge — core/split.py
Split a PDF by page ranges, fixed intervals, or bookmarks.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Callable
from pypdf import PdfReader, PdfWriter


# ── public API ────────────────────────────────────────────────────────────────

def split_by_ranges(
    input_path: str,
    output_dir: str,
    ranges: list[str],
    base_name: str | None = None,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Split PDF into multiple files, one per range string.
    range string format: "1-3"  "5"  "8-last"
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    try:
        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        stem      = base_name or Path(input_path).stem
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_files = []

        for i, rng in enumerate(ranges):
            pages = _parse_range(rng, num_pages)
            if pages is None:
                return {"success": False, "error": f"Invalid range: '{rng}'"}

            writer = PdfWriter()
            for pg in pages:
                writer.add_page(reader.pages[pg])

            out_path = os.path.join(output_dir, f"{stem}_part{i + 1}.pdf")
            with open(out_path, "wb") as f:
                writer.write(f)
            output_files.append(out_path)

            if progress_cb:
                progress_cb(i + 1, len(ranges))

        return {"success": True, "output_files": output_files, "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def split_every_n_pages(
    input_path: str,
    output_dir: str,
    n: int,
    base_name: str | None = None,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """Split PDF into chunks of n pages each."""
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}
    if n < 1:
        return {"success": False, "error": "n must be >= 1"}

    try:
        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        stem      = base_name or Path(input_path).stem
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_files = []
        chunks = list(range(0, num_pages, n))

        for i, start in enumerate(chunks):
            end    = min(start + n, num_pages)
            writer = PdfWriter()
            for pg in range(start, end):
                writer.add_page(reader.pages[pg])

            out_path = os.path.join(output_dir, f"{stem}_part{i + 1}.pdf")
            with open(out_path, "wb") as f:
                writer.write(f)
            output_files.append(out_path)

            if progress_cb:
                progress_cb(i + 1, len(chunks))

        return {"success": True, "output_files": output_files, "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def split_each_page(
    input_path: str,
    output_dir: str,
    base_name: str | None = None,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """Extract every page as a separate PDF file."""
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    try:
        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        stem      = base_name or Path(input_path).stem
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_files = []

        for i in range(num_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])

            out_path = os.path.join(output_dir, f"{stem}_page{i + 1:04d}.pdf")
            with open(out_path, "wb") as f:
                writer.write(f)
            output_files.append(out_path)

            if progress_cb:
                progress_cb(i + 1, num_pages)

        return {"success": True, "output_files": output_files, "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def split_by_bookmarks(
    input_path: str,
    output_dir: str,
    base_name: str | None = None,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """Split PDF at top-level bookmark boundaries."""
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    try:
        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        stem      = base_name or Path(input_path).stem
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Collect top-level bookmarks with their page numbers
        outlines = reader.outline
        sections = _extract_bookmark_sections(reader, outlines, num_pages)

        if not sections:
            return {"success": False, "error": "No bookmarks found in this PDF."}

        output_files = []
        for i, (title, start, end) in enumerate(sections):
            writer = PdfWriter()
            for pg in range(start, end):
                writer.add_page(reader.pages[pg])

            safe_title = "".join(c for c in title if c.isalnum() or c in " _-")[:40].strip()
            out_path   = os.path.join(output_dir, f"{stem}_{i + 1:02d}_{safe_title}.pdf")
            with open(out_path, "wb") as f:
                writer.write(f)
            output_files.append(out_path)

            if progress_cb:
                progress_cb(i + 1, len(sections))

        return {"success": True, "output_files": output_files, "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ── helpers ───────────────────────────────────────────────────────────────────

def _parse_range(range_str: str, total: int) -> list[int] | None:
    result = []
    parts  = [p.strip() for p in range_str.split(",")]
    for part in parts:
        if not part:
            continue
        part_lower = part.lower()
        if "-" in part_lower:
            sub = part_lower.split("-", 1)
            try:
                start = 1 if sub[0] == "" else int(sub[0])
                end   = total if sub[1] == "last" else int(sub[1])
            except ValueError:
                return None
            if start < 1 or end > total or start > end:
                return None
            result.extend(range(start - 1, end))
        else:
            try:
                page_num = total if part_lower == "last" else int(part_lower)
            except ValueError:
                return None
            if page_num < 1 or page_num > total:
                return None
            result.append(page_num - 1)
    return result or None


def _get_page_number(reader: PdfReader, dest) -> int | None:
    try:
        return reader.get_destination_page_number(dest)
    except Exception:
        return None


def _extract_bookmark_sections(
    reader: PdfReader, outlines, total: int
) -> list[tuple[str, int, int]]:
    sections: list[tuple[str, int]] = []

    def _walk(items):
        for item in items:
            if isinstance(item, list):
                _walk(item)
            else:
                pg = _get_page_number(reader, item)
                if pg is not None:
                    title = getattr(item, "title", f"Section_{len(sections)+1}")
                    sections.append((title, pg))

    _walk(outlines)
    sections.sort(key=lambda x: x[1])

    result = []
    for i, (title, start) in enumerate(sections):
        end = sections[i + 1][1] if i + 1 < len(sections) else total
        if start < end:
            result.append((title, start, end))
    return result
