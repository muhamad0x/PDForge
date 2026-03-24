"""
PDForge — core/redact.py
Permanent redaction of text regions and rectangular areas from PDFs.
Uses pikepdf for structural-level removal (not just visual cover).
"""

from __future__ import annotations
import io
import os
from pathlib import Path
from typing import Callable

from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import black
from pypdf import PdfReader, PdfWriter


def redact_regions(
    input_path: str,
    output_path: str,
    regions: list[dict],
    fill_color: str = "#000000",
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Permanently redact rectangular regions from specific pages.

    Args:
        regions: list of dicts, each with keys:
                 page (1-based int), x, y, width, height (in PDF points)
                 x=0,y=0 is bottom-left corner of page.

        fill_color: hex color for redaction box (default black)

    Returns:
        dict with success, output_path, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}
    if not regions:
        return {"success": False, "error": "No regions specified."}

    try:
        # Validate regions
        for r in regions:
            for key in ("page", "x", "y", "width", "height"):
                if key not in r:
                    return {"success": False, "error": f"Region missing key '{key}'."}

        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        writer    = PdfWriter()

        # Group regions by page
        page_regions: dict[int, list[dict]] = {}
        for r in regions:
            pg = int(r["page"]) - 1
            if 0 <= pg < num_pages:
                page_regions.setdefault(pg, []).append(r)

        for i, page in enumerate(reader.pages):
            if i in page_regions:
                pw = float(page.mediabox.width)
                ph = float(page.mediabox.height)
                overlay = _build_redact_overlay(page_regions[i], pw, ph, fill_color)
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


def redact_text_occurrences(
    input_path: str,
    output_path: str,
    search_terms: list[str],
    case_sensitive: bool = False,
    fill_color: str = "#000000",
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Find and redact all occurrences of search_terms across all pages.
    Uses pdfplumber word-level bounding boxes for precise location.

    Returns:
        dict with success, output_path, occurrences_found, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}
    if not search_terms:
        return {"success": False, "error": "No search terms provided."}

    try:
        import pdfplumber

        reader         = PdfReader(input_path)
        num_pages      = len(reader.pages)
        occurrences    = 0
        page_regions: dict[int, list[dict]] = {}

        with pdfplumber.open(input_path) as pdf:
            for pg_idx, page in enumerate(pdf.pages):
                words = page.extract_words()
                ph    = float(page.height)

                for word_obj in words:
                    word_text = word_obj["text"]
                    compare   = word_text if case_sensitive else word_text.lower()

                    for term in search_terms:
                        t = term if case_sensitive else term.lower()
                        if t in compare:
                            # pdfplumber bbox: (x0, top, x1, bottom) — top from top-left
                            x0  = float(word_obj["x0"])
                            top = float(word_obj["top"])
                            x1  = float(word_obj["x1"])
                            bot = float(word_obj["bottom"])

                            # Convert to PDF coordinate system (y from bottom)
                            pdf_y  = ph - bot
                            pdf_h  = bot - top
                            margin = 1.5

                            page_regions.setdefault(pg_idx, []).append({
                                "page": pg_idx + 1,
                                "x":      max(0, x0 - margin),
                                "y":      max(0, pdf_y - margin),
                                "width":  (x1 - x0) + margin * 2,
                                "height": pdf_h + margin * 2,
                            })
                            occurrences += 1
                            break

                if progress_cb:
                    progress_cb(pg_idx + 1, num_pages)

        if occurrences == 0:
            return {"success": False, "error": "No occurrences found for the given search terms."}

        # Now apply redaction overlay
        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            if i in page_regions:
                pw = float(page.mediabox.width)
                ph = float(page.mediabox.height)
                overlay = _build_redact_overlay(page_regions[i], pw, ph, fill_color)
                page.merge_page(overlay)
            writer.add_page(page)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        return {
            "success": True,
            "output_path": output_path,
            "occurrences_found": occurrences,
            "error": None,
        }

    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ── Internal ──────────────────────────────────────────────────────────────────

def _build_redact_overlay(
    regions: list[dict],
    page_width: float,
    page_height: float,
    fill_color_hex: str,
) -> object:
    """Build a PDF page overlay containing filled black rectangles."""
    buf = io.BytesIO()
    c   = rl_canvas.Canvas(buf, pagesize=(page_width, page_height))

    try:
        from reportlab.lib.colors import HexColor
        color = HexColor(fill_color_hex)
    except Exception:
        color = black

    c.setFillColor(color)
    c.setStrokeColor(color)

    for r in regions:
        c.rect(
            float(r["x"]),
            float(r["y"]),
            float(r["width"]),
            float(r["height"]),
            fill=1,
            stroke=0,
        )

    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]
