# Docker Troubleshooting

## UI Not Reachable at localhost:8080

Checks:

- Confirm port mapping includes `-p 8080:8080`.
- Confirm app starts with `--host=0.0.0.0`.
- Confirm no local firewall blocks port 8080.

Quick check:

```bash
docker ps
```

Look for `0.0.0.0:8080->8080/tcp` in PORTS.

## CUDA Not Available / GPU Not Detected

Checks:

- Run `nvidia-smi` on host.
- Run Docker GPU test:

```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-runtime-ubuntu22.04 nvidia-smi
```

If the test fails, fix NVIDIA Container Toolkit setup first.

## Model Download Fails or Repeats Every Run

Checks:

- Confirm `CACHE_DIR` is set to `/app/models`.
- Confirm a persistent mount is attached to `/app/models`.
- Confirm folder permissions allow write access.

Example run:

```bash
docker run -p 8080:8080 \
  -e CACHE_DIR=/app/models \
  -v $(pwd)/models:/app/models \
  -v $(pwd):/app \
  --rm lamacleaner \
  python3 main.py --device=cpu --port=8080 --host=0.0.0.0
```

## `sd1.4` Token Errors

Typical error: token missing or invalid when using `sd1.4`.

Options:

- Pass `--hf_access_token` on first download.
- After first successful download, use `--sd-run-local` and omit token.

Safer token handling (avoid putting token in shell history):

```bash
export HF_ACCESS_TOKEN=hf_xxx

docker run -p 8080:8080 \
  -e CACHE_DIR=/app/models \
  -v $(pwd)/models:/app/models \
  -v $(pwd):/app \
  --rm lamacleaner \
  python3 main.py --model=sd1.4 --hf_access_token "$HF_ACCESS_TOKEN" --device=cuda --port=8080 --host=0.0.0.0
```

## Out of Memory (OOM)

Suggestions:

- Use `--device=cpu` to confirm issue is GPU-memory related.
- Start with `--model=lama` instead of heavier models.
- Use lower-resolution input images first.
- If using `sd1.4`, lower generation parameters in UI.

## Permission Denied on Mounted Models Folder

Fix ownership or permissions on host folder:

```bash
mkdir -p ./models
chmod 777 ./models
```

For stricter permissions, prefer setting ownership to your current user/group instead of `777`.
