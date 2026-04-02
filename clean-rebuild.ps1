param(
    [string]$VenvPath = ".venv"
)

$ErrorActionPreference = "Stop"

$pythonExe = Join-Path $VenvPath "Scripts\python.exe"

$pythonSpec = $null

try {
    py -3.11 -c "import sys" | Out-Null
    $pythonSpec = "-3.11"
} catch {
}

if (-not $pythonSpec) {
    try {
        py -3.10 -c "import sys" | Out-Null
        $pythonSpec = "-3.10"
    } catch {
    }
}

if (-not $pythonSpec) {
    Write-Error "Python 3.10+ not found via py launcher."
    py -0p
}

if (-not (Test-Path $pythonExe)) {
    py $pythonSpec -m venv $VenvPath
}

& $pythonExe "scripts/clean_rebuild.py" --repo . --venv $VenvPath --with-deps

Write-Host ""
Write-Host "Done. Activate with: $VenvPath\Scripts\Activate.ps1"
