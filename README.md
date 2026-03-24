<p align="center">
  <img src="assets/icons/logo_512.png" alt="PDForge" width="120" />
</p>

<h1 align="center">PDForge</h1>

<p align="center">
  <strong>Professional PDF toolkit — fast, offline, no subscriptions.</strong>
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/muhamad0x/PDForge/releases"><img src="https://img.shields.io/badge/Windows-x64-0078D6?style=flat-square&logo=windows&logoColor=white" alt="Windows"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" alt="License"></a>
  <img src="https://img.shields.io/badge/Offline-100%25-success?style=flat-square" alt="Offline">
  <img src="https://img.shields.io/badge/Open_Source-Yes-8B5CF6?style=flat-square" alt="Open Source">
</p>

<p align="center">
  <a href="#-download">Download</a> •
  <a href="#-features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-build">Build</a> •
  <a href="#-license">License</a>
</p>

---

## Screenshot

<p align="center">
  <img src="assets/screenshots/app-main.png" alt="PDForge App" width="900" />
</p>

---

## Download

**[→ Download PDForge for Windows](https://github.com/muhamad0x/PDForge/releases)**

Extract the zip and run `PDForge.exe` — no installation required.

---

## Features

### Organize
| | Tool | Description |
|---|------|-------------|
| ⊕ | **Merge PDF** | Combine multiple PDFs into one file |
| ⊘ | **Split PDF** | Split by page ranges |
| ⊞ | **Organize Pages** | Reorder, delete, or reorder pages |
| ↻ | **Rotate Pages** | Rotate selected pages 90° / 180° |

### Optimize
| | Tool | Description |
|---|------|-------------|
| ↓ | **Compress PDF** | Reduce file size |
| ⚙ | **Repair PDF** | Fix corrupted or problematic PDFs |

### Convert
| | Tool | Description |
|---|------|-------------|
| W | **PDF → Word** | Export to .docx |
| X | **PDF → Excel** | Extract tables to .xlsx |
| 🖼 | **PDF → Image** | Export pages as images |
| 📄 | **Image → PDF** | Create PDF from images |
| T | **PDF → Text** | Extract plain text |

### Security
| | Tool | Description |
|---|------|-------------|
| 🔒 | **Protect PDF** | Encrypt with password |
| 🔓 | **Unlock PDF** | Remove password (with key) |
| ▬ | **Redact PDF** | Permanently remove sensitive content |

### Enrich
| | Tool | Description |
|---|------|-------------|
| ◈ | **Watermark** | Add text or image watermark |
| # | **Page Numbers** | Add page numbering |
| ≡ | **Header/Footer** | Add headers and footers |
| ◉ | **OCR** | Extract text from scanned PDFs |

### Extract
| | Tool | Description |
|---|------|-------------|
| ¶ | **Extract Text** | Get text content |
| ⬚ | **Extract Images** | Save embedded images |
| ⊟ | **Extract Tables** | Export tables to Excel |
| ℹ | **Edit Metadata** | View and edit document metadata |

### Tools
| | Tool | Description |
|---|------|-------------|
| ⇔ | **Compare PDF** | Diff two PDFs |
| ⊡ | **Batch Process** | Run operations on multiple files |
| ⊙ | **History** | Recent operations |
| ⚙ | **Settings** | App preferences |

---

## Installation

### From source

```bash
git clone https://github.com/muhamad0x/PDForge.git
cd PDForge
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## Build

```bash
pip install pyinstaller
pyinstaller pdforge.spec
```

Output: `dist/PDForge/PDForge.exe` (with `_internal` folder).

See [RELEASING.md](RELEASING.md) for release packaging.

---

## Optional external tools

For best results in some operations:

| Tool | Purpose |
|------|---------|
| **Ghostscript** | Better compression quality |
| **Tesseract OCR** | OCR for scanned documents |
| **Poppler** | PDF↔Image conversion quality |

---

## Project structure

```
PDForge/
├── assets/          # Icons, themes, screenshots
├── core/            # PDF processing logic
├── services/        # Preview, settings
├── ui/              # Main window, sidebar, tool views
├── scripts/         # Build and release scripts
├── main.py
└── pdforge.spec
```

---

## License

[MIT License](LICENSE) — free for personal and commercial use.

---

## Author

**Mohamed Abdelghani**

[![GitHub](https://img.shields.io/badge/GitHub-muhamad0x-181717?style=flat-square&logo=github)](https://github.com/muhamad0x)
[![X](https://img.shields.io/badge/X-@muhamad0x-000000?style=flat-square&logo=x)](https://x.com/muhamad0x)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-muhamad0x-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/muhamad0x)
