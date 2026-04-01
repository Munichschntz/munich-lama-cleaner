import pytest

from lama_cleaner.parse_args import _parse_preload_models


def test_parse_preload_models_empty_values():
    assert _parse_preload_models("") == []
    assert _parse_preload_models(" , ") == []


def test_parse_preload_models_all_is_exclusive():
    assert _parse_preload_models("all") == ["lama", "ldm", "zits", "mat", "fcf", "sd1.4", "cv2"]


@pytest.mark.parametrize("raw", ["all,typo_model", "typo_model,all", "all,lama"])
def test_parse_preload_models_rejects_all_with_extra_tokens(raw):
    with pytest.raises(ValueError, match="all"):
        _parse_preload_models(raw)


def test_parse_preload_models_rejects_unknown_model():
    with pytest.raises(ValueError, match="typo_model"):
        _parse_preload_models("typo_model")


def test_parse_preload_models_keeps_order_and_deduplicates():
    assert _parse_preload_models("ldm,lama,ldm") == ["ldm", "lama"]
