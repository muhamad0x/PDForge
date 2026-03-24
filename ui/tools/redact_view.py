"""PDForge — ui/tools/redact_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton
from assets.themes.theme import COLORS, RADIUS


class RedactView(BaseToolView):
    ICON     = "▬"
    TITLE    = "Redact PDF"
    SUBTITLE = "Permanently black out sensitive text — cannot be undone"

    def __init__(self, parent):
        self._file = ""
        super().__init__(parent)

    def build_ui(self, parent):
        # Warning banner
        warn = ctk.CTkFrame(parent,
            fg_color=COLORS["error_soft"],
            corner_radius=8, border_color=COLORS["error"], border_width=1)
        warn.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(warn,
            text="⚠  Redaction is permanent and irreversible. Work on a copy.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["error"]).pack(padx=16, pady=10)

        self._drop = DropZone(parent, on_files_dropped=self._set_file,
                              accept_multiple=False, height=110,
                              label="Drop a PDF here, or click to browse")
        self._drop.pack(fill="x", pady=(0, 12))
        self._file_label = ctk.CTkLabel(parent, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["accent"], anchor="w")
        self._file_label.pack(anchor="w", pady=(0, 8))

        self.section(parent, "SEARCH TERMS TO REDACT")
        ctk.CTkLabel(parent,
            text="Enter terms to find and redact (one per line):",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(anchor="w")
        self._terms_box = ctk.CTkTextbox(parent,
            height=100,
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            corner_radius=RADIUS["md"])
        self._terms_box.pack(fill="x", pady=(6, 0))

        opts_row = ctk.CTkFrame(parent, fg_color="transparent")
        opts_row.pack(anchor="w", pady=(8, 0))
        self._case_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opts_row, text="Case-sensitive matching",
            variable=self._case_var,
            checkmark_color=COLORS["text_primary"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_secondary"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
        ).pack(side="left")

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
            self.autofill_output_entry(self._out_var, self._file, "redacted")

    def build_buttons(self, parent):
        PrimaryButton(parent, text="▬  Apply Redaction", command=self.run, width=180).pack(side="left")

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return
        raw = self._terms_box.get("1.0", "end").strip()
        terms = [t.strip() for t in raw.splitlines() if t.strip()]
        if not terms:
            self.show_error("Enter at least one search term.")
            return
        out = self._out_var.get().strip() or self.suggest_output(self._file, "redacted")
        case = bool(self._case_var.get())
        self.show_progress("Searching and redacting…")

        def _work():
            from core.redact import redact_text_occurrences
            result = redact_text_occurrences(
                self._file, out, search_terms=terms, case_sensitive=case,
                progress_cb=lambda c, t: self.after(0, lambda: self.update_progress(c, t)),
            )
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result, out):
        if result["success"]:
            n = result.get("occurrences_found", 0)
            from services import history
            history.add_entry("Redact", [self._file], out, success=True,
                              details=f"{n} occurrences redacted")
            self.show_success(f"{n} occurrence(s) permanently redacted", output_path=out)
        else:
            self.show_error(result["error"])
