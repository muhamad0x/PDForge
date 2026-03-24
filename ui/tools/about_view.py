"""PDForge — ui/tools/about_view.py — Dedicated About page."""

from __future__ import annotations
import customtkinter as ctk
from assets.themes.theme import COLORS, RADIUS


class AboutView(ctk.CTkFrame):
    """Standalone About page with app info and creator links."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], corner_radius=0, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["scrollbar"],
            scrollbar_button_hover_color=COLORS["scrollbar_hover"],
        )
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=0, column=0, padx=80, pady=60, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=40, pady=36)

        ctk.CTkLabel(
            inner,
            text="PDForge  v1.0.0",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            inner,
            text="100% free · 100% offline · Open source",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", pady=(0, 12))

        ctk.CTkLabel(
            inner,
            text="Built with Python, CustomTkinter, pypdf, pdfplumber, reportlab",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 20))

        ctk.CTkFrame(inner, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            inner,
            text="Mohamed Abdelghani",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            inner,
            text="Created to give everyone a powerful PDF toolkit without paywalls or subscriptions. "
                 "Free for everyone because good tools should be accessible.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLORS["text_secondary"],
            justify="left",
            wraplength=480,
        ).pack(anchor="w", pady=(0, 24))

        def _open_url(url: str):
            import webbrowser
            webbrowser.open(url, autoraise=True)

        def _load_icon(domain: str, size: int = 28):
            try:
                import urllib.request
                from io import BytesIO
                from PIL import Image
                url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
                req = urllib.request.Request(url, headers={"User-Agent": "PDForge/1.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    img = Image.open(BytesIO(r.read())).convert("RGBA")
                if img.size[0] != size:
                    img = img.resize((size, size), Image.Resampling.LANCZOS)
                return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
            except Exception:
                return None

        links_row = ctk.CTkFrame(inner, fg_color="transparent")
        links_row.pack(anchor="w")
        for domain, profile_url in [
            ("github.com", "https://github.com/muhamad0x"),
            ("x.com", "https://x.com/muhamad0x"),
            ("linkedin.com", "https://linkedin.com/in/muhamad0x"),
        ]:
            ctk_img = _load_icon(domain)
            if ctk_img:
                btn = ctk.CTkButton(
                    links_row, text="", width=44, height=44,
                    image=ctk_img, fg_color="transparent",
                    hover_color=COLORS["bg_hover"],
                    corner_radius=RADIUS["md"],
                    command=lambda u=profile_url: _open_url(u),
                )
            else:
                btn = ctk.CTkButton(
                    links_row, text="→", width=44, height=44,
                    fg_color="transparent", hover_color=COLORS["bg_hover"],
                    text_color=COLORS["accent"],
                    command=lambda u=profile_url: _open_url(u),
                )
            btn.pack(side="left", padx=(0, 10))
