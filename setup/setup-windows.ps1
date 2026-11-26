<#
.SYNOPSIS
  Setup of the lab environment on a Windows lab VM. Run it once on Day 1, and again
  at the start of each new day (after `git pull`) to install that day's new packages.

.DESCRIPTION
  1. Finds Python 3.10+ (installs Python 3.12 for the current user if missing;
     an existing old Python such as 3.6 is left untouched)
  2. Creates a virtual environment in .venv at the repository root
  3. Installs the lab packages (CPU PyTorch by default). If .venv is Python 3.10, Spec Kit (Day 7), which needs
     Python 3.11+, goes into its own small environment, .speckit-venv (Python 3.12 is installed for the current user if needed)
  4. Finds Node.js 18+ (installs Node.js LTS for the current user if missing: Days 6-7)
  5. Installs Garnet, a Redis-compatible server, and the .NET 10 runtime it needs, for the current user (Day 8)
  6. Installs the VS Code Python + Jupyter extensions
  7. Registers a Jupyter kernel called "Python (agentic-ai-labs)"
  8. Creates .env from .env.example, or adds any new settings to an existing .env
  9. Optionally pre-downloads models and datasets (-Prefetch)
 10. Runs the environment check

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
# Node.js LTS installed per user when no Node.js 18+ is found (Day 6 Lab 16, Day 7 Lab 19). Checksum from nodejs.org/dist/v26.13.1/SHASUMS256.txt
$NodeVersionToInstall = "26.13.1"
$NodeZipSha256 = "e2edda75bfb089654705cf65a13b58933bfd5f57148e8ebda916f58a2474f1f7"
# Garnet (Day 8 Lab 22): github.com/microsoft/garnet release v2.2.14, win-x64-based-readytorun.zip, and the .NET 10 runtime it runs on.
# Checksums: the release's SHA-256 digest; builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json (SHA-512)
$GarnetVersion = "2.2.14"
$GarnetZipSha256 = "8d7a99ab34fce4ecdb6c63b54db03407fd442ac083514c752fe98328897e384a"
$DotnetRuntimeVersion = "10.0.15"
$DotnetZipSha512 = "06f0bedd59ae4ac722ada805a6d6bbf605bcdc790c71f59b7003878072902b5cde5dec8c40c0baa81192660d4748e9d79afdbdcb0c0ea9d6b821d0a044c4c6dd"

# ---------------------------------------------------------------- 1. Python
function Test-PythonExe($exe, $MinMinor = 10) {
    # Returns $true if $exe runs and is Python >= 3.$MinMinor
    try {
        $out = & $exe -c "import sys; print('%d.%d' % sys.version_info[:2]); sys.exit(0 if sys.version_info >= (3,$MinMinor) else 1)" 2>$null
        return ($LASTEXITCODE -eq 0)
    } catch { return $false }
}

function Find-Python($MinMinor = 10) {
    # Candidates in order of preference (3.$MinMinor or newer)
    $candidates = @()
    foreach ($v in @("3.12", "3.13", "3.11", "3.10")) {
        if ([int]($v.Split(".")[1]) -ge $MinMinor) { $candidates += , @("py", "-$v") }
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
    foreach ($p in $known) { if ((Test-Path $p) -and (Test-PythonExe $p $MinMinor)) { return $p } }
    $onPath = Get-Command python -ErrorAction SilentlyContinue
    if ($onPath -and (Test-PythonExe $onPath.Source $MinMinor)) { return $onPath.Source }
    return $null
}

function Install-Python312 {
    # Python 3.12 for the current user: winget first, then the python.org installer. Returns the python.exe found afterwards, or $null
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "    Installing Python 3.12 with winget (current user)..."
        try {
            winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements | Out-Host
        } catch { Write-Warn2 "winget install failed: $_" }
    }
    $found = Find-Python 12
    if (-not $found) {
        Write-Host "    Downloading the Python $PythonVersionToInstall installer from python.org..."
        $installer = Join-Path $env:TEMP "python-$PythonVersionToInstall-amd64.exe"
        Invoke-WebRequest "https://www.python.org/ftp/python/$PythonVersionToInstall/python-$PythonVersionToInstall-amd64.exe" -OutFile $installer -UseBasicParsing
        Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=0 PrependPath=0 Include_launcher=1 Include_test=0" -Wait
        $found = Find-Python 12
    }
    return $found
}

