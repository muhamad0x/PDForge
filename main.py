"""
PDForge — main.py
Application entry point.
"""

import sys
import os

# ── Add project root to sys.path so all imports work ──────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── CustomTkinter appearance (must be set before any CTk widgets) ──────────────
import customtkinter as ctk
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ── DPI awareness on Windows ───────────────────────────────────────────────────
if sys.platform == "win32":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# ── Launch ─────────────────────────────────────────────────────────────────────
def main():
    from ui.main_window import MainWindow
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
