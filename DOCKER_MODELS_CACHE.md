# Docker Models and Cache

This guide explains how model files are downloaded and persisted in Docker.

## How Cache Works

When cache root is selected, lama-cleaner configures both PyTorch and Hugging Face caches under that root.

Selection precedence at startup:

1. `--cache-dir`
2. `LAMA_CLEANER_CACHE_DIR`
3. `CACHE_DIR` (legacy)
4. persisted config file

That means this run option controls where model files are stored:

```bash
-e CACHE_DIR=/app/models
```

Recommended explicit startup argument:

```bash
python3 main.py --cache-dir /app/models --model lama --device=cpu --port=8080 --host=0.0.0.0
```

## Persist Models Between Runs

Use a bind mount or named volume for `/app/models`.

### Bind mount example

```bash
-v $(pwd)/models:/app/models
```

### Named volume example

```bash
-v lama_cleaner_models:/app/models
```

Without one of these, models are downloaded again after container removal.

## Preload Models

You can pre-download one or many models.

### Preload selected models

```bash
python3 main.py --model lama --preload-models lama,mat --preload-only
```

### Preload all supported models

```bash
python3 main.py --model lama --preload-models all --preload-only
```

You can run these commands in the container, with cache volume mounted.

## Stable Diffusion Token Notes

For `sd1.4`, first download requires a Hugging Face token unless `--sd-run-local` is used after initial download.

Examples and safer token passing approaches are in [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md) and [DOCKER_COMPOSE.md](DOCKER_COMPOSE.md).

## Cleanup

### Remove only container

```bash
docker rm -f <container_name_or_id>
```

### Remove cached models in bind-mounted folder

```bash
rm -rf ./models/*
```

### Remove a named Docker volume

```bash
docker volume rm lama_cleaner_models
```
