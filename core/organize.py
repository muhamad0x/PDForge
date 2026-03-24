"""
PDForge — core/organize.py
Rotate, reorder, delete pages inside a PDF.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Callable

from pypdf import PdfReader, PdfWriter


def rotate_pages(
    input_path: str,
    output_path: str,
    rotation: int,                   # 90 | 180 | 270
    pages: str = "all",
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Rotate specified pages by rotation degrees (clockwise).

    Args:
        rotation:  90 | 180 | 270
        pages:     "all" or range string "1-3,5"

    Returns:
        dict with success, output_path, error
    """
    if rotation not in (90, 180, 270):
        return {"success": False, "error": "Rotation must be 90, 180, or 270."}
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    try:
        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        target    = _resolve_pages(pages, num_pages)
        writer    = PdfWriter()

        for i, page in enumerate(reader.pages):
            if i in target:
                page.rotate(rotation)
            writer.add_page(page)
            if progress_cb:
                progress_cb(i + 1, num_pages)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        return {"success": True, "output_path": output_path, "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def reorder_pages(
    input_path: str,
    output_path: str,
    new_order: list[int],            # 1-based page numbers in desired order
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Reorder pages according to new_order list (1-based indices).
    Duplicate indices = duplicate pages. Omit index = delete page.

    Returns:
        dict with success, output_path, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}
    if not new_order:
        return {"success": False, "error": "new_order cannot be empty."}

    try:
        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)

        for idx in new_order:
            if idx < 1 or idx > num_pages:
                return {
                    "success": False,
                    "error": f"Page number {idx} is out of range (document has {num_pages} pages).",
                }

        writer = PdfWriter()
        total  = len(new_order)

        for step, page_num in enumerate(new_order):
            writer.add_page(reader.pages[page_num - 1])
            if progress_cb:
                progress_cb(step + 1, total)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        return {"success": True, "output_path": output_path, "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def delete_pages(
    input_path: str,
    output_path: str,
    pages_to_delete: str,            # range string "1-3,5"
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Delete specified pages from a PDF.

    Returns:
        dict with success, output_path, pages_removed, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    try:
        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        to_delete = _resolve_pages(pages_to_delete, num_pages)

        if len(to_delete) >= num_pages:
            return {"success": False, "error": "Cannot delete all pages from a PDF."}

        writer = PdfWriter()
        kept   = 0

        for i, page in enumerate(reader.pages):
            if i not in to_delete:
                writer.add_page(page)
                kept += 1
            if progress_cb:
                progress_cb(i + 1, num_pages)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        return {
            "success": True,
            "output_path": output_path,
            "pages_removed": len(to_delete),
            "pages_remaining": kept,
            "error": None,
        }

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def duplicate_pages(
    input_path: str,
    output_path: str,
    pages: str,
    copies: int = 1,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Duplicate specified pages (appended at end) n times.
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}
    if copies < 1:
        return {"success": False, "error": "copies must be >= 1."}

    try:
        reader    = PdfReader(input_path)
        num_pages = len(reader.pages)
        to_dup    = sorted(_resolve_pages(pages, num_pages))
        writer    = PdfWriter()

        # Original pages
        for page in reader.pages:
            writer.add_page(page)

        # Duplicated pages
        total_dup = len(to_dup) * copies
        step      = 0
        for _ in range(copies):
            for pg_idx in to_dup:
                writer.add_page(reader.pages[pg_idx])
                step += 1
                if progress_cb:
                    progress_cb(step, total_dup)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        return {"success": True, "output_path": output_path, "error": None}

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
