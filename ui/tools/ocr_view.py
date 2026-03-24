"""PDForge — ui/tools/ocr_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton
from assets.themes.theme import COLORS, RADIUS
from core.ocr import SUPPORTED_LANGS


class OcrView(BaseToolView):
    ICON     = "◉"
    TITLE    = "OCR — Make PDF Searchable"
    SUBTITLE = "Convert scanned PDFs to searchable text using Tesseract OCR"

    def __init__(self, parent):
        self._file = ""
        super().__init__(parent)

    def build_ui(self, parent):
        # Dependency check
        from core.ocr import check_dependencies
        deps = check_dependencies()
        if not deps["ready"]:
            missing = []
            if not deps["tesseract"]:
                missing.append("Tesseract OCR — https://github.com/tesseract-ocr/tesseract")
            if not deps["poppler"]:
                missing.append("Poppler utils — Linux: sudo apt install poppler-utils")
            warn = ctk.CTkFrame(parent,
                fg_color=COLORS["warning_soft"],
                corner_radius=8, border_color=COLORS["warning"], border_width=1)
            warn.pack(fill="x", pady=(0, 16))
            ctk.CTkLabel(warn,
                text="⚠  Missing dependencies:\n" + "\n".join(f"  • {m}" for m in missing),
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["warning"], justify="left",
            ).pack(padx=16, pady=12, anchor="w")

        self._drop = DropZone(parent, on_files_dropped=self._set_file,
                              accept_multiple=False, height=110,
                              label="Drop a scanned PDF here, or click to browse")
        self._drop.pack(fill="x", pady=(0, 12))

        self._file_label = ctk.CTkLabel(parent, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["accent"], anchor="w")
        self._file_label.pack(anchor="w", pady=(0, 8))

        self._pv_host = ctk.CTkFrame(parent, fg_color="transparent")
        self._pv_host.pack(fill="x", pady=(0, 8))
        from ui.pdf_page_preview import SimplePdfPreview
        self._page_preview = SimplePdfPreview(self._pv_host)
        self._page_preview.pack(fill="x")

        self.section(parent, "LANGUAGES")
        ctk.CTkLabel(parent,
            text="Select OCR languages (hold Ctrl for multiple in some environments):",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(anchor="w")

        lang_grid = ctk.CTkFrame(parent, fg_color="transparent")
        lang_grid.pack(anchor="w", pady=(8, 0))
        self._lang_vars: dict[str, ctk.BooleanVar] = {}
        for i, (code, name) in enumerate(SUPPORTED_LANGS.items()):
            var = ctk.BooleanVar(value=(code == "eng"))
            self._lang_vars[code] = var
            ctk.CTkCheckBox(lang_grid, text=name, variable=var,
                checkmark_color=COLORS["text_primary"],
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=12),
            ).grid(row=i // 4, column=i % 4, padx=8, pady=2, sticky="w")

        self.section(parent, "OPTIONS")
        opts = ctk.CTkFrame(parent, fg_color="transparent")
        opts.pack(fill="x")

        ctk.CTkLabel(opts, text="DPI:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).grid(row=0, column=0, sticky="w", pady=4)
        self._dpi_var = ctk.StringVar(value="200")
        ctk.CTkEntry(opts, textvariable=self._dpi_var, width=70,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=32,
            corner_radius=RADIUS["md"]).grid(row=0, column=1, sticky="w", padx=(8, 24))

        ctk.CTkLabel(opts, text="Output:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).grid(row=0, column=2, sticky="w")
        self._output_type = ctk.StringVar(value="searchable_pdf")
        for i, (val, label) in enumerate([
            ("searchable_pdf", "Searchable PDF"),
            ("text",           "Text file only"),
            ("both",           "Both"),
        ]):
            ctk.CTkRadioButton(opts, text=label, variable=self._output_type, value=val,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=12),
            ).grid(row=0, column=3 + i, sticky="w", padx=(8, 4))

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

    def _set_file(self, paths):
        if paths:
            self._file = paths[0]
            self._file_label.configure(text=f"✓  {Path(self._file).name}")
            self.autofill_output_entry(self._out_var, self._file, "ocr")
            self._page_preview.set_document(self._file)

    def _browse_out(self):
        path = self.browse_save_pdf(default_name=Path(
            self.suggest_output(self._file, "ocr") if self._file else "ocr_output.pdf"
        ).name)
        if path:
            self._out_var.set(path)

    def build_buttons(self, parent):
        PrimaryButton(parent, text="◉  Run OCR", command=self.run, width=150).pack(side="left")

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return
        langs = [code for code, var in self._lang_vars.items() if var.get()]
        if not langs:
            self.show_error("Select at least one language.")
            return
        try:
            dpi = int(self._dpi_var.get())
        except Exception:
            dpi = 200
        out = self._out_var.get().strip() or self.suggest_output(self._file, "ocr")
        output_type = self._output_type.get()
        self.show_progress("Running OCR — this may take a while…")

        def _work():
            from core.ocr import ocr_pdf
            result = ocr_pdf(
                self._file, out, languages=langs, dpi=dpi,
                output_type=output_type,
                progress_cb=lambda c, t: self.after(0, lambda: self.update_progress(
                    c, t, f"Processing page {c}/{t}…")),
            )
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result, out):
        if result["success"]:
            from services import history
            history.add_entry("OCR", [self._file], out, success=True,
                              details=f"{result.get('page_count',0)} pages")
            self.show_success(
                f"OCR complete — {result.get('page_count',0)} pages processed",
                output_path=out,
            )
        else:
            self.show_error(result["error"])
