"""PDForge — ui/tools/rotate_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton
from assets.themes.theme import COLORS, RADIUS


class RotateView(BaseToolView):
    ICON     = "↻"
    TITLE    = "Rotate Pages"
    SUBTITLE = "Rotate all or specific pages clockwise"

    def __init__(self, parent):
        self._file = ""
        super().__init__(parent)

    def build_ui(self, parent):
        self._drop = DropZone(parent, on_files_dropped=self._set_file,
                              accept_multiple=False, height=110,
                              label="Drop a PDF here, or click to browse")
        self._drop.pack(fill="x", pady=(0, 12))
        self._file_label = ctk.CTkLabel(parent, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["accent"], anchor="w")
        self._file_label.pack(anchor="w", pady=(0, 8))

        self.section(parent, "ROTATION")
        rot_row = ctk.CTkFrame(parent, fg_color="transparent")
        rot_row.pack(anchor="w")
        self._rot = ctk.StringVar(value="90")
        for val, label in [("90", "90° →"), ("180", "180°"), ("270", "← 90°")]:
            ctk.CTkRadioButton(rot_row, text=label, variable=self._rot, value=val,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
            ).pack(side="left", padx=(0, 24))

        self.section(parent, "PAGES")
        self._pages_var = ctk.StringVar(value="all")
        ctk.CTkEntry(parent, textvariable=self._pages_var,
            placeholder_text="all  or  1-3, 5, last",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"]).pack(fill="x")

        self._pv_host = ctk.CTkFrame(parent, fg_color="transparent")
        self._pv_host.pack(fill="x", pady=(12, 0))
        from ui.pdf_page_preview import SimplePdfPreview
        self._page_preview = SimplePdfPreview(self._pv_host)
        self._page_preview.pack(fill="x")

        self.section(parent, "OUTPUT")
        out_row = ctk.CTkFrame(parent, fg_color="transparent")
        out_row.pack(fill="x")
        self._out_var = ctk.StringVar()
        ctk.CTkEntry(out_row, textvariable=self._out_var,
            placeholder_text="Output path",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"]).pack(side="left", fill="x", expand=True, padx=(0, 8))
        SecondaryButton(out_row, text="Browse",
            command=lambda: self._out_var.set(self.browse_save_pdf()),
            width=90).pack(side="left")

    def _set_file(self, paths):
        if paths:
            self._file = paths[0]
            self._file_label.configure(text=f"✓  {Path(self._file).name}")
            self.autofill_output_entry(self._out_var, self._file, "rotated")
            self._page_preview.set_document(self._file)

    def build_buttons(self, parent):
        PrimaryButton(parent, text="↻  Rotate", command=self.run, width=140).pack(side="left")

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return
        out = self._out_var.get().strip() or self.suggest_output(self._file, "rotated")
        rotation = int(self._rot.get())
        pages = self._pages_var.get().strip() or "all"
        self.show_progress("Rotating pages…")

        def _work():
            from core.organize import rotate_pages
            result = rotate_pages(self._file, out, rotation=rotation, pages=pages,
                progress_cb=lambda c, t: self.after(0, lambda: self.update_progress(c, t)))
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result, out):
        if result["success"]:
            from services import history
            history.add_entry("Rotate", [self._file], out, success=True)
            self.show_success("Pages rotated successfully", output_path=out)
        else:
            self.show_error(result["error"])
