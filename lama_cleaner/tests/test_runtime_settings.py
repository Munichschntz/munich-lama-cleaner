import os
from pathlib import Path

from lama_cleaner.runtime_settings import configure_cache_settings


def _reset_cache_env(monkeypatch):
    for key in [
        "LAMA_CLEANER_CACHE_DIR",
        "CACHE_DIR",
        "TORCH_HOME",
        "HF_HOME",
        "TRANSFORMERS_CACHE",
        "HUGGINGFACE_HUB_CACHE",
    ]:
        monkeypatch.delenv(key, raising=False)


def test_cli_cache_dir_applies_env_and_persists(monkeypatch, tmp_path):
    _reset_cache_env(monkeypatch)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))

    cache_root = tmp_path / "cache-from-cli"
    settings = configure_cache_settings(str(cache_root))

    assert settings.enabled is True
    assert settings.source == "cli"
    assert settings.persisted is True
    assert os.environ["TORCH_HOME"].endswith("torch")
    assert os.environ["HF_HOME"].endswith("huggingface")
    assert os.environ["TRANSFORMERS_CACHE"].endswith("huggingface/transformers")


def test_env_overrides_persisted(monkeypatch, tmp_path):
    _reset_cache_env(monkeypatch)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))

    configure_cache_settings(str(tmp_path / "persisted"))
    monkeypatch.setenv("LAMA_CLEANER_CACHE_DIR", str(tmp_path / "from-env"))
    settings = configure_cache_settings(None)

    assert settings.source == "env"
    assert settings.root_dir == str((tmp_path / "from-env").resolve())


def test_legacy_cache_dir_env_supported(monkeypatch, tmp_path):
    _reset_cache_env(monkeypatch)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    monkeypatch.setenv("CACHE_DIR", str(tmp_path / "legacy"))

    settings = configure_cache_settings(None)

    assert settings.enabled is True
    assert settings.source == "env_legacy"
    assert settings.root_dir == str((tmp_path / "legacy").resolve())


def test_persisted_config_used_when_no_cli_or_env(monkeypatch, tmp_path):
    _reset_cache_env(monkeypatch)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))

    cache_root = tmp_path / "persisted"
    configure_cache_settings(str(cache_root))

    _reset_cache_env(monkeypatch)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))

    settings = configure_cache_settings(None)
    assert settings.enabled is True
    assert settings.source == "config"
    assert settings.root_dir == str(cache_root.resolve())


def test_malformed_persisted_config_falls_back_to_default(monkeypatch, tmp_path):
    _reset_cache_env(monkeypatch)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))

    config_path = Path(tmp_path / "cfg" / "lama-cleaner" / "config.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("{ malformed-json", encoding="utf-8")

    settings = configure_cache_settings(None)
    assert settings.enabled is False
    assert settings.source == "default"
    assert settings.root_dir is None
