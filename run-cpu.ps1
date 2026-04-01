param(
    [string]$Model = "lama",
    [int]$Port = 8080,
    [string]$Host = "127.0.0.1",
    [string]$CacheDir = "C:\lama-cleaner-models"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Error "Virtual environment not found at .\.venv. Create it first: python -m venv .venv"
}

if (-not (Test-Path $CacheDir)) {
    New-Item -ItemType Directory -Force -Path $CacheDir | Out-Null
}

$env:TORCH_HOME = $CacheDir

. .\.venv\Scripts\Activate.ps1

Write-Host "Starting lama-cleaner (CPU) with model '$Model' on http://$Host`:$Port (cache: $CacheDir)"
lama-cleaner --cache-dir "$CacheDir" --model=$Model --device=cpu --port=$Port --host=$Host
