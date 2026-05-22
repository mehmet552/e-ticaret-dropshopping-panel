# DropAgent Baslat
# Kullanim: PowerShell'de -> .\start.ps1
# veya cift tikla -> start.bat

$ErrorActionPreference = "Stop"

function Write-Step([string]$Message, [string]$Color = "White") {
    Write-Host "  $Message" -ForegroundColor $Color
}

function Get-PythonCommand {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @{ Exe = "python"; Args = @() }
    }
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @{ Exe = "py"; Args = @("-3") }
    }
    return $null
}

function Invoke-Python([string[]]$PythonArgs) {
    $py = Get-PythonCommand
    if (-not $py) {
        throw "Python bulunamadi"
    }
    & $py.Exe @($py.Args + $PythonArgs)
    if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
        throw "Python komutu basarisiz (exit $LASTEXITCODE): $($py.Exe) $($py.Args -join ' ') $PythonArgs"
    }
}

Write-Host ""
Write-Step "DropAgent Baslatiliyor..." "Cyan"
Write-Step "================================" "DarkGray"
Write-Host ""

$py = Get-PythonCommand
if (-not $py) {
    Write-Step "[HATA] Python bulunamadi!" "Red"
    Write-Step "https://www.python.org/downloads/ adresinden Python 3.11+ yukleyin." "Yellow"
    Write-Step "Kurulumda 'Add python.exe to PATH' secenegini isaretleyin." "Yellow"
    exit 1
}

$rootDir = $PSScriptRoot
if (-not $rootDir) {
    $rootDir = (Get-Location).Path
}
Set-Location $rootDir

if (-not (Test-Path "main.py")) {
    Write-Step "[HATA] main.py bulunamadi. start.ps1 proje kokunde calistirilmali." "Red"
    Write-Step "Dizin: $rootDir" "Yellow"
    exit 1
}

if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Step ".env dosyasi olusturuldu (.env.example kopyalandi)" "Green"
}

if (-not (Test-Path "requirements-local.txt")) {
    Write-Step "[HATA] requirements-local.txt bulunamadi." "Red"
    exit 1
}

Write-Step "[1/2] Bagimliliklar yukleniyor..." "Yellow"
try {
    Invoke-Python @("-m", "pip", "install", "-r", "requirements-local.txt", "-q", "--disable-pip-version-check")
} catch {
    Write-Step "[HATA] Bagimliliklar yuklenemedi: $_" "Red"
    exit 1
}
Write-Step "[1/2] Bagimliliklar hazir" "Green"

Write-Step "[2/2] Servis baslatiliyor..." "Yellow"
Write-Host ""
Write-Step "================================" "DarkGray"
Write-Step "Uygulama baslatildi!" "Green"
Write-Host ""
Write-Step "Uygulama  ->  http://localhost:8000" "Cyan"
Write-Step "API Docs  ->  http://localhost:8000/docs" "Cyan"
Write-Host ""
Write-Step "Kapatmak icin CTRL+C'ye basin." "DarkGray"
Write-Host ""

Invoke-Python @("main.py")
