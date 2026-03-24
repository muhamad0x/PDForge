"""
PDForge — core/merge.py
Merge multiple PDFs into one, with optional page range selection per file.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Callable
from pypdf import PdfWriter, PdfReader


def merge_pdfs(
    input_paths: list[str],
    output_path: str,
    page_ranges: list[str | None] | None = None,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Merge PDFs in order. Optionally specify page ranges per file.

    Args:
        input_paths:  ordered list of PDF file paths
        output_path:  destination path for merged PDF
        page_ranges:  optional list aligned with input_paths.
                      Each entry is a range string like "1-3,5,8-last"
                      or None to include all pages.
        progress_cb:  callback(current_step, total_steps)

    Returns:
        dict with keys: success, output_path, total_pages, error
    """
    if not input_paths:
        return {"success": False, "error": "No input files provided."}

    if page_ranges is None:
        page_ranges = [None] * len(input_paths)

    if len(page_ranges) != len(input_paths):
        return {"success": False, "error": "page_ranges length must match input_paths."}

    writer = PdfWriter()
    total_steps = len(input_paths)
    total_pages = 0

    try:
        for idx, (path, ranges) in enumerate(zip(input_paths, page_ranges)):
            if not os.path.isfile(path):
                return {"success": False, "error": f"File not found: {path}"}

            reader = PdfReader(path)
            num_pages = len(reader.pages)

            if ranges is None:
                pages_to_add = list(range(num_pages))
            else:
                pages_to_add = _parse_range(ranges, num_pages)
                if pages_to_add is None:
                    return {
                        "success": False,
                        "error": f"Invalid page range '{ranges}' for file: {Path(path).name}",
                    }

            for page_idx in pages_to_add:
                writer.add_page(reader.pages[page_idx])
                total_pages += 1

            if progress_cb:
                progress_cb(idx + 1, total_steps)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        return {
            "success": True,
            "output_path": output_path,
            "total_pages": total_pages,
            "error": None,
        }

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def _parse_range(range_str: str, total: int) -> list[int] | None:
    """
    Parse a range string like "1-3,5,8-last" into 0-based page indices.
    Returns None on invalid input.
    """
    result = []
    parts = [p.strip() for p in range_str.split(",")]

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
                page_num = int(part_lower) if part_lower != "last" else total
            except ValueError:
                return None

            if page_num < 1 or page_num > total:
                return None
            result.append(page_num - 1)

    # deduplicate preserving order
    seen = set()
    unique = []
    for p in result:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique
