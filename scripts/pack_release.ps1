# PDForge — Create release zip for GitHub Releases
# Run from project root: .\scripts\pack_release.ps1 [version]

param([string]$Version = "1.0.0")

$dist = "dist\PDForge"
$zipName = "PDForge-Windows-x64-v$Version.zip"

if (-not (Test-Path $dist)) {
    Write-Error "Build first: pyinstaller pdforge.spec (dist\PDForge not found)"
    exit 1
}

$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

Remove-Item $zipName -ErrorAction SilentlyContinue
Compress-Archive -Path "$dist\*" -DestinationPath $zipName -CompressionLevel Optimal

Write-Host "Created: $zipName"
Write-Host "Upload this file to GitHub Releases."
