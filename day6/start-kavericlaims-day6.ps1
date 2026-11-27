<#
.SYNOPSIS
  Day 6 (Labs 16-18): make your own working copy of KaveriClaims 2.0 and open it in VS Code.

.DESCRIPTION
  Copies day6\kavericlaims to Desktop\kavericlaims-day6 (outside this repository, so your changes never
  block a later "git pull", and your Day 5 copy in Desktop\kavericlaims stays as it was). Makes it a Git
  repository with one starting commit tagged "start", points VS Code at this repository's .venv with pytest
  turned on, adds a debug configuration for Lab 17, and opens it in a new VS Code window.

  Every terminal in that window gets the labs' .venv\Scripts folder (python, ruff, bandit) and Node.js on the
  PATH (Lab 16 Task 6). That includes the per-user Node.js that setup-windows.ps1 installs, which terminals in a
  VS Code that was already open before setup can't see yet.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\day6\start-kavericlaims-day6.ps1
  powershell -ExecutionPolicy Bypass -File .\day6\start-kavericlaims-day6.ps1 -Reset               # start again from a fresh copy
  powershell -ExecutionPolicy Bypass -File .\day6\start-kavericlaims-day6.ps1 -Reset -FromLab16    # start Lab 17 from the Lab 16 reference solution
  powershell -ExecutionPolicy Bypass -File .\day6\start-kavericlaims-day6.ps1 -Reset -FromLab17    # start Lab 18 from the Lab 17 reference solution
#>
param(
    [string]$Destination = (Join-Path ([Environment]::GetFolderPath("Desktop")) "kavericlaims-day6"),
    [switch]$Reset,
    [switch]$FromLab16,
    [switch]$FromLab17,
    [switch]$NoOpen
)
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $PSScriptRoot "kavericlaims"
$Lab16Solution = Join-Path $PSScriptRoot "lab16-consolidate-refactor\solution"
$Lab17Solution = Join-Path $PSScriptRoot "lab17-debug-tdd-sca\solution"
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
        Write-Host "Close the KaveriClaims VS Code window (File > Close Window), then run this command again." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Your previous copy was moved to $old"
}

Copy-Item $Source $Destination -Recurse
Get-ChildItem $Destination -Recurse -Directory -Include "__pycache__", ".pytest_cache", ".ruff_cache" | Remove-Item -Recurse -Force

$message = "KaveriClaims 2.0 starting point"
if ($FromLab16 -or $FromLab17) {
    Copy-Item (Join-Path $Lab16Solution "*") $Destination -Recurse -Force
    $message = "KaveriClaims after Lab 16 (reference solution)"
}
if ($FromLab17) {
    Copy-Item (Join-Path $Lab17Solution "*") $Destination -Recurse -Force
    $message = "KaveriClaims after Lab 17 (reference solution)"
}

# Node.js: the one on the PATH, or the per-user copy setup-windows.ps1 installs (a VS Code opened before setup can't see that one yet)
$NodeDir = $null
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCmd) {
    $NodeDir = Split-Path -Parent $nodeCmd.Source
} else {
    $installed = Get-ChildItem (Join-Path $env:LOCALAPPDATA "Programs\nodejs-lts") -Directory -Filter "node-v*-win-x64" -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending | Select-Object -First 1
    if ($installed) { $NodeDir = $installed.FullName }
}
$TerminalPath = (@($VenvScripts, $NodeDir) | Where-Object { $_ }) -join ";"

# Tell VS Code (and Copilot) which Python to use, turn on pytest in the Testing view, and add a debug configuration
$vscode = Join-Path $Destination ".vscode"
New-Item -ItemType Directory -Force $vscode | Out-Null
$settings = [ordered]@{
    "python.defaultInterpreterPath"       = $VenvPy
    "python.terminal.activateEnvironment" = $true
    "python.testing.pytestEnabled"        = $true
    "python.testing.unittestEnabled"      = $false
    "python.testing.pytestArgs"           = @("tests")
    "terminal.integrated.env.windows"     = [ordered]@{ "PATH" = "$TerminalPath;`${env:PATH}" }
}
# WriteAllText writes UTF-8 without a BOM
[IO.File]::WriteAllText((Join-Path $vscode "settings.json"), ($settings | ConvertTo-Json))
$launch = @'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Lab 17: team for E10 and E11",
            "type": "debugpy",
            "request": "launch",
            "module": "kavericlaims",
            "args": ["team", "--manager", "E10", "--manager", "E11", "--month", "2026-11"],
            "cwd": "${workspaceFolder}",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
'@
[IO.File]::WriteAllText((Join-Path $vscode "launch.json"), $launch)

[IO.File]::WriteAllText((Join-Path $Destination ".gitignore"), "__pycache__/`n*.pyc`n.venv/`n.pytest_cache/`n.ruff_cache/`n.coverage`nhtmlcov/`npayroll_*.csv`narchive/`n")

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
if ($NodeDir) {
    Write-Host "Node.js for Lab 16 Task 6: $NodeDir (on the PATH of every terminal in the new window)"
} else {
    Write-Host "Warning: Node.js not found. Lab 16 Task 6 needs it. Run setup\setup-windows.ps1 (it installs Node.js), then run this script again with -Reset." -ForegroundColor Yellow
}

Write-Host "`nKaveriClaims 2.0 copied to $Destination" -ForegroundColor Green
Write-Host "In the new window's terminal, activate the labs' Python and check the app runs:"
Write-Host "  & `"$RepoRoot\.venv\Scripts\Activate.ps1`"" -ForegroundColor Cyan
Write-Host "  python -m kavericlaims report --month 2026-11" -ForegroundColor Cyan
Write-Host "  python -m pytest" -ForegroundColor Cyan
Open-InCode $Destination
