# Windows 11 Native Setup (No Docker)

This guide runs lama-cleaner directly on Windows 11 without Docker.

## Scope

- Run-only workflow (no frontend rebuild).
- NVIDIA GPU path first.
- CPU fallback included.

## 1. Install Prerequisites

Install these on Windows:

- Python 3.10 or 3.11 (64-bit)
- Git (optional, only needed if you clone source)
- Latest NVIDIA driver (for GPU mode)

Check versions in PowerShell:

```powershell
python --version
pip --version
nvidia-smi
```

If `nvidia-smi` fails, fix the NVIDIA driver first.

## 2. Create a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
```

If PowerShell blocks activation, run once as Administrator:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 3. Install lama-cleaner

For run-only usage, install from PyPI:

```powershell
pip install lama-cleaner
```

## 4. Optional: Set Persistent Model Cache Location

Create a cache folder and make it persistent for your user account:

```powershell
New-Item -ItemType Directory -Force -Path C:\lama-cleaner-models | Out-Null
[System.Environment]::SetEnvironmentVariable('TORCH_HOME', 'C:\lama-cleaner-models', 'User')
$env:TORCH_HOME = 'C:\lama-cleaner-models'
```

This avoids re-downloading models every run.

## 5. Verify CUDA from Python

```powershell
python -c "import torch; print('torch', torch.__version__, 'cuda_available', torch.cuda.is_available())"
```

If output shows `cuda_available False`, use CPU mode first and fix CUDA later.

## 6. First Run (GPU)

```powershell
lama-cleaner --model=lama --device=cuda --port=8080 --host=127.0.0.1
```

Then open:

- http://localhost:8080

## 7. CPU Fallback

```powershell
lama-cleaner --model=lama --device=cpu --port=8080 --host=127.0.0.1
```

## 8. One-Command Launch Scripts (Recommended)

This repository includes two PowerShell launchers:

- `run-gpu.ps1`
- `run-cpu.ps1`

They will:

- activate `.venv`
- ensure `TORCH_HOME` exists (defaults to `C:\lama-cleaner-models`)
- start lama-cleaner with sensible defaults

Start with GPU:

```powershell
.\run-gpu.ps1
```

Start with CPU:

```powershell
.\run-cpu.ps1
```

Use a different model or port:

```powershell
.\run-gpu.ps1 -Model mat -Port 8081
```

## 9. Preload Models (Optional)

Preload selected models:

```powershell
lama-cleaner --model=lama --preload-models lama,mat --preload-only
```

Preload all models:

```powershell
lama-cleaner --model=lama --preload-models all --preload-only
```

## 10. Stable Diffusion (`sd1.4`) Note

First download requires a Hugging Face token unless you already downloaded weights and use `--sd-run-local`.

Example first-time run:

```powershell
lama-cleaner --model=sd1.4 --hf_access_token hf_xxx --device=cuda --port=8080 --host=127.0.0.1
```

After model files exist locally:

```powershell
lama-cleaner --model=sd1.4 --sd-run-local --device=cuda --port=8080 --host=127.0.0.1
```

## 11. Common Issues

- `lama-cleaner` not found:
  - Reactivate venv: `.\.venv\Scripts\Activate.ps1`
  - Reinstall: `pip install lama-cleaner`
- CUDA unavailable:
  - Check `nvidia-smi`
  - Run CPU mode to confirm baseline
- Slow first launch:
  - Normal while model files download

For containerized setup instead, see [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md).