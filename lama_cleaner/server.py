#!/usr/bin/env python3

import io
import logging
import multiprocessing
import os
import random
import threading
import time
import imghdr
from pathlib import Path
from typing import Union

import cv2
import torch
import numpy as np
from loguru import logger

from lama_cleaner.model_manager import ModelManager, get_model_class
from lama_cleaner.schema import Config, QualityPreset

try:
    torch._C._jit_override_can_fuse_on_cpu(False)
    torch._C._jit_override_can_fuse_on_gpu(False)
    torch._C._jit_set_texpr_fuser_enabled(False)
    torch._C._jit_set_nvfuser_enabled(False)
except:
    pass

from flask import Flask, request, send_file, cli, make_response, jsonify

# Disable ability for Flask to display warning about using a development server in a production environment.
# https://gist.github.com/jerblack/735b9953ba1ab6234abb43174210d356
cli.show_server_banner = lambda *_: None
from flask_cors import CORS

from lama_cleaner.helper import (
    load_img,
    numpy_to_bytes,
    resize_max_size,
)

NUM_THREADS = str(multiprocessing.cpu_count())

# fix libomp problem on windows https://github.com/Sanster/lama-cleaner/issues/56
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

os.environ["OMP_NUM_THREADS"] = NUM_THREADS
os.environ["OPENBLAS_NUM_THREADS"] = NUM_THREADS
os.environ["MKL_NUM_THREADS"] = NUM_THREADS
os.environ["VECLIB_MAXIMUM_THREADS"] = NUM_THREADS
os.environ["NUMEXPR_NUM_THREADS"] = NUM_THREADS

DEFAULT_BUILD_DIR = Path(__file__).resolve().parent / "app" / "build"
BUILD_DIR = Path(os.environ.get("LAMA_CLEANER_BUILD_DIR", str(DEFAULT_BUILD_DIR)))
PRELOAD_DOWNLOAD_CHECK_UNSUPPORTED = {"sd1.4", "cv2"}


class NoFlaskwebgui(logging.Filter):
    def filter(self, record):
        return "GET //flaskwebgui-keep-server-alive" not in record.getMessage()


logging.getLogger("werkzeug").addFilter(NoFlaskwebgui())

app = Flask(__name__, static_folder=str(BUILD_DIR / "static"))
app.config["JSON_AS_ASCII"] = False
CORS(app, expose_headers=["Content-Disposition"])
# MAX_BUFFER_SIZE = 50 * 1000 * 1000  # 50 MB
# async_mode 优先级: eventlet/gevent_uwsgi/gevent/threading
# only threading works on macOS
# socketio = SocketIO(app, max_http_buffer_size=MAX_BUFFER_SIZE, async_mode='threading')

model: ModelManager = None
device = None
input_image_path: str = None
cache_settings = None
status_lock = threading.Lock()
server_status = {
    "phase": "idle",
    "message": "Idle",
    "progress": None,
    "updated_at": time.time(),
}


def get_image_ext(img_bytes):
    w = imghdr.what("", img_bytes)
    if w is None:
        w = "jpeg"
    return w


def diffuser_callback(step: int):
    set_server_status("inpainting", f"Diffusion step {step}", step)
    # socketio.emit('diffusion_step', {'diffusion_step': step})


def set_server_status(phase: str, message: str, progress: Union[int, None] = None):
    with status_lock:
        server_status["phase"] = phase
        server_status["message"] = message
        server_status["progress"] = progress
        server_status["updated_at"] = time.time()


def status_snapshot():
    with status_lock:
        return dict(server_status)


def error_response(code: str, message: str, status: int = 400, details=None):
    payload = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return jsonify(payload), status


def parse_bool(raw_value, default: bool = False) -> bool:
    if raw_value is None:
        return default
    if isinstance(raw_value, bool):
        return raw_value
    return str(raw_value).lower() in ("1", "true", "yes", "on")


def get_form_field(form, key, aliases=None, default=None, deprecated_used=None):
    if key in form:
        return form.get(key)
    aliases = aliases or []
    for alias in aliases:
        if alias in form:
            if deprecated_used is not None:
                deprecated_used.append(alias)
            return form.get(alias)
    return default


