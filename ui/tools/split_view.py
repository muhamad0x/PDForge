"""PDForge — ui/tools/split_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton
from assets.themes.theme import COLORS, RADIUS


class SplitView(BaseToolView):
    ICON     = "⊘"
    TITLE    = "Split PDF"
    SUBTITLE = "Split by custom page ranges, fixed intervals, each page, or bookmarks"

    def __init__(self, parent):
        self._file = ""
        super().__init__(parent)

    def build_ui(self, parent):
        self._drop = DropZone(
            parent, on_files_dropped=self._set_file,
            accept_multiple=False, height=120,
            label="Drop a PDF file here, or click to browse",
        )
        self._drop.pack(fill="x", pady=(0, 16))

        self._file_label = ctk.CTkLabel(
            parent, text="", font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["accent"], anchor="w",
        )
        self._file_label.pack(anchor="w", pady=(0, 8))

        self.section(parent, "SPLIT MODE")
        self._mode = ctk.StringVar(value="ranges")

        modes = [
            ("ranges",    "Custom page ranges  (e.g. 1-3, 5, 8-last)"),
            ("every_n",   "Every N pages"),
            ("each_page", "Each page as separate file"),
            ("bookmarks", "Split by bookmarks"),
        ]
        for val, label in modes:
            rb = ctk.CTkRadioButton(
                parent, text=label, variable=self._mode, value=val,
                command=self._on_mode_change,
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
            )
            rb.pack(anchor="w", pady=3)

        self._opts = ctk.CTkFrame(parent, fg_color="transparent")
        self._opts.pack(fill="x", pady=(12, 0))
        self._build_opts()

        self._preview_host = ctk.CTkFrame(parent, fg_color="transparent")
        self._preview_host.pack(fill="x", pady=(16, 0))
        self._sync_split_preview()

        self.section(parent, "OUTPUT FOLDER")
        out_row = ctk.CTkFrame(parent, fg_color="transparent")
        out_row.pack(fill="x")
        self._out_var = ctk.StringVar()
        ctk.CTkEntry(
            out_row, textvariable=self._out_var,
            placeholder_text="Output folder (same as input if empty)",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"],
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))
        SecondaryButton(out_row, text="Browse", command=self._browse_out, width=90).pack(side="left")

    def _build_opts(self):
        for w in self._opts.winfo_children():
            w.destroy()

        mode = self._mode.get()
        if mode == "ranges":
            ctk.CTkLabel(
                self._opts, text="Page ranges (comma-separated):",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_secondary"],
            ).pack(anchor="w")
            self._ranges_var = ctk.StringVar()
            ctk.CTkEntry(
                self._opts, textvariable=self._ranges_var,
                placeholder_text="e.g.  1-3, 4-7, 8-last",
                fg_color=COLORS["bg_card"], border_color=COLORS["border"],
                text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
                font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
                corner_radius=RADIUS["md"],
            ).pack(fill="x", pady=(4, 0))

        elif mode == "every_n":
            row = ctk.CTkFrame(self._opts, fg_color="transparent")
            row.pack(anchor="w")
            ctk.CTkLabel(
                row, text="Split every",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_secondary"],
            ).pack(side="left")
            self._n_var = ctk.StringVar(value="1")
            ctk.CTkEntry(
                row, textvariable=self._n_var, width=70,
                fg_color=COLORS["bg_card"], border_color=COLORS["border"],
                text_color=COLORS["text_primary"],
                font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
                corner_radius=RADIUS["md"],
            ).pack(side="left", padx=8)
            ctk.CTkLabel(
                row, text="pages",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_secondary"],
            ).pack(side="left")

    def _on_mode_change(self):
        self._build_opts()
        self._sync_split_preview()

    def _sync_split_preview(self):
        for w in self._preview_host.winfo_children():
            w.destroy()

        if not self._file:
            ctk.CTkLabel(
                self._preview_host,
                text="Load a PDF to see page previews while you choose split options.",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_muted"],
                wraplength=520,
                justify="left",
            ).pack(anchor="w")
            return

        mode = self._mode.get()
        if mode == "ranges":
            from ui.pdf_page_preview import RangePdfPreview
            rv = getattr(self, "_ranges_var", None)
            if rv is None:
                return
            rp = RangePdfPreview(
                self._preview_host,
                ranges_var=rv,
                get_pdf_path=lambda: self._file,
            )
            rp.pack(fill="x")
            rp.refresh_path()
        else:
            from ui.pdf_page_preview import SimplePdfPreview
            sp = SimplePdfPreview(self._preview_host)
            sp.pack(fill="x")
            sp.set_document(self._file)

    def _set_file(self, paths: list[str]):
        if paths:
            self._file = paths[0]
            self._file_label.configure(text=f"✓  {Path(self._file).name}")
            if not str(self._out_var.get()).strip():
                self._out_var.set(self.suggest_output_dir(self._file, "split"))
            self._sync_split_preview()

    def _browse_out(self):
        d = self.browse_directory()
        if d:
            self._out_var.set(d)

    def build_buttons(self, parent):
        PrimaryButton(parent, text="⊘  Split PDF", command=self.run, width=150).pack(side="left")

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return

        mode   = self._mode.get()
        out_dir = self._out_var.get().strip() or self.suggest_output_dir(self._file, "split")

        self.show_progress("Splitting PDF…")

        def _work():
            from core.split import (
                split_by_ranges, split_every_n_pages,
                split_each_page, split_by_bookmarks,
            )
            cb = lambda c, t: self.after(0, lambda: self.update_progress(c, t))

            if mode == "ranges":
                raw = getattr(self, "_ranges_var", ctk.StringVar()).get().strip()
                if not raw:
                    self.after(0, lambda: self.show_error("Enter at least one page range."))
                    return
                ranges = [r.strip() for r in raw.split(",") if r.strip()]
                result = split_by_ranges(self._file, out_dir, ranges, progress_cb=cb)

            elif mode == "every_n":
                try:
                    n = int(self._n_var.get())
                except Exception:
                    self.after(0, lambda: self.show_error("Enter a valid number for N."))
                    return
                result = split_every_n_pages(self._file, out_dir, n, progress_cb=cb)

            elif mode == "each_page":
                result = split_each_page(self._file, out_dir, progress_cb=cb)

            else:
                result = split_by_bookmarks(self._file, out_dir, progress_cb=cb)

            self.after(0, lambda: self._on_done(result, out_dir))

        self.run_in_thread(_work)

    def _on_done(self, result: dict, out_dir: str):
        if result["success"]:
            n = len(result.get("output_files", []))
            from services import history
            history.add_entry("Split", [self._file], out_dir, success=True, details=f"{n} parts")
            self.show_success(f"Split into {n} files", output_path=out_dir)
        else:
            self.show_error(result["error"])
