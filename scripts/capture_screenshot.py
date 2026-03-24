"""Capture PDForge window screenshot. Run from project root."""
import sys
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import customtkinter as ctk
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

if sys.platform == "win32":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

from ui.main_window import MainWindow
from PIL import ImageGrab

OUT = os.path.join(ROOT, "assets", "screenshots", "app-main.png")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

app = MainWindow()

def capture():
    app.update_idletasks()
    x = app.winfo_rootx()
    y = app.winfo_rooty()
    w = app.winfo_width()
    h = app.winfo_height()
    if w > 100 and h > 100:
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        img.save(OUT)
        print(f"Saved: {OUT}")
    app.quit()

app.after(800, capture)
app.mainloop()
