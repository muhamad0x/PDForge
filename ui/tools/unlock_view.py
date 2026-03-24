"""PDForge — ui/tools/unlock_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton
from assets.themes.theme import COLORS, RADIUS


class UnlockView(BaseToolView):
    ICON     = "🔓"
    TITLE    = "Unlock PDF"
    SUBTITLE = "Remove password protection from an encrypted PDF"

    def __init__(self, parent):
        self._file = ""
        super().__init__(parent)

    def build_ui(self, parent):
        self._drop = DropZone(parent, on_files_dropped=self._set_file,
                              accept_multiple=False, height=110,
                              label="Drop an encrypted PDF file here")
        self._drop.pack(fill="x", pady=(0, 12))

        self._file_label = ctk.CTkLabel(parent, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["accent"], anchor="w")
        self._file_label.pack(anchor="w", pady=(0, 8))

        self.section(parent, "PASSWORD")
        self._pwd_entry = ctk.CTkEntry(parent, show="•",
            placeholder_text="Enter the PDF password",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"])
        self._pwd_entry.pack(fill="x", pady=(4, 0))

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
        SecondaryButton(out_row, text="Browse", command=self._browse_out, width=90).pack(side="left")

    def build_buttons(self, parent):
        PrimaryButton(parent, text="🔓  Unlock PDF", command=self.run, width=160).pack(side="left")

    def _set_file(self, paths):
        if paths:
            self._file = paths[0]
            self._file_label.configure(text=f"✓  {Path(self._file).name}")
            self.autofill_output_entry(self._out_var, self._file, "unlocked")

    def _browse_out(self):
        path = self.browse_save_pdf(default_name=Path(
            self.suggest_output(self._file, "unlocked") if self._file else "unlocked.pdf"
        ).name)
        if path:
            self._out_var.set(path)

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return
        pwd = self._pwd_entry.get()
        out = self._out_var.get().strip() or self.suggest_output(self._file, "unlocked")
        self.show_progress("Decrypting…")

        def _work():
            from core.protect import decrypt_pdf
            result = decrypt_pdf(self._file, out, password=pwd,
                progress_cb=lambda c, t: self.after(0, lambda: self.update_progress(c, t)))
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result, out):
        if result["success"]:
            from services import history
            history.add_entry("Unlock", [self._file], out, success=True)
            self.show_success("Password removed successfully", output_path=out)
        else:
            self.show_error(result["error"])
