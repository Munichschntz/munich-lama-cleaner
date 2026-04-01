# Docker Quickstart

This guide helps you run lama-cleaner in Docker on CPU or GPU.

## Prerequisites

- Docker Engine installed and running.
- A terminal opened at the repository root.
- For GPU mode: complete the host setup in [DOCKER_GPU_SETUP.md](DOCKER_GPU_SETUP.md).

## Build Image

```bash
docker build -f Dockerfile -t lamacleaner .
```

## Run on CPU

```bash
docker run -p 8080:8080 \
  -e CACHE_DIR=/app/models \
  -v $(pwd)/models:/app/models \
  -v $(pwd):/app \
  --rm lamacleaner \
  python3 main.py --device=cpu --port=8080 --host=0.0.0.0
```

## Run on GPU

```bash
docker run --gpus all -p 8080:8080 \
  -e CACHE_DIR=/app/models \
  -v $(pwd)/models:/app/models \
  -v $(pwd):/app \
  --rm lamacleaner \
  python3 main.py --device=cuda --port=8080 --host=0.0.0.0
```

## Open the App

Open http://localhost:8080

## First Run Notes

- The first start can take longer because model files are downloaded.
- Keep the models volume mount so downloads are reused between runs.
- In Docker, `--host=0.0.0.0` is required so the app is reachable outside the container.

## Next

- GPU prerequisites and checks: [DOCKER_GPU_SETUP.md](DOCKER_GPU_SETUP.md)
- Model cache details and preloading: [DOCKER_MODELS_CACHE.md](DOCKER_MODELS_CACHE.md)
- Common failure fixes: [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md)
- Compose workflow: [DOCKER_COMPOSE.md](DOCKER_COMPOSE.md)
