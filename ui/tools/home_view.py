"""
PDForge — ui/tools/home_view.py
Dashboard home screen with tool cards grid.
"""

from __future__ import annotations
import os
import customtkinter as ctk
from PIL import Image
from assets.themes.theme import COLORS, RADIUS

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_LOGO_PATH = os.path.join(_ROOT, "assets", "icons", "logo.png")


TOOL_CARDS = [
    {"id": "merge",         "icon": "⊕", "label": "Merge PDF",      "desc": "Combine multiple PDFs into one"},
    {"id": "split",         "icon": "⊘", "label": "Split PDF",       "desc": "Split by pages, ranges or bookmarks"},
    {"id": "compress",      "icon": "↓", "label": "Compress PDF",    "desc": "Reduce file size with quality control"},
    {"id": "pdf_to_word",   "icon": "W", "label": "PDF → Word",      "desc": "Convert to editable .docx"},
    {"id": "pdf_to_excel",  "icon": "X", "label": "PDF → Excel",     "desc": "Extract tables to spreadsheet"},
    {"id": "pdf_to_image",  "icon": "🖼","label": "PDF → Image",     "desc": "Export pages as PNG / JPEG"},
    {"id": "image_to_pdf",  "icon": "📄","label": "Image → PDF",     "desc": "Convert images to PDF"},
    {"id": "protect",       "icon": "🔒","label": "Protect PDF",     "desc": "Add password & permissions"},
    {"id": "unlock",        "icon": "🔓","label": "Unlock PDF",      "desc": "Remove password protection"},
    {"id": "watermark",     "icon": "◈", "label": "Watermark",       "desc": "Add text or image watermark"},
    {"id": "rotate",        "icon": "↻", "label": "Rotate Pages",    "desc": "Rotate all or specific pages"},
    {"id": "organize",      "icon": "⊞", "label": "Organize Pages",  "desc": "Reorder, delete or duplicate"},
    {"id": "number",        "icon": "#", "label": "Page Numbers",    "desc": "Add page numbering"},
    {"id": "header",        "icon": "≡", "label": "Header / Footer", "desc": "Add custom headers and footers"},
    {"id": "ocr",           "icon": "◉", "label": "OCR",             "desc": "Make scanned PDFs searchable"},
    {"id": "extract_text",  "icon": "¶", "label": "Extract Text",    "desc": "Export all text content"},
    {"id": "extract_images","icon": "⬚", "label": "Extract Images",  "desc": "Pull all embedded images"},
    {"id": "extract_tables","icon": "⊟", "label": "Extract Tables",  "desc": "Save tables to Excel or CSV"},
    {"id": "redact",        "icon": "▬", "label": "Redact PDF",      "desc": "Permanently black out content"},
    {"id": "metadata",      "icon": "ℹ", "label": "Edit Metadata",   "desc": "View and edit PDF properties"},
    {"id": "repair",        "icon": "⚙", "label": "Repair PDF",      "desc": "Fix corrupted PDF files"},
    {"id": "compare",       "icon": "⇔", "label": "Compare PDF",     "desc": "Diff two PDF versions"},
    {"id": "batch",         "icon": "⊡", "label": "Batch Process",   "desc": "Run operations on many files"},
    {"id": "pdf_to_text",   "icon": "T", "label": "PDF → Text",      "desc": "Plain text extraction to file"},
]


