param(
    [string]$Port = "8765",
    [string]$WorkspaceDir = "",
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$VenvDir = Join-Path $RepoRoot ".venv"
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (Test-Path $VenvPython) {
    $Python = $VenvPython
} else {
    Write-Host "Creating local Python environment in $VenvDir ..."
    & python -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        throw "Python venv creation failed"
    }
    $Python = $VenvPython
    Write-Host "Installing DiamondDust trial dependencies ..."
    & $Python -m pip install -e $RepoRoot
    if ($LASTEXITCODE -ne 0) {
        throw "DiamondDust dependency installation failed"
    }
}

$env:PYTHONPATH = Join-Path $RepoRoot "src"

$ArgsList = @(
    "-m",
    "diamonddust",
    "trial-client",
    "--root",
    $RepoRoot,
    "--port",
    $Port
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

Write-Host "DiamondDust trial client: http://127.0.0.1:$Port/"
if (-not $NoBrowser) {
    try {
        Start-Process "http://127.0.0.1:$Port/" | Out-Null
    } catch {
        Write-Host "Open http://127.0.0.1:$Port/ in your browser."
    }
}
& $Python $ArgsList
