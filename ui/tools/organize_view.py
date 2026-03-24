"""PDForge — ui/tools/organize_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton
from assets.themes.theme import COLORS, RADIUS


class OrganizeView(BaseToolView):
    ICON     = "⊞"
    TITLE    = "Organize Pages"
    SUBTITLE = "Reorder, delete or duplicate pages inside a PDF"

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

        self.section(parent, "OPERATION")
        self._op = ctk.StringVar(value="reorder")
        ops = [
            ("reorder", "Reorder pages  (enter new order as comma-separated numbers)"),
            ("delete",  "Delete pages  (specify pages to remove)"),
        ]
        for val, label in ops:
            ctk.CTkRadioButton(parent, text=label, variable=self._op, value=val,
                command=self._build_opts,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
            ).pack(anchor="w", pady=3)

        self._opts = ctk.CTkFrame(parent, fg_color="transparent")
        self._opts.pack(fill="x", pady=(10, 0))
        self._build_opts()

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

    def _build_opts(self):
        for w in self._opts.winfo_children():
            w.destroy()
        if self._op.get() == "reorder":
            ctk.CTkLabel(self._opts,
                text="New page order (e.g.  3,1,2,4  to put page 3 first):",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_secondary"]).pack(anchor="w")
            self._order_var = ctk.StringVar()
            ctk.CTkEntry(self._opts, textvariable=self._order_var,
                placeholder_text="e.g.  2, 1, 3, 4, 5",
                fg_color=COLORS["bg_card"], border_color=COLORS["border"],
                text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
                font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
                corner_radius=RADIUS["md"]).pack(fill="x", pady=(4, 0))
        else:
            ctk.CTkLabel(self._opts,
                text="Pages to delete (range string — e.g. 1, 3-5, last):",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_secondary"]).pack(anchor="w")
            self._del_var = ctk.StringVar()
            ctk.CTkEntry(self._opts, textvariable=self._del_var,
                placeholder_text="e.g.  1, 3-5, last",
                fg_color=COLORS["bg_card"], border_color=COLORS["border"],
                text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
                font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
                corner_radius=RADIUS["md"]).pack(fill="x", pady=(4, 0))

    def _set_file(self, paths):
        if paths:
            self._file = paths[0]
            self._file_label.configure(text=f"✓  {Path(self._file).name}")
            self.autofill_output_entry(self._out_var, self._file, "organized")
            self._page_preview.set_document(self._file)

    def build_buttons(self, parent):
        PrimaryButton(parent, text="⊞  Apply", command=self.run, width=140).pack(side="left")

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return
        out = self._out_var.get().strip() or self.suggest_output(self._file, "organized")
        op = self._op.get()
        self.show_progress("Processing…")

        def _work():
            cb = lambda c, t: self.after(0, lambda: self.update_progress(c, t))
            if op == "reorder":
                raw = getattr(self, "_order_var", ctk.StringVar()).get().strip()
                try:
                    order = [int(x.strip()) for x in raw.split(",") if x.strip()]
                except Exception:
                    self.after(0, lambda: self.show_error("Enter valid page numbers."))
                    return
                from core.organize import reorder_pages
                result = reorder_pages(self._file, out, order, progress_cb=cb)
            else:
                raw = getattr(self, "_del_var", ctk.StringVar()).get().strip()
                if not raw:
                    self.after(0, lambda: self.show_error("Specify pages to delete."))
                    return
                from core.organize import delete_pages
                result = delete_pages(self._file, out, raw, progress_cb=cb)
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result, out):
        if result["success"]:
            from services import history
            history.add_entry("Organize", [self._file], out, success=True)
            self.show_success("Pages organized successfully", output_path=out)
        else:
            self.show_error(result["error"])