def apply_quality_preset(preset: str, model_name: str, config_values: dict):
    if preset == QualityPreset.fast:
        config_values["ldm_steps"] = 15
        config_values["sd_steps"] = 20
        config_values["sd_guidance_scale"] = 6.5
        config_values["sd_sampler"] = "ddim"
    elif preset == QualityPreset.best:
        config_values["ldm_steps"] = 50
        config_values["sd_steps"] = 60
        config_values["sd_guidance_scale"] = 8.0
        config_values["sd_sampler"] = "pndm"
    else:
        config_values["ldm_steps"] = 25
        config_values["sd_steps"] = 40
        config_values["sd_guidance_scale"] = 7.5
        config_values["sd_sampler"] = "ddim"

    # Keep per-model defaults intuitive even when a global preset is selected.
    if model_name == "cv2":
        config_values["cv2_radius"] = config_values.get("cv2_radius", 3)


@app.route("/inpaint", methods=["POST"])
def process():
    files = request.files
    if "image" not in files or "mask" not in files:
        return error_response(
            "MISSING_FILE",
            "Request must include both image and mask files",
            status=400,
        )

    set_server_status("inpainting", "Preparing request", 0)
    deprecated_used = []
    try:
        # RGB
        origin_image_bytes = files["image"].read()
        image, alpha_channel = load_img(origin_image_bytes)
        original_shape = image.shape
        interpolation = cv2.INTER_CUBIC

        form = request.form
        size_limit: Union[int, str] = form.get("sizeLimit", "1080")
        if size_limit == "Original":
            size_limit = max(image.shape)
        else:
            size_limit = int(size_limit)

        quality_preset = get_form_field(form, "qualityPreset", default=QualityPreset.balanced)
        config_values = {
            "ldm_steps": get_form_field(form, "ldmSteps"),
            "ldm_sampler": get_form_field(form, "ldmSampler"),
            "hd_strategy": get_form_field(form, "hdStrategy"),
            "zits_wireframe": get_form_field(form, "zitsWireframe"),
            "hd_strategy_crop_margin": get_form_field(form, "hdStrategyCropMargin"),
            "hd_strategy_crop_trigger_size": get_form_field(
                form,
                "hdStrategyCropTriggerSize",
                aliases=["hdStrategyCropTrigerSize"],
                deprecated_used=deprecated_used,
            ),
            "hd_strategy_resize_limit": get_form_field(form, "hdStrategyResizeLimit"),
            "prompt": get_form_field(form, "prompt", default=""),
            "use_cropper": parse_bool(
                get_form_field(
                    form,
                    "useCropper",
                    aliases=["useCroper"],
                    default=False,
                    deprecated_used=deprecated_used,
                )
            ),
            "cropper_x": get_form_field(
                form,
                "cropperX",
                aliases=["croperX"],
                deprecated_used=deprecated_used,
            ),
            "cropper_y": get_form_field(
                form,
                "cropperY",
                aliases=["croperY"],
                deprecated_used=deprecated_used,
            ),
            "cropper_height": get_form_field(
                form,
                "cropperHeight",
                aliases=["croperHeight"],
                deprecated_used=deprecated_used,
            ),
            "cropper_width": get_form_field(
                form,
                "cropperWidth",
                aliases=["croperWidth"],
                deprecated_used=deprecated_used,
            ),
            "quality_preset": quality_preset,
            "mask_feather": get_form_field(form, "maskFeather", default=0),
            "sd_mask_blur": get_form_field(form, "sdMaskBlur", default=0),
            "sd_strength": get_form_field(form, "sdStrength", default=0.75),
            "sd_steps": get_form_field(form, "sdSteps", default=50),
            "sd_guidance_scale": get_form_field(form, "sdGuidanceScale", default=7.5),
            "sd_sampler": get_form_field(form, "sdSampler", default="ddim"),
            "sd_seed": get_form_field(form, "sdSeed", default=-1),
            "cv2_radius": get_form_field(form, "cv2Radius", default=3),
            "cv2_flag": get_form_field(form, "cv2Flag", default="INPAINT_TELEA"),
            "enable_tiling": parse_bool(get_form_field(form, "enableTiling", default=False)),
            "tile_size": get_form_field(form, "tileSize", default=1024),
            "tile_overlap": get_form_field(form, "tileOverlap", default=64),
        }

        apply_quality_preset(quality_preset, model.name, config_values)
        config = Config(**config_values)

        if config.sd_seed == -1:
            config.sd_seed = random.randint(1, 9999999)

        logger.info(f"Origin image shape: {original_shape}")
        set_server_status("inpainting", "Resizing image", 15)
        image = resize_max_size(image, size_limit=size_limit, interpolation=interpolation)
        logger.info(f"Resized image shape: {image.shape}")

        mask, _ = load_img(files["mask"].read(), gray=True)
        mask = resize_max_size(mask, size_limit=size_limit, interpolation=interpolation)

        set_server_status("inpainting", "Running model", 40)
        start = time.time()
        res_np_img = model(image, mask, config)
        logger.info(f"process time: {(time.time() - start) * 1000}ms")

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        if alpha_channel is not None:
            if alpha_channel.shape[:2] != res_np_img.shape[:2]:
                alpha_channel = cv2.resize(
                    alpha_channel, dsize=(res_np_img.shape[1], res_np_img.shape[0])
                )
            res_np_img = np.concatenate(
                (res_np_img, alpha_channel[:, :, np.newaxis]), axis=-1
            )

        set_server_status("inpainting", "Encoding output", 95)
        ext = get_image_ext(origin_image_bytes)
        response = make_response(
            send_file(
                io.BytesIO(numpy_to_bytes(res_np_img, ext)),
                mimetype=f"image/{ext}",
            )
        )
        response.headers["X-Seed"] = str(config.sd_seed)
        if deprecated_used:
            response.headers["X-Deprecated-Fields"] = ",".join(sorted(set(deprecated_used)))

        set_server_status("idle", "Idle", None)
        return response
    except Exception as e:
        logger.exception("inpaint failed")
        set_server_status("error", "Inpainting failed", None)
        error_payload = error_response(
            "INPAINT_FAILED",
            "Unable to inpaint image with current parameters",
            status=500,
            details=str(e),
        )
        if deprecated_used:
            error_payload[0].headers["X-Deprecated-Fields"] = ",".join(
                sorted(set(deprecated_used))
            )
        return error_payload


