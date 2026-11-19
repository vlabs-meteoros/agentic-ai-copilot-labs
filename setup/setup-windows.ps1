<#
.SYNOPSIS
  Setup of the lab environment on a Windows lab VM. Run it once on Day 1, and again
  at the start of each new day (after `git pull`) to install that day's new packages.

.DESCRIPTION
  1. Finds Python 3.10+ (installs Python 3.12 for the current user if missing;
     an existing old Python such as 3.6 is left untouched)
  2. Creates a virtual environment in .venv at the repository root
  3. Installs the lab packages (CPU PyTorch by default)
  4. Installs the VS Code Python + Jupyter extensions
  5. Registers a Jupyter kernel called "Python (agentic-ai-labs)"
  6. Creates .env from .env.example, or adds any new settings to an existing .env
  7. Optionally pre-downloads models and datasets (-Prefetch)
  8. Runs the environment check

.EXAMPLE
  # From the repository root, in a VS Code PowerShell terminal:
  powershell -ExecutionPolicy Bypass -File .\setup\setup-windows.ps1 -Prefetch

.PARAMETER Prefetch
  Download all models/datasets now (~2.5 GB) so the labs never wait on downloads.

.PARAMETER Cuda
  Install the CUDA build of PyTorch (only for VMs with an NVIDIA GPU).
#>
param(
    [switch]$Prefetch,
    [switch]$Cuda
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"   # makes Invoke-WebRequest much faster
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    [ OK ] $msg" -ForegroundColor Green }
function Write-Warn2($msg){ Write-Host "    [WARN] $msg" -ForegroundColor Yellow }

$PythonVersionToInstall = "3.12.10"

# ---------------------------------------------------------------- 1. Python
function Test-PythonExe($exe) {
    # Returns $true if $exe runs and is Python >= 3.10
    try {
        $out = & $exe -c "import sys; print('%d.%d' % sys.version_info[:2]); sys.exit(0 if sys.version_info >= (3,10) else 1)" 2>$null
        return ($LASTEXITCODE -eq 0)
    } catch { return $false }
}

function Find-Python {
    # Candidates in order of preference
    $candidates = @()
    foreach ($v in @("3.12", "3.13", "3.11", "3.10")) {
        $candidates += , @("py", "-$v")
    }
    foreach ($c in $candidates) {
        try {
            $path = & $c[0] $c[1] -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $path) { return $path.Trim() }
        } catch { }
    }
    $known = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python313\python.exe",
        "C:\Program Files\Python311\python.exe"
    )
    foreach ($p in $known) { if ((Test-Path $p) -and (Test-PythonExe $p)) { return $p } }
    $onPath = Get-Command python -ErrorAction SilentlyContinue
    if ($onPath -and (Test-PythonExe $onPath.Source)) { return $onPath.Source }
    return $null
}

Write-Step "Looking for Python 3.10 or newer"
$py = Find-Python
if (-not $py) {
    Write-Warn2 "No Python 3.10+ found (an older Python such as 3.6 may exist - it is not used)."
    $installed = $false
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "    Installing Python 3.12 with winget (current user)..."
        try {
            winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements | Out-Host
            $installed = $true
        } catch { Write-Warn2 "winget install failed: $_" }
    }
    $py = Find-Python
    if (-not $py) {
        Write-Host "    Downloading the Python $PythonVersionToInstall installer from python.org..."
        $installer = Join-Path $env:TEMP "python-$PythonVersionToInstall-amd64.exe"
        Invoke-WebRequest "https://www.python.org/ftp/python/$PythonVersionToInstall/python-$PythonVersionToInstall-amd64.exe" -OutFile $installer -UseBasicParsing
        Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=0 PrependPath=0 Include_launcher=1 Include_test=0" -Wait
        $py = Find-Python
    }
    if (-not $py) { throw "Python 3.10+ could not be installed automatically. Install Python 3.12 from python.org and re-run." }
}
Write-Ok "Using $py ($(& $py --version))"

