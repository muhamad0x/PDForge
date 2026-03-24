"""PDForge — ui/tools/repair_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton
from assets.themes.theme import COLORS, RADIUS


class RepairView(BaseToolView):
    ICON     = "⚙"
    TITLE    = "Repair PDF"
    SUBTITLE = "Attempt to fix corrupted or malformed PDF files"

    def __init__(self, parent):
        self._file = ""
        super().__init__(parent)

    def build_ui(self, parent):
        self._drop = DropZone(parent, on_files_dropped=self._set_file,
                              accept_multiple=False, height=130,
                              label="Drop a corrupted PDF here, or click to browse")
        self._drop.pack(fill="x", pady=(0, 12))
        self._file_label = ctk.CTkLabel(parent, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["accent"], anchor="w")
        self._file_label.pack(anchor="w", pady=(0, 8))

        info = ctk.CTkFrame(parent,
            fg_color=COLORS["info_soft"],
            corner_radius=8, border_color=COLORS["info"], border_width=1)
        info.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(info,
            text="ℹ  Uses qpdf when installed, otherwise falls back to pypdf reconstruction.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["info"]).pack(padx=16, pady=10)

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
            self.autofill_output_entry(self._out_var, self._file, "repaired")

    def build_buttons(self, parent):
        PrimaryButton(parent, text="⚙  Repair PDF", command=self.run, width=150).pack(side="left")

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return
        out = self._out_var.get().strip() or self.suggest_output(self._file, "repaired")
        self.show_progress("Attempting repair…")

        def _work():
            from core.repair import repair_pdf
            result = repair_pdf(self._file, out,
                progress_cb=lambda c, t: self.after(0, lambda: self.update_progress(c, t)))
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result, out):
        if result["success"]:
            method = result.get("method", "")
            from services import history
            history.add_entry("Repair", [self._file], out, success=True, details=method)
            self.show_success(f"PDF repaired using {method}", output_path=out)
        else:
            self.show_error(result["error"])
