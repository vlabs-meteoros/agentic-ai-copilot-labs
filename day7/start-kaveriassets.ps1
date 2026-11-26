<#
.SYNOPSIS
  Day 7 (Labs 20-21): make your own working copy of the KaveriAssets app (Python) and open it in VS Code.

.DESCRIPTION
  Copies day7\kaveriassets to Desktop\kaveriassets (outside this repository, so your changes never block a
  later "git pull"), makes it a Git repository with one starting commit, tagged 'start' (so you can see and
  undo every change Copilot makes), points VS Code at this repository's .venv with pytest turned on, and opens
  it in a new VS Code window.

  Terminals in that window get the labs' .venv\Scripts on the PATH (no activation needed) and LABS_ENV, the
  path of this repository's .env (Lab 21 reads the Azure values from it).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\day7\start-kaveriassets.ps1
  powershell -ExecutionPolicy Bypass -File .\day7\start-kaveriassets.ps1 -Reset               # start again from a fresh copy
  powershell -ExecutionPolicy Bypass -File .\day7\start-kaveriassets.ps1 -Reset -FromLab20    # start Lab 21 from the Lab 20 reference solution
#>
param(
    [string]$Destination = (Join-Path ([Environment]::GetFolderPath("Desktop")) "kaveriassets"),
    [switch]$Reset,
    [switch]$FromLab20,
    [switch]$NoOpen
)
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $PSScriptRoot "kaveriassets"
$Lab20Solution = Join-Path $PSScriptRoot "lab20-add-features\solution"
$VenvScripts = Join-Path $RepoRoot ".venv\Scripts"
$VenvPy = Join-Path $VenvScripts "python.exe"

function Open-InCode($path) {
    if ($NoOpen) { return }
    if (Get-Command code -ErrorAction SilentlyContinue) {
        code -n $path
        Write-Host "Opened in a NEW VS Code window. Keep this window open too." -ForegroundColor Green
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
        Write-Host "Close the KaveriAssets VS Code window (File > Close Window), then run this command again." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Your previous copy was moved to $old"
}

Copy-Item $Source $Destination -Recurse
Get-ChildItem $Destination -Recurse -Directory -Include "__pycache__", ".pytest_cache" | Remove-Item -Recurse -Force

$message = "KaveriAssets starting point"
if ($FromLab20) {
    Copy-Item (Join-Path $Lab20Solution "*") $Destination -Recurse -Force
    $message = "KaveriAssets after Lab 20 (reference solution)"
}

# VS Code: the labs' Python, pytest in the Testing view, and terminals that need no activation
$vscode = Join-Path $Destination ".vscode"
New-Item -ItemType Directory -Force $vscode | Out-Null
$settings = [ordered]@{
    "python.defaultInterpreterPath"       = $VenvPy
    "python.terminal.activateEnvironment" = $false
    "python.testing.pytestEnabled"        = $true
    "python.testing.unittestEnabled"      = $false
    "python.testing.pytestArgs"           = @("tests")
    "terminal.integrated.env.windows"     = [ordered]@{
        "PATH"     = "$VenvScripts;`${env:PATH}"
        "LABS_ENV" = (Join-Path $RepoRoot ".env")
    }
}
# WriteAllText writes UTF-8 without a BOM
[IO.File]::WriteAllText((Join-Path $vscode "settings.json"), ($settings | ConvertTo-Json))

[IO.File]::WriteAllText((Join-Path $Destination ".gitignore"), "__pycache__/`n*.pyc`n.venv/`n.pytest_cache/`n.env`n")

if (Get-Command git -ErrorAction SilentlyContinue) {
    git -C $Destination init -q
    git -C $Destination config core.safecrlf false   # no "LF will be replaced by CRLF" warning per file
    git -C $Destination config user.name "Lab participant"
    git -C $Destination config user.email "lab@example.com"
    git -C $Destination add -A
    git -C $Destination commit -q -m $message
    git -C $Destination tag start
    Write-Host "Git repository created with one commit, tagged 'start': '$message'"
} else {
    Write-Host "Git not found: the copy works, but you can't use Source Control to undo changes." -ForegroundColor Yellow
}

if (-not (Test-Path $VenvPy)) {
    Write-Host "Warning: $VenvPy not found. Run setup\setup-windows.ps1 first." -ForegroundColor Yellow
}

Write-Host "`nKaveriAssets copied to $Destination" -ForegroundColor Green
Write-Host "In the new window's terminal, check the app runs:"
Write-Host "  python -m kaveriassets list" -ForegroundColor Cyan
Write-Host "  python -m pytest" -ForegroundColor Cyan
Open-InCode $Destination
