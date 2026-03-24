"""
PDForge — core/protect.py
Encrypt, decrypt, and set permissions on PDF files.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Callable

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError


def encrypt_pdf(
    input_path: str,
    output_path: str,
    user_password: str,
    owner_password: str | None = None,
    allow_printing: bool = True,
    allow_copying: bool = True,
    allow_editing: bool = False,
    allow_annotations: bool = True,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Encrypt a PDF with user and optional owner passwords.

    Args:
        user_password:    password to open the document
        owner_password:   password for full permissions (defaults to user_password)
        allow_printing:   allow printing
        allow_copying:    allow text/image copying
        allow_editing:    allow editing/modifying content
        allow_annotations: allow adding annotations/comments

    Returns:
        dict with success, output_path, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}
    if not user_password:
        return {"success": False, "error": "User password cannot be empty."}

    owner_pwd = owner_password or user_password

    try:
        reader = PdfReader(input_path)
        if reader.is_encrypted:
            return {"success": False, "error": "PDF is already encrypted. Decrypt it first."}

        writer = PdfWriter()
        num_pages = len(reader.pages)

        for i, page in enumerate(reader.pages):
            writer.add_page(page)
            if progress_cb:
                progress_cb(i + 1, num_pages + 1)

        # Build permission flags
        from pypdf.constants import UserAccessPermissions
        perms = UserAccessPermissions(0)
        if allow_printing:
            perms |= UserAccessPermissions.PRINT
            perms |= UserAccessPermissions.PRINT_TO_REPRESENTATION
        if allow_copying:
            perms |= UserAccessPermissions.EXTRACT
            perms |= UserAccessPermissions.EXTRACT_TEXT_AND_GRAPHICS
        if allow_editing:
            perms |= UserAccessPermissions.MODIFY
            perms |= UserAccessPermissions.MODIFY_TEXT_ANNOTATIONS
        if allow_annotations:
            perms |= UserAccessPermissions.ADD_OR_MODIFY
            perms |= UserAccessPermissions.FILL_FORM_FIELDS

        writer.encrypt(
            user_password=user_password,
            owner_password=owner_pwd,
            use_128bit=True,
            permissions_flag=perms,
        )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        if progress_cb:
            progress_cb(num_pages + 1, num_pages + 1)

        return {"success": True, "output_path": output_path, "error": None}

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def decrypt_pdf(
    input_path: str,
    output_path: str,
    password: str,
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Remove encryption from a PDF.

    Returns:
        dict with success, output_path, error
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    try:
        reader = PdfReader(input_path)

        if not reader.is_encrypted:
            return {"success": False, "error": "This PDF is not encrypted."}

        result = reader.decrypt(password)
        if result == 0:
            return {"success": False, "error": "Incorrect password."}

        writer = PdfWriter()
        num_pages = len(reader.pages)

        for i, page in enumerate(reader.pages):
            writer.add_page(page)
            if progress_cb:
                progress_cb(i + 1, num_pages)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        return {"success": True, "output_path": output_path, "error": None}

    except PdfReadError as exc:
        return {"success": False, "error": f"Cannot read PDF: {exc}"}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def get_pdf_info(input_path: str, password: str = "") -> dict:
    """
    Get info about a PDF — page count, encryption status, permissions.
    """
    if not os.path.isfile(input_path):
        return {"success": False, "error": f"File not found: {input_path}"}

    try:
        reader = PdfReader(input_path)
        encrypted = reader.is_encrypted

        if encrypted:
            if not password:
                return {
                    "success": True,
                    "encrypted": True,
                    "page_count": None,
                    "metadata": {},
                    "needs_password": True,
                }
            result = reader.decrypt(password)
            if result == 0:
                return {"success": False, "error": "Incorrect password."}

        meta = {}
        if reader.metadata:
            for k, v in reader.metadata.items():
                meta[k.lstrip("/")] = str(v)

        return {
            "success": True,
            "encrypted": encrypted,
            "page_count": len(reader.pages),
            "metadata": meta,
            "needs_password": False,
        }

    except Exception as exc:
        return {"success": False, "error": str(exc)}