Write-Step "Looking for Python 3.10 or newer"
$py = Find-Python
if (-not $py) {
    Write-Warn2 "No Python 3.10+ found (an older Python such as 3.6 may exist - it is not used)."
    $py = Install-Python312
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

# Spec Kit (Day 7 Lab 19) needs Python 3.11+. requirements.txt puts it in .venv when .venv is 3.11+; a 3.10 .venv skips it,
# so Spec Kit gets its own small environment, .speckit-venv. day7\start-kaverirooms.ps1 puts its Scripts folder on the PATH.
& $venvPy -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Step "Spec Kit needs Python 3.11+ and .venv is $(& $venvPy --version): setting it up in .speckit-venv (Day 7 Lab 19)"
    try {
        $specPy = Join-Path $RepoRoot ".speckit-venv\Scripts\python.exe"
        if (-not ((Test-Path $specPy) -and (Test-PythonExe $specPy 11))) {
            $py311 = Find-Python 11
            if (-not $py311) { $py311 = Install-Python312 }
            if (-not $py311) { throw "Python 3.11+ could not be installed (python.org or winget may be blocked)" }
            & $py311 -m venv --clear .speckit-venv
            if ($LASTEXITCODE -ne 0) { throw "could not create .speckit-venv with $py311" }
        }
        & $specPy -m pip install --upgrade pip --quiet --disable-pip-version-check
        & $specPy -m pip install "specify-cli>=1.4,<2" --quiet --disable-pip-version-check
        if ($LASTEXITCODE -ne 0) { throw "pip install specify-cli failed - check the proxy/network" }
        Write-Ok "Spec Kit installed in .speckit-venv ($(& $specPy --version))"
    } catch {
        Write-Warn2 "Spec Kit could not be set up: $_"
        Write-Warn2 "Day 7 Lab 19 needs it: ask your trainer."
    }
}

# ------------------------------------------------------------- 4. Node.js
function Get-NodeMajor {
    # Major version of the 'node' on the PATH (for example 22), or 0 if there's none
    try {
        $v = & node --version 2>$null
        if ($v -match '^v(\d+)') { return [int]$Matches[1] }
    } catch { }
    return 0
}

Write-Step "Looking for Node.js 18 or newer (Day 6 Lab 16, Day 7 Lab 19)"
if ((Get-NodeMajor) -ge 18) {
    Write-Ok "Using Node.js $(node --version)"
} else {
    $nodeHome = Join-Path $env:LOCALAPPDATA "Programs\nodejs-lts"
    $nodeDir = Join-Path $nodeHome "node-v$NodeVersionToInstall-win-x64"
    $nodeExe = Join-Path $nodeDir "node.exe"
    if (-not (Test-Path $nodeExe)) {
        Write-Host "    Downloading Node.js $NodeVersionToInstall (about 35 MB) from nodejs.org, for the current user (no admin rights needed)..."
        try {
            $zip = Join-Path $env:TEMP "node-v$NodeVersionToInstall-win-x64.zip"
            Invoke-WebRequest "https://nodejs.org/dist/v$NodeVersionToInstall/node-v$NodeVersionToInstall-win-x64.zip" -OutFile $zip -UseBasicParsing
            $hash = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
            if ($hash -ne $NodeZipSha256) { throw "the download's SHA-256 checksum doesn't match ($hash)" }
            New-Item -ItemType Directory -Force $nodeHome | Out-Null
            Expand-Archive $zip -DestinationPath $nodeHome -Force
            Remove-Item $zip -Force
        } catch {
            Write-Warn2 "Node.js could not be installed: $_"
        }
    }
    if (Test-Path $nodeExe) {
        # Add it to the user's PATH (for new terminals) and to this session's PATH (for the check below)
        $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if (-not $userPath) { $userPath = "" }
        if (-not (($userPath -split ";") -contains $nodeDir)) {
            [Environment]::SetEnvironmentVariable("Path", (($userPath.TrimEnd(";") + ";" + $nodeDir).TrimStart(";")), "User")
        }
        $env:Path = "$nodeDir;$env:Path"
        Write-Ok "Node.js $(& $nodeExe --version) installed in $nodeDir. Open a NEW terminal (or restart VS Code) to use 'node'."
    } else {
        Write-Warn2 "No Node.js 18+. Day 6 Lab 16 Task 6 and Day 7 Lab 19 need it: ask your trainer (nodejs.org may be blocked)."
    }
}

