"""
PDForge — services/
FileManager, History, Settings — all persistence logic.
"""

from __future__ import annotations
import json
import os
import shutil
import sqlite3
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════
# Paths
# ═══════════════════════════════════════════════════════════════════════════

APP_NAME    = "PDForge"
APP_DIR     = Path(os.path.expanduser("~")) / ".pdforge"
DB_PATH     = APP_DIR / "pdforge.db"
SETTINGS_PATH = APP_DIR / "settings.json"
TEMP_DIR    = APP_DIR / "tmp"


def _ensure_app_dir():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
# FILE MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class FileManager:
    """Manages temp files and output path generation."""

    def __init__(self):
        _ensure_app_dir()
        self._temp_files: list[str] = []

    def _output_parent(self, input_path: Path) -> Path:
        """Prefer Settings → default output folder; else same folder as the input file."""
        raw = (settings.get("default_output_dir") or "").strip()
        if raw:
            try:
                d = Path(raw).expanduser()
                d.mkdir(parents=True, exist_ok=True)
                if d.is_dir():
                    return d
            except Exception:
                pass
        return input_path.parent

    def make_temp_path(self, suffix: str = ".pdf") -> str:
        """Create a unique temp file path (not yet created)."""
        fd, path = tempfile.mkstemp(suffix=suffix, dir=str(TEMP_DIR))
        os.close(fd)
        self._temp_files.append(path)
        return path

    def suggest_output_path(
        self,
        input_path: str,
        operation: str,
        suffix: str = ".pdf",
    ) -> str:
        """
        Generate a smart output filename.
        e.g. document.pdf + merge → document_merged.pdf
        """
        p        = Path(input_path)
        parent   = self._output_parent(p)
        out_name = f"{p.stem}_{operation}{suffix}"
        out_path = parent / out_name
        # Avoid overwriting existing files
        counter  = 1
        while out_path.exists():
            out_path = parent / f"{p.stem}_{operation}_{counter}{suffix}"
            counter += 1
        return str(out_path)

    def suggest_output_dir(self, input_path: str, operation: str = "images") -> str:
        """Unique folder path for multi-file exports (e.g. PDF → images per page)."""
        p = Path(input_path)
        parent = self._output_parent(p)
        base = parent / f"{p.stem}_{operation}"
        counter = 1
        candidate = base
        while candidate.exists():
            candidate = parent / f"{p.stem}_{operation}_{counter}"
            counter += 1
        return str(candidate)

    def cleanup_temp(self):
        """Delete all tracked temp files."""
        for path in self._temp_files:
            try:
                if os.path.isfile(path):
                    os.remove(path)
            except Exception:
                pass
        self._temp_files.clear()

    def cleanup_old_temps(self, max_age_hours: int = 24):
        """Delete temp files older than max_age_hours."""
        cutoff = time.time() - max_age_hours * 3600
        try:
            for f in TEMP_DIR.iterdir():
                if f.is_file() and f.stat().st_mtime < cutoff:
                    f.unlink(missing_ok=True)
        except Exception:
            pass

    @staticmethod
    def file_size_human(path: str) -> str:
        try:
            size = os.path.getsize(path)
            for unit in ("B", "KB", "MB", "GB"):
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except Exception:
            return "Unknown"

    @staticmethod
    def get_pdf_page_count(path: str) -> int | None:
        try:
            from pypdf import PdfReader
            return len(PdfReader(path).pages)
        except Exception:
            return None


# ═══════════════════════════════════════════════════════════════════════════
# HISTORY (SQLite)
# ═══════════════════════════════════════════════════════════════════════════

