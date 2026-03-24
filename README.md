# PDForge

**Professional PDF toolkit — 100% free, 100% offline, open source.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)](https://github.com/muhamad0x/PDForge)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Download (Windows)

**[→ Get PDForge.exe from Releases](https://github.com/muhamad0x/PDForge/releases)** — no installation required. Extract the zip, run `PDForge.exe`.

---

## Features

| Category | Tools |
|----------|-------|
| **Organize** | Merge, Split, Organize Pages, Rotate |
| **Optimize** | Compress, Repair |
| **Convert** | PDF↔Word, PDF↔Excel, PDF↔Images, PDF↔Text |
| **Security** | Protect (encrypt), Unlock (decrypt), Redact |
| **Enrich** | Watermark, Page Numbers, Header/Footer, OCR |
| **Extract** | Text, Images, Tables, Metadata |
| **Tools** | Compare, Batch Process, History, Settings |

---

## Run from source

```bash
git clone https://github.com/muhamad0x/PDForge.git
cd PDForge
pip install -r requirements.txt
python main.py
```

---

## Optional system tools (for best results)

| Tool | Purpose |
|------|---------|
| **Ghostscript** | Better PDF compression |
| **Tesseract OCR** | OCR feature |
| **Poppler** | PDF→Image conversion, OCR |

---

## Build executable (Windows)

```bash
pip install pyinstaller
pyinstaller pdforge.spec
# Output: dist/PDForge/PDForge.exe (+ _internal folder)
```

---

## License

[MIT License](LICENSE) — free for personal and commercial use.

---

**Made by [Mohamed Abdelghani](https://github.com/muhamad0x)** · [GitHub](https://github.com/muhamad0x) · [X](https://x.com/muhamad0x) · [LinkedIn](https://linkedin.com/in/muhamad0x)
