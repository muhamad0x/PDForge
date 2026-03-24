"""PDForge — ui/tools/watermark_view.py"""

from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from ui.base_view import BaseToolView
from ui.widgets import DropZone, PrimaryButton, SecondaryButton, ThemedComboBox
from assets.themes.theme import COLORS, RADIUS


POSITIONS = ["center", "top-left", "top-right", "bottom-left", "bottom-right", "tile"]


class WatermarkView(BaseToolView):
    ICON     = "◈"
    TITLE    = "Watermark PDF"
    SUBTITLE = "Add text or image watermarks with full position and opacity control"

    def __init__(self, parent):
        self._file = ""
        self._img_file = ""
        super().__init__(parent)

    def build_ui(self, parent):
        self._drop = DropZone(parent, on_files_dropped=self._set_file,
                              accept_multiple=False, height=110,
                              label="Drop a PDF file here, or click to browse")
        self._drop.pack(fill="x", pady=(0, 12))

        self._file_label = ctk.CTkLabel(parent, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["accent"], anchor="w")
        self._file_label.pack(anchor="w", pady=(0, 8))

        # Mode toggle
        self.section(parent, "WATERMARK TYPE")
        self._mode = ctk.StringVar(value="text")
        mode_row = ctk.CTkFrame(parent, fg_color="transparent")
        mode_row.pack(anchor="w")
        for val, label in [("text", "Text watermark"), ("image", "Image watermark")]:
            ctk.CTkRadioButton(mode_row, text=label, variable=self._mode, value=val,
                command=self._on_mode_change,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
            ).pack(side="left", padx=(0, 20))

        self._mode_opts = ctk.CTkFrame(parent, fg_color="transparent")
        self._mode_opts.pack(fill="x", pady=(10, 0))
        self._build_text_opts()

        # Common options
        self.section(parent, "POSITION & APPEARANCE")
        opts_grid = ctk.CTkFrame(parent, fg_color="transparent")
        opts_grid.pack(fill="x")

        # Position
        ctk.CTkLabel(opts_grid, text="Position:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).grid(row=0, column=0, sticky="w", pady=4)
        self._pos_var = ctk.StringVar(value="center")
        ThemedComboBox(opts_grid, values=POSITIONS, variable=self._pos_var, width=160
            ).grid(row=0, column=1, sticky="w", padx=(8, 24), pady=4)

        # Opacity
        ctk.CTkLabel(opts_grid, text="Opacity:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).grid(row=0, column=2, sticky="w", pady=4)
        self._opacity_var = ctk.DoubleVar(value=0.25)
        self._opacity_label = ctk.CTkLabel(opts_grid, text="25%",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_muted"], width=36)
        self._opacity_label.grid(row=0, column=4, sticky="w", padx=4)
        ctk.CTkSlider(opts_grid, from_=0.05, to=1.0,
            variable=self._opacity_var,
            command=lambda v: self._opacity_label.configure(text=f"{int(float(v)*100)}%"),
            fg_color=COLORS["progress_bg"], progress_color=COLORS["accent"],
            button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"],
            width=120,
        ).grid(row=0, column=3, sticky="w", padx=(8, 0), pady=4)

        # Pages
        ctk.CTkLabel(opts_grid, text="Pages:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).grid(row=1, column=0, sticky="w", pady=4)
        self._pages_var = ctk.StringVar(value="all")
        ctk.CTkEntry(opts_grid, textvariable=self._pages_var, width=160,
            placeholder_text="all or 1-3,5",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=32,
            corner_radius=RADIUS["md"]).grid(row=1, column=1, sticky="w", padx=(8, 0))

        self.section(parent, "OUTPUT")
        out_row = ctk.CTkFrame(parent, fg_color="transparent")
        out_row.pack(fill="x")
        self._out_var = ctk.StringVar()
        ctk.CTkEntry(out_row, textvariable=self._out_var,
            placeholder_text="Output path",
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], placeholder_text_color=COLORS["text_muted"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"]).pack(side="left", fill="x", expand=True, padx=(0, 8))
        SecondaryButton(out_row, text="Browse", command=self._browse_out, width=90).pack(side="left")

    def _build_text_opts(self):
        for w in self._mode_opts.winfo_children():
            w.destroy()
        f = self._mode_opts

        row1 = ctk.CTkFrame(f, fg_color="transparent")
        row1.pack(fill="x")

        ctk.CTkLabel(row1, text="Watermark text:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(anchor="w")
        self._text_var = ctk.StringVar(value="CONFIDENTIAL")
        ctk.CTkEntry(f, textvariable=self._text_var,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=36,
            corner_radius=RADIUS["md"]).pack(fill="x", pady=(4, 8))

        row2 = ctk.CTkFrame(f, fg_color="transparent")
        row2.pack(fill="x")

        ctk.CTkLabel(row2, text="Font size:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(side="left")
        self._size_var = ctk.StringVar(value="48")
        ctk.CTkEntry(row2, textvariable=self._size_var, width=60,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=32,
            corner_radius=RADIUS["md"]).pack(side="left", padx=8)

        ctk.CTkLabel(row2, text="Angle:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(side="left", padx=(16, 0))
        self._angle_var = ctk.StringVar(value="45")
        ctk.CTkEntry(row2, textvariable=self._angle_var, width=60,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=32,
            corner_radius=RADIUS["md"]).pack(side="left", padx=8)

        ctk.CTkLabel(row2, text="Color (hex):",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(side="left", padx=(16, 0))
        self._color_var = ctk.StringVar(value="#FF0000")
        ctk.CTkEntry(row2, textvariable=self._color_var, width=90,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13), height=32,
            corner_radius=RADIUS["md"]).pack(side="left", padx=8)

    def _build_image_opts(self):
        for w in self._mode_opts.winfo_children():
            w.destroy()
        f = self._mode_opts

        ctk.CTkLabel(f, text="Watermark image (PNG/JPEG):",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]).pack(anchor="w")

        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=(4, 0))

        self._img_label = ctk.CTkLabel(row,
            text="No image selected",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_muted"])
        self._img_label.pack(side="left", fill="x", expand=True)

        SecondaryButton(row, text="Browse Image",
            command=self._browse_image, width=120).pack(side="left")

    def _on_mode_change(self):
        if self._mode.get() == "text":
            self._build_text_opts()
        else:
            self._build_image_opts()

    def _browse_image(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select watermark image",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.webp;*.gif;*.bmp;*.tif;*.tiff"), ("All files", "*.*")],
        )
        if path:
            self._img_file = path
            self._img_label.configure(text=Path(path).name, text_color=COLORS["accent"])

    def _set_file(self, paths):
        if paths:
            self._file = paths[0]
            self._file_label.configure(text=f"✓  {Path(self._file).name}")
            self.autofill_output_entry(self._out_var, self._file, "watermarked")

    def _browse_out(self):
        path = self.browse_save_pdf(default_name=Path(
            self.suggest_output(self._file, "watermarked") if self._file else "watermarked.pdf"
        ).name)
        if path:
            self._out_var.set(path)

    def build_buttons(self, parent):
        PrimaryButton(parent, text="◈  Add Watermark", command=self.run, width=170).pack(side="left")

    def run(self):
        if not self._file:
            self.show_error("Select a PDF file first.")
            return
        out = self._out_var.get().strip() or self.suggest_output(self._file, "watermarked")
        opacity = float(self._opacity_var.get())
        position = self._pos_var.get()
        pages = self._pages_var.get().strip() or "all"
        self.show_progress("Adding watermark…")

        def _work():
            cb = lambda c, t: self.after(0, lambda: self.update_progress(c, t))
            if self._mode.get() == "text":
                from core.watermark import add_text_watermark
                try:
                    fs    = int(self._size_var.get())
                    angle = int(self._angle_var.get())
                except Exception:
                    fs, angle = 48, 45
                result = add_text_watermark(
                    self._file, out,
                    text=self._text_var.get() or "WATERMARK",
                    font_size=fs, color_hex=self._color_var.get(),
                    opacity=opacity, angle=angle,
                    position=position, pages=pages,
                    progress_cb=cb,
                )
            else:
                if not self._img_file:
                    self.after(0, lambda: self.show_error("Select a watermark image first."))
                    return
                from core.watermark import add_image_watermark
                result = add_image_watermark(
                    self._file, out,
                    image_path=self._img_file,
                    opacity=opacity, position=position,
                    pages=pages, progress_cb=cb,
                )
            self.after(0, lambda: self._on_done(result, out))

        self.run_in_thread(_work)

    def _on_done(self, result, out):
        if result["success"]:
            from services import history
            history.add_entry("Watermark", [self._file], out, success=True)
            self.show_success("Watermark added successfully", output_path=out)
        else:
            self.show_error(result["error"])