class HomeView(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=COLORS["bg_primary"],
            scrollbar_button_color=COLORS["scrollbar"],
            scrollbar_button_hover_color=COLORS["scrollbar_hover"],
            corner_radius=0,
        )

        # Find navigate callback from main window
        self._navigate = self._find_navigate(parent)
        self._build()

    def _find_navigate(self, widget):
        """Walk up widget tree to find MainWindow._navigate."""
        try:
            w = widget
            for _ in range(10):
                if hasattr(w, "_navigate"):
                    return w._navigate
                w = w.master
        except Exception:
            pass
        return lambda x: None

    def _build(self):
        # ── Hero ───────────────────────────────────────────────
        hero = ctk.CTkFrame(self, fg_color="transparent")
        hero.pack(fill="x", padx=40, pady=(36, 0))

        hero_row = ctk.CTkFrame(hero, fg_color="transparent")
        hero_row.pack(anchor="w")

        self._hero_logo = None
        if os.path.isfile(_LOGO_PATH):
            try:
                pil = Image.open(_LOGO_PATH).convert("RGBA")
                self._hero_logo = ctk.CTkImage(light_image=pil, dark_image=pil, size=(48, 48))
                ctk.CTkLabel(hero_row, image=self._hero_logo, text="").pack(side="left", padx=(0, 12))
            except Exception:
                pass

        ctk.CTkLabel(
            hero_row,
            text="PDForge",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            hero,
            text="Professional PDF toolkit — 100% free, 100% offline",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(anchor="w", pady=(6, 0))

        # Red accent bar
        ctk.CTkFrame(
            self,
            height=3,
            fg_color=COLORS["accent"],
            corner_radius=2,
        ).pack(fill="x", padx=40, pady=(20, 28))

        # ── Stats row ──────────────────────────────────────────
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=40, pady=(0, 28))

        self._recent_count_label = ctk.CTkLabel(
            stats_row,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_muted"],
        )
        self._recent_count_label.pack(side="left")
        self._load_stats()

        # ── Recent files ───────────────────────────────────────
        self._build_recent()

        # ── Tool grid ──────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="ALL TOOLS",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS["text_muted"],
            anchor="w",
        ).pack(anchor="w", padx=40, pady=(8, 12))

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=36, pady=(0, 40))

        cols = 4
        for i, card in enumerate(TOOL_CARDS):
            col = i % cols
            row = i // cols
            self._make_card(grid, card).grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        for c in range(cols):
            grid.columnconfigure(c, weight=1)

    def _make_card(self, parent, card: dict) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
            cursor="hand2",
        )

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(padx=16, pady=14, anchor="w")

        icon_frame = ctk.CTkFrame(
            inner,
            width=40, height=40,
            fg_color=COLORS["accent_subtle"],
            corner_radius=RADIUS["md"],
        )
        icon_frame.pack(anchor="w")
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(
            icon_frame,
            text=card["icon"],
            font=ctk.CTkFont(family="Segoe UI", size=18),
            text_color=COLORS["accent"],
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            inner,
            text=card["label"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(anchor="w", pady=(10, 0))

        ctk.CTkLabel(
            inner,
            text=card["desc"],
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_muted"],
            anchor="w",
            wraplength=160,
        ).pack(anchor="w", pady=(2, 0))

        # Hover effects
        def on_enter(e):
            frame.configure(border_color=COLORS["accent"], fg_color=COLORS["bg_hover"])
        def on_leave(e):
            frame.configure(border_color=COLORS["border"], fg_color=COLORS["bg_card"])
        def on_click(e, cid=card["id"]):
            self._navigate(cid)

        for w in [frame, inner] + list(inner.winfo_children()):
            try:
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.bind("<Button-1>", on_click)
            except Exception:
                pass

        return frame

    def _build_recent(self):
        from services import history
        recent = history.get_recent_files(limit=5)
        if not recent:
            return

        ctk.CTkLabel(
            self,
            text="RECENT FILES",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS["text_muted"],
            anchor="w",
        ).pack(anchor="w", padx=40, pady=(0, 8))

        recent_row = ctk.CTkFrame(self, fg_color="transparent")
        recent_row.pack(fill="x", padx=36, pady=(0, 24))

        for f in recent[:5]:
            import os
            name = os.path.basename(f["path"])
            size_str = ""
            if f.get("file_size"):
                sz = f["file_size"]
                size_str = f"{sz/1024:.0f} KB" if sz < 1048576 else f"{sz/1048576:.1f} MB"

            chip = ctk.CTkFrame(
                recent_row,
                fg_color=COLORS["bg_card"],
                corner_radius=RADIUS["md"],
                border_width=1,
                border_color=COLORS["border"],
                cursor="hand2",
            )
            chip.pack(side="left", padx=(0, 8))

            ctk.CTkLabel(
                chip,
                text=f"PDF  {name[:24]}{'…' if len(name) > 24 else ''}  {size_str}",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_secondary"],
                padx=12, pady=8,
            ).pack()

    def _load_stats(self):
        try:
            from services import history
            recent = history.get_recent_files(limit=100)
            hist   = history.get_history(limit=200)
            ops    = len(hist)
            self._recent_count_label.configure(
                text=f"{len(recent)} recent files  ·  {ops} operations total"
            )
        except Exception:
            pass
