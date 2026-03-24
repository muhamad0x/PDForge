"""
PDForge — core/repair.py + core/metadata.py combined
Repair corrupted PDFs and edit/strip metadata.
"""

from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable

from pypdf import PdfReader, PdfWriter
from pypdf.generic import create_string_object


# ═══════════════════════════════════════════════════════════════════════════
# REPAIR
# ═══════════════════════════════════════════════════════════════════════════

def repair_pdf(
    input_path: str,
    output_path: str,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Attempt to repair a corrupted or malformed PDF.
    Uses qpdf when available, falls back to pypdf reconstruct.

    Returns:
        dict with success, output_path, method, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if _qpdf_available():
        return _repair_qpdf(input_path, output_path, progress_cb)
    return _repair_pypdf(input_path, output_path, progress_cb)


def _qpdf_available() -> bool:
    return shutil.which("qpdf") is not None


def _repair_qpdf(input_path, output_path, progress_cb):
    if progress_cb:
        progress_cb(1, 2)
    cmd = [
        "qpdf", "--replace-input",
        "--linearize",
        input_path,
        output_path,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=60)
        if progress_cb:
            progress_cb(2, 2)
        return {"success": True, "output_path": output_path, "method": "qpdf", "error": None}
    except subprocess.CalledProcessError as e:
        # qpdf exit code 3 = warnings only — still success
        if e.returncode == 3:
            return {"success": True, "output_path": output_path, "method": "qpdf", "error": None}
        err = e.stderr.decode(errors="replace") if e.stderr else str(e)
        return {"success": False, "error": f"qpdf: {err}"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def _repair_pypdf(input_path, output_path, progress_cb):
    try:
        if progress_cb:
            progress_cb(1, 3)
        reader = PdfReader(input_path, strict=False)
        if progress_cb:
            progress_cb(2, 3)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)
        if progress_cb:
            progress_cb(3, 3)
        return {"success": True, "output_path": output_path, "method": "pypdf", "error": None}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ═══════════════════════════════════════════════════════════════════════════
# METADATA
# ═══════════════════════════════════════════════════════════════════════════

METADATA_FIELDS = [
    "Title", "Author", "Subject", "Keywords",
    "Creator", "Producer", "CreationDate", "ModDate",
]


def get_metadata(input_path: str, password: str = "") -> dict:
    """Read all metadata from a PDF."""
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}
    try:
        reader = PdfReader(input_path)
        if reader.is_encrypted:
            if not password:
                return {"success": False, "error": "PDF is encrypted. Provide password."}
            if reader.decrypt(password) == 0:
                return {"success": False, "error": "Incorrect password."}
        meta = {}
        if reader.metadata:
            for k, v in reader.metadata.items():
                meta[k.lstrip("/")] = str(v) if v is not None else ""
        return {"success": True, "metadata": meta, "error": None}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def set_metadata(
    input_path: str,
    output_path: str,
    updates: dict[str, str],
    strip_existing: bool = False,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Set or update PDF metadata fields.

    Args:
        updates:        dict of field→value e.g. {"Title": "My Doc", "Author": "John"}
        strip_existing: if True, remove all existing metadata before applying updates

    Returns:
        dict with success, output_path, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()

        if progress_cb:
            progress_cb(1, 3)

        for page in reader.pages:
            writer.add_page(page)

        if progress_cb:
            progress_cb(2, 3)

        if strip_existing:
            meta = {f"/{k}": "" for k in METADATA_FIELDS}
        else:
            meta = {}
            if reader.metadata:
                for k, v in reader.metadata.items():
                    meta[k] = str(v) if v is not None else ""

        for k, v in updates.items():
            key = f"/{k}" if not k.startswith("/") else k
            meta[key] = v

        writer.add_metadata(meta)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        if progress_cb:
            progress_cb(3, 3)

        return {"success": True, "output_path": output_path, "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def strip_metadata(
    input_path: str,
    output_path: str,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """Remove all metadata from a PDF (privacy cleanup)."""
    return set_metadata(
        input_path, output_path,
        updates={},
        strip_existing=True,
        progress_cb=progress_cb,
    )
