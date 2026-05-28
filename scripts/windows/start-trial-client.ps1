param(
    [string]$Port = "8765",
    [string]$WorkspaceDir = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (Test-Path $VenvPython) {
    $Python = $VenvPython
} else {
    $Python = "python"
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
& $Python $ArgsList
