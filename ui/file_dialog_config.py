"""Shared file-open patterns so dialogs list PDFs, images, etc. without hiding formats."""

from __future__ import annotations

# Windows Tk accepts multiple patterns in one tuple entry.
FILETYPES_PDF_DEFAULT = [
    ("PDF files", "*.pdf"),
    ("All files", "*.*"),
]

FILETYPES_PDF_AND_IMAGES = [
    ("PDF & images", "*.pdf;*.jpg;*.jpeg;*.png;*.webp;*.tif;*.tiff;*.bmp;*.gif"),
    ("PDF", "*.pdf"),
    ("Images", "*.jpg;*.jpeg;*.png;*.webp;*.tif;*.tiff;*.bmp;*.gif"),
    ("All files", "*.*"),
]

# Image → PDF: raster images only (PIL); PDF paths are listed for convenience in dialogs elsewhere.
FILETYPES_IMAGES = [
    ("All images", "*.jpg;*.jpeg;*.png;*.webp;*.tif;*.tiff;*.bmp;*.gif;*.jfif;*.heic"),
    ("JPEG", "*.jpg;*.jpeg"),
    ("PNG", "*.png"),
    ("WebP", "*.webp"),
    ("TIFF", "*.tif;*.tiff"),
    ("All files", "*.*"),
]

EXT_PDF = frozenset({".pdf"})
EXT_COMMON_IMAGES = frozenset({".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp", ".gif", ".heic", ".jfif"})
EXT_PDF_AND_IMAGES = EXT_PDF | EXT_COMMON_IMAGES
