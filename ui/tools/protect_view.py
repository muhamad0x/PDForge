"""PDForge — ui/tools/protect_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton, ThemedSwitch
from assets.themes.theme import COLORS, RADIUS


class ProtectView(BaseToolView):
    ICON     = "🔒"
    TITLE    = "Protect PDF"
    SUBTITLE = "Encrypt with password and set document permissions"

    def __init__(self, parent):
        self._file = ""
        super().__init__(parent)

    def build_ui(self, parent):
        self._drop = DropZone(parent, on_files_dropped=self._set_file,
                              accept_multiple=False, height=110,
                              label="Drop a PDF file here, or click to browse")
        self._drop.pack(fill="x", pady=(0, 12))

        self._file_label = ctk.CTkLabel(parent, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["accent"], anchor="w")
        self._file_label.pack(anchor="w", pady=(0, 8))

        self.section(parent, "PASSWORDS")
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x")

        for col, (label, attr) in enumerate([
            ("User password (to open)", "_user_pwd"),
            ("Owner password (full control)", "_owner_pwd"),
        ]):
            f = ctk.CTkFrame(grid, fg_color="transparent")
            f.grid(row=0, column=col, padx=(0, 16) if col == 0 else 0, sticky="ew")
            ctk.CTkLabel(f, text=label,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_secondary"]).pack(anchor="w")
            entry = ctk.CTkEntry(f, show="•",
                fg_color=COLORS["bg_card"], border_color=COLORS["border"],
                text_color=COLORS["text_primary"],
                font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
                corner_radius=RADIUS["md"])
            entry.pack(fill="x", pady=(4, 0))
            setattr(self, attr, entry)

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        self.section(parent, "PERMISSIONS")
        perms = [
            ("_allow_print",  "Allow printing"),
            ("_allow_copy",   "Allow copying text/images"),
            ("_allow_edit",   "Allow editing content"),
            ("_allow_annot",  "Allow annotations"),
        ]
        defaults = [True, True, False, True]
        for (attr, label), default in zip(perms, defaults):
            sw = ThemedSwitch(parent, text=label)
            sw.pack(anchor="w", pady=3)
            if default:
                sw.select()
            setattr(self, attr, sw)

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
        PrimaryButton(parent, text="🔒  Protect PDF", command=self.run, width=160).pack(side="left")

    def _set_file(self, paths):
        if paths:
            self._file = paths[0]
            self._file_label.configure(text=f"✓  {Path(self._file).name}")
            self.autofill_output_entry(self._out_var, self._file, "protected")

    def _browse_out(self):
        path = self.browse_save_pdf(default_name=Path(
            self.suggest_output(self._file, "protected") if self._file else "protected.pdf"
        ).name)
        if path:
            self._out_var.set(path)

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return
        user_pwd = self._user_pwd.get().strip()
        if not user_pwd:
            self.show_error("User password cannot be empty.")
            return
        owner_pwd = self._owner_pwd.get().strip() or None
        out = self._out_var.get().strip() or self.suggest_output(self._file, "protected")
        self.show_progress("Encrypting…")

        def _work():
            from core.protect import encrypt_pdf
            result = encrypt_pdf(
                self._file, out,
                user_password=user_pwd,
                owner_password=owner_pwd,
                allow_printing=bool(self._allow_print.get()),
                allow_copying=bool(self._allow_copy.get()),
                allow_editing=bool(self._allow_edit.get()),
                allow_annotations=bool(self._allow_annot.get()),
                progress_cb=lambda c, t: self.after(0, lambda: self.update_progress(c, t)),
            )
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result, out):
        if result["success"]:
            from services import history
            history.add_entry("Protect", [self._file], out, success=True)
            self.show_success("PDF protected with password", output_path=out)
        else:
            self.show_error(result["error"])
