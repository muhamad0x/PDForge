"""PDForge — ui/tools/merge_view.py"""

from __future__ import annotations
import os
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, FileListItem, PrimaryButton, SecondaryButton
from assets.themes.theme import COLORS, RADIUS


class MergeView(BaseToolView):
    ICON     = "⊕"
    TITLE    = "Merge PDF"
    SUBTITLE = "Combine multiple PDF files into a single document — drag to reorder"

    def __init__(self, parent):
        self._files: list[str] = []
        self._count_var = ctk.StringVar(value="")
        super().__init__(parent)

    def build_ui(self, parent):
        # Drop zone
        self._drop = DropZone(
            parent,
            on_files_dropped=self._add_files,
            accept_multiple=True,
            height=130,
        )
        self._drop.pack(fill="x", pady=(0, 16))

        # File list
        self.section(parent, "FILES TO MERGE (drag to reorder)")
        self._list_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self._list_frame.pack(fill="x")

        self._empty_label = ctk.CTkLabel(
            self._list_frame,
            text="No files added yet",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_muted"],
        )
        self._empty_label.pack(pady=20)

        # Output path
        self.section(parent, "OUTPUT")
        out_row = ctk.CTkFrame(parent, fg_color="transparent")
        out_row.pack(fill="x")

        self._out_var = ctk.StringVar()
        ctk.CTkEntry(
            out_row,
            textvariable=self._out_var,
            placeholder_text="Output path (auto-generated if empty)",
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            height=36,
            corner_radius=RADIUS["md"],
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        SecondaryButton(out_row, text="Browse", command=self._browse_out, width=90).pack(side="left")

    def build_buttons(self, parent):
        PrimaryButton(parent, text="⊕  Merge PDFs", command=self.run, width=160).pack(side="left")
        SecondaryButton(parent, text="Clear all", command=self._clear, width=100).pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            parent,
            textvariable=self._count_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_muted"],
        ).pack(side="left", padx=16)

    def _add_files(self, paths: list[str]):
        for p in paths:
            if p not in self._files:
                self._files.append(p)
        self._refresh_list()

    def _refresh_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()

        if not self._files:
            self._empty_label = ctk.CTkLabel(
                self._list_frame,
                text="No files added yet",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS["text_muted"],
            )
            self._empty_label.pack(pady=20)
            self._count_var.set("")
            return

        total_size = 0
        for i, path in enumerate(self._files):
            item = FileListItem(
                self._list_frame,
                file_path=path,
                index=i,
                on_remove=self._remove_file,
            )
            item.pack(fill="x", pady=2)
            try:
                total_size += os.path.getsize(path)
            except Exception:
                pass

        sz = f"{total_size/1048576:.1f} MB" if total_size >= 1048576 else f"{total_size/1024:.0f} KB"
        self._count_var.set(f"{len(self._files)} files · {sz} total")
        if len(self._files) >= 2:
            self.autofill_output_entry(self._out_var, self._files[0], "merged")

    def _remove_file(self, index: int):
        if 0 <= index < len(self._files):
            self._files.pop(index)
            self._refresh_list()

    def _clear(self):
        self._files.clear()
        self._refresh_list()

    def _browse_out(self):
        default = ""
        if self._files:
            default = self.suggest_output(self._files[0], "merged")
        path = self.browse_save_pdf(default_name=Path(default).name if default else "merged.pdf")
        if path:
            self._out_var.set(path)

    def run(self):
        if len(self._files) < 2:
            self.show_error("Add at least 2 PDF files to merge.")
            return

        out = self._out_var.get().strip()
        if not out:
            out = self.suggest_output(self._files[0], "merged")

        self.show_progress(f"Merging {len(self._files)} files...")

        def _work():
            from core.merge import merge_pdfs
            result = merge_pdfs(
                self._files, out,
                progress_cb=lambda c, t: self.after(0, lambda: self.update_progress(c, t, f"Processing file {c}/{t}…")),
            )
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result: dict, out: str):
        if result["success"]:
            from services import history
            history.add_entry("Merge", self._files, out, success=True,
                              details=f"{result['total_pages']} pages")
            self.show_success(
                f"Merged {len(self._files)} files → {result['total_pages']} pages",
                output_path=out,
            )
        else:
            self.show_error(result["error"])
