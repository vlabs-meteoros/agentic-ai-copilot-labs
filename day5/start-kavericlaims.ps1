<#
.SYNOPSIS
  Day 5 (Labs 13-15): make your own working copy of the KaveriClaims app and open it in VS Code.

.DESCRIPTION
  Copies day5\kavericlaims to Desktop\kavericlaims (outside this repository, so your changes never
  block a later "git pull"), makes it a Git repository with one starting commit (so you can see
  and undo every change Copilot makes), points VS Code at this repository's .venv with pytest
  turned on, and opens it in a new VS Code window.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\day5\start-kavericlaims.ps1
  powershell -ExecutionPolicy Bypass -File .\day5\start-kavericlaims.ps1 -Reset               # start again from a fresh copy
  powershell -ExecutionPolicy Bypass -File .\day5\start-kavericlaims.ps1 -Reset -FromLab14    # start Lab 15 from the Lab 14 reference solution
#>
param(
    [string]$Destination = (Join-Path ([Environment]::GetFolderPath("Desktop")) "kavericlaims"),
    [switch]$Reset,
    [switch]$FromLab14,
    [switch]$NoOpen
)
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $PSScriptRoot "kavericlaims"
$Lab13 = Join-Path $PSScriptRoot "lab13-context-multimodal"
$Lab14Solution = Join-Path $PSScriptRoot "lab14-refactor\solution"
$VenvPy = Join-Path $RepoRoot ".venv\Scripts\python.exe"

function Open-InCode($path) {
    if ($NoOpen) { return }
    if (Get-Command code -ErrorAction SilentlyContinue) {
        code -n $path
        Write-Host "Opened in a NEW VS Code window. Keep this window open too (Lab 13 Task 6 runs here)." -ForegroundColor Green
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
    try {
        Rename-Item $Destination $old -ErrorAction Stop
    } catch {
        Write-Host "Can't move $Destination because it's open in another window." -ForegroundColor Yellow
        Write-Host "Close the KaveriClaims VS Code window (File > Close Window), then run this command again." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Your previous copy was moved to $old"
}

Copy-Item $Source $Destination -Recurse
Get-ChildItem $Destination -Recurse -Directory -Include "__pycache__", ".pytest_cache" | Remove-Item -Recurse -Force

$message = "KaveriClaims starting point"
if ($FromLab14) {
    # Lab 14 reference solution, plus the instructions files from Lab 13
    Copy-Item (Join-Path $Lab14Solution "*") $Destination -Recurse -Force
    $instructions = Join-Path $Destination ".github\instructions"
    New-Item -ItemType Directory -Force $instructions | Out-Null
    Copy-Item (Join-Path $Lab13 "copilot-instructions.md") (Join-Path $Destination ".github")
    Copy-Item (Join-Path $Lab13 "tests.instructions.md") $instructions
    $message = "KaveriClaims after Lab 14 (reference solution)"
}

# Tell VS Code (and Copilot) which Python to use, and turn on pytest in the Testing view
$vscode = Join-Path $Destination ".vscode"
New-Item -ItemType Directory -Force $vscode | Out-Null
$settings = [ordered]@{
    "python.defaultInterpreterPath"       = $VenvPy
    "python.terminal.activateEnvironment" = $true
    "python.testing.pytestEnabled"        = $true
    "python.testing.unittestEnabled"      = $false
    "python.testing.pytestArgs"           = @("tests")
}
# WriteAllText writes UTF-8 without a BOM
[IO.File]::WriteAllText((Join-Path $vscode "settings.json"), ($settings | ConvertTo-Json))

[IO.File]::WriteAllText((Join-Path $Destination ".gitignore"), "__pycache__/`n*.pyc`n.venv/`n.pytest_cache/`n.coverage`nhtmlcov/`npayroll_*.csv`n")

if (Get-Command git -ErrorAction SilentlyContinue) {
    git -C $Destination init -q
    git -C $Destination config core.safecrlf false   # no "LF will be replaced by CRLF" warning per file
    git -C $Destination add -A
    git -C $Destination -c user.name="Lab participant" -c user.email="lab@example.com" commit -q -m $message
    Write-Host "Git repository created with one commit: '$message'"
} else {
    Write-Host "Git not found: the copy works, but you can't use Source Control to undo changes." -ForegroundColor Yellow
}

if (-not (Test-Path $VenvPy)) {
    Write-Host "Warning: $VenvPy not found. Run setup\setup-windows.ps1 first." -ForegroundColor Yellow
}

Write-Host "`nKaveriClaims copied to $Destination" -ForegroundColor Green
Write-Host "In the new window's terminal, activate the labs' Python and check the app runs:"
Write-Host "  & `"$RepoRoot\.venv\Scripts\Activate.ps1`"" -ForegroundColor Cyan
Write-Host "  python -m kavericlaims report --month 2026-11" -ForegroundColor Cyan
Write-Host "  python -m pytest" -ForegroundColor Cyan
Open-InCode $Destination
