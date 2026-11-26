<#
.SYNOPSIS
  Day 7 (Lab 19): make your own working copy of the KaveriRooms app (JavaScript) and open it in VS Code.

.DESCRIPTION
  Copies day7\kaverirooms to Desktop\kaverirooms (outside this repository, so your changes never block a
  later "git pull"), makes it a Git repository with one starting commit (so you can see and undo every
  change Copilot makes), and opens it in a new VS Code window.

  It also writes .vscode\settings.json so that every terminal in that window (yours and Copilot's) can run
  the app and the Spec Kit scripts: the labs' .venv\Scripts folder (python, specify), .speckit-venv\Scripts (specify, when
  setup put Spec Kit there because .venv is Python 3.10) and Node.js are on the PATH,
  PowerShell scripts are allowed for those terminals only (PSExecutionPolicyPreference=Bypass), and Spec Kit uses
  the labs' Python.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\day7\start-kaverirooms.ps1
  powershell -ExecutionPolicy Bypass -File .\day7\start-kaverirooms.ps1 -Reset      # start again from a fresh copy
#>
param(
    [string]$Destination = (Join-Path ([Environment]::GetFolderPath("Desktop")) "kaverirooms"),
    [switch]$Reset,
    [switch]$NoOpen
)
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $PSScriptRoot "kaverirooms"
$VenvScripts = Join-Path $RepoRoot ".venv\Scripts"
$VenvPy = Join-Path $VenvScripts "python.exe"
# Spec Kit's own environment, which setup creates only when .venv is Python 3.10 (Spec Kit needs 3.11+)
$SpecKitScripts = Join-Path $RepoRoot ".speckit-venv\Scripts"

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
        Write-Host "Close the KaveriRooms VS Code window (File > Close Window), stop 'node src/server.js' if it's running, then run this command again." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Your previous copy was moved to $old"
}

Copy-Item $Source $Destination -Recurse

# Node.js: the one on the PATH, or the per-user copy setup-windows.ps1 installs (a terminal opened before setup can't see that one yet)
$NodeDir = $null
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCmd) {
    $NodeDir = Split-Path -Parent $nodeCmd.Source
} else {
    $installed = Get-ChildItem (Join-Path $env:LOCALAPPDATA "Programs\nodejs-lts") -Directory -Filter "node-v*-win-x64" -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending | Select-Object -First 1
    if ($installed) { $NodeDir = $installed.FullName }
}
# .speckit-venv\Scripts is always listed (a folder that doesn't exist is ignored), after .venv\Scripts so 'python' stays the labs' Python
$TerminalPath = (@($VenvScripts, $SpecKitScripts, $NodeDir) | Where-Object { $_ }) -join ";"

# Terminals in the KaveriRooms window: labs' Python, 'specify' and Node.js on the PATH, .ps1 scripts allowed, Spec Kit uses the labs' Python
$vscode = Join-Path $Destination ".vscode"
New-Item -ItemType Directory -Force $vscode | Out-Null
$settings = [ordered]@{
    "terminal.integrated.env.windows" = [ordered]@{
        "PATH"                        = "$TerminalPath;`${env:PATH}"
        "PSExecutionPolicyPreference" = "Bypass"
        "SPECKIT_PYTHON_EXECUTABLE"   = $VenvPy
    }
}
# WriteAllText writes UTF-8 without a BOM
[IO.File]::WriteAllText((Join-Path $vscode "settings.json"), ($settings | ConvertTo-Json))

[IO.File]::WriteAllText((Join-Path $Destination ".gitignore"), "node_modules/`n*.tmp`n")

if (Get-Command git -ErrorAction SilentlyContinue) {
    git -C $Destination init -q
    git -C $Destination config core.safecrlf false   # no "LF will be replaced by CRLF" warning per file
    git -C $Destination config user.name "Lab participant"
    git -C $Destination config user.email "lab@example.com"
    git -C $Destination add -A
    git -C $Destination commit -q -m "KaveriRooms starting point"
    git -C $Destination tag start
    Write-Host "Git repository created with one commit, tagged 'start'."
} else {
    Write-Host "Git not found: the copy works, but you can't use Source Control to undo changes." -ForegroundColor Yellow
}

if (-not $NodeDir) {
    Write-Host "Warning: Node.js not found. Run setup\setup-windows.ps1 first (it installs Node.js), then run this script again with -Reset." -ForegroundColor Yellow
}
if (-not ((Test-Path (Join-Path $VenvScripts "specify.exe")) -or (Test-Path (Join-Path $SpecKitScripts "specify.exe")))) {
    Write-Host "Warning: Spec Kit ('specify') isn't installed yet. Run setup\setup-windows.ps1 first (Day 7 'Before you start')." -ForegroundColor Yellow
}

Write-Host "`nKaveriRooms copied to $Destination" -ForegroundColor Green
Write-Host "In the new window's terminal, check the app:"
Write-Host "  node --test" -ForegroundColor Cyan
Write-Host "  node src/server.js        (then open http://localhost:3000/?date=2026-12-08)" -ForegroundColor Cyan
Open-InCode $Destination