# ------------------------------------------------------------- 2. venv
Write-Step "Creating virtual environment in .venv"
$venvPy = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if ((Test-Path $venvPy) -and (Test-PythonExe $venvPy)) {
    Write-Ok ".venv already exists - reusing it"
} else {
    & $py -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Failed to create .venv" }
    Write-Ok ".venv created"
}

# ---------------------------------------------------------- 3. packages
Write-Step "Installing packages (several minutes: PyTorch is ~200 MB)"
& $venvPy -m pip install --upgrade pip --quiet --disable-pip-version-check
if ($Cuda) {
    Write-Host "    Installing CUDA build of PyTorch..."
    & $venvPy -m pip install torch --index-url https://download.pytorch.org/whl/cu128
    if ($LASTEXITCODE -ne 0) { throw "CUDA PyTorch install failed" }
}
& $venvPy -m pip install -r requirements.txt --disable-pip-version-check
if ($LASTEXITCODE -ne 0) { throw "pip install failed - check the proxy/network and re-run" }
Write-Ok "Packages installed"

# ---------------------------------------------------- 4. VS Code extensions
Write-Step "Installing VS Code extensions (Python, Jupyter)"
$code = Get-Command code -ErrorAction SilentlyContinue
$codeCmd = if ($code) { $code.Source } else { $null }
if (-not $codeCmd) {
    foreach ($p in @("$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd",
                     "C:\Program Files\Microsoft VS Code\bin\code.cmd")) {
        if (Test-Path $p) { $codeCmd = $p; break }
    }
}
if ($codeCmd) {
    foreach ($ext in @("ms-python.python", "ms-toolsai.jupyter")) {
        & $codeCmd --install-extension $ext --force | Out-Null
        Write-Ok $ext
    }
} else {
    Write-Warn2 "VS Code command line not found - install 'Python' and 'Jupyter' from the Extensions view (Ctrl+Shift+X)."
}

# ------------------------------------------------------------ 5. kernel
Write-Step "Registering Jupyter kernel"
& $venvPy -m ipykernel install --user --name agentic-ai-labs --display-name "Python (agentic-ai-labs)" | Out-Null
Write-Ok "Kernel 'Python (agentic-ai-labs)' registered"

# --------------------------------------------------------------- 6. .env
Write-Step "Preparing .env"
if (Test-Path ".env") {
    # Keep every existing value; append only settings that are new in .env.example (e.g. Day 2 keys)
    $existing = @{}
    foreach ($line in Get-Content ".env") {
        if ($line -match '^\s*#?\s*([A-Z0-9_]+)\s*=') { $existing[$Matches[1]] = $true }
    }
    $added = @()
    foreach ($line in Get-Content ".env.example") {
        if ($line -match '^\s*#?\s*([A-Z0-9_]+)\s*=' -and -not $existing.ContainsKey($Matches[1])) {
            $added += $line
            $existing[$Matches[1]] = $true
        }
    }
    if ($added.Count -gt 0) {
        Add-Content ".env" ("`n# Added by setup-windows.ps1 on " + (Get-Date -Format "yyyy-MM-dd"))
        Add-Content ".env" $added
        Write-Ok (".env kept; added new settings: " + (($added | ForEach-Object { ($_ -split '=')[0].Trim('# ') }) -join ", "))
    } else {
        Write-Ok ".env already exists and is up to date - left unchanged"
    }
} else {
    Copy-Item ".env.example" ".env"
    Write-Ok ".env created - add the Azure values from your trainer before Lab 1"
}

# ----------------------------------------------------------- 7. prefetch
if ($Prefetch) {
    Write-Step "Pre-downloading models and datasets (~2.5 GB)"
    & $venvPy setup\prefetch_assets.py
}

# -------------------------------------------------------------- 8. check
Write-Step "Checking the environment"
& $venvPy setup\verify_env.py

Write-Host "`nSetup finished. In VS Code: open a lab notebook, click 'Select Kernel' (top right)" -ForegroundColor Cyan
Write-Host "and choose  .venv (Python 3.x)  or  'Python (agentic-ai-labs)'." -ForegroundColor Cyan