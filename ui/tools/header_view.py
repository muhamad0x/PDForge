"""PDForge — ui/tools/header_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton
from assets.themes.theme import COLORS, RADIUS


class HeaderView(BaseToolView):
    ICON     = "≡"
    TITLE    = "Header / Footer"
    SUBTITLE = "Add custom header and footer text — use {page} and {total} as placeholders"

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

        self.section(parent, "HEADER TEXT")
        self._header_var = ctk.StringVar()
        ctk.CTkEntry(parent, textvariable=self._header_var,
            placeholder_text="e.g.  My Document  |  {page} of {total}",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"]).pack(fill="x")

        self.section(parent, "FOOTER TEXT")
        self._footer_var = ctk.StringVar()
        ctk.CTkEntry(parent, textvariable=self._footer_var,
            placeholder_text="e.g.  Confidential  |  Page {page}",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"]).pack(fill="x")

        self.section(parent, "STYLE")
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(anchor="w")
        for label, attr, default in [
            ("Font size", "_hf_fs", "10"),
            ("Color (hex)", "_hf_col", "#333333"),
            ("Margin (pt)", "_hf_margin", "15"),
        ]:
            ctk.CTkLabel(row, text=label + ":",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_secondary"]).pack(side="left")
            var = ctk.StringVar(value=default)
            setattr(self, attr + "_var", var)
            ctk.CTkEntry(row, textvariable=var, width=80,
                fg_color=COLORS["bg_card"], border_color=COLORS["border"],
                text_color=COLORS["text_primary"],
                font=ctk.CTkFont(family="Segoe UI", size=13), height=32,
                corner_radius=RADIUS["md"]).pack(side="left", padx=(4, 20))

        self.section(parent, "PAGES")
        self._pages_var = ctk.StringVar(value="all")
        ctk.CTkEntry(parent, textvariable=self._pages_var,
            placeholder_text="all  or  1-3, 5",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"]).pack(fill="x")

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
            self.autofill_output_entry(self._out_var, self._file, "header_footer")

    def build_buttons(self, parent):
        PrimaryButton(parent, text="≡  Apply", command=self.run, width=140).pack(side="left")

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return
        header = self._header_var.get().strip()
        footer = self._footer_var.get().strip()
        if not header and not footer:
            self.show_error("Enter header text and/or footer text.")
            return
        out = self._out_var.get().strip() or self.suggest_output(self._file, "header_footer")
        try:
            fs     = int(self._hf_fs_var.get())
            margin = int(self._hf_margin_var.get())
        except Exception:
            fs, margin = 10, 15
        pages = self._pages_var.get().strip() or "all"
        self.show_progress("Adding header/footer…")

        def _work():
            from core.number import add_header_footer
            result = add_header_footer(
                self._file, out,
                header_text=header, footer_text=footer,
                font_size=fs, color_hex=self._hf_col_var.get() or "#333333",
                margin=margin, pages=pages,
                progress_cb=lambda c, t: self.after(0, lambda: self.update_progress(c, t)),
            )
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result, out):
        if result["success"]:
            from services import history
            history.add_entry("Header/Footer", [self._file], out, success=True)
            self.show_success("Header/footer added", output_path=out)
        else:
            self.show_error(result["error"])
