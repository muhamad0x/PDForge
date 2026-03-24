"""PDForge — ui/tools/convert_view.py"""

from __future__ import annotations
from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton, FileListItem
from assets.themes.theme import COLORS, RADIUS
from ui.file_dialog_config import FILETYPES_IMAGES, EXT_COMMON_IMAGES

MODE_META = {
    "pdf_to_word":  {"icon": "W",  "title": "PDF → Word",   "sub": "Convert PDF to editable .docx document",           "multi": False},
    "pdf_to_excel": {"icon": "X",  "title": "PDF → Excel",  "sub": "Extract all tables to .xlsx spreadsheet",          "multi": False},
    "pdf_to_image": {"icon": "🖼", "title": "PDF → Image",  "sub": "Export each page as PNG, JPEG or WEBP",            "multi": False},
    "image_to_pdf": {"icon": "📄", "title": "Image → PDF",  "sub": "Combine images (PNG/JPEG) into a single PDF",      "multi": True},
    "pdf_to_text":  {"icon": "T",  "title": "PDF → Text",   "sub": "Extract all text content to a .txt file",          "multi": False},
}


class ConvertView(BaseToolView):
    def __init__(self, parent, mode: str = "pdf_to_word"):
        self._mode  = mode
        self._file  = ""
        self._files = []
        meta = MODE_META.get(mode, {})
        self.ICON     = meta.get("icon", "⇄")
        self.TITLE    = meta.get("title", "Convert")
        self.SUBTITLE = meta.get("sub", "")
        super().__init__(parent)

    def build_ui(self, parent):
        multi = MODE_META.get(self._mode, {}).get("multi", False)

        if multi:
            self._drop = DropZone(
                parent, on_files_dropped=self._set_files,
                accept_multiple=True, height=110,
                label="Drop images here, or click to browse",
                filetypes=FILETYPES_IMAGES,
                allowed_extensions=EXT_COMMON_IMAGES,
                dialog_title="Select images (JPEG, PNG, WebP, TIFF…)",
                sublabel="Images appear directly — no need for “All files”",
            )
        else:
            self._drop = DropZone(
                parent, on_files_dropped=self._set_files,
                accept_multiple=False, height=110,
                label="Drop file(s) here, or click to browse",
            )
        self._drop.pack(fill="x", pady=(0, 12))

        self._file_label = ctk.CTkLabel(parent, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["accent"], anchor="w")
        self._file_label.pack(anchor="w", pady=(0, 4))

        # Mode-specific options
        if self._mode == "pdf_to_image":
            self._build_image_opts(parent)
        elif self._mode == "image_to_pdf":
            self._build_img2pdf_opts(parent)

        self.section(parent, "OUTPUT")
        out_row = ctk.CTkFrame(parent, fg_color="transparent")
        out_row.pack(fill="x")
        self._out_var = ctk.StringVar()

        ext_map = {
            "pdf_to_word": ".docx", "pdf_to_excel": ".xlsx",
            "pdf_to_image": "", "image_to_pdf": ".pdf", "pdf_to_text": ".txt",
        }
        self._out_ext = ext_map.get(self._mode, ".pdf")
        placeholder = "Output path" if self._out_ext else "Output folder (for images)"

        ctk.CTkEntry(out_row, textvariable=self._out_var,
            placeholder_text=placeholder,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"]).pack(side="left", fill="x", expand=True, padx=(0, 8))
        SecondaryButton(out_row, text="Browse",
            command=self._browse_out, width=90).pack(side="left")

    def _build_image_opts(self, parent):
        self.section(parent, "IMAGE OPTIONS")
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkLabel(row, text="Format:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(side="left")
        self._img_fmt = ctk.StringVar(value="PNG")
        for fmt in ("PNG", "JPEG", "WEBP"):
            ctk.CTkRadioButton(row, text=fmt, variable=self._img_fmt, value=fmt,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
            ).pack(side="left", padx=12)
        ctk.CTkLabel(row, text="DPI:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(side="left", padx=(16, 0))
        self._dpi_var = ctk.StringVar(value="150")
        ctk.CTkEntry(row, textvariable=self._dpi_var, width=65,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=32,
            corner_radius=RADIUS["md"]).pack(side="left", padx=8)

    def _build_img2pdf_opts(self, parent):
        self.section(parent, "PAGE SIZE")
        self._page_size = ctk.StringVar(value="A4")
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(anchor="w")
        for val in ("A4", "letter", "fit"):
            ctk.CTkRadioButton(row, text=val, variable=self._page_size, value=val,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
            ).pack(side="left", padx=(0, 16))

    def _set_files(self, paths):
        if not paths:
            return
        if MODE_META.get(self._mode, {}).get("multi"):
            self._files = paths
            self._file_label.configure(
                text=f"✓  {len(paths)} image(s) selected")
            self.autofill_output_entry(self._out_var, paths[0], "from_images", ".pdf")
        else:
            self._file = paths[0]
            self._file_label.configure(
                text=f"✓  {Path(self._file).name}")
            if self._mode == "pdf_to_image":
                if not str(self._out_var.get()).strip():
                    self._out_var.set(self.suggest_output_dir(self._file, "images"))
            else:
                op_map = {
                    "pdf_to_word": "word", "pdf_to_excel": "excel",
                    "pdf_to_text": "text",
                }
                self.autofill_output_entry(
                    self._out_var, self._file,
                    op_map.get(self._mode, "converted"),
                    self._out_ext or ".pdf",
                )

    def _browse_out(self):
        if self._mode == "pdf_to_image":
            d = self.browse_directory()
            if d:
                self._out_var.set(d)
        elif self._mode == "image_to_pdf":
            path = self.browse_save_pdf()
            if path:
                self._out_var.set(path)
        else:
            ext = self._out_ext
            ft_map = {
                ".docx": [("Word Document", "*.docx")],
                ".xlsx": [("Excel Spreadsheet", "*.xlsx")],
                ".txt":  [("Text file", "*.txt")],
            }
            filetypes = ft_map.get(ext, [("All files", "*.*")])
            src = self._file or "output"
            default = Path(src).stem + ext
            path = self.browse_save_file(default_name=default, ext=ext, filetypes=filetypes)
            if path:
                self._out_var.set(path)

    def build_buttons(self, parent):
        PrimaryButton(parent, text=f"{self.ICON}  Convert", command=self.run, width=150).pack(side="left")

    def run(self):
        mode = self._mode

        if mode == "image_to_pdf":
            if not self._files:
                self.show_error("Add image files first.")
                return
            out = self._out_var.get().strip() or str(
                Path(self._files[0]).parent / "images_combined.pdf")
        else:
            if not self._file:
                self.show_error("Select a file first.")
                return
            if not self._out_var.get().strip():
                op_map = {
                    "pdf_to_word": "word", "pdf_to_excel": "excel",
                    "pdf_to_image": "", "pdf_to_text": "text",
                }
                if mode == "pdf_to_image":
                    out = self.suggest_output_dir(self._file, "images")
                else:
                    out = self.suggest_output(
                        self._file, op_map.get(mode, "converted"), ext=self._out_ext
                    )
            else:
                out = self._out_var.get().strip()

        self.show_progress(f"Converting…")

        def _work():
            cb = lambda c, t: self.after(0, lambda: self.update_progress(c, t))
            try:
                if mode == "pdf_to_word":
                    from core.convert import pdf_to_word
                    result = pdf_to_word(self._file, out, progress_cb=cb)
                elif mode == "pdf_to_excel":
                    from core.convert import pdf_to_excel
                    result = pdf_to_excel(self._file, out, progress_cb=cb)
                elif mode == "pdf_to_image":
                    from core.convert import pdf_to_images
                    fmt = getattr(self, "_img_fmt", ctk.StringVar(value="PNG")).get()
                    try:
                        dpi = int(getattr(self, "_dpi_var", ctk.StringVar(value="150")).get())
                    except Exception:
                        dpi = 150
                    result = pdf_to_images(self._file, out, image_format=fmt, dpi=dpi, progress_cb=cb)
                elif mode == "image_to_pdf":
                    from core.convert import images_to_pdf
                    ps = getattr(self, "_page_size", ctk.StringVar(value="A4")).get()
                    result = images_to_pdf(self._files, out, page_size=ps, progress_cb=cb)
                elif mode == "pdf_to_text":
                    from core.convert import pdf_to_text
                    result = pdf_to_text(self._file, out, progress_cb=cb)
                else:
                    result = {"success": False, "error": "Unknown mode"}
            except Exception as e:
                result = {"success": False, "error": str(e)}
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result, out):
        if result["success"]:
            src = self._files if self._mode == "image_to_pdf" else [self._file]
            from services import history
            history.add_entry(self.TITLE, src, out, success=True)
            n = result.get("count") or result.get("table_count") or ""
            extra = f" ({n} items)" if n else ""
            self.show_success(f"Conversion complete{extra}", output_path=out)
        else:
            self.show_error(result["error"])
