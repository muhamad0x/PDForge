"""PDForge — ui/tools/compare_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton
from assets.themes.theme import COLORS, RADIUS


class CompareView(BaseToolView):
    ICON     = "⇔"
    TITLE    = "Compare PDF"
    SUBTITLE = "Compare text content of two PDF versions and highlight differences"

    def __init__(self, parent):
        self._file_a = ""
        self._file_b = ""
        super().__init__(parent)

    def build_ui(self, parent):
        two_col = ctk.CTkFrame(parent, fg_color="transparent")
        two_col.pack(fill="x")
        two_col.columnconfigure(0, weight=1)
        two_col.columnconfigure(1, weight=1)

        for col, (attr, label) in enumerate([("_file_a", "FILE A (original)"), ("_file_b", "FILE B (modified)")]):
            frame = ctk.CTkFrame(two_col,
                fg_color=COLORS["bg_card"], corner_radius=RADIUS["lg"],
                border_width=1, border_color=COLORS["border"])
            frame.grid(row=0, column=col, padx=(0, 8) if col == 0 else 0, sticky="nsew")

            ctk.CTkLabel(frame, text=label,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=COLORS["text_muted"]).pack(anchor="w", padx=16, pady=(14, 4))

            drop = DropZone(frame, on_files_dropped=lambda ps, a=attr, f=frame: self._set_file(a, ps, f),
                            accept_multiple=False, height=90,
                            label="Drop PDF or click")
            drop.pack(padx=16, pady=(0, 16), fill="x")

            lbl = ctk.CTkLabel(frame, text="",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS["accent"])
            lbl.pack(anchor="w", padx=16, pady=(0, 12))
            setattr(self, attr + "_label", lbl)

        self.section(parent, "OUTPUT")
        out_row = ctk.CTkFrame(parent, fg_color="transparent")
        out_row.pack(fill="x", pady=(8, 0))
        self._out_var = ctk.StringVar()
        ctk.CTkEntry(out_row, textvariable=self._out_var,
            placeholder_text="Output path for diff report (.txt)",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"]).pack(side="left", fill="x", expand=True, padx=(0, 8))
        SecondaryButton(out_row, text="Browse",
            command=lambda: self._out_var.set(
                self.browse_save_file(default_name="diff_report.txt", ext=".txt")),
            width=90).pack(side="left")

        self._diff_box = ctk.CTkTextbox(parent, height=200,
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"], border_width=1,
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=RADIUS["md"])
        self._diff_box.pack(fill="x", pady=(16, 0))
        self._diff_box.insert("1.0", "Diff output will appear here after comparison…")
        self._diff_box.configure(state="disabled")

    def _set_file(self, attr, paths, frame):
        if paths:
            setattr(self, attr, paths[0])
            lbl = getattr(self, attr + "_label")
            lbl.configure(text=f"✓  {Path(paths[0]).name}")
            if self._file_a and self._file_b:
                self.autofill_output_entry(self._out_var, self._file_a, "compare", ".txt")

    def build_buttons(self, parent):
        PrimaryButton(parent, text="⇔  Compare", command=self.run, width=150).pack(side="left")

    def run(self):
        if not self._file_a or not self._file_b:
            self.show_error("Select both PDF files.")
            return
        out = self._out_var.get().strip() or self.suggest_output(self._file_a, "compare", ".txt")
        self.show_progress("Comparing documents…")

        def _work():
            try:
                import difflib
                from core.extract import extract_text

                res_a = extract_text(self._file_a, None)
                res_b = extract_text(self._file_b, None)

                if not res_a["success"]:
                    self.after(0, lambda: self.show_error(f"File A error: {res_a['error']}"))
                    return
                if not res_b["success"]:
                    self.after(0, lambda: self.show_error(f"File B error: {res_b['error']}"))
                    return

                lines_a = res_a["text"].splitlines(keepends=True)
                lines_b = res_b["text"].splitlines(keepends=True)

                diff = list(difflib.unified_diff(
                    lines_a, lines_b,
                    fromfile=Path(self._file_a).name,
                    tofile=Path(self._file_b).name,
                    lineterm="",
                ))

                report = "".join(diff) if diff else "No text differences found between the two files."

                Path(out).parent.mkdir(parents=True, exist_ok=True)
                with open(out, "w", encoding="utf-8") as f:
                    f.write(report)

                self.after(0, lambda: self._on_done(report, out))

            except Exception as e:
                self.after(0, lambda: self.show_error(str(e)))

        self.run_in_thread(_work)

    def _on_done(self, report: str, out: str):
        self.hide_progress()
        self._diff_box.configure(state="normal")
        self._diff_box.delete("1.0", "end")
        self._diff_box.insert("1.0", report[:8000] + ("\n…(truncated, see full file)" if len(report) > 8000 else ""))
        self._diff_box.configure(state="disabled")
        from services import history
        history.add_entry("Compare", [self._file_a, self._file_b], out, success=True)
        self._result.show_success("Comparison complete", output_path=out)
