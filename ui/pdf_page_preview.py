"""Reusable PDF thumbnail previews for tools that need page context."""

from __future__ import annotations

import threading
from typing import Callable

import customtkinter as ctk
from PIL import Image

from assets.themes.theme import COLORS, RADIUS
from services.pdf_preview import pdf_page_count, render_page_pil


def _pil_to_ctk_image(pil: Image.Image) -> ctk.CTkImage:
    return ctk.CTkImage(light_image=pil, dark_image=pil, size=(pil.width, pil.height))


class SimplePdfPreview(ctk.CTkFrame):
    """Single-page navigator: ◀ page ▶ + thumbnail."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self._path = ""
        self._page = 1
        self._total = 0
        self._thumb_job = None
        self._gen = 0
        self._ctk_img: ctk.CTkImage | None = None

        ctk.CTkLabel(
            self,
            text="PAGE PREVIEW",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", padx=10, pady=(8, 4))

        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=8, pady=(0, 4))
        ctk.CTkButton(
            nav, text="◀", width=36, height=30,
            fg_color=COLORS["bg_hover"], hover_color=COLORS["accent"],
            font=ctk.CTkFont(size=14),
            command=self._prev,
        ).pack(side="left")
        self._page_var = ctk.StringVar(value="1")
        ent = ctk.CTkEntry(
            nav, textvariable=self._page_var, width=52, height=30,
            fg_color=COLORS["bg_primary"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            justify="center",
        )
        ent.pack(side="left", padx=6)
        ent.bind("<Return>", lambda e: self._apply_page_entry())
        ent.bind("<FocusOut>", lambda e: self._apply_page_entry())
        ctk.CTkButton(
            nav, text="▶", width=36, height=30,
            fg_color=COLORS["bg_hover"], hover_color=COLORS["accent"],
            font=ctk.CTkFont(size=14),
            command=self._next,
        ).pack(side="left")
        self._count_lbl = ctk.CTkLabel(
            nav, text="", font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_muted"],
        )
        self._count_lbl.pack(side="left", padx=(10, 0))

        self._img_lbl = ctk.CTkLabel(self, text="No PDF loaded", text_color=COLORS["text_muted"])
        self._img_lbl.pack(padx=10, pady=(4, 10))

    def set_document(self, path: str) -> None:
        self._path = path or ""
        self._total = pdf_page_count(self._path) if self._path else 0
        self._page = 1 if self._total else 1
        if self._total:
            self._page = min(self._page, self._total)
        self._page_var.set(str(self._page))
        self._count_lbl.configure(text=f"/ {self._total} pages" if self._total else "")
        self._schedule_render()

    def _prev(self) -> None:
        if self._total < 1:
            return
        self._page = max(1, self._page - 1)
        self._page_var.set(str(self._page))
        self._schedule_render()

    def _next(self) -> None:
        if self._total < 1:
            return
        self._page = min(self._total, self._page + 1)
        self._page_var.set(str(self._page))
        self._schedule_render()

    def _apply_page_entry(self) -> None:
        if self._total < 1:
            return
        try:
            p = int(self._page_var.get().strip())
        except ValueError:
            self._page_var.set(str(self._page))
            return
        self._page = max(1, min(self._total, p))
        self._page_var.set(str(self._page))
        self._schedule_render()

    def _schedule_render(self) -> None:
        if self._thumb_job is not None:
            try:
                self.after_cancel(self._thumb_job)
            except Exception:
                pass
        self._thumb_job = self.after(120, self._start_render_thread)

    def _start_render_thread(self) -> None:
        self._thumb_job = None
        path = self._path
        if not path or self._total < 1:
            self._img_lbl.configure(image=None, text="No PDF loaded")
            self._ctk_img = None
            return
        idx = self._page - 1
        self._gen += 1
        gen = self._gen

        def work() -> None:
            pil = render_page_pil(path, idx, max_side=220)
            self.after(0, lambda: self._apply_thumb(gen, pil))

        threading.Thread(target=work, daemon=True).start()

    def _apply_thumb(self, gen: int, pil: Image.Image | None) -> None:
        if gen != self._gen:
            return
        if pil is None:
            self._ctk_img = None
            self._img_lbl.configure(image=None, text="Preview unavailable")
            return
        self._ctk_img = _pil_to_ctk_image(pil)
        self._img_lbl.configure(image=self._ctk_img, text="")


class RangePdfPreview(ctk.CTkFrame):
    """Start / end page thumbnails + quick insert into a StringVar (comma ranges)."""

    def __init__(
        self,
        parent,
        ranges_var: ctk.StringVar,
        get_pdf_path: Callable[[], str],
        **kwargs,
    ):
        super().__init__(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self._ranges_var = ranges_var
        self._get_path = get_pdf_path
        self._gen = 0
        self._left_img: ctk.CTkImage | None = None
        self._right_img: ctk.CTkImage | None = None
        self._debounce = None

        ctk.CTkLabel(
            self,
            text="RANGE PREVIEW — see first & last page of the segment",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", padx=10, pady=(8, 6))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(row, text="From", font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(side="left")
        self._from_var = ctk.StringVar(value="1")
        ctk.CTkEntry(
            row, textvariable=self._from_var, width=56, height=30,
            fg_color=COLORS["bg_primary"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=13), justify="center",
        ).pack(side="left", padx=(6, 12))
        ctk.CTkLabel(row, text="To", font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(side="left")
        self._to_var = ctk.StringVar(value="1")
        ctk.CTkEntry(
            row, textvariable=self._to_var, width=56, height=30,
            fg_color=COLORS["bg_primary"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=13), justify="center",
        ).pack(side="left", padx=6)

        def add_range() -> None:
            path = self._get_path()
            n = pdf_page_count(path)
            if n < 1:
                return
            try:
                a = int(self._from_var.get().strip())
                b = int(self._to_var.get().strip())
            except ValueError:
                return
            a = max(1, min(n, a))
            b = max(1, min(n, b))
            if a > b:
                a, b = b, a
            seg = f"{a}-{b}"
            cur = self._ranges_var.get().strip()
            if cur:
                self._ranges_var.set(f"{cur}, {seg}")
            else:
                self._ranges_var.set(seg)

        ctk.CTkButton(
            row, text="Add to ranges", width=120, height=30,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=add_range,
        ).pack(side="left", padx=(16, 0))

        thumbs = ctk.CTkFrame(self, fg_color="transparent")
        thumbs.pack(fill="x", padx=8, pady=(0, 10))
        self._lbl_a = ctk.CTkLabel(thumbs, text="Start page", text_color=COLORS["text_muted"], width=200)
        self._lbl_a.pack(side="left", padx=(0, 12), expand=True)
        self._lbl_b = ctk.CTkLabel(thumbs, text="End page", text_color=COLORS["text_muted"], width=200)
        self._lbl_b.pack(side="left", expand=True)

        for v in (self._from_var, self._to_var):
            v.trace_add("write", lambda *_: self._schedule_dual_update())

    def refresh_path(self) -> None:
        self._schedule_dual_update()

    def _schedule_dual_update(self) -> None:
        if self._debounce is not None:
            try:
                self.after_cancel(self._debounce)
            except Exception:
                pass
        self._debounce = self.after(200, self._run_dual_render)

    def _run_dual_render(self) -> None:
        self._debounce = None
        path = self._get_path()
        n = pdf_page_count(path)
        if n < 1:
            self._left_img = self._right_img = None
            self._lbl_a.configure(image=None, text="Start page")
            self._lbl_b.configure(image=None, text="End page")
            return
        try:
            a = int(self._from_var.get().strip())
            b = int(self._to_var.get().strip())
        except ValueError:
            return
        a = max(1, min(n, a))
        b = max(1, min(n, b))
        self._gen += 1
        gen = self._gen
        ia, ib = a - 1, b - 1

        def work() -> None:
            p1 = render_page_pil(path, ia, max_side=180)
            p2 = render_page_pil(path, ib, max_side=180)
            self.after(0, lambda: self._apply_dual(gen, p1, p2, a, b))

        threading.Thread(target=work, daemon=True).start()

    def _apply_dual(
        self,
        gen: int,
        p1: Image.Image | None,
        p2: Image.Image | None,
        a: int,
        b: int,
    ) -> None:
        if gen != self._gen:
            return
        if p1 is None:
            self._left_img = None
            self._lbl_a.configure(image=None, text=f"Page {a}\n(unavailable)")
        else:
            self._left_img = _pil_to_ctk_image(p1)
            self._lbl_a.configure(image=self._left_img, text="")
        if p2 is None:
            self._right_img = None
            self._lbl_b.configure(image=None, text=f"Page {b}\n(unavailable)")
        else:
            self._right_img = _pil_to_ctk_image(p2)
            self._lbl_b.configure(image=self._right_img, text="")
