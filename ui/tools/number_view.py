"""PDForge — ui/tools/number_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton, ThemedComboBox
from assets.themes.theme import COLORS, RADIUS

POSITIONS = ["bottom-center", "bottom-right", "bottom-left",
             "top-center", "top-right", "top-left"]


class NumberView(BaseToolView):
    ICON     = "#"
    TITLE    = "Page Numbers"
    SUBTITLE = "Add page numbers in any position and style"

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

        self.section(parent, "NUMBER STYLE")
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x")

        labels = ["Position", "Start at", "Prefix", "Suffix", "Font size", "Color (hex)"]
        self._pos_var   = ctk.StringVar(value="bottom-center")
        self._start_var = ctk.StringVar(value="1")
        self._pre_var   = ctk.StringVar(value="")
        self._suf_var   = ctk.StringVar(value="")
        self._fs_var    = ctk.StringVar(value="11")
        self._col_var   = ctk.StringVar(value="#333333")

        for row_i, (label, var, widget_type) in enumerate([
            ("Position",    self._pos_var,   "combo"),
            ("Start at",    self._start_var, "entry"),
            ("Prefix",      self._pre_var,   "entry"),
            ("Suffix",      self._suf_var,   "entry"),
            ("Font size",   self._fs_var,    "entry"),
            ("Color (hex)", self._col_var,   "entry"),
        ]):
            ctk.CTkLabel(grid, text=label + ":",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_secondary"],
                width=100, anchor="e",
            ).grid(row=row_i // 3, column=(row_i % 3) * 2, padx=(16, 4), pady=4, sticky="e")

            if widget_type == "combo":
                ThemedComboBox(grid, values=POSITIONS, variable=var, width=160
                    ).grid(row=row_i // 3, column=(row_i % 3) * 2 + 1, padx=(0, 16), pady=4, sticky="w")
            else:
                ctk.CTkEntry(grid, textvariable=var, width=80,
                    fg_color=COLORS["bg_card"], border_color=COLORS["border"],
                    text_color=COLORS["text_primary"],
                    font=ctk.CTkFont(family="Segoe UI", size=13), height=32,
                    corner_radius=RADIUS["md"],
                ).grid(row=row_i // 3, column=(row_i % 3) * 2 + 1, padx=(0, 16), pady=4, sticky="w")

        self.section(parent, "SKIP PAGES")
        skip_row = ctk.CTkFrame(parent, fg_color="transparent")
        skip_row.pack(anchor="w")
        ctk.CTkLabel(skip_row, text="Skip numbering on pages:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(side="left")
        self._skip_var = ctk.StringVar(value="")
        ctk.CTkEntry(skip_row, textvariable=self._skip_var, width=160,
            placeholder_text="e.g. 1 (leave blank for none)",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=32,
            corner_radius=RADIUS["md"]).pack(side="left", padx=8)

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
            self.autofill_output_entry(self._out_var, self._file, "numbered")
            self._page_preview.set_document(self._file)

    def build_buttons(self, parent):
        PrimaryButton(parent, text="#  Add Numbers", command=self.run, width=160).pack(side="left")

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return
        out = self._out_var.get().strip() or self.suggest_output(self._file, "numbered")
        try:
            start = int(self._start_var.get())
            fs    = int(self._fs_var.get())
        except Exception:
            start, fs = 1, 11
        self.show_progress("Adding page numbers…")

        def _work():
            from core.number import add_page_numbers
            result = add_page_numbers(
                self._file, out,
                position=self._pos_var.get(),
                start_number=start,
                prefix=self._pre_var.get(),
                suffix=self._suf_var.get(),
                font_size=fs,
                color_hex=self._col_var.get() or "#333333",
                skip_pages=self._skip_var.get().strip(),
                progress_cb=lambda c, t: self.after(0, lambda: self.update_progress(c, t)),
            )
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result, out):
        if result["success"]:
            from services import history
            history.add_entry("Page Numbers", [self._file], out, success=True)
            self.show_success("Page numbers added", output_path=out)
        else:
            self.show_error(result["error"])
