import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


APP_CACHE_DIR_ENV = "LAMA_CLEANER_CACHE_DIR"
LEGACY_CACHE_DIR_ENV = "CACHE_DIR"


@dataclass
class CacheSettings:
    enabled: bool
    source: str
    root_dir: Optional[str]
    torch_home: Optional[str]
    hf_home: Optional[str]
    transformers_cache: Optional[str]
    huggingface_hub_cache: Optional[str]
    config_file: str
    persisted: bool

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "enabled": self.enabled,
            "source": self.source,
            "root_dir": self.root_dir,
            "torch_home": self.torch_home,
            "hf_home": self.hf_home,
            "transformers_cache": self.transformers_cache,
            "huggingface_hub_cache": self.huggingface_hub_cache,
            "config_file": self.config_file,
            "persisted": self.persisted,
        }


def _config_dir() -> Path:
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "lama-cleaner"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "lama-cleaner"
    return Path.home() / ".config" / "lama-cleaner"


def config_file_path() -> Path:
    return _config_dir() / "config.json"


def _normalize_dir(path: str) -> str:
    return str(Path(path).expanduser().resolve())


def _validate_writable_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path, delete=True):
        pass


def _load_persisted_cache_dir(config_path: Path) -> Optional[str]:
    if not config_path.exists():
        return None
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    cache_dir = data.get("cache_dir")
    if not cache_dir:
        return None
    return str(cache_dir)


def _persist_cache_dir(config_path: Path, cache_dir: str) -> None:
    os.makedirs(config_path.parent, exist_ok=True)
    data = {"cache_dir": cache_dir}
    config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _env_mapping_from_root(root_dir: str) -> Dict[str, str]:
    torch_home = str(Path(root_dir) / "torch")
    hf_home = str(Path(root_dir) / "huggingface")
    transformers_cache = str(Path(hf_home) / "transformers")
    huggingface_hub_cache = str(Path(hf_home) / "hub")
    return {
        "TORCH_HOME": torch_home,
        "HF_HOME": hf_home,
        "TRANSFORMERS_CACHE": transformers_cache,
        "HUGGINGFACE_HUB_CACHE": huggingface_hub_cache,
    }


def configure_cache_settings(
    cache_dir_cli: Optional[str],
    *,
    persist_cli_choice: bool = True,
) -> CacheSettings:
    config_path = config_file_path()
    source = "default"
    cache_root = None

    if cache_dir_cli:
        cache_root = cache_dir_cli
        source = "cli"
    elif os.environ.get(APP_CACHE_DIR_ENV):
        cache_root = os.environ.get(APP_CACHE_DIR_ENV)
        source = "env"
    elif os.environ.get(LEGACY_CACHE_DIR_ENV):
        cache_root = os.environ.get(LEGACY_CACHE_DIR_ENV)
        source = "env_legacy"
    else:
        persisted = _load_persisted_cache_dir(config_path)
        if persisted:
            cache_root = persisted
            source = "config"

    if not cache_root:
        return CacheSettings(
            enabled=False,
            source=source,
            root_dir=None,
            torch_home=os.environ.get("TORCH_HOME"),
            hf_home=os.environ.get("HF_HOME"),
            transformers_cache=os.environ.get("TRANSFORMERS_CACHE"),
            huggingface_hub_cache=os.environ.get("HUGGINGFACE_HUB_CACHE"),
            config_file=str(config_path),
            persisted=False,
        )

    cache_root = _normalize_dir(cache_root)
    _validate_writable_dir(cache_root)

    env_mapping = _env_mapping_from_root(cache_root)
    for key, value in env_mapping.items():
        os.environ[key] = value

    persisted = False
    if source == "cli" and persist_cli_choice:
        _persist_cache_dir(config_path, cache_root)
        persisted = True

    return CacheSettings(
        enabled=True,
        source=source,
        root_dir=cache_root,
        torch_home=env_mapping["TORCH_HOME"],
        hf_home=env_mapping["HF_HOME"],
        transformers_cache=env_mapping["TRANSFORMERS_CACHE"],
        huggingface_hub_cache=env_mapping["HUGGINGFACE_HUB_CACHE"],
        config_file=str(config_path),
        persisted=persisted,
    )
