"""PDForge — ui/tools/history_view.py"""

from __future__ import annotations
import os
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import PrimaryButton, SecondaryButton, DangerButton
from assets.themes.theme import COLORS, RADIUS


class HistoryView(BaseToolView):
    ICON     = "⊙"
    TITLE    = "History"
    SUBTITLE = "All operations performed in PDForge"

    def __init__(self, parent):
        super().__init__(parent)

    def build_ui(self, parent):
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 12))

        SecondaryButton(toolbar, text="⟳  Refresh", command=self._load, width=100).pack(side="left")
        DangerButton(toolbar, text="Clear All", command=self._clear_all, width=100).pack(side="left", padx=(10, 0))

        self._scroll = ctk.CTkScrollableFrame(parent,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"],
            scrollbar_button_color=COLORS["scrollbar"],
            scrollbar_button_hover_color=COLORS["scrollbar_hover"],
            height=500,
        )
        self._scroll.pack(fill="both", expand=True)
        self._load()

    def _load(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        from services import history
        entries = history.get_history(limit=200)

        if not entries:
            ctk.CTkLabel(self._scroll, text="No history yet",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=COLORS["text_muted"]).pack(pady=40)
            return

        # Header row
        hdr = ctk.CTkFrame(self._scroll, fg_color="transparent")
        hdr.pack(fill="x", padx=8, pady=(4, 2))
        for text, width in [("Time", 140), ("Operation", 120), ("Input", 220), ("Output", 220), ("Status", 70)]:
            ctk.CTkLabel(hdr, text=text, width=width,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=COLORS["text_muted"], anchor="w").pack(side="left")

        # Separator
        ctk.CTkFrame(self._scroll, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=4)

        for entry in entries:
            row = ctk.CTkFrame(self._scroll,
                fg_color=COLORS["bg_hover"] if entries.index(entry) % 2 == 0 else "transparent",
                corner_radius=RADIUS["sm"], height=38)
            row.pack(fill="x", padx=4, pady=1)
            row.pack_propagate(False)

            ts = entry["timestamp"][:16] if entry["timestamp"] else ""
            inputs = ", ".join(os.path.basename(f) for f in entry["input_files"][:2])
            if len(entry["input_files"]) > 2:
                inputs += f" +{len(entry['input_files'])-2} more"
            out = os.path.basename(entry["output_path"]) if entry["output_path"] else "—"
            status_color = COLORS["success"] if entry["success"] else COLORS["error"]
            status_text  = "✓" if entry["success"] else "✗"

            for text, width in [(ts, 140), (entry["operation"], 120), (inputs, 220), (out, 220)]:
                ctk.CTkLabel(row, text=text, width=width,
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color=COLORS["text_secondary"], anchor="w",
                ).pack(side="left", padx=(8, 0))

            ctk.CTkLabel(row, text=status_text, width=70,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=status_color, anchor="w",
            ).pack(side="left", padx=(8, 0))

    def _clear_all(self):
        from services import history
        history.clear_history()
        self._load()

    def build_buttons(self, parent):
        pass  # no action buttons needed
