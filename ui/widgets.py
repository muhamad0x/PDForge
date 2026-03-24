"""
PDForge — ui/widgets.py
Reusable themed UI components. All widgets respect the PDForge dark-red palette.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Callable, Iterable

import customtkinter as ctk
from assets.themes.theme import COLORS, FONTS, RADIUS, SPACING
from ui.file_dialog_config import EXT_PDF, FILETYPES_PDF_DEFAULT


# ═══════════════════════════════════════════════════════════════════════════
# THEMED BUTTON
# ═══════════════════════════════════════════════════════════════════════════

class PrimaryButton(ctk.CTkButton):
    """Red accent primary action button."""
    def __init__(self, parent, text: str, command=None, width=140, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=38,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=RADIUS["md"],
            **kwargs,
        )


class SecondaryButton(ctk.CTkButton):
    """Ghost / outline secondary button."""
    def __init__(self, parent, text: str, command=None, width=120, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=36,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            border_color=COLORS["border"],
            border_width=1,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            corner_radius=RADIUS["md"],
            **kwargs,
        )


class DangerButton(ctk.CTkButton):
    """Red destructive action button."""
    def __init__(self, parent, text: str, command=None, width=120, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=36,
            fg_color=COLORS["error"],
            hover_color="#DC2626",
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            corner_radius=RADIUS["md"],
            **kwargs,
        )


class IconButton(ctk.CTkButton):
    """Small square icon-only button."""
    def __init__(self, parent, text: str = "", command=None, size: int = 32, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            width=size,
            height=size,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=RADIUS["sm"],
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════════════
# SECTION CARD
# ═══════════════════════════════════════════════════════════════════════════

class Card(ctk.CTkFrame):
    """Elevated card container."""
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"],
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════════════
# SECTION LABEL
# ═══════════════════════════════════════════════════════════════════════════

class SectionLabel(ctk.CTkLabel):
    """Section heading inside a tool view."""
    def __init__(self, parent, text: str, **kwargs):
        super().__init__(
            parent,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS["text_muted"],
            **kwargs,
        )


class HeadingLabel(ctk.CTkLabel):
    """Large tool heading."""
    def __init__(self, parent, text: str, **kwargs):
        super().__init__(
            parent,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"],
            **kwargs,
        )


class BodyLabel(ctk.CTkLabel):
    """Standard body text label."""
    def __init__(self, parent, text: str, **kwargs):
        super().__init__(
            parent,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"],
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════════════
# THEMED INPUT
# ═══════════════════════════════════════════════════════════════════════════

class ThemedEntry(ctk.CTkEntry):
    def __init__(self, parent, placeholder: str = "", **kwargs):
        super().__init__(
            parent,
            placeholder_text=placeholder,
            fg_color=COLORS["bg_primary"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            height=36,
            corner_radius=RADIUS["md"],
            **kwargs,
        )


class ThemedComboBox(ctk.CTkComboBox):
    def __init__(self, parent, values: list[str], **kwargs):
        super().__init__(
            parent,
            values=values,
            fg_color=COLORS["bg_primary"],
            border_color=COLORS["border"],
            button_color=COLORS["bg_hover"],
            button_hover_color=COLORS["accent"],
            text_color=COLORS["text_primary"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_text_color=COLORS["text_primary"],
            dropdown_hover_color=COLORS["bg_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            height=36,
            corner_radius=RADIUS["md"],
            **kwargs,
        )


class ThemedSlider(ctk.CTkSlider):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["progress_bg"],
            progress_color=COLORS["accent"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            **kwargs,
        )


class ThemedSwitch(ctk.CTkSwitch):
    def __init__(self, parent, text: str, **kwargs):
        super().__init__(
            parent,
            text=text,
            progress_color=COLORS["accent"],
            button_color=COLORS["text_primary"],
            button_hover_color=COLORS["accent_hover"],
            fg_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            **kwargs,
        )


# ═══════════════════════════════════════════════════════════════════════════
# DROP ZONE
# ═══════════════════════════════════════════════════════════════════════════

class DropZone(ctk.CTkFrame):
    """
    Drag-and-drop file zone.
    Falls back to click-to-browse when tkinterdnd2 is unavailable.
    """

    def __init__(
        self,
        parent,
        on_files_dropped: Callable[[list[str]], None],
        accept_multiple: bool = True,
        height: int = 160,
        label: str = "Drop PDF files here, or click to browse",
        *,
        filetypes: list[tuple[str, str]] | None = None,
        allowed_extensions: Iterable[str] | frozenset | None = None,
        dialog_title: str | None = None,
        sublabel: str | None = None,
        **kwargs,
    ):
        super().__init__(
            parent,
            fg_color=COLORS["accent_subtle"],
            corner_radius=RADIUS["xl"],
            border_width=2,
            border_color=COLORS["accent_muted"],
            height=height,
            **kwargs,
        )
        self._callback = on_files_dropped
        self._accept_multiple = accept_multiple
        self._hover = False
        self._filetypes = list(filetypes) if filetypes else list(FILETYPES_PDF_DEFAULT)
        self._allowed_ext = frozenset(allowed_extensions) if allowed_extensions is not None else EXT_PDF
        self._dialog_title = dialog_title or (
            "Select PDF files" if accept_multiple else "Select PDF file"
        )
        self._sublabel_text = sublabel or (
            "PDF files supported"
            if self._allowed_ext <= EXT_PDF
            else "Supported file types"
        )
        self._selected_files: list[str] = []

        self.bind("<Enter>",   self._on_enter)
        self.bind("<Leave>",   self._on_leave)
        self.bind("<Button-1>", self._on_click)

        # Inner layout
        self._icon = ctk.CTkLabel(
            self,
            text="⬆",
            font=ctk.CTkFont(family="Segoe UI", size=32),
            text_color=COLORS["accent_muted"],
        )
        self._icon.place(relx=0.5, rely=0.35, anchor="center")

        self._label = ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_muted"],
        )
        self._label.place(relx=0.5, rely=0.62, anchor="center")

        self._sub = ctk.CTkLabel(
            self,
            text=self._sublabel_text,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_muted"],
        )
        self._sub.place(relx=0.5, rely=0.78, anchor="center")

        self._clear_btn = ctk.CTkButton(
            self,
            text="✕",
            width=22,
            height=22,
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["error"],
            text_color=COLORS["text_muted"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=RADIUS["sm"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.clear_selection,
        )
        self._clear_btn.place(relx=0.975, rely=0.08, anchor="ne")
        self._clear_btn.place_forget()

        # Bind children too
        for w in (self._icon, self._label, self._sub):
            w.bind("<Button-1>", self._on_click)
            w.bind("<Enter>",   self._on_enter)
            w.bind("<Leave>",   self._on_leave)

        # Try tkinterdnd2
        self._setup_dnd()

    def _setup_dnd(self):
        try:
            self.drop_target_register("DND_Files")  # type: ignore
            self.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore
        except Exception:
            pass

    def _path_allowed(self, path: str) -> bool:
        suf = Path(path).suffix.lower()
        return suf in self._allowed_ext

    def _on_drop(self, event):
        files = self._parse_dnd_files(event.data)
        ok = [f for f in files if self._path_allowed(f)]
        if ok:
            if not self._accept_multiple:
                ok = ok[:1]
            self._selected_files = list(ok)
            self._sync_selected_state()
            self._callback(ok)

    def _parse_dnd_files(self, data: str) -> list[str]:
        """Parse tkinterdnd2 file drop data."""
        import re
        # Handles {path with spaces} and plain paths
        paths = re.findall(r'\{([^}]+)\}|(\S+)', data)
        return [p[0] or p[1] for p in paths]

    def _on_click(self, event=None):
        from tkinter import filedialog
        if self._accept_multiple:
            files = filedialog.askopenfilenames(
                title=self._dialog_title,
                filetypes=self._filetypes,
            )
        else:
            files = filedialog.askopenfilename(
                title=self._dialog_title,
                filetypes=self._filetypes,
            )
            files = [files] if files else []

        if files:
            filtered = [f for f in files if self._path_allowed(f)]
            if filtered:
                self._selected_files = list(filtered)
                self._sync_selected_state()
                self._callback(list(filtered))

    def _on_enter(self, event=None):
        self.configure(border_color=COLORS["accent"], fg_color=COLORS["bg_active"])
        self._icon.configure(text_color=COLORS["accent"])

    def _on_leave(self, event=None):
        self.configure(border_color=COLORS["accent_muted"], fg_color=COLORS["accent_subtle"])
        self._icon.configure(text_color=COLORS["accent_muted"])

    def clear_selection(self):
        """Clear currently selected files and notify the view."""
        self._selected_files = []
        self._clear_bound_view_state()
        self._sync_selected_state()
        self._callback([])

    def _sync_selected_state(self):
        if self._selected_files:
            n = len(self._selected_files)
            self._label.configure(text=f"{n} file(s) selected")
            self._sub.configure(text="Click ✕ to remove and choose another file")
            self._clear_btn.place(relx=0.975, rely=0.08, anchor="ne")
        else:
            self._sub.configure(text=self._sublabel_text)
            self._clear_btn.place_forget()

    def _clear_bound_view_state(self):
        """Best-effort clear for tool views that don't handle empty paths."""
        w = self.master
        for _ in range(8):
            if w is None:
                return
            if any(hasattr(w, k) for k in ("_file", "_files", "_file_label")):
                break
            w = getattr(w, "master", None)
        if w is None:
            return
        try:
            if hasattr(w, "_file"):
                setattr(w, "_file", "")
            if hasattr(w, "_files"):
                setattr(w, "_files", [])
            if hasattr(w, "_file_a"):
                setattr(w, "_file_a", "")
            if hasattr(w, "_file_b"):
                setattr(w, "_file_b", "")
            if hasattr(w, "_file_label"):
                w._file_label.configure(text="")
            if hasattr(w, "_label_a"):
                w._label_a.configure(text="")
            if hasattr(w, "_label_b"):
                w._label_b.configure(text="")
            if hasattr(w, "_out_var"):
                w._out_var.set("")
            if hasattr(w, "_page_preview"):
                w._page_preview.set_document("")
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════════
# FILE LIST ITEM
# ═══════════════════════════════════════════════════════════════════════════

