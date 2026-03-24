"""PDForge — ui/tools/settings_view.py"""

from __future__ import annotations
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import PrimaryButton, SecondaryButton, ThemedSwitch, ThemedComboBox
from assets.themes.theme import COLORS, RADIUS


class SettingsView(BaseToolView):
    ICON     = "⚙"
    TITLE    = "Settings"
    SUBTITLE = "Configure PDForge preferences"

    def __init__(self, parent):
        super().__init__(parent)

    def build_ui(self, parent):
        from services import settings

        # ── General ────────────────────────────────────────────
        self.section(parent, "GENERAL")

        # Default output directory
        ctk.CTkLabel(parent, text="Default output folder:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(anchor="w")
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(4, 8))
        self._out_dir_var = ctk.StringVar(value=settings.get("default_output_dir", ""))
        ctk.CTkEntry(row, textvariable=self._out_dir_var,
            placeholder_text="Same folder as input file (default)",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"]).pack(side="left", fill="x", expand=True, padx=(0, 8))
        SecondaryButton(row, text="Browse",
            command=lambda: self._out_dir_var.set(self.browse_directory()),
            width=90).pack(side="left")

        # Remember window size
        self._remember_size = ctk.BooleanVar(value=settings.get("remember_window_size", True))
        ThemedSwitch(parent, text="Remember window size",
            variable=self._remember_size).pack(anchor="w", pady=3)

        self._auto_open = ctk.BooleanVar(value=settings.get("auto_open_output", False))
        ThemedSwitch(parent, text="Auto-open output folder after operation",
            variable=self._auto_open).pack(anchor="w", pady=3)

        self._confirm_overwrite = ctk.BooleanVar(value=settings.get("confirm_overwrite", True))
        ThemedSwitch(parent, text="Confirm before overwriting existing files",
            variable=self._confirm_overwrite).pack(anchor="w", pady=3)

        # ── Compress defaults ──────────────────────────────────
        self.section(parent, "COMPRESSION DEFAULTS")
        preset_row = ctk.CTkFrame(parent, fg_color="transparent")
        preset_row.pack(anchor="w")
        ctk.CTkLabel(preset_row, text="Default quality preset:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(side="left")
        self._compress_preset = ctk.StringVar(value=settings.get("default_compress_preset", "ebook"))
        ThemedComboBox(preset_row,
            values=["screen", "ebook", "printer", "prepress"],
            variable=self._compress_preset, width=140).pack(side="left", padx=8)

        # ── Convert defaults ───────────────────────────────────
        self.section(parent, "CONVERT DEFAULTS")
        fmt_row = ctk.CTkFrame(parent, fg_color="transparent")
        fmt_row.pack(anchor="w")
        ctk.CTkLabel(fmt_row, text="Default image format:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(side="left")
        self._img_format = ctk.StringVar(value=settings.get("default_image_format", "PNG"))
        ThemedComboBox(fmt_row,
            values=["PNG", "JPEG", "WEBP"],
            variable=self._img_format, width=100).pack(side="left", padx=8)

        dpi_row = ctk.CTkFrame(parent, fg_color="transparent")
        dpi_row.pack(anchor="w", pady=(8, 0))
        ctk.CTkLabel(dpi_row, text="Default DPI:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(side="left")
        self._dpi_var = ctk.StringVar(value=str(settings.get("default_dpi", 150)))
        ctk.CTkEntry(dpi_row, textvariable=self._dpi_var, width=70,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=32,
            corner_radius=RADIUS["md"]).pack(side="left", padx=8)

        # ── OCR defaults ───────────────────────────────────────
        self.section(parent, "OCR DEFAULTS")
        lang_row = ctk.CTkFrame(parent, fg_color="transparent")
        lang_row.pack(anchor="w")
        ctk.CTkLabel(lang_row, text="Default OCR language:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(side="left")
        self._ocr_lang = ctk.StringVar(value=settings.get("default_ocr_lang", "eng"))
        ThemedComboBox(lang_row,
            values=["eng", "ara", "fra", "deu", "spa", "ita", "por", "rus"],
            variable=self._ocr_lang, width=120).pack(side="left", padx=8)

    def build_buttons(self, parent):
        PrimaryButton(parent, text="⚙  Save Settings", command=self._save, width=160).pack(side="left")
        SecondaryButton(parent, text="Reset to defaults", command=self._reset, width=150).pack(side="left", padx=(10, 0))

    def _save(self):
        from services import settings
        try:
            dpi = int(self._dpi_var.get())
        except Exception:
            dpi = 150

        settings.set("default_output_dir",      self._out_dir_var.get().strip())
        settings.set("remember_window_size",     bool(self._remember_size.get()))
        settings.set("auto_open_output",         bool(self._auto_open.get()))
        settings.set("confirm_overwrite",        bool(self._confirm_overwrite.get()))
        settings.set("default_compress_preset",  self._compress_preset.get())
        settings.set("default_image_format",     self._img_format.get())
        settings.set("default_dpi",              dpi)
        settings.set("default_ocr_lang",         self._ocr_lang.get())

        self._result.show_success("Settings saved")

    def _reset(self):
        from services import settings
        settings.reset()
        self._result.show_success("Settings reset to defaults — reopen this page to see changes")
