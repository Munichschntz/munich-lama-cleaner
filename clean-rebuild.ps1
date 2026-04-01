param(
    [string]$VenvPath = ".venv311"
)

$ErrorActionPreference = "Stop"

$pythonExe = Join-Path $VenvPath "Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    py -3.11 -m venv $VenvPath
}

& $pythonExe "scripts/clean_rebuild.py" --repo . --venv $VenvPath --with-deps

Write-Host ""
Write-Host "Done. Activate with: $VenvPath\Scripts\Activate.ps1"
