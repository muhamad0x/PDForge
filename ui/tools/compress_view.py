"""PDForge — ui/tools/compress_view.py"""

from __future__ import annotations
import os
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton
from assets.themes.theme import COLORS, RADIUS

PRESETS = {
    "screen":   ("Screen / Web",   "72 DPI — smallest size, low quality"),
    "ebook":    ("eBook",          "96 DPI — good balance (recommended)"),
    "printer":  ("Print",          "150 DPI — high quality for printing"),
    "prepress": ("Pre-press",      "300 DPI — maximum quality"),
}


class CompressView(BaseToolView):
    ICON     = "↓"
    TITLE    = "Compress PDF"
    SUBTITLE = "Reduce file size while controlling output quality"

    def __init__(self, parent):
        self._file = ""
        super().__init__(parent)

    def build_ui(self, parent):
        self._drop = DropZone(
            parent, on_files_dropped=self._set_file,
            accept_multiple=False, height=120,
            label="Drop a PDF file here, or click to browse",
        )
        self._drop.pack(fill="x", pady=(0, 12))

        self._file_label = ctk.CTkLabel(
            parent, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["accent"], anchor="w",
        )
        self._file_label.pack(anchor="w", pady=(0, 8))

        # Quality preset
        self.section(parent, "QUALITY PRESET")
        self._preset = ctk.StringVar(value="ebook")

        for val, (label, desc) in PRESETS.items():
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(anchor="w", pady=3)
            ctk.CTkRadioButton(
                row, text=label, variable=self._preset, value=val,
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_primary"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
                width=130,
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=f"— {desc}",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_muted"],
            ).pack(side="left", padx=(8, 0))

        # Output
        self.section(parent, "OUTPUT")
        out_row = ctk.CTkFrame(parent, fg_color="transparent")
        out_row.pack(fill="x")
        self._out_var = ctk.StringVar()
        ctk.CTkEntry(
            out_row, textvariable=self._out_var,
            placeholder_text="Output path (auto-generated if empty)",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"],
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))
        SecondaryButton(out_row, text="Browse", command=self._browse_out, width=90).pack(side="left")

    def build_buttons(self, parent):
        PrimaryButton(parent, text="↓  Compress", command=self.run, width=150).pack(side="left")
        self._size_label = ctk.CTkLabel(
            parent, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_muted"],
        )
        self._size_label.pack(side="left", padx=16)

    def _set_file(self, paths: list[str]):
        if paths:
            self._file = paths[0]
            try:
                sz = os.path.getsize(self._file)
                sz_str = f"{sz/1048576:.1f} MB" if sz >= 1048576 else f"{sz/1024:.0f} KB"
            except Exception:
                sz_str = ""
            name = Path(self._file).name
            self._file_label.configure(text=f"✓  {name}  ({sz_str})")
            self.autofill_output_entry(self._out_var, self._file, "compressed")

    def _browse_out(self):
        default = self.suggest_output(self._file, "compressed") if self._file else "compressed.pdf"
        path = self.browse_save_pdf(default_name=Path(default).name)
        if path:
            self._out_var.set(path)

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return

        out    = self._out_var.get().strip() or self.suggest_output(self._file, "compressed")
        preset = self._preset.get()
        self.show_progress("Compressing…")

        def _work():
            from core.compress import compress_pdf
            result = compress_pdf(
                self._file, out, preset=preset,
                progress_cb=lambda c, t: self.after(0, lambda: self.update_progress(c, t)),
            )
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result: dict, out: str):
        if result["success"]:
            orig = result.get("original_size", 0)
            comp = result.get("compressed_size", 0)
            ratio = result.get("ratio", 0)
            orig_s = f"{orig/1048576:.1f} MB" if orig >= 1048576 else f"{orig/1024:.0f} KB"
            comp_s = f"{comp/1048576:.1f} MB" if comp >= 1048576 else f"{comp/1024:.0f} KB"
            msg = f"Compressed {orig_s} → {comp_s}  ({ratio:.1f}% reduction)"
            from services import history
            history.add_entry("Compress", [self._file], out, success=True, details=msg)
            self.show_success(msg, output_path=out)
        else:
            self.show_error(result["error"])
