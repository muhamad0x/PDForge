"""
PDForge — ui/base_view.py
Base class for all tool views. Provides standard layout scaffolding.
"""

from __future__ import annotations
import threading
from pathlib import Path
from tkinter import filedialog
from typing import Callable

import customtkinter as ctk
from assets.themes.theme import COLORS, RADIUS, SPACING
from ui.file_dialog_config import FILETYPES_PDF_DEFAULT, FILETYPES_PDF_AND_IMAGES
from ui.widgets import (
    HeadingLabel, BodyLabel, SectionLabel,
    PrimaryButton, SecondaryButton,
    ProgressBar, ResultPanel, Separator,
)


class BaseToolView(ctk.CTkFrame):
    """Scrollable content above; fixed footer (progress, result, action buttons) always visible."""

    ICON    = "⬛"
    TITLE   = "Tool"
    SUBTITLE = ""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], corner_radius=0, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self._worker: threading.Thread | None = None

        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_primary"],
            scrollbar_button_color=COLORS["scrollbar"],
            scrollbar_button_hover_color=COLORS["scrollbar_hover"],
            corner_radius=0,
        )
        self._scroll.grid(row=0, column=0, sticky="nsew")

        header = ctk.CTkFrame(self._scroll, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(18, 0))

        ctk.CTkLabel(
            header,
            text=f"{self.ICON}  {self.TITLE}",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(anchor="w")

        if self.SUBTITLE:
            ctk.CTkLabel(
                header,
                text=self.SUBTITLE,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_secondary"],
                anchor="w",
            ).pack(anchor="w", pady=(4, 0))

        Separator(self._scroll).pack(fill="x", padx=28, pady=12)

        self._body = ctk.CTkFrame(self._scroll, fg_color="transparent")
        self._body.pack(fill="both", expand=True, padx=28)
        self.build_ui(self._body)

        Separator(self._scroll).pack(fill="x", padx=28, pady=12)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=1, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        self._progress = ProgressBar(footer)
        self._progress.pack(fill="x", padx=28, pady=(0, 6))
        self._progress.pack_forget()

        self._result = ResultPanel(footer)
        self._result.pack(fill="x", padx=28, pady=(0, 6))

        btn_row = ctk.CTkFrame(footer, fg_color="transparent")
        btn_row.pack(fill="x", padx=28, pady=(0, 16))
        self.build_buttons(btn_row)

    # ── Subclass interface ─────────────────────────────────────────────────

    def build_ui(self, parent: ctk.CTkFrame):
        """Override: build tool-specific content."""
        pass

    def build_buttons(self, parent: ctk.CTkFrame):
        """Override: build action buttons row."""
        PrimaryButton(parent, text="Run", command=self.run).pack(side="left")

    def run(self):
        """Override: execute tool operation."""
        pass

    # ── Helpers ────────────────────────────────────────────────────────────

    def browse_pdf(self, title="Select PDF file", filetypes=None) -> str:
        return filedialog.askopenfilename(
            title=title,
            filetypes=list(filetypes or FILETYPES_PDF_DEFAULT),
        ) or ""

    def browse_pdfs(self, title="Select PDF files", filetypes=None) -> list[str]:
        files = filedialog.askopenfilenames(
            title=title,
            filetypes=list(filetypes or FILETYPES_PDF_DEFAULT),
        )
        return list(files)

    def browse_pdf_or_images(self, title="Select PDF or image", filetypes=None) -> str:
        return filedialog.askopenfilename(
            title=title,
            filetypes=list(filetypes or FILETYPES_PDF_AND_IMAGES),
        ) or ""

    def browse_pdfs_or_images(self, title="Select files", filetypes=None) -> list[str]:
        files = filedialog.askopenfilenames(
            title=title,
            filetypes=list(filetypes or FILETYPES_PDF_AND_IMAGES),
        )
        return list(files)

    def browse_save_pdf(self, default_name="output.pdf", title="Save as") -> str:
        return filedialog.asksaveasfilename(
            title=title,
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        ) or ""

    def browse_save_file(self, default_name="output", ext=".txt", filetypes=None) -> str:
        if filetypes is None:
            filetypes = [(f"{ext.upper()} files", f"*{ext}"), ("All files", "*.*")]
        return filedialog.asksaveasfilename(
            title="Save as",
            defaultextension=ext,
            initialfile=default_name,
            filetypes=filetypes,
        ) or ""

    def browse_directory(self, title="Select output folder") -> str:
        return filedialog.askdirectory(title=title) or ""

    def show_progress(self, label: str = "Processing..."):
        self._result._clear()
        self._progress.reset()
        self._progress.set_label(label)
        self._progress.pack(fill="x", padx=36, pady=(0, 8))
        self.update_idletasks()

    def update_progress(self, current: int, total: int, label: str = ""):
        self._progress.update(current, total, label)

    def hide_progress(self):
        self._progress.pack_forget()

    def show_success(self, msg: str, output_path: str | None = None):
        self.hide_progress()
        self._result.show_success(msg, output_path)
        if output_path:
            from services import settings
            import os
            import subprocess
            import sys
            if settings.get("auto_open_output"):
                p = os.path.normpath(os.path.abspath(output_path))
                folder = p if os.path.isdir(p) else os.path.dirname(p)
                try:
                    if sys.platform == "win32":
                        os.startfile(folder)
                    elif sys.platform == "darwin":
                        subprocess.Popen(["open", folder])
                    else:
                        subprocess.Popen(["xdg-open", folder])
                except Exception:
                    pass

    def show_error(self, msg: str):
        self.hide_progress()
        self._result.show_error(msg)

    def run_in_thread(self, fn: Callable, *args, **kwargs):
        """Run fn(*args, **kwargs) in background thread, safe for UI updates."""
        if self._worker and self._worker.is_alive():
            return  # already running
        self._worker = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
        self._worker.start()

    def suggest_output(self, input_path: str, operation: str, ext: str = ".pdf") -> str:
        from services import file_manager
        return file_manager.suggest_output_path(input_path, operation, suffix=ext)

    def suggest_output_dir(self, input_path: str, operation: str = "images") -> str:
        from services import file_manager
        return file_manager.suggest_output_dir(input_path, operation)

    def autofill_output_entry(self, var, input_path: str, operation: str, ext: str = ".pdf") -> None:
        """Fill the output path field once when empty — respects Settings default folder."""
        if not input_path or var is None:
            return
        if str(var.get()).strip():
            return
        var.set(self.suggest_output(input_path, operation, ext))

    @staticmethod
    def section(parent, label: str):
        """Add a section label spacer."""
        SectionLabel(parent, text=label).pack(anchor="w", pady=(10, 4))
