"""
PDForge — core/convert.py
Convert PDF to/from Word, Excel, Images, and HTML.
"""

from __future__ import annotations
import io
import os
from pathlib import Path
from typing import Callable

from PIL import Image
from pypdf import PdfWriter
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas as rl_canvas


# ── PDF → Image ───────────────────────────────────────────────────────────────

def pdf_to_images(
    input_path: str,
    output_dir: str,
    image_format: str = "PNG",     # "PNG" | "JPEG" | "WEBP"
    dpi: int = 150,
    pages: str = "all",
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Convert each PDF page to an image file.

    Returns:
        dict with success, output_files, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    image_format = image_format.upper()
    if image_format not in ("PNG", "JPEG", "WEBP"):
        return {"success": False, "error": "image_format must be PNG, JPEG, or WEBP"}

    try:
        from pdf2image import convert_from_path
        from pypdf import PdfReader

        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        target    = _resolve_pages(pages, num_pages)
        target_sorted = sorted(target)

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        stem         = Path(input_path).stem
        output_files = []
        ext          = image_format.lower().replace("jpeg", "jpg")

        # Convert only targeted pages; pdf2image uses 1-based
        page_numbers_1based = [p + 1 for p in target_sorted]
        images = convert_from_path(
            input_path,
            dpi=dpi,
            first_page=min(page_numbers_1based),
            last_page=max(page_numbers_1based),
        )

        # Filter only the ones in target
        img_iter = iter(images)
        min_pg   = min(page_numbers_1based)
        img_map  = {}
        for offset, img in enumerate(images):
            pg_1based = min_pg + offset
            if (pg_1based - 1) in target:
                img_map[pg_1based - 1] = img

        total = len(img_map)
        for step, pg_idx in enumerate(target_sorted):
            img = img_map.get(pg_idx)
            if img is None:
                continue
            out_path = os.path.join(output_dir, f"{stem}_page{pg_idx + 1:04d}.{ext}")
            if image_format == "JPEG" and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(out_path, format=image_format, dpi=(dpi, dpi))
            output_files.append(out_path)
            if progress_cb:
                progress_cb(step + 1, total)

        return {"success": True, "output_files": output_files, "error": None}

    except ImportError:
        return {
            "success": False,
            "error": "pdf2image requires poppler installed on your system. "
                     "Windows: download poppler from https://github.com/oschwartz10612/poppler-windows "
                     "Linux: sudo apt install poppler-utils",
        }
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ── Image → PDF ───────────────────────────────────────────────────────────────

def images_to_pdf(
    image_paths: list[str],
    output_path: str,
    page_size: str = "A4",          # "A4" | "letter" | "fit"
    dpi: int = 150,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Convert a list of images to a single PDF.

    Args:
        page_size: "A4" | "letter" | "fit" (fit page to image size)

    Returns:
        dict with success, output_path, error
    """
    if not image_paths:
        return {"success": False, "error": "No images provided."}

    size_map = {"A4": A4, "letter": letter}

    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        images_pil = []

        for i, path in enumerate(image_paths):
            if not os.path.isfile(path):
                return {"success": False, "error": f"Image not found: {path}"}
            img = Image.open(path)
            if img.mode in ("RGBA", "P"):
                bg  = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")
            images_pil.append(img)
            if progress_cb:
                progress_cb(i + 1, len(image_paths))

        if not images_pil:
            return {"success": False, "error": "No valid images to convert."}

        if page_size == "fit":
            # Each image defines its own page size
            buf    = io.BytesIO()
            first  = images_pil[0]
            pw, ph = first.width * (72 / dpi), first.height * (72 / dpi)
            c      = rl_canvas.Canvas(buf, pagesize=(pw, ph))
            for idx, img in enumerate(images_pil):
                pw = img.width  * (72 / dpi)
                ph = img.height * (72 / dpi)
                c.setPageSize((pw, ph))
                img_buf = io.BytesIO()
                img.save(img_buf, "JPEG", quality=92)
                img_buf.seek(0)
                c.drawImage(rl_canvas.ImageReader(img_buf), 0, 0, pw, ph)
                if idx < len(images_pil) - 1:
                    c.showPage()
            c.save()
            buf.seek(0)
            with open(output_path, "wb") as f:
                f.write(buf.getvalue())
        else:
            pw, ph = size_map.get(page_size, A4)
            buf = io.BytesIO()
            c   = rl_canvas.Canvas(buf, pagesize=(pw, ph))
            for idx, img in enumerate(images_pil):
                # Fit image inside page with margins
                margin   = 20
                max_w    = pw - 2 * margin
                max_h    = ph - 2 * margin
                scale    = min(max_w / img.width, max_h / img.height) * (72 / dpi)
                draw_w   = img.width  * scale
                draw_h   = img.height * scale
                x        = (pw - draw_w) / 2
                y        = (ph - draw_h) / 2
                img_buf  = io.BytesIO()
                img.save(img_buf, "JPEG", quality=92)
                img_buf.seek(0)
                c.drawImage(rl_canvas.ImageReader(img_buf), x, y, draw_w, draw_h)
                if idx < len(images_pil) - 1:
                    c.showPage()
            c.save()
            buf.seek(0)
            with open(output_path, "wb") as f:
                f.write(buf.getvalue())

        return {"success": True, "output_path": output_path, "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ── PDF → Word ────────────────────────────────────────────────────────────────

def pdf_to_word(
    input_path: str,
    output_path: str,
    pages: str = "all",
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Convert PDF to Word (.docx) using pdf2docx.

    Returns:
        dict with success, output_path, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    try:
        from pdf2docx import Converter

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if progress_cb:
            progress_cb(1, 3)

        cv = Converter(input_path)

        if progress_cb:
            progress_cb(2, 3)

        if pages.strip().lower() == "all":
            cv.convert(output_path, multi_processing=False)
        else:
            from pypdf import PdfReader
            num_pages = len(PdfReader(input_path).pages)
            idxs      = sorted(_resolve_pages(pages, num_pages))
            start     = idxs[0]
            end       = idxs[-1] + 1
            cv.convert(output_path, start=start, end=end, multi_processing=False)

        cv.close()

        if progress_cb:
            progress_cb(3, 3)

        return {"success": True, "output_path": output_path, "error": None}

    except ImportError:
        return {"success": False, "error": "pdf2docx is not installed. Run: pip install pdf2docx"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ── PDF → Excel ───────────────────────────────────────────────────────────────

def pdf_to_excel(
    input_path: str,
    output_path: str,
    pages: str = "all",
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Extract tables from PDF and save to Excel.
    Delegates to core/extract.py:extract_tables.

    Returns:
        dict with success, output_path, table_count, error
    """
    from core.extract import extract_tables
    return extract_tables(input_path, output_path, pages=pages, progress_cb=progress_cb)


# ── PDF → Text ────────────────────────────────────────────────────────────────

def pdf_to_text(
    input_path: str,
    output_path: str,
    pages: str = "all",
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """Convenience wrapper for text extraction to file."""
    from core.extract import extract_text
    return extract_text(input_path, output_path, pages=pages, progress_cb=progress_cb)


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
