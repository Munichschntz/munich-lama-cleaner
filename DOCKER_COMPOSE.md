# Docker Compose

This guide shows a Compose setup for CPU mode and an optional GPU profile.

## Compose File

Create a `compose.yaml` in the project root:

```yaml
services:
  lama-cleaner:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      CACHE_DIR: /app/models
    volumes:
      - ./models:/app/models
      - ./:/app
    command: >
      python3 main.py --device=cpu --port=8080 --host=0.0.0.0
    restart: unless-stopped

  lama-cleaner-gpu:
    profiles: ["gpu"]
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      CACHE_DIR: /app/models
      HF_ACCESS_TOKEN: ${HF_ACCESS_TOKEN:-}
    volumes:
      - ./models:/app/models
      - ./:/app
    command: >
      python3 main.py --device=cuda --port=8080 --host=0.0.0.0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped
```

## Start CPU Service

```bash
docker compose up --build
```

## Start GPU Service

```bash
HF_ACCESS_TOKEN=hf_xxx docker compose --profile gpu up --build lama-cleaner-gpu
```

If your environment uses an older Compose implementation, GPU reservation syntax may vary. In that case, use plain `docker run --gpus all` from [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md).

## Stop Services

```bash
docker compose down
```

## Notes

- Keep the `./models:/app/models` mount to persist model downloads.
- Keep `--host=0.0.0.0` so the UI is reachable on the host.
- Open http://localhost:8080 after startup.
