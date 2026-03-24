# Release instructions

## 1. Build the executable

```powershell
cd PDForge
.\venv\Scripts\activate
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
pyinstaller pdforge.spec
```

## 2. Create release zip

```powershell
Compress-Archive -Path "dist\PDForge\*" -DestinationPath "PDForge-Windows-x64-v1.0.0.zip"
```

> **Important:** Include the entire `dist\PDForge\` folder contents (PDForge.exe + _internal). Users extract the zip and run PDForge.exe from inside.

## 3. Create GitHub release

1. Go to [https://github.com/muhamad0x/PDForge/releases](https://github.com/muhamad0x/PDForge/releases)
2. Click **"Draft a new release"**
3. **Tag:** `v1.0.0` (create new tag)
4. **Title:** `PDForge v1.0.0`
5. **Description** (example):

   ```markdown
   ## PDForge v1.0.0
   
   - Windows 64-bit standalone build
   - No installation required — extract zip and run PDForge.exe
   
   ### Download
   - **PDForge-Windows-x64-v1.0.0.zip** — extract and run
   ```

6. Attach `PDForge-Windows-x64-v1.0.0.zip`
7. Click **Publish release**
