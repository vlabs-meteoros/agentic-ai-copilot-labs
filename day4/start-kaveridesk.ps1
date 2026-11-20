<#
.SYNOPSIS
  Day 4 (Labs 11 and 13): make your own working copy of the KaveriDesk app and open it in VS Code.

.DESCRIPTION
  Copies day4\kaveridesk to Desktop\kaveridesk (outside this repository, so your changes never
  block a later "git pull"), makes it a Git repository with one starting commit (so you can see
  and undo every change Copilot makes), points VS Code at this repository's .venv, and opens it.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\day4\start-kaveridesk.ps1
  powershell -ExecutionPolicy Bypass -File .\day4\start-kaveridesk.ps1 -Reset    # start again from a fresh copy
#>
param(
    [string]$Destination = (Join-Path ([Environment]::GetFolderPath("Desktop")) "kaveridesk"),
    [switch]$Reset,
    [switch]$NoOpen
)
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $PSScriptRoot "kaveridesk"
$VenvPy = Join-Path $RepoRoot ".venv\Scripts\python.exe"

function Open-InCode($path) {
    if ($NoOpen) { return }
    if (Get-Command code -ErrorAction SilentlyContinue) {
        code -n $path
        Write-Host "Opened in a NEW VS Code window. Keep this window for Lab 12." -ForegroundColor Green
    } else {
        Write-Host "Open it yourself: File > Open Folder... > $path" -ForegroundColor Yellow
    }
}

if (Test-Path $Destination) {
    if (-not $Reset) {
        Write-Host "$Destination already exists. Opening it (use -Reset to start again from a fresh copy)."
        Open-InCode $Destination
        return
    }
    $old = "$Destination-old-$(Get-Date -Format yyyyMMdd-HHmmss)"
    Rename-Item $Destination $old
    Write-Host "Your previous copy was moved to $old"
}

Copy-Item $Source $Destination -Recurse
Get-ChildItem $Destination -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Tell VS Code (and Copilot) which Python to use: the labs' .venv
$vscode = Join-Path $Destination ".vscode"
New-Item -ItemType Directory -Force $vscode | Out-Null
$settings = [ordered]@{
    "python.defaultInterpreterPath"   = $VenvPy
    "python.terminal.activateEnvironment" = $true
    "python.testing.unittestEnabled"  = $true
    "python.testing.pytestEnabled"    = $false
    "python.testing.unittestArgs"     = @("-v", "-s", "tests", "-t", ".", "-p", "test_*.py")
}
# WriteAllText writes UTF-8 without a BOM
[IO.File]::WriteAllText((Join-Path $vscode "settings.json"), ($settings | ConvertTo-Json))

[IO.File]::WriteAllText((Join-Path $Destination ".gitignore"), "__pycache__/`n*.pyc`n.venv/`n")

if (Get-Command git -ErrorAction SilentlyContinue) {
    git -C $Destination init -q
    git -C $Destination add -A
    git -C $Destination -c user.name="Lab participant" -c user.email="lab@example.com" commit -q -m "KaveriDesk starting point"
    Write-Host "Git repository created with one commit: 'KaveriDesk starting point'"
} else {
    Write-Host "Git not found: the copy works, but you can't use Source Control to undo changes." -ForegroundColor Yellow
}

if (-not (Test-Path $VenvPy)) {
    Write-Host "Warning: $VenvPy not found. Run setup\setup-windows.ps1 first." -ForegroundColor Yellow
}

Write-Host "`nKaveriDesk copied to $Destination" -ForegroundColor Green
Write-Host "In the new window's terminal, activate the labs' Python and check the app runs:"
Write-Host "  & `"$RepoRoot\.venv\Scripts\Activate.ps1`"" -ForegroundColor Cyan
Write-Host "  python -m kaveridesk --now `"2026-11-20 11:00`" list" -ForegroundColor Cyan
Open-InCode $Destination
