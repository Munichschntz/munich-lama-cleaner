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

If you are modifying this repository, install the local package in editable mode:

```powershell
pip uninstall -y lama-cleaner
pip install -e .
```

If you want a full reset + rebuild + reinstall flow, use the repo wrappers:

- CMD: `clean-rebuild.cmd`
- PowerShell: `./clean-rebuild.ps1`

These wrappers create/use `.venv311` and run a full clean rebuild with dependency resolution.

For run-only usage, install from PyPI instead:

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

You can also let lama-cleaner persist this automatically by launching once with:

```powershell
lama-cleaner --cache-dir "C:\lama-cleaner-models" --model=lama --device=cuda --port=8080 --host=127.0.0.1
```

The path is saved in a user config file and reused on next launches.

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

Start with GPU and explicit cache path:

```powershell
.\run-gpu.ps1 -CacheDir "D:\lama-cache"
```

Start with CPU:

```powershell
.\run-cpu.ps1
```

Use a different model or port:

```powershell
.\run-gpu.ps1 -Model mat -Port 8081
```

## 8.1 One-Command Clean Rebuild (Recommended for local code changes)

PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\clean-rebuild.ps1
```

CMD:

```cmd
clean-rebuild.cmd
```

This does all of the following in one run:

- create `.venv311` if missing
- clean untracked build/cache artifacts
- build a fresh wheel from current source
- reinstall `lama-cleaner` into `.venv311`

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
  - For local repo development reinstall: `pip install -e .`
  - For PyPI install reinstall: `pip install lama-cleaner`
- CUDA unavailable:
  - Check `nvidia-smi`
  - Run CPU mode to confirm baseline
- Slow first launch:
  - Normal while model files download
- `pip install` fails on Python 3.12 with `scikit-image==0.19.3` build errors:
  - Use Python 3.10/3.11 for full dependency installs
  - Run `clean-rebuild.cmd` or `./clean-rebuild.ps1` to rebuild in `.venv311`

For containerized setup instead, see [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md).