class FileListItem(ctk.CTkFrame):
    """Single file row in a file list."""

    def __init__(
        self,
        parent,
        file_path: str,
        index: int,
        on_remove: Callable[[int], None] | None = None,
        show_pages: bool = True,
        **kwargs,
    ):
        super().__init__(
            parent,
            fg_color=COLORS["bg_hover"],
            corner_radius=RADIUS["md"],
            height=48,
            **kwargs,
        )
        from pathlib import Path
        import os

        self.grid_propagate(False)

        name  = Path(file_path).name
        try:
            size = os.path.getsize(file_path)
            size_str = f"{size / 1024:.0f} KB" if size < 1048576 else f"{size / 1048576:.1f} MB"
        except Exception:
            size_str = ""

        # Index badge
        ctk.CTkLabel(
            self,
            text=str(index + 1),
            width=28,
            height=28,
            fg_color=COLORS["accent_muted"],
            corner_radius=RADIUS["full"],
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS["text_primary"],
        ).place(x=10, rely=0.5, anchor="w")

        # PDF icon text
        ctk.CTkLabel(
            self,
            text="PDF",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=COLORS["accent"],
            fg_color="transparent",
        ).place(x=44, rely=0.5, anchor="w")

        # Filename
        ctk.CTkLabel(
            self,
            text=name,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).place(x=76, rely=0.5, anchor="w")

        # Size
        if size_str:
            ctk.CTkLabel(
                self,
                text=size_str,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS["text_muted"],
            ).place(relx=0.78, rely=0.5, anchor="center")

        # Remove button
        if on_remove is not None:
            btn = ctk.CTkButton(
                self,
                text="✕",
                width=28,
                height=28,
                fg_color="transparent",
                hover_color=COLORS["error"],
                text_color=COLORS["text_muted"],
                font=ctk.CTkFont(family="Segoe UI", size=12),
                corner_radius=RADIUS["sm"],
                command=lambda: on_remove(index),
            )
            btn.place(relx=0.96, rely=0.5, anchor="e")


