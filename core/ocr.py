"""
PDForge — core/ocr.py
OCR scanned PDFs using Tesseract + pdf2image.
Produces a searchable PDF with embedded text layer.
"""

from __future__ import annotations
import io
import os
import shutil
from pathlib import Path
from typing import Callable


SUPPORTED_LANGS = {
    "eng": "English",
    "ara": "Arabic",
    "fra": "French",
    "deu": "German",
    "spa": "Spanish",
    "ita": "Italian",
    "por": "Portuguese",
    "rus": "Russian",
    "chi_sim": "Chinese (Simplified)",
    "chi_tra": "Chinese (Traditional)",
    "jpn": "Japanese",
    "kor": "Korean",
}


def check_dependencies() -> dict:
    """Check if Tesseract and poppler are available."""
    tesseract = shutil.which("tesseract") is not None
    poppler   = shutil.which("pdftoppm") is not None or shutil.which("pdftocairo") is not None
    return {
        "tesseract": tesseract,
        "poppler":   poppler,
        "ready":     tesseract and poppler,
    }


def ocr_pdf(
    input_path: str,
    output_path: str,
    languages: list[str] | None = None,
    dpi: int = 200,
    pages: str = "all",
    output_type: str = "searchable_pdf",   # "searchable_pdf" | "text" | "both"
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Run OCR on a PDF and produce a searchable PDF and/or plain text.

    Args:
        languages:    list of Tesseract lang codes e.g. ["eng", "ara"]
        dpi:          rendering DPI for page images (higher = better accuracy, slower)
        pages:        "all" or range string
        output_type:  "searchable_pdf" | "text" | "both"

    Returns:
        dict with success, output_path, text_path, page_count, error
    """
    deps = check_dependencies()
    if not deps["ready"]:
        missing = []
        if not deps["tesseract"]:
            missing.append("Tesseract OCR (https://github.com/tesseract-ocr/tesseract)")
        if not deps["poppler"]:
            missing.append("Poppler utils (Linux: apt install poppler-utils)")
        return {
            "success": False,
            "error": "Missing dependencies:\n" + "\n".join(f"  • {m}" for m in missing),
        }

    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    languages = languages or ["eng"]
    lang_str  = "+".join(languages)

    try:
        import pytesseract
        from pdf2image import convert_from_path
        from pypdf import PdfReader, PdfWriter
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.colors import white

        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        target    = _resolve_pages(pages, num_pages)
        target_sorted = sorted(target)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        stem = Path(output_path).stem

        # Render PDF pages to images
        images = convert_from_path(
            input_path,
            dpi=dpi,
            first_page=target_sorted[0] + 1,
            last_page=target_sorted[-1] + 1,
        )

        # Map rendered images back to page indices
        min_pg  = target_sorted[0]
        img_map = {}
        for offset, img in enumerate(images):
            pg = min_pg + offset
            if pg in target:
                img_map[pg] = img

        all_text = []
        writer   = PdfWriter()

        # Add non-OCR pages from original first (maintain structure)
        for pg_idx in range(num_pages):
            if pg_idx not in target:
                writer.add_page(reader.pages[pg_idx])
            else:
                img = img_map.get(pg_idx)
                if img is None:
                    writer.add_page(reader.pages[pg_idx])
                    continue

                # Run OCR
                ocr_data = pytesseract.image_to_data(
                    img,
                    lang=lang_str,
                    output_type=pytesseract.Output.DICT,
                    config="--psm 3",
                )

                page_text = pytesseract.image_to_string(img, lang=lang_str)
                all_text.append(f"--- Page {pg_idx + 1} ---\n{page_text}\n")

                # Build searchable PDF page: image + invisible text layer
                if output_type in ("searchable_pdf", "both"):
                    pdf_page = _build_searchable_page(img, ocr_data, dpi)
                    writer.add_page(pdf_page)
                else:
                    writer.add_page(reader.pages[pg_idx])

            if progress_cb:
                progress_cb(pg_idx + 1, num_pages)

        result = {"success": True, "error": None, "page_count": len(target)}

        if output_type in ("searchable_pdf", "both"):
            with open(output_path, "wb") as f:
                writer.write(f)
            result["output_path"] = output_path

        if output_type in ("text", "both"):
            text_path = str(Path(output_path).with_suffix(".txt"))
            with open(text_path, "w", encoding="utf-8") as f:
                f.write("\n".join(all_text))
            result["text_path"] = text_path

        return result

    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_searchable_page(img, ocr_data: dict, dpi: int):
    """
    Build a PDF page with the image rendered full-page
    and an invisible text layer positioned over each word.
    """
    import io
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.colors import white
    from pypdf import PdfReader as _Reader

    img_w_px, img_h_px = img.size
    scale  = 72.0 / dpi
    pw     = img_w_px * scale
    ph     = img_h_px * scale

    buf = io.BytesIO()
    c   = rl_canvas.Canvas(buf, pagesize=(pw, ph))

    # Draw full image
    img_buf = io.BytesIO()
    img.save(img_buf, "JPEG", quality=90)
    img_buf.seek(0)
    c.drawImage(rl_canvas.ImageReader(img_buf), 0, 0, pw, ph)

    # Invisible text layer
    n_boxes = len(ocr_data.get("text", []))
    for i in range(n_boxes):
        word = (ocr_data["text"][i] or "").strip()
        conf = int(ocr_data["conf"][i])
        if not word or conf < 30:
            continue

        x_px = ocr_data["left"][i]
        y_px = ocr_data["top"][i]
        w_px = ocr_data["width"][i]
        h_px = ocr_data["height"][i]

        if w_px <= 0 or h_px <= 0:
            continue

        x_pt  = x_px * scale
        y_pt  = ph - (y_px + h_px) * scale
        w_pt  = w_px * scale
        h_pt  = h_px * scale
        fs    = max(6, h_pt * 0.9)

        c.setFillColor(white, alpha=0.0)
        c.setFont("Helvetica", fs)
        try:
            c.drawString(x_pt, y_pt, word)
        except Exception:
            pass

    c.save()
    buf.seek(0)
    return _Reader(buf).pages[0]


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
