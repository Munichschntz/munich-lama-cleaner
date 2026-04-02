#!/usr/bin/env python3

import argparse
import multiprocessing
import os
import time
from typing import Optional

import numpy as np
import psutil
import torch

try:
    import nvidia_smi
except ImportError:
    nvidia_smi = None

from lama_cleaner.runtime_settings import configure_cache_settings

NUM_THREADS = str(max(1, multiprocessing.cpu_count() // 2))

os.environ["OMP_NUM_THREADS"] = NUM_THREADS
os.environ["OPENBLAS_NUM_THREADS"] = NUM_THREADS
os.environ["MKL_NUM_THREADS"] = NUM_THREADS
os.environ["VECLIB_MAXIMUM_THREADS"] = NUM_THREADS
os.environ["NUMEXPR_NUM_THREADS"] = NUM_THREADS


def build_config():
    from lama_cleaner.schema import Config, HDStrategy, LDMSampler, SDSampler, QualityPreset

    return Config(
        ldm_steps=25,
        ldm_sampler=LDMSampler.plms,
        zits_wireframe=True,
        hd_strategy=HDStrategy.RESIZE,
        hd_strategy_crop_margin=128,
        hd_strategy_crop_trigger_size=1024,
        hd_strategy_resize_limit=1024,
        prompt="",
        use_cropper=False,
        quality_preset=QualityPreset.balanced,
        mask_feather=0,
        sd_mask_blur=5,
        sd_strength=0.75,
        sd_steps=40,
        sd_guidance_scale=7.5,
        sd_sampler=SDSampler.ddim,
        sd_seed=42,
        cv2_radius=3,
        cv2_flag="INPAINT_TELEA",
        enable_tiling=False,
        tile_size=1024,
        tile_overlap=64,
    )


def run_model(manager, size, config):
    image = np.random.randint(0, 256, (size[0], size[1], 3), dtype=np.uint8)
    mask = np.random.randint(0, 255, size, dtype=np.uint8)
    manager(image, mask, config)


def benchmark(
    manager,
    times: int,
    empty_cache: bool,
    use_cuda_metrics: bool,
):
    sizes = [
        (512, 512),
        (768, 768),
        (1080, 800),
        (1600, 1200),
        (2000, 2000),
    ]

    handle: Optional[object] = None
    if use_cuda_metrics and nvidia_smi is not None:
        nvidia_smi.nvmlInit()
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)

    def metric(values):
        return f"{np.mean(values):.2f} ± {np.std(values):.2f}"

    process = psutil.Process(os.getpid())
    config = build_config()

    for size in sizes:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        latency_ms = []
        cpu_rss_mb = []
        gpu_mem_mb = []

        for _ in range(times):
            start = time.time()
            run_model(manager, size, config)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
                if empty_cache:
                    torch.cuda.empty_cache()

            latency_ms.append((time.time() - start) * 1000)
            cpu_rss_mb.append(process.memory_info().rss / 1024 / 1024)
            if handle is not None and nvidia_smi is not None:
                gpu_mem_mb.append(
                    nvidia_smi.nvmlDeviceGetMemoryInfo(handle).used / 1024 / 1024
                )

        print(f"size: {size}".center(80, "-"))
        print(f"latency: {metric(latency_ms)} ms")
        print(f"cpu memory: {metric(cpu_rss_mb)} MB")
        if gpu_mem_mb:
            print(f"gpu memory: {metric(gpu_mem_mb)} MB")

    if handle is not None and nvidia_smi is not None:
        nvidia_smi.nvmlShutdown()


def get_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="lama", type=str)
    parser.add_argument("--device", default="cuda", type=str)
    parser.add_argument("--times", default=10, type=int)
    parser.add_argument("--empty-cache", action="store_true")
    parser.add_argument("--cache-dir", default=None, type=str)
    parser.add_argument("--hf_access_token", default=None, type=str)
    parser.add_argument("--sd-run-local", action="store_true")
    parser.add_argument("--sd-disable-nsfw", action="store_true")
    parser.add_argument("--sd-cpu-textencoder", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args_parser()
    configure_cache_settings(args.cache_dir, persist_cli_choice=False)

    from lama_cleaner.model_manager import ModelManager

    device = torch.device(args.device)

    manager = ModelManager(
        args.model,
        device,
        hf_access_token=args.hf_access_token,
        sd_run_local=args.sd_run_local,
        sd_disable_nsfw=args.sd_disable_nsfw,
        sd_cpu_textencoder=args.sd_cpu_textencoder,
    )

    benchmark(
        manager,
        times=args.times,
        empty_cache=args.empty_cache,
        use_cuda_metrics=("cuda" in args.device and torch.cuda.is_available()),
    )
