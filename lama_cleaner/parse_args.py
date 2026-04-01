import os
import imghdr
import argparse


MODEL_CHOICES = ["lama", "ldm", "zits", "mat", "fcf", "sd1.4", "cv2"]


def _parse_preload_models(raw: str):
    if not raw:
        return []

    names = [name.strip() for name in raw.split(",") if name.strip()]
    if not names:
        return []

    normalized = []
    seen = set()
    if "all" in names:
        names = MODEL_CHOICES

    for name in names:
        if name not in MODEL_CHOICES:
            raise ValueError(name)
        if name in seen:
            continue
        seen.add(name)
        normalized.append(name)

    return normalized


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    parser.add_argument(
        "--model",
        default="lama",
        choices=MODEL_CHOICES,
    )
    parser.add_argument(
        "--preload-models",
        default="",
        help="Pre-download model weights before launch. Comma-separated model names or 'all'",
    )
    parser.add_argument(
        "--preload-only",
        action="store_true",
        help="Only pre-download model weights and exit",
    )
    parser.add_argument(
        "--hf_access_token",
        default="",
        help="Huggingface access token. Check how to get token from: https://huggingface.co/docs/hub/security-tokens",
    )
    parser.add_argument(
        "--sd-disable-nsfw",
        action="store_true",
        help="Disable Stable Diffusion NSFW checker",
    )
    parser.add_argument(
        "--sd-cpu-textencoder",
        action="store_true",
        help="Always run Stable Diffusion TextEncoder model on CPU",
    )
    parser.add_argument(
        "--sd-run-local",
        action="store_true",
        help="After first time Stable Diffusion model downloaded, you can add this arg and remove --hf_access_token",
    )
    parser.add_argument("--device", default="cuda", type=str, choices=["cuda", "cpu"])
    parser.add_argument("--gui", action="store_true", help="Launch as desktop app")
    parser.add_argument(
        "--gui-size",
        default=[1600, 1000],
        nargs=2,
        type=int,
        help="Set window size for GUI",
    )
    parser.add_argument(
        "--input", type=str, help="Path to image you want to load by default"
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="Root directory for model caches (torch + huggingface). Persisted when set.",
    )
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    try:
        args.preload_models = _parse_preload_models(args.preload_models)
    except ValueError as e:
        parser.error(
            f"invalid --preload-models value: {e}. valid values: {', '.join(MODEL_CHOICES)} or all"
        )

    if args.preload_only and not args.preload_models:
        args.preload_models = [args.model]

    if args.input is not None:
        if not os.path.exists(args.input):
            parser.error(f"invalid --input: {args.input} not exists")
        if imghdr.what(args.input) is None:
            parser.error(f"invalid --input: {args.input} is not a valid image file")

    needs_sd_token = any(name.startswith("sd") for name in [args.model, *args.preload_models])
    if needs_sd_token and not args.sd_run_local:
        if not args.hf_access_token.startswith("hf_"):
            parser.error(
                f"sd(stable-diffusion) model requires huggingface access token. Check how to get token from: https://huggingface.co/docs/hub/security-tokens"
            )

    return args
