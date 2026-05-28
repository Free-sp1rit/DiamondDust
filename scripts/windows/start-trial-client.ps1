param(
    [string]$Port = "8765",
    [string]$WorkspaceDir = "",
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

$RuntimeDir = Join-Path $RepoRoot ".diamonddust-trial"
$LogDir = Join-Path $RuntimeDir "logs"
$SecretsDir = Join-Path $RuntimeDir "secrets"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
New-Item -ItemType Directory -Path $SecretsDir -Force | Out-Null
$LogFile = Join-Path $LogDir "trial-client-launch.log"
$SecretsEnvFile = Join-Path $SecretsDir "provider-secrets.env"

function Write-LaunchLog {
    param([string]$Message)
    Add-Content -Path $LogFile -Encoding UTF8 -Value $Message
}

function Invoke-PythonCandidate {
    param(
        [string[]]$Candidate,
        [string[]]$ExtraArgs
    )
    $executable = $Candidate[0]
    $baseArgs = @()
    if ($Candidate.Count -gt 1) {
        $baseArgs = $Candidate[1..($Candidate.Count - 1)]
    }
    & $executable @baseArgs @ExtraArgs
}

function Get-PythonCommand {
    $candidates = @(
        , @("py", "-3.13"),
        , @("py", "-3.12"),
        , @("py", "-3.11"),
        , @("py", "-3"),
        , @("python")
    )
    foreach ($candidate in $candidates) {
        Invoke-PythonCandidate -Candidate $candidate -ExtraArgs @(
            "-c",
            "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
        ) *> $null
        if ($LASTEXITCODE -eq 0) {
            Write-LaunchLog "Selected Python: $($candidate -join ' ')"
            return $candidate
        }
    }
    throw "DiamondDust trial client requires Python 3.11 or newer"
}

function Test-TrialPortAvailable {
    param([int]$CandidatePort)
    try {
        $listener = [System.Net.Sockets.TcpListener]::new(
            [System.Net.IPAddress]::Parse("127.0.0.1"),
            $CandidatePort
        )
        $listener.Start()
        $listener.Stop()
        return $true
    } catch {
        return $false
    }
}

function Get-TrialPort {
    param([string]$RequestedPort)
    if ($env:DIAMONDDUST_TRIAL_PORT) {
        Write-LaunchLog "Selected port from DIAMONDDUST_TRIAL_PORT: $env:DIAMONDDUST_TRIAL_PORT"
        return $env:DIAMONDDUST_TRIAL_PORT
    }
    $startPort = [int]$RequestedPort
    if ($startPort -ne 8765) {
        Write-LaunchLog "Selected requested port: $RequestedPort"
        return $RequestedPort
    }
    foreach ($candidate in 8765..8775) {
        if (Test-TrialPortAvailable $candidate) {
            Write-LaunchLog "Selected port: $candidate"
            return "$candidate"
        }
    }
    throw "Could not find an available port from 8765 through 8775"
}

Write-LaunchLog ""
Write-LaunchLog "==== DiamondDust trial client launch ===="
Write-LaunchLog "Repo root: $RepoRoot"

$VenvDir = Join-Path $RepoRoot ".venv"
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

try {
    if (Test-Path $VenvPython) {
        & $VenvPython -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >> $LogFile 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Existing .venv does not use Python 3.11 or newer. Delete $VenvDir and run the launcher again."
        }
        $Python = $VenvPython
    } else {
        $PythonCommand = Get-PythonCommand
        Write-Host "Creating local Python environment in $VenvDir ..."
        Write-LaunchLog "Creating local Python environment..."
        Invoke-PythonCandidate -Candidate $PythonCommand -ExtraArgs @(
            "-m",
            "venv",
            $VenvDir
        ) >> $LogFile 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python venv creation failed"
        }
        $Python = $VenvPython
        Write-Host "Installing DiamondDust trial dependencies ..."
        Write-LaunchLog "Installing DiamondDust trial dependencies..."
        & $Python -m pip install -e $RepoRoot >> $LogFile 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "DiamondDust dependency installation failed"
        }
    }
    $SelectedPort = Get-TrialPort $Port
} catch {
    Write-Host $_.Exception.Message
    Write-Host "Launch log: $LogFile"
    throw
}

$env:PYTHONPATH = Join-Path $RepoRoot "src"

$ArgsList = @(
    "-m",
    "diamonddust",
    "trial-client",
    "--root",
    $RepoRoot,
    "--port",
    $SelectedPort,
    "--secrets-env-file",
    $SecretsEnvFile
)

$FrontendDist = Join-Path $RepoRoot "frontend\trial-client\dist"
if (Test-Path (Join-Path $FrontendDist "index.html")) {
    $ArgsList += @(
        "--frontend-dist",
        $FrontendDist
    )
}

if ($WorkspaceDir.Trim()) {
    $WorkspaceRoot = Resolve-Path -Path $WorkspaceDir -ErrorAction SilentlyContinue
    if ($null -eq $WorkspaceRoot) {
        New-Item -ItemType Directory -Path $WorkspaceDir | Out-Null
        $WorkspaceRoot = Resolve-Path -Path $WorkspaceDir
    }
    $ArgsList += @(
        "--input-dir",
        (Join-Path $WorkspaceRoot "input-notes"),
        "--vault-root",
        (Join-Path $WorkspaceRoot "knowledge-vault"),
        "--feedback-dir",
        (Join-Path $WorkspaceRoot "feedback")
    )
}

Write-Host "DiamondDust trial client: http://127.0.0.1:$SelectedPort/"
Write-Host "Launch log: $LogFile"
Write-Host "API key file: $SecretsEnvFile"
if (-not $NoBrowser) {
    try {
        Start-Process "http://127.0.0.1:$SelectedPort/" | Out-Null
    } catch {
        Write-Host "Open http://127.0.0.1:$SelectedPort/ in your browser."
    }
}
& $Python $ArgsList
