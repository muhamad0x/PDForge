"""PDF page count + raster preview via pypdfium2 (bundled with pdfplumber)."""

from __future__ import annotations

from typing import Optional

from PIL import Image


def pdf_page_count(path: str) -> int:
    if not path:
        return 0
    try:
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(path)
        try:
            return len(doc)
        finally:
            doc.close()
    except Exception:
        try:
            from pypdf import PdfReader
            return len(PdfReader(path).pages)
        except Exception:
            return 0


def render_page_pil(path: str, page_0based: int, max_side: int = 280) -> Optional[Image.Image]:
    """Render one page to RGB PIL; returns None on failure or out of range."""
    if not path or page_0based < 0:
        return None
    try:
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(path)
        try:
            if page_0based >= len(doc):
                return None
            page = doc[page_0based]
            pil = page.render(scale=1.15, prefer_bgrx=True).to_pil().convert("RGB")
        finally:
            doc.close()
        w, h = pil.size
        m = max(w, h)
        if m > max_side:
            s = max_side / m
            pil = pil.resize((max(1, int(w * s)), max(1, int(h * s))), Image.Resampling.LANCZOS)
        return pil
    except Exception:
        return None
