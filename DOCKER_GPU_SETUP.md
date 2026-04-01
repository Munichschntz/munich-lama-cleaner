# Docker GPU Setup

Use this guide before running lama-cleaner with `--device=cuda`.

## Host Requirements

- NVIDIA GPU with recent drivers installed on the host.
- Docker Engine 19.03+.
- NVIDIA Container Toolkit installed and configured for Docker.

## Install NVIDIA Container Toolkit (Ubuntu/Debian)

Run these commands on the host:

```bash
sudo apt-get update
sudo apt-get install -y curl gpg

distribution=$(. /etc/os-release; echo ${ID}${VERSION_ID})
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

If your exact distro version is not listed by NVIDIA, use the nearest supported Ubuntu/Debian repository from the official NVIDIA Container Toolkit documentation.

## Verify Host GPU

```bash
nvidia-smi
```

If this fails, fix host driver installation first.

## Verify Docker GPU Access

```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-runtime-ubuntu22.04 nvidia-smi
```

If this command shows your GPU, Docker GPU passthrough is working.

## Run lama-cleaner with GPU

```bash
docker run --gpus all -p 8080:8080 \
  -e CACHE_DIR=/app/models \
  -v $(pwd)/models:/app/models \
  -v $(pwd):/app \
  --rm lamacleaner \
  python3 main.py --device=cuda --port=8080 --host=0.0.0.0
```

## Optional: Preload Models

You can pre-download model files before regular usage:

```bash
docker run --gpus all \
  -e CACHE_DIR=/app/models \
  -v $(pwd)/models:/app/models \
  -v $(pwd):/app \
  --rm lamacleaner \
  python3 main.py --model lama --preload-models lama,mat --preload-only
```

## If It Still Fails

See [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md), especially the CUDA and OOM sections.
