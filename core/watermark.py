"""
PDForge — core/watermark.py
Add text or image watermarks to PDF files.
"""

from __future__ import annotations
import io
import os
from pathlib import Path
from typing import Callable

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as rl_canvas
from PIL import Image as PILImage


def add_text_watermark(
    input_path: str,
    output_path: str,
    text: str,
    font_size: int = 48,
    color_hex: str = "#FF0000",
    opacity: float = 0.25,
    angle: int = 45,
    position: str = "center",   # "center" | "top-left" | "top-right" | "bottom-left" | "bottom-right" | "tile"
    pages: str = "all",          # "all" | "1-3,5" range string
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Overlay a text watermark on every specified page.

    Returns:
        dict with success, output_path, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}
    if not text.strip():
        return {"success": False, "error": "Watermark text cannot be empty."}
    if not 0.0 <= opacity <= 1.0:
        return {"success": False, "error": "Opacity must be between 0.0 and 1.0."}

    try:
        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        target    = _resolve_pages(pages, num_pages)

        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            if i in target:
                pw  = float(page.mediabox.width)
                ph  = float(page.mediabox.height)
                wm  = _build_text_watermark_page(
                    text, font_size, color_hex, opacity, angle, position, pw, ph
                )
                page.merge_page(wm)
            writer.add_page(page)
            if progress_cb:
                progress_cb(i + 1, num_pages)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        return {"success": True, "output_path": output_path, "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def add_image_watermark(
    input_path: str,
    output_path: str,
    image_path: str,
    opacity: float = 0.30,
    position: str = "center",
    scale: float = 0.4,
    pages: str = "all",
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Overlay an image (PNG/JPEG) watermark on specified pages.

    Returns:
        dict with success, output_path, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}
    if not os.path.isfile(image_path):
        return {"success": False, "error": f"Image not found: {image_path}"}

    try:
        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        target    = _resolve_pages(pages, num_pages)

        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            if i in target:
                pw = float(page.mediabox.width)
                ph = float(page.mediabox.height)
                wm = _build_image_watermark_page(image_path, opacity, position, scale, pw, ph)
                page.merge_page(wm)
            writer.add_page(page)
            if progress_cb:
                progress_cb(i + 1, num_pages)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        return {"success": True, "output_path": output_path, "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ── Internal builders ─────────────────────────────────────────────────────────

def _build_text_watermark_page(text, font_size, color_hex, opacity, angle, position, pw, ph):
    """Create a single-page PDF with the text watermark, return as pypdf page."""
    buf = io.BytesIO()
    c   = rl_canvas.Canvas(buf, pagesize=(pw, ph))
    c.setPageSize((pw, ph))

    try:
        color = HexColor(color_hex)
    except Exception:
        color = HexColor("#FF0000")

    c.setFillColor(color, alpha=opacity)
    c.setFont("Helvetica-Bold", font_size)

    if position == "tile":
        # Tile the watermark across the page
        c.saveState()
        c.rotate(angle)
        step_x = font_size * (len(text) * 0.6 + 4)
        step_y = font_size * 2.5
        for x in range(-int(pw), int(pw * 2), int(step_x)):
            for y in range(-int(ph), int(ph * 2), int(step_y)):
                c.drawString(x, y, text)
        c.restoreState()
    else:
        x, y = _get_text_position(position, pw, ph, font_size, len(text))
        c.saveState()
        c.translate(x, y)
        c.rotate(angle)
        c.drawCentredString(0, 0, text)
        c.restoreState()

    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def _build_image_watermark_page(image_path, opacity, position, scale, pw, ph):
    """Create a single-page PDF with the image watermark, return as pypdf page."""
    img     = PILImage.open(image_path).convert("RGBA")
    img_w   = pw * scale
    img_h   = img.height * (img_w / img.width)

    # Apply opacity to alpha channel
    r, g, b, a = img.split()
    a = a.point(lambda x: int(x * opacity))
    img.putalpha(a)

    # Convert back to RGB for PDF embedding
    bg   = PILImage.new("RGB", img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[3])

    img_buf = io.BytesIO()
    bg.save(img_buf, "PNG")
    img_buf.seek(0)

    buf = io.BytesIO()
    c   = rl_canvas.Canvas(buf, pagesize=(pw, ph))
    x, y = _get_image_position(position, pw, ph, img_w, img_h)
    c.drawImage(
        rl_canvas.ImageReader(img_buf),
        x, y, img_w, img_h,
        mask="auto",
    )
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def _get_text_position(position, pw, ph, font_size, text_len):
    text_w = font_size * text_len * 0.55
    positions = {
        "center":       (pw / 2, ph / 2),
        "top-left":     (text_w / 2 + 20, ph - font_size - 20),
        "top-right":    (pw - text_w / 2 - 20, ph - font_size - 20),
        "bottom-left":  (text_w / 2 + 20, font_size + 20),
        "bottom-right": (pw - text_w / 2 - 20, font_size + 20),
    }
    return positions.get(position, (pw / 2, ph / 2))


def _get_image_position(position, pw, ph, img_w, img_h):
    positions = {
        "center":       ((pw - img_w) / 2, (ph - img_h) / 2),
        "top-left":     (20, ph - img_h - 20),
        "top-right":    (pw - img_w - 20, ph - img_h - 20),
        "bottom-left":  (20, 20),
        "bottom-right": (pw - img_w - 20, 20),
    }
    return positions.get(position, ((pw - img_w) / 2, (ph - img_h) / 2))


def _resolve_pages(pages_str: str, total: int) -> set[int]:
    """Parse 'all' or range string to 0-based page index set."""
    if pages_str.strip().lower() == "all":
        return set(range(total))
    result = set()
    for part in pages_str.split(","):
        part = part.strip().lower()
        if "-" in part:
            a, b = part.split("-", 1)
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