# ---------------------------------------------------- 5. Garnet (Day 8)
function Get-Download($url, $file, $algorithm, $expected) {
    # Download $url to $file and check its checksum; throws if it doesn't match
    Invoke-WebRequest $url -OutFile $file -UseBasicParsing
    $hash = (Get-FileHash $file -Algorithm $algorithm).Hash.ToLower()
    if ($hash -ne $expected) { Remove-Item $file -Force; throw "the $algorithm checksum of $url doesn't match ($hash)" }
}

Write-Step "Garnet, a Redis-compatible server, and the .NET 10 runtime (Day 8 Lab 22)"
$garnetDir = Join-Path $env:LOCALAPPDATA "Programs\garnet\$GarnetVersion"
$garnetExe = Join-Path $garnetDir "net10.0\GarnetServer.exe"
$dotnetDir = Join-Path $env:LOCALAPPDATA "Programs\dotnet10"
$machineDotnet10 = Test-Path (Join-Path $env:ProgramFiles "dotnet\shared\Microsoft.NETCore.App\10.*")
$userDotnet10 = Test-Path (Join-Path $dotnetDir "shared\Microsoft.NETCore.App\10.*")
try {
    if (-not (Test-Path $garnetExe)) {
        Write-Host "    Downloading Garnet $GarnetVersion (about 30 MB) from github.com, for the current user (no admin rights needed)..."
        $zip = Join-Path $env:TEMP "garnet-$GarnetVersion-win-x64.zip"
        Get-Download "https://github.com/microsoft/garnet/releases/download/v$GarnetVersion/win-x64-based-readytorun.zip" $zip "SHA256" $GarnetZipSha256
        New-Item -ItemType Directory -Force $garnetDir | Out-Null
        Expand-Archive $zip -DestinationPath $garnetDir -Force
        Remove-Item $zip -Force
    }
    if (-not ($machineDotnet10 -or $userDotnet10)) {
        Write-Host "    Downloading the .NET $DotnetRuntimeVersion runtime (about 35 MB) from builds.dotnet.microsoft.com, for the current user..."
        $zip = Join-Path $env:TEMP "dotnet-runtime-$DotnetRuntimeVersion-win-x64.zip"
        Get-Download "https://builds.dotnet.microsoft.com/dotnet/Runtime/$DotnetRuntimeVersion/dotnet-runtime-$DotnetRuntimeVersion-win-x64.zip" $zip "SHA512" $DotnetZipSha512
        New-Item -ItemType Directory -Force $dotnetDir | Out-Null
        Expand-Archive $zip -DestinationPath $dotnetDir -Force
        Remove-Item $zip -Force
    }
    if (Test-Path $garnetExe) {
        $runtime = if ($machineDotnet10) { "the machine's .NET 10" } else { "the .NET runtime in $dotnetDir" }
        Write-Ok "Garnet $GarnetVersion in $garnetDir (runs on $runtime). Start it with day8\start-garnet.ps1"
    }
} catch {
    Write-Warn2 "Garnet could not be installed: $_"
    Write-Warn2 "Day 8 Lab 22 needs it: ask your trainer (github.com release downloads or builds.dotnet.microsoft.com may be blocked)."
}

# ---------------------------------------------------- 6. VS Code extensions
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

# ------------------------------------------------------------ 7. kernel
Write-Step "Registering Jupyter kernel"
& $venvPy -m ipykernel install --user --name agentic-ai-labs --display-name "Python (agentic-ai-labs)" | Out-Null
Write-Ok "Kernel 'Python (agentic-ai-labs)' registered"

# --------------------------------------------------------------- 8. .env
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

# ----------------------------------------------------------- 9. prefetch
if ($Prefetch) {
    Write-Step "Pre-downloading models and datasets (~2.5 GB)"
    & $venvPy setup\prefetch_assets.py
}

# ------------------------------------------------------------- 10. check
Write-Step "Checking the environment"
& $venvPy setup\verify_env.py

Write-Host "`nSetup finished. In VS Code: open a lab notebook, click 'Select Kernel' (top right)" -ForegroundColor Cyan
Write-Host "and choose  .venv (Python 3.x)  or  'Python (agentic-ai-labs)'." -ForegroundColor Cyan