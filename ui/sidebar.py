"""
PDForge — ui/sidebar.py
Collapsible sidebar with tool categories and navigation items.
"""

from __future__ import annotations
import os
from typing import Callable
import customtkinter as ctk
from PIL import Image
from assets.themes.theme import COLORS, FONTS, RADIUS, SPACING, SIDEBAR_WIDTH

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOGO_PATH = os.path.join(_ROOT, "assets", "icons", "logo.png")


TOOL_GROUPS = [
    {
        "label": "ORGANIZE",
        "items": [
            {"id": "home",       "label": "Home",         "icon": "⌂"},
            {"id": "merge",      "label": "Merge PDF",     "icon": "⊕"},
            {"id": "split",      "label": "Split PDF",     "icon": "⊘"},
            {"id": "organize",   "label": "Organize Pages","icon": "⊞"},
            {"id": "rotate",     "label": "Rotate Pages",  "icon": "↻"},
        ],
    },
    {
        "label": "OPTIMIZE",
        "items": [
            {"id": "compress",   "label": "Compress PDF",  "icon": "↓"},
            {"id": "repair",     "label": "Repair PDF",    "icon": "⚙"},
        ],
    },
    {
        "label": "CONVERT",
        "items": [
            {"id": "pdf_to_word",    "label": "PDF → Word",    "icon": "W"},
            {"id": "pdf_to_excel",   "label": "PDF → Excel",   "icon": "X"},
            {"id": "pdf_to_image",   "label": "PDF → Image",   "icon": "🖼"},
            {"id": "image_to_pdf",   "label": "Image → PDF",   "icon": "📄"},
            {"id": "pdf_to_text",    "label": "PDF → Text",    "icon": "T"},
        ],
    },
    {
        "label": "SECURITY",
        "items": [
            {"id": "protect",    "label": "Protect PDF",   "icon": "🔒"},
            {"id": "unlock",     "label": "Unlock PDF",    "icon": "🔓"},
            {"id": "redact",     "label": "Redact PDF",    "icon": "▬"},
        ],
    },
    {
        "label": "ENRICH",
        "items": [
            {"id": "watermark",  "label": "Watermark",     "icon": "◈"},
            {"id": "number",     "label": "Page Numbers",  "icon": "#"},
            {"id": "header",     "label": "Header/Footer", "icon": "≡"},
            {"id": "ocr",        "label": "OCR",           "icon": "◉"},
        ],
    },
    {
        "label": "EXTRACT",
        "items": [
            {"id": "extract_text",   "label": "Extract Text",   "icon": "¶"},
            {"id": "extract_images", "label": "Extract Images", "icon": "⬚"},
            {"id": "extract_tables", "label": "Extract Tables", "icon": "⊟"},
            {"id": "metadata",       "label": "Edit Metadata",  "icon": "ℹ"},
        ],
    },
    {
        "label": "TOOLS",
        "items": [
            {"id": "compare",    "label": "Compare PDF",   "icon": "⇔"},
            {"id": "batch",      "label": "Batch Process", "icon": "⊡"},
            {"id": "about",      "label": "About",         "icon": "ℹ"},
        ],
    },
]


class Sidebar(ctk.CTkFrame):
    """
    Left-side navigation panel.
    Calls on_navigate(tool_id: str) on item click.
    """

    def __init__(
        self,
        parent,
        on_navigate: Callable[[str], None],
        **kwargs,
    ):
        super().__init__(
            parent,
            width=SIDEBAR_WIDTH,
            fg_color=COLORS["bg_secondary"],
            corner_radius=0,
            **kwargs,
        )
        self.grid_propagate(False)
        self._on_navigate = on_navigate
        self._active_id   = "home"
        self._buttons: dict[str, ctk.CTkButton] = {}

        self._build()

    def _build(self):
        # ── Logo area ──────────────────────────────────────────
        logo_frame = ctk.CTkFrame(self, fg_color="transparent", height=64)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        logo_inner = ctk.CTkFrame(logo_frame, fg_color="transparent")
        logo_inner.place(x=16, rely=0.5, anchor="w")
        self._logo_img = None
        if os.path.isfile(_LOGO_PATH):
            try:
                pil = Image.open(_LOGO_PATH).convert("RGBA")
                self._logo_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(40, 40))
                ctk.CTkLabel(logo_inner, image=self._logo_img, text="").pack(side="left")
                ctk.CTkLabel(
                    logo_inner, text="PDForge",
                    font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
                    text_color=COLORS["text_primary"], anchor="w",
                ).pack(side="left", padx=(10, 0))
            except Exception:
                ctk.CTkLabel(
                    logo_inner, text="PDForge",
                    font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
                    text_color=COLORS["text_primary"], anchor="w",
                ).pack()
        else:
            ctk.CTkLabel(
                logo_inner, text="PDForge",
                font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
                text_color=COLORS["text_primary"], anchor="w",
            ).pack()

        # Separator
        ctk.CTkFrame(self, height=1, fg_color=COLORS["border"]).pack(fill="x")

        # ── Scrollable tool list ───────────────────────────────
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["scrollbar"],
            scrollbar_button_hover_color=COLORS["scrollbar_hover"],
        )
        scroll.pack(fill="both", expand=True, pady=(8, 0))

        for group in TOOL_GROUPS:
            # Group label
            ctk.CTkLabel(
                scroll,
                text=group["label"],
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color=COLORS["text_muted"],
                anchor="w",
                padx=20,
            ).pack(fill="x", pady=(12, 2))

            for item in group["items"]:
                btn = self._make_nav_button(scroll, item)
                btn.pack(fill="x", padx=8, pady=1)
                self._buttons[item["id"]] = btn

        # ── Bottom: History & Settings ─────────────────────────
        ctk.CTkFrame(self, height=1, fg_color=COLORS["border"]).pack(fill="x")

        bottom = ctk.CTkFrame(self, fg_color="transparent", height=52)
        bottom.pack(fill="x")
        bottom.pack_propagate(False)

        for tool_id, label, icon in [
            ("history",  "History",  "⊙"),
            ("settings", "Settings", "⚙"),
        ]:
            btn = ctk.CTkButton(
                bottom,
                text=f"{icon}  {label}",
                command=lambda tid=tool_id: self._navigate(tid),
                fg_color="transparent",
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=12),
                anchor="w",
                corner_radius=RADIUS["md"],
                height=36,
                width=100,
            )
            btn.pack(side="left", padx=6, pady=8)
            self._buttons[tool_id] = btn

    def _make_nav_button(self, parent, item: dict) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=f"{item['icon']}  {item['label']}",
            command=lambda: self._navigate(item["id"]),
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            anchor="w",
            corner_radius=RADIUS["md"],
            height=38,
        )

    def _navigate(self, tool_id: str):
        self._set_active(tool_id)
        self._on_navigate(tool_id)

    def _set_active(self, tool_id: str):
        # Deactivate previous
        if self._active_id in self._buttons:
            self._buttons[self._active_id].configure(
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
            )
        # Activate new
        self._active_id = tool_id
        if tool_id in self._buttons:
            self._buttons[tool_id].configure(
                fg_color=COLORS["bg_active"],
                text_color=COLORS["accent"],
            )

    def set_active(self, tool_id: str):
        """External setter."""
        self._set_active(tool_id)
