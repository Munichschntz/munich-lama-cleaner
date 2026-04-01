<h1 align="center">Lama Cleaner</h1>
<p align="center">A free and open-source inpainting tool powered by SOTA AI model.</p>

<p align="center">
  <a href="https://github.com/Sanster/lama-cleaner">
    <img alt="total download" src="https://pepy.tech/badge/lama-cleaner" />
  </a>
  <a href="https://pypi.org/project/lama-cleaner/">
    <img alt="version" src="https://img.shields.io/pypi/v/lama-cleaner" />
  </a>
  <a href="https://colab.research.google.com/drive/1e3ZkAJxvkK3uzaTGu91N9TvI_Mahs0Wb?usp=sharing">
    <img alt="Open in Colab" src="https://colab.research.google.com/assets/colab-badge.svg" />
  </a>
  <a href="https://www.buymeacoffee.com/Sanster"> 
    <img height="20px" src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Sanster" />
  </a>
</p>

![img](./assets/dark.jpg)

## Features

- Completely free and open-source
- Fully self-hosted
- Classical image inpainting algorithm powered by [cv2](https://docs.opencv.org/3.4/df/d3d/tutorial_py_inpainting.html)
- Multiple SOTA AI models
  1. [LaMa](https://github.com/saic-mdal/lama)
  1. [LDM](https://github.com/CompVis/latent-diffusion)
  1. [ZITS](https://github.com/DQiaole/ZITS_inpainting)
  1. [MAT](https://github.com/fenglinglwb/MAT)
  1. [FcF](https://github.com/SHI-Labs/FcF-Inpainting)
  1. [SD1.4](https://github.com/CompVis/stable-diffusion)
- Support CPU & GPU
- Various inpainting [strategy](#inpainting-strategy)
- Run as a desktop APP

## Usage

| Usage                  | Before                                        | After                                                          |
| ---------------------- | --------------------------------------------- | -------------------------------------------------------------- |
| Remove unwanted things | ![unwant_object2](./assets/unwant_object.jpg) | ![unwant_object2](./assets/unwant_object_clean.jpg)            |
| Remove unwanted person | ![unwant_person](./assets/unwant_person.jpg)  | ![unwant_person](./assets/unwant_person_clean.jpg)             |
| Remove Text            | ![text](./assets/unwant_text.jpg)             | ![text](./assets/unwant_text_clean.jpg)                        |
| Remove watermark       | ![watermark](./assets/watermark.jpg)          | ![watermark_clean](./assets/watermark_cleanup.jpg)             |
| Fix old photo          | ![oldphoto](./assets/old_photo.jpg)           | ![oldphoto_clean](./assets/old_photo_clean.jpg)                |
| Text Driven Inpainting | ![dog](./assets/dog.jpg)                      | Prompt: a fox sitting on a bench<br/> ![fox](./assets/fox.jpg) |

## Quick Start

```bash
pip install lama-cleaner

# Model will be downloaded automatically
lama-cleaner --model=lama --device=cpu --port=8080
# Lama Cleaner is now running at http://localhost:8080

# Optional: pre-download selected model weights before launch
lama-cleaner --preload-models lama,mat --model lama

# Optional: download model weights and exit (no server start)
lama-cleaner --preload-models all --preload-only

# Optional: choose and persist model cache root directory
lama-cleaner --cache-dir "D:/lama-cleaner-cache"

# Optional: set cache root via environment variable
LAMA_CLEANER_CACHE_DIR="$HOME/lama-cleaner-cache" lama-cleaner --model lama
```

Windows 11 without Docker: [Windows Native Setup](WINDOWS_NATIVE_SETUP.md)

Quick launch scripts (PowerShell): `run-gpu.ps1` and `run-cpu.ps1`

Available arguments:

| Name              | Description                                                                                                                   | Default  |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------| -------- |
| --model           | lama/ldm/zits/mat/fcf/sd1.4 See details in [Inpaint Model](#inpainting-model)                                                 | lama     |
| --preload-models  | Pre-download model weights before launch. Comma-separated model names or `all`                                                 |          |
| --preload-only    | Download selected model weights and exit without starting server. If no `--preload-models`, uses `--model`                    |          |
| --hf_access_token | stable-diffusion(sd) model need [huggingface access token](https://huggingface.co/docs/hub/security-tokens) to download model |          |
| --sd-run-local    | Once the model is downloaded, you can pass this arg and remove `--hf_access_token`                                            |          |
| --sd-disable-nsfw | Disable stable-diffusion NSFW checker.                                                                                        |          |
| --sd-cpu-textencoder | Always run stable-diffusion TextEncoder model on CPU.                                                                         |          |
| --device          | cuda or cpu                                                                                                                   | cuda     |
| --cache-dir       | Root directory for model caches (torch + huggingface). Persisted when set.                                                   |          |
| --port            | Port for backend flask web server                                                                                             | 8080     |
| --gui             | Launch lama-cleaner as a desktop application                                                                                  |          |
| --gui-size        | Set the window size for the application                                                                                       | 1600 1000 |
| --input           | Path to image you want to load by default                                                                                     | None     |
| --debug           | Enable debug mode for flask web server                                                                                        |          |

Cache directory precedence (highest to lowest):

1. `--cache-dir`
2. `LAMA_CLEANER_CACHE_DIR`
3. `CACHE_DIR` (legacy)
4. persisted config file (`~/.config/lama-cleaner/config.json` on Linux)

When a cache root is configured, lama-cleaner derives and exports these paths:

- `TORCH_HOME=<cache_root>/torch`
- `HF_HOME=<cache_root>/huggingface`
- `TRANSFORMERS_CACHE=<cache_root>/huggingface/transformers`
- `HUGGINGFACE_HUB_CACHE=<cache_root>/huggingface/hub`

## Inpainting Model

| Model | Description                                                                                                                                                                                                            | Config                                                                                                                                                                                                                                                                            |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| cv2   | :+1: No GPU is required, and for simple backgrounds, the results may even be better than AI models.                                                                                                                    |                                                                                                                                                                                                                                                                                   |
| LaMa  | :+1: Generalizes well on high resolutions(~2k)<br/>                                                                                                                                                                    |                                                                                                                                                                                                                                                                                   |
| LDM   | :+1: Possible to get better and more detail result <br/> :+1: The balance of time and quality can be achieved by adjusting `steps` <br/> :neutral_face: Slower than GAN model<br/> :neutral_face: Need more GPU memory | `Steps`: You can get better result with large steps, but it will be more time-consuming <br/> `Sampler`: ddim or [plms](https://arxiv.org/abs/2202.09778). In general plms can get [better results](https://github.com/Sanster/lama-cleaner/releases/tag/0.13.0) with fewer steps |
| ZITS  | :+1: Better holistic structures compared with previous methods <br/> :neutral_face: Wireframe module is **very** slow on CPU                                                                                           | `Wireframe`: Enable edge and line detect                                                                                                                                                                                                                                          |
| MAT   | TODO                                                                                                                                                                                                                   |                                                                                                                                                                                                                                                                                   |
| FcF   | :+1: Better structure and texture generation <br/> :neutral_face: Only support fixed size (512x512) input                                                                                                              |                                                                                                                                                                                                                                                                                   |
| SD1.4 | :+1: SOTA text-to-image diffusion model                                                                                                                                                                                |                                                                                                                                                                                                                                                                                   |

### Which Model Should I Use?

Use this quick guide when starting a new task:

- **Fast cleanup with low hardware requirements**: `cv2` (CPU friendly, best for simple backgrounds and watermark/text removal).
- **General purpose and stable quality**: `lama` (best default for most photos, good quality/speed balance).
- **Higher detail synthesis**: `ldm` (slower, better semantic fills, benefits from higher steps).
- **Structure-heavy scenes**: `zits` (good at preserving lines/geometry, slower especially on CPU).
- **Texture-focused holes**: `fcf` (works on 512x512 crops, strong texture quality).
- **Prompt-driven replacements**: `sd1.4` (best when you need to control generated content using text prompts).

In the settings panel, use **Quality presets** (`fast`, `balanced`, `best`) as a first pass:

- `fast`: fastest latency, lower detail.
- `balanced`: recommended default.
- `best`: slower but strongest quality.

For very large images, enable **Tiled Inference** in settings to reduce GPU memory pressure.

### LaMa vs LDM

| Original Image                                                                                                                            | LaMa                                                                                                                                                   | LDM                                                                                                                                                   |
| ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| ![photo-1583445095369-9c651e7e5d34](https://user-images.githubusercontent.com/3998421/156923525-d6afdec3-7b98-403f-ad20-88ebc6eb8d6d.jpg) | ![photo-1583445095369-9c651e7e5d34_cleanup_lama](https://user-images.githubusercontent.com/3998421/156923620-a40cc066-fd4a-4d85-a29f-6458711d1247.png) | ![photo-1583445095369-9c651e7e5d34_cleanup_ldm](https://user-images.githubusercontent.com/3998421/156923652-0d06c8c8-33ad-4a42-a717-9c99f3268933.png) |

### LaMa vs ZITS

| Original Image                                                                                                         | ZITS                                                                                                                       | LaMa                                                                                                                       |
| ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| ![zits_original](https://user-images.githubusercontent.com/3998421/180464918-eb13ebfb-8718-461c-9e8b-7f6d8bb7a84f.png) | ![zits_compare_zits](https://user-images.githubusercontent.com/3998421/180464914-4db722c9-047f-48fe-9bb4-916ba09eb5c6.png) | ![zits_compare_lama](https://user-images.githubusercontent.com/3998421/180464903-ffb5f770-4372-4488-ba76-4b4a8c3323f5.png) |

Image is from [ZITS](https://github.com/DQiaole/ZITS_inpainting) paper. I didn't find a good example to show the advantages of ZITS and let me know if you have a good example. There can also be possible problems with my code, if you find them, please let me know too!

### LaMa vs FcF

| Original Image                                                                                                    | Lama                                                                                                                   | FcF                                                                                                                   |
| ----------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| ![texture](https://user-images.githubusercontent.com/3998421/188305027-a4260545-c24e-4df7-9739-ac5dc3cae879.jpeg) | ![texture_lama](https://user-images.githubusercontent.com/3998421/188305024-2064ed3e-5af4-4843-ac10-7f9da71e15f8.jpeg) | ![texture_fcf](https://user-images.githubusercontent.com/3998421/188305006-a08d2896-a65f-43d5-b9a5-ef62c3129f0c.jpeg) |

## Inpainting Strategy

Lama Cleaner provides three ways to run inpainting model on images, you can change it in the settings dialog.

| Strategy     | Description                                                                                                                                    | VRAM                 |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| **Original** | Use the resolution of the original image                                                                                                       | :tada:               |
| **Resize**   | Resize the image to a smaller size before inpainting. Lama Cleaner will make sure that the area of the image outside the mask is not degraded. | :tada: :tada:        |
| **Crop**     | Crop masking area from the original image to do inpainting                                                                                     | :tada: :tada: :tada: |

## Download Model Manually

If you have problems downloading the model automatically when lama-cleaner start,
you can download it manually and place files under your configured cache root.

- If cache root is set (recommended):
  - checkpoints go in `<cache_root>/torch/hub/checkpoints/`
  - huggingface files go under `<cache_root>/huggingface/`
- If no cache root is set, `TORCH_HOME`/`HF_HOME` defaults are used by your Python environment.

- Github:
  - [LaMa](https://github.com/Sanster/models/releases/tag/add_big_lama)
  - [LDM](https://github.com/Sanster/models/releases/tag/add_ldm)
  - [ZITS](https://github.com/Sanster/models/releases/tag/add_zits)
  - [MAT](https://github.com/Sanster/models/releases/tag/add_mat)
  - [FcF](https://github.com/Sanster/models/releases/tag/add_fcf)
- Baidu:
  - https://pan.baidu.com/s/1vUd3BVqIpK6e8N_EA_ZJfw
  - password: flsu

## Troubleshooting

### Model download issues

- Set `--cache-dir` or `LAMA_CLEANER_CACHE_DIR` to a writable folder (`CACHE_DIR` is still supported as legacy).
- Pre-download model files into your checkpoint cache if auto-download is blocked.
- For `sd1.4`, pass `--hf_access_token` once to fetch private model artifacts.

### CUDA / GPU issues

- Verify CUDA visibility with `nvidia-smi`.
- If your GPU is memory constrained, switch to `lama` or `cv2`, lower resolution strategy, or enable tiled inference.
- Try `--device=cpu` to verify whether failures are CUDA-specific.

### Out of memory (OOM)

- Use `Resize` or `Crop` in high-resolution strategy.
- Enable tiled inference and reduce tile size.
- Lower `sdSteps`/`ldmSteps` or switch to `fast` preset.

### Slow performance

- Use `fast` quality preset.
- Disable ZITS wireframe for speed.
- Reduce image resolution or run on GPU.

## Benchmarking

The benchmark utility is in [lama_cleaner/benchmark.py](lama_cleaner/benchmark.py).

Example runs:

```bash
# Benchmark LaMa on GPU
python -m lama_cleaner.benchmark --model lama --device cuda --times 10

# Benchmark LDM on GPU
python -m lama_cleaner.benchmark --model ldm --device cuda --times 5

# Benchmark on CPU
python -m lama_cleaner.benchmark --model lama --device cpu --times 3
```

Recommended reporting format:

- Model name and device
- Image size
- Mean latency ± std
- CPU memory and (if available) GPU memory

This makes results comparable across machines and pull requests.

## Adding New Models (Extension Points)

To add a model cleanly:

1. Implement a new model class under `lama_cleaner/model/` by extending `InpaintModel` in [lama_cleaner/model/base.py](lama_cleaner/model/base.py).
2. Register it in `models` and `MODEL_CAPABILITIES` in [lama_cleaner/model_manager.py](lama_cleaner/model_manager.py).
3. Add any new request fields to [lama_cleaner/schema.py](lama_cleaner/schema.py).
4. If needed, parse new form fields in [lama_cleaner/server.py](lama_cleaner/server.py).
5. Add model-specific UI controls in [lama_cleaner/app/src/components/Settings/ModelSettingBlock.tsx](lama_cleaner/app/src/components/Settings/ModelSettingBlock.tsx).

This keeps backend inference, request validation, and frontend controls aligned.

## Development

Only needed if you plan to modify the frontend and recompile yourself.

### Frontend

Frontend code are modified from [cleanup.pictures](https://github.com/initml/cleanup.pictures), You can experience their
great online services [here](https://cleanup.pictures/).

- Install dependencies:`cd lama_cleaner/app/ && yarn`
- Start development server: `yarn start`
- Build: `yarn build`

### Publish

- Linux/macOS: `bash publish.sh`
- Windows PowerShell: `./publish.ps1`

## Docker

Run lama-cleaner in Docker. Models are downloaded automatically and should be persisted with a mounted cache directory.

### Build Docker image

```
docker build -f Dockerfile -t lamacleaner .
```

### Run Docker (cpu)

```
docker run -p 8080:8080 -e LAMA_CLEANER_CACHE_DIR=/app/models -v  $(pwd)/models:/app/models -v $(pwd):/app --rm lamacleaner \
python3 main.py --device=cpu --port=8080 --host=0.0.0.0
```

### Run Docker (gpu)

```
docker run --gpus all -p 8080:8080 -e LAMA_CLEANER_CACHE_DIR=/app/models -v $(pwd)/models:/app/models -v $(pwd):/app --rm lamacleaner \
python3 main.py --device=cuda --port=8080 --host=0.0.0.0
```

> `LAMA_CLEANER_CACHE_DIR` is the preferred environment variable. `CACHE_DIR` remains supported for backward compatibility.

Then open [http://localhost:8080](http://localhost:8080)

### Docker documentation

- [Docker Quickstart](DOCKER_QUICKSTART.md)
- [Docker GPU Setup](DOCKER_GPU_SETUP.md)
- [Docker Models and Cache](DOCKER_MODELS_CACHE.md)
- [Docker Troubleshooting](DOCKER_TROUBLESHOOTING.md)
- [Docker Compose](DOCKER_COMPOSE.md)
