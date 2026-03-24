"""
PDForge — core/number.py
Add page numbers and headers/footers to PDF files.
"""

from __future__ import annotations
import io
import os
from pathlib import Path
from typing import Callable

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import HexColor, black


def add_page_numbers(
    input_path: str,
    output_path: str,
    position: str = "bottom-center",  # "bottom-center"|"bottom-right"|"bottom-left"|"top-center"|"top-right"|"top-left"
    start_number: int = 1,
    prefix: str = "",
    suffix: str = "",
    font_size: int = 11,
    color_hex: str = "#333333",
    margin: int = 20,
    skip_pages: str = "",             # pages to leave unnumbered e.g. "1" or "1-2"
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Add page numbers to all (or specified) pages.

    Returns:
        dict with success, output_path, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    try:
        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        skip      = _resolve_pages(skip_pages, num_pages) if skip_pages.strip() else set()
        writer    = PdfWriter()

        page_counter = start_number

        for i, page in enumerate(reader.pages):
            if i not in skip:
                pw    = float(page.mediabox.width)
                ph    = float(page.mediabox.height)
                label = f"{prefix}{page_counter}{suffix}"
                overlay = _build_number_overlay(
                    label, position, pw, ph, font_size, color_hex, margin
                )
                page.merge_page(overlay)
                page_counter += 1
            writer.add_page(page)
            if progress_cb:
                progress_cb(i + 1, num_pages)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        return {"success": True, "output_path": output_path, "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def add_header_footer(
    input_path: str,
    output_path: str,
    header_text: str = "",
    footer_text: str = "",
    font_size: int = 10,
    color_hex: str = "#333333",
    margin: int = 15,
    pages: str = "all",
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Add header and/or footer text to specified pages.
    Use {page} and {total} placeholders in text strings.

    Returns:
        dict with success, output_path, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}
    if not header_text and not footer_text:
        return {"success": False, "error": "Provide header_text and/or footer_text."}

    try:
        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        target    = _resolve_pages(pages, num_pages)
        writer    = PdfWriter()

        for i, page in enumerate(reader.pages):
            if i in target:
                pw = float(page.mediabox.width)
                ph = float(page.mediabox.height)

                header = header_text.replace("{page}", str(i + 1)).replace("{total}", str(num_pages))
                footer = footer_text.replace("{page}", str(i + 1)).replace("{total}", str(num_pages))

                overlay = _build_header_footer_overlay(
                    header, footer, pw, ph, font_size, color_hex, margin
                )
                page.merge_page(overlay)
            writer.add_page(page)
            if progress_cb:
                progress_cb(i + 1, num_pages)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        return {"success": True, "output_path": output_path, "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ── Builders ──────────────────────────────────────────────────────────────────

def _build_number_overlay(label, position, pw, ph, font_size, color_hex, margin):
    buf = io.BytesIO()
    c   = rl_canvas.Canvas(buf, pagesize=(pw, ph))
    try:
        color = HexColor(color_hex)
    except Exception:
        color = black

    c.setFillColor(color)
    c.setFont("Helvetica", font_size)

    x, y = _resolve_position(position, pw, ph, margin)

    if "center" in position:
        c.drawCentredString(x, y, label)
    elif "right" in position:
        c.drawRightString(x, y, label)
    else:
        c.drawString(x, y, label)

    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def _build_header_footer_overlay(header, footer, pw, ph, font_size, color_hex, margin):
    buf = io.BytesIO()
    c   = rl_canvas.Canvas(buf, pagesize=(pw, ph))
    try:
        color = HexColor(color_hex)
    except Exception:
        color = black

    c.setFillColor(color)
    c.setFont("Helvetica", font_size)

    if header:
        c.drawCentredString(pw / 2, ph - margin - font_size, header)
        # Separator line
        c.setStrokeColor(color, alpha=0.3)
        c.line(margin * 2, ph - margin - font_size - 4, pw - margin * 2, ph - margin - font_size - 4)

    if footer:
        c.drawCentredString(pw / 2, margin, footer)
        c.setStrokeColor(color, alpha=0.3)
        c.line(margin * 2, margin + font_size + 4, pw - margin * 2, margin + font_size + 4)

    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def _resolve_position(position: str, pw: float, ph: float, margin: int) -> tuple[float, float]:
    positions = {
        "bottom-center": (pw / 2,  margin),
        "bottom-right":  (pw - margin, margin),
        "bottom-left":   (margin, margin),
        "top-center":    (pw / 2,  ph - margin - 12),
        "top-right":     (pw - margin, ph - margin - 12),
        "top-left":      (margin, ph - margin - 12),
    }
    return positions.get(position, (pw / 2, margin))


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