@app.route("/model")
def current_model():
    return jsonify({"model": model.name}), 200


@app.route("/model_downloaded/<name>")
def model_downloaded(name):
    try:
        return jsonify({"downloaded": model.is_downloaded(name)}), 200
    except NotImplementedError:
        return error_response("MODEL_NOT_IMPLEMENTED", f"{name} not implemented", status=404)


@app.route("/model_capabilities")
def model_capabilities():
    return jsonify(model.capabilities()), 200


@app.route("/model_capabilities/<name>")
def model_capability(name):
    try:
        return jsonify(model.capabilities(name)), 200
    except NotImplementedError:
        return error_response("MODEL_NOT_IMPLEMENTED", f"{name} not implemented", status=404)


@app.route("/server_status")
def current_status():
    status = status_snapshot()
    status["model"] = model.name if model else None
    status["cache_settings"] = cache_settings or {}
    return jsonify(status), 200


@app.route("/cache_settings")
def current_cache_settings():
    return jsonify(cache_settings or {}), 200


@app.route("/model", methods=["POST"])
def switch_model():
    new_name = request.form.get("name")
    if not new_name:
        return error_response("INVALID_MODEL", "name is required", status=400)
    if new_name == model.name:
        return jsonify({"message": "Same model", "model": model.name}), 200

    try:
        set_server_status("switching_model", f"Switching to {new_name}", 10)
        model.switch(new_name)
    except NotImplementedError:
        set_server_status("error", f"{new_name} not implemented", None)
        return error_response(
            "MODEL_NOT_IMPLEMENTED", f"{new_name} not implemented", status=404
        )
    except Exception as e:
        logger.exception("switch model failed")
        set_server_status("error", f"Switch model failed: {new_name}", None)
        return error_response(
            "MODEL_SWITCH_FAILED",
            f"Failed to switch to {new_name}",
            status=500,
            details=str(e),
        )

    set_server_status("idle", "Idle", None)
    return jsonify({"message": f"ok, switch to {new_name}", "model": new_name}), 200


@app.route("/")
def index():
    return send_file(str(BUILD_DIR / "index.html"))


