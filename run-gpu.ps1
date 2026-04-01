param(
    [string]$Model = "lama",
    [int]$Port = 8080,
    [string]$Host = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Error "Virtual environment not found at .\.venv. Create it first: python -m venv .venv"
}

if (-not $env:TORCH_HOME) {
    $env:TORCH_HOME = "C:\lama-cleaner-models"
}

if (-not (Test-Path $env:TORCH_HOME)) {
    New-Item -ItemType Directory -Force -Path $env:TORCH_HOME | Out-Null
}

. .\.venv\Scripts\Activate.ps1

Write-Host "Starting lama-cleaner (GPU) with model '$Model' on http://$Host`:$Port"
lama-cleaner --model=$Model --device=cuda --port=$Port --host=$Host