class HistoryManager:
    """Persistent operation history stored in SQLite."""

    def __init__(self):
        _ensure_app_dir()
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp   TEXT    NOT NULL,
                    operation   TEXT    NOT NULL,
                    input_files TEXT    NOT NULL,
                    output_path TEXT,
                    success     INTEGER NOT NULL DEFAULT 1,
                    details     TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recent_files (
                    path        TEXT PRIMARY KEY,
                    last_opened TEXT NOT NULL,
                    page_count  INTEGER,
                    file_size   INTEGER
                )
            """)
            conn.commit()

    def add_entry(
        self,
        operation: str,
        input_files: list[str],
        output_path: str | None = None,
        success: bool = True,
        details: str = "",
    ):
        ts = datetime.now().isoformat(sep=" ", timespec="seconds")
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute(
                "INSERT INTO history (timestamp, operation, input_files, output_path, success, details) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (ts, operation, json.dumps(input_files), output_path, int(success), details),
            )
            conn.commit()

    def get_history(self, limit: int = 100) -> list[dict]:
        with sqlite3.connect(str(DB_PATH)) as conn:
            rows = conn.execute(
                "SELECT id, timestamp, operation, input_files, output_path, success, details "
                "FROM history ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        result = []
        for r in rows:
            result.append({
                "id":           r[0],
                "timestamp":    r[1],
                "operation":    r[2],
                "input_files":  json.loads(r[3]),
                "output_path":  r[4],
                "success":      bool(r[5]),
                "details":      r[6],
            })
        return result

    def clear_history(self):
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute("DELETE FROM history")
            conn.commit()

    def add_recent_file(self, path: str):
        try:
            size = os.path.getsize(path)
            from pypdf import PdfReader
            try:
                pages = len(PdfReader(path).pages)
            except Exception:
                pages = None
        except Exception:
            size  = 0
            pages = None

        ts = datetime.now().isoformat(sep=" ", timespec="seconds")
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO recent_files (path, last_opened, page_count, file_size) "
                "VALUES (?, ?, ?, ?)",
                (path, ts, pages, size),
            )
            conn.commit()

    def get_recent_files(self, limit: int = 20) -> list[dict]:
        with sqlite3.connect(str(DB_PATH)) as conn:
            rows = conn.execute(
                "SELECT path, last_opened, page_count, file_size FROM recent_files "
                "WHERE path IS NOT NULL ORDER BY last_opened DESC LIMIT ?",
                (limit,),
            ).fetchall()
        result = []
        for r in rows:
            if os.path.isfile(r[0]):
                result.append({
                    "path":        r[0],
                    "last_opened": r[1],
                    "page_count":  r[2],
                    "file_size":   r[3],
                    "name":        Path(r[0]).name,
                })
        return result

    def remove_recent_file(self, path: str):
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute("DELETE FROM recent_files WHERE path = ?", (path,))
            conn.commit()


# ═══════════════════════════════════════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_SETTINGS: dict[str, Any] = {
    "theme":                   "dark",
    "default_output_dir":      "",       # "" = same as input
    "default_compress_preset": "ebook",
    "default_image_format":    "PNG",
    "default_dpi":             150,
    "default_ocr_lang":        "eng",
    "remember_window_size":    True,
    "window_width":            1280,
    "window_height":           800,
    "sidebar_collapsed":       False,
    "show_preview":            True,
    "confirm_overwrite":       True,
    "max_recent_files":        20,
    "auto_open_output":        False,
    "pdf_viewer":              "",        # "" = system default
}


class SettingsManager:
    """JSON-based settings persistence."""

    def __init__(self):
        _ensure_app_dir()
        self._data = dict(DEFAULT_SETTINGS)
        self._load()

    def _load(self):
        if SETTINGS_PATH.exists():
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self._data.update(saved)
            except Exception:
                pass

    def save(self):
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get(self, key: str, default=None):
        return self._data.get(key, DEFAULT_SETTINGS.get(key, default))

    def set(self, key: str, value: Any):
        self._data[key] = value
        self.save()

    def reset(self):
        self._data = dict(DEFAULT_SETTINGS)
        self.save()

    def all(self) -> dict:
        return dict(self._data)


# ═══════════════════════════════════════════════════════════════════════════
# Singletons for use across the app
# ═══════════════════════════════════════════════════════════════════════════

file_manager  = FileManager()
history       = HistoryManager()
settings      = SettingsManager()
