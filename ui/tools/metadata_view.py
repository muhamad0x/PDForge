"""PDForge — ui/tools/metadata_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton, DangerButton
from assets.themes.theme import COLORS, RADIUS
from core.repair import METADATA_FIELDS


class MetadataView(BaseToolView):
    ICON     = "ℹ"
    TITLE    = "Edit Metadata"
    SUBTITLE = "View and edit PDF properties — title, author, keywords, and more"

    def __init__(self, parent):
        self._file = ""
        self._field_vars: dict[str, ctk.StringVar] = {}
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

        self.section(parent, "METADATA FIELDS")
        self._fields_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self._fields_frame.pack(fill="x")
        self._build_fields()

        strip_row = ctk.CTkFrame(parent, fg_color="transparent")
        strip_row.pack(anchor="w", pady=(12, 0))
        self._strip_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(strip_row, text="Strip all existing metadata before saving",
            variable=self._strip_var,
            checkmark_color=COLORS["text_primary"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_secondary"],
            font=ctk.CTkFont(family="Segoe UI", size=12)).pack(side="left")

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

    def _build_fields(self):
        for w in self._fields_frame.winfo_children():
            w.destroy()
        self._field_vars.clear()
        for i, field in enumerate(METADATA_FIELDS):
            row = ctk.CTkFrame(self._fields_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=field + ":",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_secondary"],
                width=110, anchor="e").pack(side="left", padx=(0, 8))
            var = ctk.StringVar()
            self._field_vars[field] = var
            ctk.CTkEntry(row, textvariable=var,
                fg_color=COLORS["bg_card"], border_color=COLORS["border"],
                text_color=COLORS["text_primary"],
                font=ctk.CTkFont(family="Segoe UI", size=13), height=32,
                corner_radius=RADIUS["md"]).pack(side="left", fill="x", expand=True)

    def _set_file(self, paths):
        if paths:
            self._file = paths[0]
            self._file_label.configure(text=f"✓  {Path(self._file).name}")
            self.autofill_output_entry(self._out_var, self._file, "metadata")
            self._load_metadata()

    def _load_metadata(self):
        if not self._file:
            return
        from core.repair import get_metadata
        result = get_metadata(self._file)
        if result["success"]:
            meta = result["metadata"]
            for field, var in self._field_vars.items():
                var.set(meta.get(field, ""))

    def build_buttons(self, parent):
        PrimaryButton(parent, text="ℹ  Save Metadata", command=self.run, width=170).pack(side="left")
        SecondaryButton(parent, text="Reload from file", command=self._load_metadata, width=150).pack(side="left", padx=(10, 0))

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return
        out = self._out_var.get().strip() or self.suggest_output(self._file, "metadata")
        updates = {field: var.get() for field, var in self._field_vars.items() if var.get().strip()}
        strip = bool(self._strip_var.get())
        self.show_progress("Saving metadata…")

        def _work():
            from core.repair import set_metadata
            result = set_metadata(self._file, out, updates=updates, strip_existing=strip,
                progress_cb=lambda c, t: self.after(0, lambda: self.update_progress(c, t)))
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result, out):
        if result["success"]:
            from services import history
            history.add_entry("Metadata", [self._file], out, success=True)
            self.show_success("Metadata saved successfully", output_path=out)
        else:
            self.show_error(result["error"])
