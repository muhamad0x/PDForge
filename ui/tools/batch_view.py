"""PDForge — ui/tools/batch_view.py"""

from __future__ import annotations
import os
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton, FileListItem
from assets.themes.theme import COLORS, RADIUS

BATCH_OPS = [
    ("compress",   "Compress",     "Reduce file size"),
    ("rotate",     "Rotate 90°",   "Rotate all pages 90° clockwise"),
    ("rotate180",  "Rotate 180°",  "Rotate all pages 180°"),
    ("number",     "Page Numbers", "Add page numbers (bottom-center)"),
    ("pdf_to_word","PDF → Word",   "Convert each file to .docx"),
    ("pdf_to_text","PDF → Text",   "Extract text from each file"),
    ("pdf_to_image","PDF → Images","Export pages as PNG images"),
    ("watermark",  "Watermark",    "Add DRAFT text watermark"),
    ("metadata_strip","Strip Metadata","Remove all metadata"),
]


class BatchView(BaseToolView):
    ICON     = "⊡"
    TITLE    = "Batch Process"
    SUBTITLE = "Apply one operation to many PDF files at once"

    def __init__(self, parent):
        self._files: list[str] = []
        super().__init__(parent)

    def build_ui(self, parent):
        self._drop = DropZone(parent, on_files_dropped=self._add_files,
                              accept_multiple=True, height=110,
                              label="Drop multiple PDF files here")
        self._drop.pack(fill="x", pady=(0, 12))

        self._count_label = ctk.CTkLabel(parent, text="No files added",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_muted"], anchor="w")
        self._count_label.pack(anchor="w", pady=(0, 4))

        SecondaryButton(parent, text="Clear all", command=self._clear, width=90).pack(anchor="w")

        self.section(parent, "OPERATION")
        self._op_var = ctk.StringVar(value="compress")
        op_grid = ctk.CTkFrame(parent, fg_color="transparent")
        op_grid.pack(fill="x")
        for i, (val, label, desc) in enumerate(BATCH_OPS):
            row = ctk.CTkFrame(op_grid, fg_color="transparent")
            row.grid(row=i // 2, column=i % 2, padx=(0, 20), pady=2, sticky="w")
            ctk.CTkRadioButton(row, text=label, variable=self._op_var, value=val,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_primary"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
            ).pack(side="left")
            ctk.CTkLabel(row, text=f"— {desc}",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS["text_muted"]).pack(side="left", padx=(4, 0))

        self.section(parent, "OUTPUT FOLDER")
        out_row = ctk.CTkFrame(parent, fg_color="transparent")
        out_row.pack(fill="x")
        self._out_var = ctk.StringVar()
        ctk.CTkEntry(out_row, textvariable=self._out_var,
            placeholder_text="Output folder (defaults to input folder)",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"]).pack(side="left", fill="x", expand=True, padx=(0, 8))
        SecondaryButton(out_row, text="Browse",
            command=lambda: self._out_var.set(self.browse_directory()),
            width=90).pack(side="left")

        # Log area
        self.section(parent, "PROCESSING LOG")
        self._log = ctk.CTkTextbox(parent, height=140,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"], border_width=1,
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=RADIUS["md"])
        self._log.pack(fill="x")
        self._log.configure(state="disabled")

    def _add_files(self, paths):
        for p in paths:
            if p not in self._files:
                self._files.append(p)
        self._count_label.configure(text=f"{len(self._files)} file(s) queued")

    def _clear(self):
        self._files.clear()
        self._count_label.configure(text="No files added")

    def _log_line(self, text: str):
        self._log.configure(state="normal")
        self._log.insert("end", text + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def build_buttons(self, parent):
        PrimaryButton(parent, text="⊡  Run Batch", command=self.run, width=160).pack(side="left")
        self._status_label = ctk.CTkLabel(parent, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_muted"])
        self._status_label.pack(side="left", padx=16)

    def run(self):
        if not self._files:
            self.show_error("Add PDF files first.")
            return
        op      = self._op_var.get()
        out_dir = self._out_var.get().strip()
        self.show_progress(f"Batch processing {len(self._files)} files…")
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")

        def _work():
            done = 0
            errors = 0
            total = len(self._files)
            for i, fp in enumerate(self._files):
                self.after(0, lambda i=i: self.update_progress(i + 1, total,
                    f"Processing {Path(fp).name}…"))
                dest = out_dir or str(Path(fp).parent)
                result = _run_single(fp, op, dest)
                if result["success"]:
                    done += 1
                    self.after(0, lambda n=Path(fp).name: self._log_line(f"✓  {n}"))
                else:
                    errors += 1
                    self.after(0, lambda n=Path(fp).name, e=result["error"]:
                               self._log_line(f"✗  {n}  →  {e}"))

            self.after(0, lambda: self._on_done(done, errors, total, out_dir or "(same as input)"))

        self.run_in_thread(_work)

    def _on_done(self, done, errors, total, out_dir):
        self.hide_progress()
        msg = f"{done}/{total} files processed successfully"
        if errors:
            msg += f"  ·  {errors} error(s)"
        from services import history
        history.add_entry("Batch", self._files[:5], out_dir, success=(errors == 0),
                          details=f"op={self._op_var.get()}, {msg}")
        if errors == 0:
            self._result.show_success(msg)
        else:
            self._result.show_error(msg + " — check log above")


def _run_single(fp: str, op: str, out_dir: str) -> dict:
    """Execute one batch operation on one file."""
    stem    = Path(fp).stem
    os.makedirs(out_dir, exist_ok=True)

    try:
        if op == "compress":
            from core.compress import compress_pdf
            out = os.path.join(out_dir, f"{stem}_compressed.pdf")
            return compress_pdf(fp, out, preset="ebook")

        elif op == "rotate":
            from core.organize import rotate_pages
            out = os.path.join(out_dir, f"{stem}_rotated.pdf")
            return rotate_pages(fp, out, rotation=90)

        elif op == "rotate180":
            from core.organize import rotate_pages
            out = os.path.join(out_dir, f"{stem}_rotated180.pdf")
            return rotate_pages(fp, out, rotation=180)

        elif op == "number":
            from core.number import add_page_numbers
            out = os.path.join(out_dir, f"{stem}_numbered.pdf")
            return add_page_numbers(fp, out)

        elif op == "pdf_to_word":
            from core.convert import pdf_to_word
            out = os.path.join(out_dir, f"{stem}.docx")
            return pdf_to_word(fp, out)

        elif op == "pdf_to_text":
            from core.extract import extract_text
            out = os.path.join(out_dir, f"{stem}.txt")
            return extract_text(fp, out)

        elif op == "pdf_to_image":
            from core.convert import pdf_to_images
            img_dir = os.path.join(out_dir, stem + "_images")
            return pdf_to_images(fp, img_dir, image_format="PNG", dpi=150)

        elif op == "watermark":
            from core.watermark import add_text_watermark
            out = os.path.join(out_dir, f"{stem}_watermarked.pdf")
            return add_text_watermark(fp, out, text="DRAFT", opacity=0.2, angle=45)

        elif op == "metadata_strip":
            from core.repair import strip_metadata
            out = os.path.join(out_dir, f"{stem}_clean.pdf")
            return strip_metadata(fp, out)

        else:
            return {"success": False, "error": f"Unknown operation: {op}"}

    except Exception as e:
        return {"success": False, "error": str(e)}
