# Architecture

This repository is a self-hosted image inpainting application with a Python backend and a React frontend.
The backend owns model lifecycle, image preprocessing, and inference. The frontend provides the editor,
collects masks and settings, and renders results.

## High-Level Structure

- `main.py`: minimal executable entrypoint.
- `lama_cleaner/__init__.py`: application startup wrapper.
- `lama_cleaner/parse_args.py`: CLI parsing and runtime options.
- `lama_cleaner/runtime_settings.py`: cache directory resolution and environment setup.
- `lama_cleaner/server.py`: Flask API, model switching, request handling, and static app serving.
- `lama_cleaner/model_manager.py`: model registry, lazy imports, active model switching, capability lookup.
- `lama_cleaner/model/`: concrete model implementations and the shared inpainting base class.
- `lama_cleaner/helper.py`: image decode, normalization, resizing, padding, and mask box extraction.
- `lama_cleaner/schema.py`: typed request configuration shared across models.
- `lama_cleaner/app/src/`: React frontend, editor UI, settings state, and API adapters.

## Runtime Startup Flow

The process starts in `main.py`, which calls `lama_cleaner.entry_point()`.

Startup sequence:

1. `parse_args()` reads CLI flags such as model name, device, port, GUI mode, and cache configuration.
2. `configure_cache_settings()` derives cache paths and exports `TORCH_HOME`, `HF_HOME`, and related environment variables when a cache root is configured.
3. `server.main(args)` creates the Flask app runtime, instantiates a `ModelManager`, and optionally preloads selected models.
4. Flask serves both the API endpoints and the built frontend assets from `lama_cleaner/app/build`.

This keeps deployment simple: one Python process owns both the UI and the inference server.

## Frontend and Backend Split

### Frontend

The React app under `lama_cleaner/app/src` is responsible for:

- loading the initial image
- providing the drawing canvas for the inpainting mask
- storing settings in Recoil state
- calling backend endpoints to inpaint images or switch models
- rendering the returned image history in the editor

Important frontend files:

- `lama_cleaner/app/src/App.tsx`: top-level shell and workspace selection.
- `lama_cleaner/app/src/components/Workspace.tsx`: model synchronization and settings dialog flow.
- `lama_cleaner/app/src/components/Editor/Editor.tsx`: mask drawing, request triggering, and render history.
- `lama_cleaner/app/src/adapters/inpainting.ts`: request serialization for `/inpaint` and model endpoints.
- `lama_cleaner/app/src/store/Atoms.tsx`: global settings, per-model defaults, cropper state, and inpainting state.

### Backend

The Flask backend in `lama_cleaner/server.py` is responsible for:

- decoding uploaded images and masks
- translating form fields into a validated `Config`
- reporting progress and current status
- routing requests to the active inpainting model
- switching models at runtime
- encoding and returning the final image

Important API endpoints:

- `POST /inpaint`: run one inpainting request
- `GET /model`: report the current model
- `POST /model`: switch to another model
- `GET /model_downloaded/<name>`: check model availability when supported
- `GET /model_capabilities`: expose model metadata for the UI
- `GET /server_status`: expose progress and server state

## How Inpainting Works

The inpainting flow is built around a stable contract:

- input image
- binary or grayscale mask
- a typed `Config` containing strategy and model-specific parameters
- a model implementation that returns a BGR image of the same size as its input

### Request Path

1. The editor draws the mask on a hidden canvas.
2. The frontend adapter converts the mask canvas to a blob and builds a `FormData` payload.
3. The payload includes the source image, the mask, and the current settings such as:
   - HD strategy
   - crop margins and resize limits
   - LDM sampler and steps
   - Stable Diffusion prompt, sampler, strength, and seed
   - OpenCV radius and algorithm
   - optional tiling settings
4. The frontend sends the request to `POST /inpaint`.

### Server-Side Request Handling

Inside `server.py`, the `/inpaint` handler performs the following steps:

1. Validate that both `image` and `mask` files are present.
2. Decode the image and optional alpha channel with `load_img()`.
3. Read form fields and build a `Config` object from `schema.py`.
4. Apply a quality preset, which adjusts some model-specific defaults for LDM and Stable Diffusion.
5. Resize the input image and mask to the requested `sizeLimit` when needed.
6. Call the active model through `ModelManager`.
7. Reattach the original alpha channel if the uploaded image had one.
8. Encode the result and return it as an image response.

The server also returns the effective seed in the `X-Seed` response header so the UI can keep Stable Diffusion runs reproducible.

## Shared Inpainting Abstraction

Most of the execution logic is centralized in `lama_cleaner/model/base.py`.
This is the core architectural idea in the repository.

Each model subclass only needs to implement:

- `init_model()`
- `is_downloaded()`
- `forward()`

The base class handles everything around raw inference.

### Padding and Size Constraints

Different models require different input shapes. The base class pads the image and mask with `pad_img_to_modulo()` so the model receives a valid shape.

Examples:

- LaMa uses `pad_mod = 8`
- LDM uses `pad_mod = 32`
- Stable Diffusion uses `pad_mod = 64` and `min_size = 512`
- OpenCV uses `pad_mod = 1`

After inference, the padded output is cropped back to the original dimensions.

### Preserving Unmasked Pixels

After each model returns an inpainted image, the base class copies original pixels back into all unmasked positions.
This means the framework guarantees that only masked regions are modified, even if the raw model output changes more than it should.

### HD Strategies

The repository supports three high-resolution strategies through `Config.hd_strategy`:

- `Original`: run on the full image as-is.
- `Resize`: downscale before inference, then upscale and paste only masked pixels back.
- `Crop`: find bounding boxes around masked regions, expand them with a margin, inpaint locally, then paste the crops back.

