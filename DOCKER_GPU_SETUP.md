# Docker GPU Setup

Use this guide before running lama-cleaner with `--device=cuda`.

## Host Requirements

- NVIDIA GPU with recent drivers installed on the host.
- Docker Engine 19.03+.
- NVIDIA Container Toolkit installed and configured for Docker.

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
