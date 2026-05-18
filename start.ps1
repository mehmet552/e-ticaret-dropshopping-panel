# DropAgent Baslat
# Kullanim: PowerShell'de calistirin -> .\start.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  DropAgent Baslatiliyor..." -ForegroundColor Cyan
Write-Host "  ================================" -ForegroundColor DarkGray
Write-Host ""

# Python kontrolu
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "  [HATA] Python bulunamadi!" -ForegroundColor Red
    Write-Host "  https://python.org adresinden Python 3.11+ yukleyin." -ForegroundColor Yellow
    exit 1
}

$rootDir = $PSScriptRoot
Set-Location $rootDir

# Bagimliliklar
Write-Host "  [1/2] Bagimliliklar yukleniyor..." -ForegroundColor Yellow
python -m pip install -r requirements-local.txt -q --disable-pip-version-check
Write-Host "  [1/2] Bagimliliklar hazir" -ForegroundColor Green

# Uygulamayi baslat
Write-Host "  [2/2] Servis baslatiliyor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  ================================" -ForegroundColor DarkGray
Write-Host "  Uygulama baslatildi!" -ForegroundColor Green
Write-Host ""
Write-Host "  Uygulama  ->  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs  ->  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Kapatmak icin CTRL+C'ye basin." -ForegroundColor DarkGray
Write-Host ""

python main.py
