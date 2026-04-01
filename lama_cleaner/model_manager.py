from importlib import import_module

from lama_cleaner.schema import Config

MODEL_IMPORTS = {
    "lama": ("lama_cleaner.model.lama", "LaMa"),
    "ldm": ("lama_cleaner.model.ldm", "LDM"),
    "zits": ("lama_cleaner.model.zits", "ZITS"),
    "mat": ("lama_cleaner.model.mat", "MAT"),
    "fcf": ("lama_cleaner.model.fcf", "FcF"),
    "sd1.4": ("lama_cleaner.model.sd", "SD14"),
    "cv2": ("lama_cleaner.model.opencv2", "OpenCV2"),
}

# Exported to preserve compatibility with existing imports.
models = MODEL_IMPORTS
_MODEL_CLASS_CACHE = {}


def get_model_class(name: str):
    if name not in MODEL_IMPORTS:
        raise NotImplementedError(f"Not supported model: {name}")

    if name in _MODEL_CLASS_CACHE:
        return _MODEL_CLASS_CACHE[name]

    module_name, class_name = MODEL_IMPORTS[name]
    try:
        module = import_module(module_name)
        model_class = getattr(module, class_name)
    except Exception as e:
        raise RuntimeError(
            f"Failed to import model '{name}'. Optional dependencies may be missing or incompatible: {e}"
        ) from e

    _MODEL_CLASS_CACHE[name] = model_class
    return model_class

MODEL_CAPABILITIES = {
    "lama": {
        "display_name": "LaMa",
        "recommended_resolution": "up to 2k",
        "vram_estimate": "4-8 GB",
        "speed": "fast",
        "quality": "balanced",
    },
    "ldm": {
        "display_name": "LDM",
        "recommended_resolution": "up to 1080p",
        "vram_estimate": "8-12 GB",
        "speed": "slow",
        "quality": "high",
    },
    "zits": {
        "display_name": "ZITS",
        "recommended_resolution": "up to 1024p",
        "vram_estimate": "8-12 GB",
        "speed": "slow",
        "quality": "high structure",
    },
    "mat": {
        "display_name": "MAT",
        "recommended_resolution": "up to 1024p",
        "vram_estimate": "8-12 GB",
        "speed": "medium",
        "quality": "high",
    },
    "fcf": {
        "display_name": "FcF",
        "recommended_resolution": "512 only",
        "vram_estimate": "6-10 GB",
        "speed": "medium",
        "quality": "texture",
    },
    "sd1.4": {
        "display_name": "Stable Diffusion 1.4",
        "recommended_resolution": "512-768",
        "vram_estimate": "8-16 GB",
        "speed": "slow",
        "quality": "prompt-driven",
    },
    "cv2": {
        "display_name": "OpenCV2",
        "recommended_resolution": "any",
        "vram_estimate": "0 GB",
        "speed": "very fast",
        "quality": "simple scenes",
    },
}


class ModelManager:
    def __init__(self, name: str, device, **kwargs):
        self.name = name
        self.device = device
        self.kwargs = kwargs
        self._cache = {}
        self.model = self.init_model(name, device, **kwargs)

    def evict_cache_except(self, keep_names):
        keep = set(keep_names)
        for cached_name in list(self._cache.keys()):
            if cached_name not in keep:
                del self._cache[cached_name]

    def init_model(self, name: str, device, **kwargs):
        if name not in models:
            raise NotImplementedError(f"Not supported model: {name}")
        if name in self._cache:
            return self._cache[name]
        model_class = get_model_class(name)
        model = model_class(device, **kwargs)
        self._cache[name] = model
        return model

    def is_downloaded(self, name: str) -> bool:
        if name in models:
            return get_model_class(name).is_downloaded()
        else:
            raise NotImplementedError(f"Not supported model: {name}")

    def __call__(self, image, mask, config: Config):
        return self.model(image, mask, config)

    def switch(self, new_name: str):
        if new_name == self.name:
            return
        try:
            self.model = self.init_model(new_name, self.device, **self.kwargs)
            self.name = new_name
            # Keep only the active model in cache to avoid unbounded memory growth
            # when users switch between multiple heavyweight models.
            self.evict_cache_except({new_name})
        except NotImplementedError as e:
            raise e

    def capabilities(self, name: str = None):
        if name is None:
            return MODEL_CAPABILITIES
        if name not in MODEL_CAPABILITIES:
            raise NotImplementedError(f"Not supported model: {name}")
        return MODEL_CAPABILITIES[name]
