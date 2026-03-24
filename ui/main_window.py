"""
PDForge — ui/main_window.py
Main application window: sidebar + content area routing.
"""

from __future__ import annotations
import os
import customtkinter as ctk
from assets.themes.theme import COLORS, SIDEBAR_WIDTH, TOOLBAR_HEIGHT, MIN_WIDTH, MIN_HEIGHT
from ui.sidebar import Sidebar

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOGO_ICO = os.path.join(_ROOT, "assets", "icons", "logo.ico")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ── Window config ──────────────────────────────────────
        self.title("PDForge")
        if os.path.isfile(_LOGO_ICO):
            try:
                self.iconbitmap(_LOGO_ICO)
            except Exception:
                pass
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.geometry("1280x800")
        self.configure(fg_color=COLORS["bg_primary"])

        # Load saved size
        from services import settings
        if settings.get("remember_window_size"):
            w = settings.get("window_width", 1280)
            h = settings.get("window_height", 800)
            self.geometry(f"{w}x{h}")

        self.bind("<Configure>", self._on_resize)

        # ── Layout ─────────────────────────────────────────────
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self._sidebar = Sidebar(self, on_navigate=self._navigate)
        self._sidebar.grid(row=0, column=0, sticky="nsew")

        # Content area
        self._content = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_primary"],
            corner_radius=0,
        )
        self._content.grid(row=0, column=1, sticky="nsew")
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

        self._sidebar_visible = True
        self._sidebar_toggle_btn = ctk.CTkButton(
            self,
            text="◂",
            width=34,
            height=40,
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["accent"],
            text_color=COLORS["text_primary"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self._toggle_sidebar,
        )
        self._sidebar_toggle_btn.place(x=176, y=32, anchor="w")

        self._current_view = None
        self._view_cache: dict[str, ctk.CTkFrame] = {}
        self._resize_job = None
        self._navigate("home")

    def _navigate(self, tool_id: str):
        if self._current_view is not None:
            self._current_view.grid_remove()

        if tool_id in self._view_cache:
            view = self._view_cache[tool_id]
            view.grid(row=0, column=0, sticky="nsew")
            self._current_view = view
        else:
            view = self._make_view(tool_id)
            view.grid(row=0, column=0, sticky="nsew")
            self._current_view = view
            if not getattr(view, "_pdforge_skip_cache", False):
                self._view_cache[tool_id] = view

        self._sidebar.set_active(tool_id)
        self._sidebar_toggle_btn.lift()

    def _toggle_sidebar(self):
        if self._sidebar_visible:
            self._sidebar.grid_remove()
            self._sidebar_visible = False
            self._sidebar_toggle_btn.configure(text="▸")
            self._sidebar_toggle_btn.place(x=0, y=28)
        else:
            self._sidebar.grid(row=0, column=0, sticky="nsew")
            self._sidebar_visible = True
            self._sidebar_toggle_btn.configure(text="◂")
            self._sidebar_toggle_btn.place(x=176, y=32, anchor="w")
        self._sidebar_toggle_btn.lift()

    def _make_view(self, tool_id: str) -> ctk.CTkFrame:
        from ui.tools.home_view      import HomeView
        from ui.tools.merge_view     import MergeView
        from ui.tools.split_view     import SplitView
        from ui.tools.compress_view  import CompressView
        from ui.tools.protect_view   import ProtectView
        from ui.tools.unlock_view    import UnlockView
        from ui.tools.watermark_view import WatermarkView
        from ui.tools.organize_view  import OrganizeView
        from ui.tools.rotate_view    import RotateView
        from ui.tools.convert_view   import ConvertView
        from ui.tools.ocr_view       import OcrView
        from ui.tools.extract_view   import ExtractView
        from ui.tools.redact_view    import RedactView
        from ui.tools.number_view    import NumberView
        from ui.tools.header_view    import HeaderView
        from ui.tools.repair_view    import RepairView
        from ui.tools.metadata_view  import MetadataView
        from ui.tools.compare_view   import CompareView
        from ui.tools.batch_view     import BatchView
        from ui.tools.history_view   import HistoryView
        from ui.tools.settings_view  import SettingsView
        from ui.tools.about_view     import AboutView

        VIEW_MAP = {
            "home":          HomeView,
            "merge":         MergeView,
            "split":         SplitView,
            "compress":      CompressView,
            "protect":       ProtectView,
            "unlock":        UnlockView,
            "watermark":     WatermarkView,
            "organize":      OrganizeView,
            "rotate":        RotateView,
            "pdf_to_word":   lambda p: ConvertView(p, mode="pdf_to_word"),
            "pdf_to_excel":  lambda p: ConvertView(p, mode="pdf_to_excel"),
            "pdf_to_image":  lambda p: ConvertView(p, mode="pdf_to_image"),
            "image_to_pdf":  lambda p: ConvertView(p, mode="image_to_pdf"),
            "pdf_to_text":   lambda p: ConvertView(p, mode="pdf_to_text"),
            "ocr":           OcrView,
            "extract_text":  lambda p: ExtractView(p, mode="text"),
            "extract_images":lambda p: ExtractView(p, mode="images"),
            "extract_tables":lambda p: ExtractView(p, mode="tables"),
            "redact":        RedactView,
            "number":        NumberView,
            "header":        HeaderView,
            "repair":        RepairView,
            "metadata":      MetadataView,
            "compare":       CompareView,
            "batch":         BatchView,
            "history":       HistoryView,
            "about":         AboutView,
            "settings":      SettingsView,
        }

        cls = VIEW_MAP.get(tool_id)
        if cls is None:
            return self._placeholder(tool_id)

        try:
            return cls(self._content)
        except Exception as e:
            return self._error_view(str(e))

    def _placeholder(self, tool_id: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg_primary"])
        frame._pdforge_skip_cache = True
        ctk.CTkLabel(
            frame,
            text=f"Tool: {tool_id}\n(Coming soon)",
            font=ctk.CTkFont(family="Segoe UI", size=18),
            text_color=COLORS["text_muted"],
        ).place(relx=0.5, rely=0.5, anchor="center")
        return frame

    def _error_view(self, error: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg_primary"])
        frame._pdforge_skip_cache = True
        ctk.CTkLabel(
            frame,
            text=f"Error loading view:\n{error}",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["error"],
            wraplength=500,
        ).place(relx=0.5, rely=0.5, anchor="center")
        return frame

    def _on_resize(self, event):
        if event.widget is not self:
            return
        from services import settings
        if not settings.get("remember_window_size"):
            return
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(450, self._persist_window_size)

    def _persist_window_size(self):
        self._resize_job = None
        from services import settings
        if not settings.get("remember_window_size"):
            return
        w, h = self.winfo_width(), self.winfo_height()
        if w < 200 or h < 200:
            return
        settings.set("window_width", w)
        settings.set("window_height", h)
