# Project Guidelines

## Code Style
- Keep Python changes small and consistent with existing modules in [lama_cleaner/](lama_cleaner/).
- Preserve the Flask + model-manager separation: avoid putting model-specific logic directly into request handlers.
- For frontend changes, follow existing TypeScript + React patterns in [lama_cleaner/app/src/](lama_cleaner/app/src/) and keep API calls inside adapters.
- Do not commit large unrelated refactors; this repository prefers focused, behavior-preserving edits.

## Architecture
- Entrypoint flow: [main.py](main.py) -> [lama_cleaner/__init__.py](lama_cleaner/__init__.py) -> [lama_cleaner/parse_args.py](lama_cleaner/parse_args.py) -> [lama_cleaner/server.py](lama_cleaner/server.py).
- Inference endpoint: POST /inpaint in [lama_cleaner/server.py](lama_cleaner/server.py).
- Model lifecycle and switching are owned by [lama_cleaner/model_manager.py](lama_cleaner/model_manager.py); model implementations live in [lama_cleaner/model/](lama_cleaner/model/).
- Frontend source is in [lama_cleaner/app/src/](lama_cleaner/app/src/); Flask serves built assets from [lama_cleaner/app/build/](lama_cleaner/app/build/).
- See [ARCHITECTURE.md](ARCHITECTURE.md) for full component boundaries and request flow.

## Build and Test
- Backend install for development: pip install -e .
- Backend run: lama-cleaner --model=lama --device=cpu --port=8080
- Backend tests (fast/safe): pytest lama_cleaner/tests/test_parse_args.py lama_cleaner/tests/test_runtime_settings.py
- Full model tests are heavy and may require GPU + model artifacts: pytest lama_cleaner/tests/test_model.py
- Frontend setup: cd lama_cleaner/app && yarn install
- Frontend checks: yarn check
- Frontend build for packaged backend: yarn build (or yarn build:win on Windows)
- After editing [lama_cleaner/app/src/](lama_cleaner/app/src/), rebuild [lama_cleaner/app/build/](lama_cleaner/app/build/) before validating end-to-end behavior.

## Conventions
- Prefer lazy model imports via [lama_cleaner/model_manager.py](lama_cleaner/model_manager.py) patterns; avoid eager imports of optional model dependencies.
- Keep request schema compatibility through [lama_cleaner/schema.py](lama_cleaner/schema.py) when adding or changing API options.
- When changing CLI flags or defaults, update parser behavior and tests together in [lama_cleaner/parse_args.py](lama_cleaner/parse_args.py) and [lama_cleaner/tests/test_parse_args.py](lama_cleaner/tests/test_parse_args.py).
- Package builds include frontend static assets via [setup.py](setup.py); do not remove the [lama_cleaner/app/build/](lama_cleaner/app/build/) packaging path.

## Pitfalls
- Python 3.12 can fail on scikit-image 0.19.3 during dependency resolution; prefer Python 3.10/3.11 for full local setup.
- On Windows with newer Node, use yarn build:win (OpenSSL legacy provider is required by react-scripts 4).
- Stable Diffusion sd1.4 may require Hugging Face access token on first download.

## Docs
- Main setup and usage: [README.md](README.md)
- Architecture details: [ARCHITECTURE.md](ARCHITECTURE.md)
- Windows native setup: [WINDOWS_NATIVE_SETUP.md](WINDOWS_NATIVE_SETUP.md)
- Docker setup and troubleshooting: [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md), [DOCKER_GPU_SETUP.md](DOCKER_GPU_SETUP.md), [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md), [DOCKER_MODELS_CACHE.md](DOCKER_MODELS_CACHE.md), [DOCKER_COMPOSE.md](DOCKER_COMPOSE.md)