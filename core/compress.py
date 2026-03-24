"""
PDForge — core/compress.py
Compress PDF using pypdf + image downsampling via Pillow.
Ghostscript used as optional high-quality backend when available.
"""

from __future__ import annotations
import io
import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable

from pypdf import PdfReader, PdfWriter
from PIL import Image


QUALITY_PRESETS = {
    "screen":  {"dpi": 72,  "img_quality": 35, "gs_setting": "/screen"},
    "ebook":   {"dpi": 96,  "img_quality": 55, "gs_setting": "/ebook"},
    "printer": {"dpi": 150, "img_quality": 75, "gs_setting": "/printer"},
    "prepress":{"dpi": 300, "img_quality": 90, "gs_setting": "/prepress"},
}


def compress_pdf(
    input_path: str,
    output_path: str,
    preset: str = "ebook",
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Compress PDF file.
    Tries Ghostscript first; falls back to pure-Python image re-compression.

    Args:
        input_path:  source PDF
        output_path: destination PDF
        preset:      "screen" | "ebook" | "printer" | "prepress"
        progress_cb: callback(current, total)

    Returns:
        dict with success, output_path, original_size, compressed_size, ratio, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    if preset not in QUALITY_PRESETS:
        return {"success": False, "error": f"Unknown preset '{preset}'. Choose from: {list(QUALITY_PRESETS)}"}

    original_size = os.path.getsize(input_path)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Try Ghostscript first — better compression
    if _ghostscript_available():
        result = _compress_ghostscript(input_path, output_path, preset, progress_cb)
    else:
        result = _compress_pypdf(input_path, output_path, preset, progress_cb)

    if result["success"]:
        compressed_size = os.path.getsize(output_path)
        ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        result.update({
            "original_size":    original_size,
            "compressed_size":  compressed_size,
            "ratio":            round(ratio, 1),
            "output_path":      output_path,
        })

    return result


# ── Ghostscript backend ────────────────────────────────────────────────────────

def _ghostscript_available() -> bool:
    for cmd in ("gs", "gswin64c", "gswin32c"):
        if shutil.which(cmd):
            return True
    return False


def _get_gs_cmd() -> str:
    for cmd in ("gs", "gswin64c", "gswin32c"):
        if shutil.which(cmd):
            return cmd
    return "gs"


def _compress_ghostscript(
    input_path: str,
    output_path: str,
    preset: str,
    progress_cb: Callable | None,
) -> dict:
    gs_setting = QUALITY_PRESETS[preset]["gs_setting"]
    cmd = [
        _get_gs_cmd(),
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.5",
        f"-dPDFSETTINGS={gs_setting}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path,
    ]
    try:
        if progress_cb:
            progress_cb(1, 2)
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
        if progress_cb:
            progress_cb(2, 2)
        return {"success": True, "backend": "ghostscript", "error": None}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": f"Ghostscript error: {e.stderr.decode(errors='replace')}"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ── Pure-Python fallback ───────────────────────────────────────────────────────

def _compress_pypdf(
    input_path: str,
    output_path: str,
    preset: str,
    progress_cb: Callable | None,
) -> dict:
    cfg = QUALITY_PRESETS[preset]
    dpi          = cfg["dpi"]
    img_quality  = cfg["img_quality"]

    try:
        reader    = PdfReader(input_path)
        writer    = PdfWriter()
        num_pages = len(reader.pages)

        for i, page in enumerate(reader.pages):
            # Compress page content streams
            page.compress_content_streams()

            # Re-compress embedded images
            _recompress_page_images(page, dpi, img_quality)

            writer.add_page(page)

            if progress_cb:
                progress_cb(i + 1, num_pages)

        # Remove duplicate objects
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

        with open(output_path, "wb") as f:
            writer.write(f)

        return {"success": True, "backend": "pypdf", "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def _recompress_page_images(page, dpi: int, quality: int):
    """Downsample and re-compress all images on a page."""
    try:
        if "/Resources" not in page:
            return
        resources = page["/Resources"]
        if "/XObject" not in resources:
            return
        xobject = resources["/XObject"].get_object()

        for obj_name in list(xobject.keys()):
            obj = xobject[obj_name].get_object()
            if obj.get("/Subtype") != "/Image":
                continue

            try:
                data   = obj.get_data()
                width  = int(obj["/Width"])
                height = int(obj["/Height"])

                # Reconstruct PIL image
                cs = str(obj.get("/ColorSpace", "/DeviceRGB"))
                mode = "RGB" if "RGB" in cs else ("L" if "Gray" in cs or "Grey" in cs else "RGB")
                img  = Image.frombytes(mode, (width, height), data)

                # Optionally downsample large images
                if width > dpi * 8 or height > dpi * 8:
                    factor = min(dpi * 8 / width, dpi * 8 / height)
                    new_w  = max(1, int(width * factor))
                    new_h  = max(1, int(height * factor))
                    img    = img.resize((new_w, new_h), Image.LANCZOS)

                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=quality, optimize=True)
                buf.seek(0)

                obj._data        = buf.read()
                obj["/Filter"]   = "/DCTDecode"
                obj["/Width"]    = img.width
                obj["/Height"]   = img.height
                obj["/Length"]   = len(obj._data)
                if "/DecodeParms" in obj:
                    del obj["/DecodeParms"]

            except Exception:
                # Skip images that can't be recompressed; don't crash
                continue

    except Exception:
        pass