@app.route("/inputimage")
def set_input_photo():
    if input_image_path:
        with open(input_image_path, "rb") as f:
            image_in_bytes = f.read()
        send_kwargs = {
            "as_attachment": True,
            "mimetype": f"image/{get_image_ext(image_in_bytes)}",
        }
        # Flask>=2.0 uses download_name; older versions use attachment_filename.
        try:
            return send_file(
                input_image_path,
                download_name=Path(input_image_path).name,
                **send_kwargs,
            )
        except TypeError:
            return send_file(
                input_image_path,
                attachment_filename=Path(input_image_path).name,
                **send_kwargs,
            )
    else:
        return "No Input Image"


def main(args):
    global model
    global device
    global input_image_path
    global cache_settings

    cache_settings_obj = getattr(args, "cache_settings", None)
    cache_settings = (
        cache_settings_obj.to_dict() if cache_settings_obj is not None else {"enabled": False, "source": "default"}
    )
    logger.info(f"Cache settings: {cache_settings}")

    device = torch.device(args.device)
    input_image_path = args.input

    startup_kwargs = dict(
        hf_access_token=args.hf_access_token,
        sd_disable_nsfw=args.sd_disable_nsfw,
        sd_cpu_textencoder=args.sd_cpu_textencoder,
        sd_run_local=args.sd_run_local,
        callbacks=[diffuser_callback],
    )

    preload_models = list(args.preload_models)
    if preload_models:
        if args.model not in preload_models:
            preload_models.append(args.model)
        logger.info(f"Preloading models before launch: {', '.join(preload_models)}")

        preload_status_before = {}
        for preload_name in preload_models:
            if preload_name in PRELOAD_DOWNLOAD_CHECK_UNSUPPORTED:
                preload_status_before[preload_name] = None
                continue
            preload_status_before[preload_name] = get_model_class(preload_name).is_downloaded()

        preload_manager = ModelManager(
            name=preload_models[0],
            device=device,
            **startup_kwargs,
        )
        for preload_name in preload_models[1:]:
            if preload_name in preload_manager._cache:
                continue
            preload_manager.init_model(preload_name, device, **startup_kwargs)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        preload_status_counts = {
            "already_cached": 0,
            "newly_downloaded": 0,
            "unknown": 0,
        }
        preload_status_lines = []
        for preload_name in preload_models:
            status_before = preload_status_before.get(preload_name)
            if status_before is None:
                preload_status_counts["unknown"] += 1
                preload_status_lines.append(
                    f"{preload_name}=unknown(download check unavailable)"
                )
                continue

            status_after = get_model_class(preload_name).is_downloaded()
            if status_before:
                preload_status_counts["already_cached"] += 1
                preload_status_lines.append(f"{preload_name}=already_cached")
            elif status_after:
                preload_status_counts["newly_downloaded"] += 1
                preload_status_lines.append(f"{preload_name}=newly_downloaded")
            else:
                preload_status_counts["unknown"] += 1
                preload_status_lines.append(f"{preload_name}=unknown(post-check failed)")

        logger.info(
            "Preload summary: "
            f"already_cached={preload_status_counts['already_cached']}, "
            f"newly_downloaded={preload_status_counts['newly_downloaded']}, "
            f"unknown={preload_status_counts['unknown']}"
        )
        logger.info(f"Preload details: {', '.join(preload_status_lines)}")

        if args.preload_only:
            logger.info("Model preloading finished (--preload-only), exiting.")
            return

        if args.model in preload_manager._cache:
            preload_manager.model = preload_manager._cache[args.model]
            preload_manager.name = args.model
            model = preload_manager

            # Drop other loaded model instances after cache warm-up.
            for cached_name in list(model._cache.keys()):
                if cached_name != args.model:
                    del model._cache[cached_name]
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    if model is None:
        model = ModelManager(
            name=args.model,
            device=device,
            **startup_kwargs,
        )

    if args.gui:
        app_width, app_height = args.gui_size
        from flaskwebgui import FlaskUI

        ui = FlaskUI(
            app, width=app_width, height=app_height, host=args.host, port=args.port
        )
        ui.run()
    else:
        # TODO: socketio
        app.run(host=args.host, port=args.port, debug=args.debug)