# ═══════════════════════════════════════════════════════════════════════════
# PROGRESS BAR
# ═══════════════════════════════════════════════════════════════════════════

class ProgressBar(ctk.CTkFrame):
    """Progress bar with label and percentage."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs,
        )
        self._label = ctk.CTkLabel(
            self,
            text="Processing...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"],
        )
        self._label.pack(anchor="w")

        self._bar = ctk.CTkProgressBar(
            self,
            fg_color=COLORS["progress_bg"],
            progress_color=COLORS["accent"],
            corner_radius=RADIUS["full"],
            height=6,
        )
        self._bar.pack(fill="x", pady=(4, 0))
        self._bar.set(0)

        self._pct = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_muted"],
        )
        self._pct.pack(anchor="e")

    def update(self, current: int, total: int, label: str = ""):
        pct = current / max(total, 1)
        self._bar.set(pct)
        self._pct.configure(text=f"{int(pct * 100)}%")
        if label:
            self._label.configure(text=label)

    def set_label(self, text: str):
        self._label.configure(text=text)

    def reset(self):
        self._bar.set(0)
        self._pct.configure(text="0%")


# ═══════════════════════════════════════════════════════════════════════════
# STATUS BADGE
# ═══════════════════════════════════════════════════════════════════════════

class StatusBadge(ctk.CTkFrame):
    """Small colored status indicator."""

    COLORS_MAP = {
        "success": (COLORS["success"], COLORS["success_soft"]),
        "error":   (COLORS["error"],   COLORS["error_soft"]),
        "warning": (COLORS["warning"], COLORS["warning_soft"]),
        "info":    (COLORS["info"],    COLORS["info_soft"]),
    }

    def __init__(self, parent, text: str, status: str = "info", **kwargs):
        accent, panel = self.COLORS_MAP.get(status, (COLORS["info"], COLORS["info_soft"]))
        super().__init__(
            parent,
            fg_color=panel,
            corner_radius=RADIUS["full"],
            border_width=1,
            border_color=accent,
            **kwargs,
        )
        ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=accent,
            padx=10,
            pady=3,
        ).pack()


# ═══════════════════════════════════════════════════════════════════════════
# SEPARATOR
# ═══════════════════════════════════════════════════════════════════════════

class Separator(ctk.CTkFrame):
    def __init__(self, parent, orient: str = "horizontal", **kwargs):
        if orient == "horizontal":
            super().__init__(parent, height=1, fg_color=COLORS["border"], **kwargs)
        else:
            super().__init__(parent, width=1, fg_color=COLORS["border"], **kwargs)


# ═══════════════════════════════════════════════════════════════════════════
# RESULT PANEL
# ═══════════════════════════════════════════════════════════════════════════

class ResultPanel(ctk.CTkFrame):
    """Success/error result display at bottom of tool views."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._visible = False

    def show_success(self, message: str, output_path: str | None = None):
        self._clear()
        frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["success_soft"],
            corner_radius=RADIUS["md"],
            border_color=COLORS["success"],
            border_width=1,
        )
        frame.pack(fill="x", padx=0, pady=4)

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            inner,
            text="✓  " + message,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["success"],
            anchor="w",
        ).pack(anchor="w")

        if output_path:
            import os
            import subprocess
            import sys

            norm = os.path.normpath(os.path.abspath(output_path))
            path_is_dir = os.path.isdir(norm)
            folder = norm if path_is_dir else os.path.dirname(norm)

            path_lbl = ctk.CTkLabel(
                inner,
                text=norm,
                font=ctk.CTkFont(family="Consolas", size=11),
                text_color=COLORS["text_secondary"],
                anchor="w",
                justify="left",
                wraplength=520,
            )
            path_lbl.pack(anchor="w", pady=(6, 0))

            def _open_folder():
                try:
                    if sys.platform == "win32":
                        os.startfile(folder)
                    elif sys.platform == "darwin":
                        subprocess.Popen(["open", folder])
                    else:
                        subprocess.Popen(["xdg-open", folder])
                except Exception:
                    pass

            def _open_file():
                try:
                    if sys.platform == "win32":
                        os.startfile(norm)
                    elif sys.platform == "darwin":
                        subprocess.Popen(["open", norm])
                    else:
                        subprocess.Popen(["xdg-open", norm])
                except Exception:
                    pass

            def _copy_path():
                try:
                    top = self.winfo_toplevel()
                    top.clipboard_clear()
                    top.clipboard_append(norm)
                    top.update()
                except Exception:
                    pass

            btn_row = ctk.CTkFrame(inner, fg_color="transparent")
            btn_row.pack(anchor="w", pady=(8, 0))
            ctk.CTkButton(
                btn_row,
                text="Open folder",
                command=_open_folder,
                width=100,
                height=30,
                fg_color="transparent",
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["success"],
                border_color=COLORS["success"],
                border_width=1,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                corner_radius=RADIUS["sm"],
            ).pack(side="left", padx=(0, 8))
            if not path_is_dir:
                ctk.CTkButton(
                    btn_row,
                    text="Open file",
                    command=_open_file,
                    width=90,
                    height=30,
                    fg_color="transparent",
                    hover_color=COLORS["bg_hover"],
                    text_color=COLORS["success"],
                    border_color=COLORS["success"],
                    border_width=1,
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    corner_radius=RADIUS["sm"],
                ).pack(side="left", padx=(0, 8))
            ctk.CTkButton(
                btn_row,
                text="Copy path",
                command=_copy_path,
                width=90,
                height=30,
                fg_color="transparent",
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["text_secondary"],
                border_color=COLORS["border"],
                border_width=1,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                corner_radius=RADIUS["sm"],
            ).pack(side="left")

    def show_error(self, message: str):
        self._clear()
        frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["error_soft"],
            corner_radius=RADIUS["md"],
            border_color=COLORS["error"],
            border_width=1,
        )
        frame.pack(fill="x", padx=0, pady=4)

        ctk.CTkLabel(
            frame,
            text="✗  " + message,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["error"],
            anchor="w",
            wraplength=600,
        ).pack(padx=16, pady=12, anchor="w")

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()
