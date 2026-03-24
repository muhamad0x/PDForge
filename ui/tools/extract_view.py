"""PDForge — ui/tools/extract_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton
from assets.themes.theme import COLORS, RADIUS

MODE_META = {
    "text":   {"icon": "¶",  "title": "Extract Text",   "sub": "Export all text content to a .txt file"},
    "images": {"icon": "⬚",  "title": "Extract Images", "sub": "Pull all embedded images from the PDF"},
    "tables": {"icon": "⊟",  "title": "Extract Tables", "sub": "Save all tables to Excel or CSV"},
}


class ExtractView(BaseToolView):
    def __init__(self, parent, mode: str = "text"):
        self._mode = mode
        self._file = ""
        meta = MODE_META.get(mode, {})
        self.ICON     = meta.get("icon", "⬚")
        self.TITLE    = meta.get("title", "Extract")
        self.SUBTITLE = meta.get("sub", "")
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

        self.section(parent, "PAGES")
        self._pages_var = ctk.StringVar(value="all")
        ctk.CTkEntry(parent, textvariable=self._pages_var,
            placeholder_text="all  or  1-3, 5",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"]).pack(fill="x")

        self._pv_host = ctk.CTkFrame(parent, fg_color="transparent")
        self._pv_host.pack(fill="x", pady=(12, 0))
        from ui.pdf_page_preview import SimplePdfPreview
        self._page_preview = SimplePdfPreview(self._pv_host)
        self._page_preview.pack(fill="x")

        if self._mode == "images":
            self._build_image_opts(parent)
        elif self._mode == "tables":
            self._build_table_opts(parent)

        self.section(parent, "OUTPUT")
        out_row = ctk.CTkFrame(parent, fg_color="transparent")
        out_row.pack(fill="x")
        self._out_var = ctk.StringVar()
        if self._mode == "images":
            placeholder = "Output folder for images"
        elif self._mode == "tables":
            placeholder = "Output path (.xlsx or .csv)"
        else:
            placeholder = "Output path (.txt)"

        ctk.CTkEntry(out_row, textvariable=self._out_var,
            placeholder_text=placeholder,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"]).pack(side="left", fill="x", expand=True, padx=(0, 8))
        SecondaryButton(out_row, text="Browse",
            command=self._browse_out, width=90).pack(side="left")

    def _build_image_opts(self, parent):
        self.section(parent, "IMAGE FORMAT")
        self._img_fmt = ctk.StringVar(value="PNG")
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(anchor="w")
        for fmt in ("PNG", "JPEG", "WEBP"):
            ctk.CTkRadioButton(row, text=fmt, variable=self._img_fmt, value=fmt,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
            ).pack(side="left", padx=(0, 16))

    def _build_table_opts(self, parent):
        self.section(parent, "OUTPUT FORMAT")
        self._tbl_fmt = ctk.StringVar(value=".xlsx")
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(anchor="w")
        for val, label in [(".xlsx", "Excel (.xlsx)"), (".csv", "CSV (.csv)")]:
            ctk.CTkRadioButton(row, text=label, variable=self._tbl_fmt, value=val,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
            ).pack(side="left", padx=(0, 20))

    def _set_file(self, paths):
        if paths:
            self._file = paths[0]
            self._file_label.configure(text=f"✓  {Path(self._file).name}")
            self._page_preview.set_document(self._file)
            if self._mode == "images":
                if not str(self._out_var.get()).strip():
                    self._out_var.set(self.suggest_output_dir(self._file, "images"))
            elif self._mode == "tables":
                ext = getattr(self, "_tbl_fmt", None)
                suf = ext.get() if ext else ".xlsx"
                self.autofill_output_entry(self._out_var, self._file, "tables", suf)
            else:
                self.autofill_output_entry(self._out_var, self._file, "text", ".txt")

    def _browse_out(self):
        if self._mode == "images":
            d = self.browse_directory()
            if d:
                self._out_var.set(d)
        elif self._mode == "tables":
            ext = getattr(self, "_tbl_fmt", ctk.StringVar(value=".xlsx")).get()
            ft = [("Excel", "*.xlsx")] if ext == ".xlsx" else [("CSV", "*.csv")]
            path = self.browse_save_file(default_name=Path(self._file).stem + ext if self._file else "tables" + ext,
                                         ext=ext, filetypes=ft)
            if path:
                self._out_var.set(path)
        else:
            path = self.browse_save_file(
                default_name=Path(self._file).stem + ".txt" if self._file else "extracted.txt",
                ext=".txt", filetypes=[("Text file", "*.txt")])
            if path:
                self._out_var.set(path)

    def build_buttons(self, parent):
        PrimaryButton(parent, text=f"{self.ICON}  Extract", command=self.run, width=140).pack(side="left")

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return
        pages = self._pages_var.get().strip() or "all"
        cb = lambda c, t: self.after(0, lambda: self.update_progress(c, t))
        self.show_progress("Extracting…")

        def _work():
            try:
                if self._mode == "text":
                    out = self._out_var.get().strip() or self.suggest_output(self._file, "text", ".txt")
                    from core.extract import extract_text
                    result = extract_text(self._file, out, pages=pages, progress_cb=cb)
                elif self._mode == "images":
                    out = self._out_var.get().strip() or str(Path(self._file).parent / (Path(self._file).stem + "_images"))
                    fmt = getattr(self, "_img_fmt", ctk.StringVar(value="PNG")).get()
                    from core.extract import extract_images
                    result = extract_images(self._file, out, pages=pages, image_format=fmt, progress_cb=cb)
                else:
                    ext = getattr(self, "_tbl_fmt", ctk.StringVar(value=".xlsx")).get()
                    out = self._out_var.get().strip() or self.suggest_output(self._file, "tables", ext)
                    from core.extract import extract_tables
                    result = extract_tables(self._file, out, pages=pages, progress_cb=cb)
            except Exception as e:
                result = {"success": False, "error": str(e)}
                out = ""
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result, out):
        if result["success"]:
            from services import history
            history.add_entry(self.TITLE, [self._file], out, success=True)
            extra = ""
            if "count" in result:
                extra = f" — {result['count']} images"
            elif "table_count" in result:
                extra = f" — {result['table_count']} tables"
            elif "char_count" in result:
                extra = f" — {result['char_count']:,} characters"
            self.show_success(f"Extraction complete{extra}", output_path=out)
        else:
            self.show_error(result["error"])