The crop logic uses `boxes_from_mask()` from `helper.py`, which extracts bounding boxes from external mask contours.

### Tiled Inference

For large images, the base class can split the image into overlapping tiles and only process tiles that contain masked pixels.
This reduces peak memory usage while still preserving local detail where the mask exists.

## Model Lifecycle

`ModelManager` in `lama_cleaner/model_manager.py` is the single runtime owner of the active model.

Its responsibilities are:

- mapping model names to implementation classes
- lazy-importing optional model modules
- instantiating models on demand
- switching models without restarting the server
- exposing model capabilities to the frontend
- keeping a small cache and evicting inactive heavyweight models

The lazy import design is important because some model families have optional dependencies. It prevents unrelated models from failing at process startup.

## Model-Specific Inpainting Behavior

### LaMa

File: `lama_cleaner/model/lama.py`

LaMa is the simplest deep-learning path in this repository.

Flow:

1. Load a TorchScript checkpoint from cache or download it.
2. Normalize image and mask into channel-first tensors in `[0, 1]`.
3. Binarize the mask.
4. Run a single forward pass.
5. Convert the result back to a BGR image.

Architecturally, LaMa is a direct feed-forward inpainting model. It relies heavily on the shared base class for resolution strategy and compositing.

### LDM

File: `lama_cleaner/model/ldm.py`

LDM is a latent diffusion inpainting implementation that loads three TorchScript artifacts:

- an encoder
- a decoder
- a diffusion model

Flow:

1. Normalize the image and binarize the mask.
2. Compute a masked image by zeroing the masked area.
3. Encode the masked image into latent space.
4. Resize the mask to latent resolution and concatenate it to the conditioning tensor.
5. Sample the latent representation with DDIM or PLMS.
6. Decode the latent sample back into image space.

Compared with LaMa, LDM spends more time in iterative sampling but can generate stronger semantic replacements in many cases.

### Stable Diffusion 1.4

File: `lama_cleaner/model/sd.py`

Stable Diffusion uses a diffusers-based inpainting pipeline and is the prompt-driven path in the repository.

Flow:

1. Load the pipeline from Hugging Face or local cache.
2. Select a scheduler based on the configured sampler.
3. Seed Python, NumPy, and Torch RNGs.
4. Optionally blur the mask before inference.
5. Run the pipeline with prompt, image, mask, strength, guidance scale, and step count.
6. Convert the generated RGB output back to BGR.

This model overrides the generic call flow to support the explicit cropper rectangle from the UI, which is useful for prompt-guided local edits.

### OpenCV2

File: `lama_cleaner/model/opencv2.py`

OpenCV2 is the classical, non-generative path. It does not require model downloads and simply calls `cv2.inpaint()` with the configured radius and algorithm.

This is useful for simple backgrounds, watermark removal, and low-resource environments.

## Image and Mask Utilities

`lama_cleaner/helper.py` contains most of the low-level array handling used across models.

Important helpers:

- `load_img()`: decode bytes into RGB or grayscale arrays and preserve alpha when present
- `norm_img()`: convert arrays into channel-first float tensors in `[0, 1]`
- `resize_max_size()`: downscale large images while preserving aspect ratio
- `pad_img_to_modulo()`: pad arrays to valid model shapes
- `boxes_from_mask()`: compute bounding boxes around masked regions
- `numpy_to_bytes()`: encode output arrays into PNG or JPEG bytes

These utilities keep model code smaller and ensure the same preprocessing rules are applied consistently.

## Frontend Settings and Their Effect on Inference

The frontend stores settings in `lama_cleaner/app/src/store/Atoms.tsx`.

Important categories:

- selected model
- HD settings per model
- LDM step count and sampler
- ZITS wireframe toggle
- Stable Diffusion prompt and generation controls
- OpenCV radius and algorithm
- tiling controls

The per-model HD defaults are important because they determine how large images are processed before they reach the model implementation.

## End-to-End Example

For a typical LaMa request:

1. The user loads an image and paints a mask in the editor.
2. `Editor.tsx` serializes the current mask and settings.
3. `adapters/inpainting.ts` posts the image and mask to `/inpaint`.
4. `server.py` decodes the files, builds `Config`, and resizes if needed.
5. `ModelManager` calls the active `LaMa` instance.
6. `InpaintModel` decides whether to run original, resize, crop, or tiled strategy.
7. `LaMa.forward()` runs the TorchScript model.
8. The base class restores all unmasked pixels from the original image.
9. The server reattaches alpha if necessary and returns the final image.
10. The frontend inserts the returned image into the editor history.

For LDM and Stable Diffusion, steps 1 through 6 and 8 through 10 stay mostly the same. The main difference is the model-specific inference in step 7.

## Key Files For Future Reference

- `main.py`
- `lama_cleaner/__init__.py`
- `lama_cleaner/server.py`
- `lama_cleaner/schema.py`
- `lama_cleaner/model_manager.py`
- `lama_cleaner/model/base.py`
- `lama_cleaner/model/lama.py`
- `lama_cleaner/model/ldm.py`
- `lama_cleaner/model/sd.py`
- `lama_cleaner/model/opencv2.py`
- `lama_cleaner/helper.py`
- `lama_cleaner/app/src/components/Editor/Editor.tsx`
- `lama_cleaner/app/src/adapters/inpainting.ts`
- `lama_cleaner/app/src/store/Atoms.tsx`

## Summary

The repository is designed around a clear separation of concerns:

- the frontend captures edits and parameters
- the backend validates and orchestrates inference
- `ModelManager` controls active model lifecycle
- `InpaintModel` centralizes padding, cropping, resizing, tiling, and masked-pixel preservation
- concrete model files focus on the actual inference implementation

That structure makes it straightforward to add new models or change inference strategies without rewriting the rest of the application stack.