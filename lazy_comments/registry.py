"""
Catalog of speech-to-text models available to Lazy Comments.

Add a new model by appending to MODELS. Each entry describes:

    engine:               "vosk" or "sherpa-onnx"
    engine_subtype:       sherpa-onnx factory variant
                          ("nemo-ctc", "nemo-transducer", "whisper",
                           "sense-voice", "moonshine")
    url:                  archive URL (zip for Vosk, tar.bz2 for sherpa-onnx)
    archive_format:       "zip" | "tar.bz2"
    extracted_dir:        the top-level folder produced by extracting
                          the archive into the models dir
    files:                dict of relative paths inside extracted_dir,
                          named by the engine factory (see engines.py)
    needs_term_replace:   apply TERM_REPLACEMENTS post-processing
    needs_punctuation:    apply add_punctuation post-processing
"""

from __future__ import annotations

import os
from typing import Any

from lazy_comments.config import get_models_dir


_SHERPA_BASE = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models"


MODELS: dict[str, dict[str, Any]] = {
    # ---------------- Vosk ----------------
    "vosk-ru-small": {
        "name": "Vosk Russian Small",
        "engine": "vosk",
        "language": "ru",
        "size_mb": 45,
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip",
        "archive_format": "zip",
        "extracted_dir": "vosk-model-small-ru-0.22",
        "files": {},  # Vosk loads the whole directory
        "needs_term_replace": True,
        "needs_punctuation": True,
        "description": (
            "Маленькая русская модель Vosk. Самая лёгкая (~45 МБ). "
            "Запускается на любом железе, без пунктуации и заглавных."
        ),
        "tag": "Лёгкая",
    },
    "vosk-ru-large": {
        "name": "Vosk Russian Large 0.42",
        "engine": "vosk",
        "language": "ru",
        "size_mb": 1800,
        "url": "https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip",
        "archive_format": "zip",
        "extracted_dir": "vosk-model-ru-0.42",
        "files": {},
        "needs_term_replace": True,
        "needs_punctuation": True,
        "description": (
            "Полная русская модель Vosk. Лучшее качество среди Vosk-моделей. "
            "Требует ~2 ГБ ОЗУ и медленнее на слабом ЦП."
        ),
        "tag": "Тяжёлая",
    },

    # ---------------- GigaAM v3 (Russian) — recommended for RU ----------------
    "gigaam-v3-ctc-punct": {
        "name": "GigaAM v3 (русский + пунктуация)",
        "engine": "sherpa-onnx",
        "engine_subtype": "nemo-ctc",
        "language": "ru",
        "size_mb": 215,
        "url": f"{_SHERPA_BASE}/sherpa-onnx-nemo-ctc-punct-giga-am-v3-russian-2025-12-16.tar.bz2",
        "archive_format": "tar.bz2",
        "extracted_dir": "sherpa-onnx-nemo-ctc-punct-giga-am-v3-russian-2025-12-16",
        "files": {
            "model": "model.int8.onnx",
            "tokens": "tokens.txt",
        },
        "needs_term_replace": True,
        "needs_punctuation": False,  # model emits punct/casing/digits
        "description": (
            "Лучший выбор для русского. Распознаёт цифры и латиницу, "
            "сама ставит знаки препинания. Чуть тяжелее малой Vosk, "
            "но качество ощутимо выше."
        ),
        "tag": "Рекомендуется (RU)",
    },
    "gigaam-v3-ctc": {
        "name": "GigaAM v3 (русский, без пунктуации)",
        "engine": "sherpa-onnx",
        "engine_subtype": "nemo-ctc",
        "language": "ru",
        "size_mb": 215,
        "url": f"{_SHERPA_BASE}/sherpa-onnx-nemo-ctc-giga-am-v3-russian-2025-12-16.tar.bz2",
        "archive_format": "tar.bz2",
        "extracted_dir": "sherpa-onnx-nemo-ctc-giga-am-v3-russian-2025-12-16",
        "files": {
            "model": "model.int8.onnx",
            "tokens": "tokens.txt",
        },
        "needs_term_replace": True,
        "needs_punctuation": True,
        "description": (
            "Вариант GigaAM v3 без встроенной пунктуации — Lazy Comments добавит её сам "
            "по своим правилам. Полезно, если хочешь единый стиль с Vosk."
        ),
    },

    # ---------------- Parakeet TDT v3 (25 EU languages) ----------------
    "parakeet-tdt-0.6b-v3": {
        "name": "Parakeet TDT v3 (25 EU языков)",
        "engine": "sherpa-onnx",
        "engine_subtype": "nemo-transducer",
        "language": "multi",
        "size_mb": 670,
        "url": f"{_SHERPA_BASE}/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2",
        "archive_format": "tar.bz2",
        "extracted_dir": "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8",
        "files": {
            "encoder": "encoder.int8.onnx",
            "decoder": "decoder.int8.onnx",
            "joiner": "joiner.int8.onnx",
            "tokens": "tokens.txt",
        },
        "needs_term_replace": False,
        "needs_punctuation": False,
        "description": (
            "Универсальная модель от NVIDIA: английский + 24 европейских "
            "языка, включая русский. Быстрая, очень точная. Числа пишет "
            "словами."
        ),
    },

    # ---------------- Whisper (99+ languages) ----------------
    "whisper-tiny": {
        "name": "Whisper Tiny (мультиязык)",
        "engine": "sherpa-onnx",
        "engine_subtype": "whisper",
        "language": "multi",
        "size_mb": 230,
        "url": f"{_SHERPA_BASE}/sherpa-onnx-whisper-tiny.tar.bz2",
        "archive_format": "tar.bz2",
        "extracted_dir": "sherpa-onnx-whisper-tiny",
        "files": {
            "encoder": "tiny-encoder.int8.onnx",
            "decoder": "tiny-decoder.int8.onnx",
            "tokens": "tiny-tokens.txt",
        },
        "needs_term_replace": False,
        "needs_punctuation": False,
        "description": "Самая лёгкая Whisper. Быстрая, качество среднее. 99+ языков.",
    },
    "whisper-base": {
        "name": "Whisper Base (мультиязык)",
        "engine": "sherpa-onnx",
        "engine_subtype": "whisper",
        "language": "multi",
        "size_mb": 290,
        "url": f"{_SHERPA_BASE}/sherpa-onnx-whisper-base.tar.bz2",
        "archive_format": "tar.bz2",
        "extracted_dir": "sherpa-onnx-whisper-base",
        "files": {
            "encoder": "base-encoder.int8.onnx",
            "decoder": "base-decoder.int8.onnx",
            "tokens": "base-tokens.txt",
        },
        "needs_term_replace": False,
        "needs_punctuation": False,
        "description": "Whisper Base. Качество выше Tiny при близкой скорости.",
    },
    "whisper-small": {
        "name": "Whisper Small (мультиязык)",
        "engine": "sherpa-onnx",
        "engine_subtype": "whisper",
        "language": "multi",
        "size_mb": 640,
        "url": f"{_SHERPA_BASE}/sherpa-onnx-whisper-small.tar.bz2",
        "archive_format": "tar.bz2",
        "extracted_dir": "sherpa-onnx-whisper-small",
        "files": {
            "encoder": "small-encoder.int8.onnx",
            "decoder": "small-decoder.int8.onnx",
            "tokens": "small-tokens.txt",
        },
        "needs_term_replace": False,
        "needs_punctuation": False,
        "description": "Whisper Small. Хороший баланс качества и скорости.",
    },
    "whisper-medium": {
        "name": "Whisper Medium (мультиязык, тяжёлая)",
        "engine": "sherpa-onnx",
        "engine_subtype": "whisper",
        "language": "multi",
        "size_mb": 1900,
        "url": f"{_SHERPA_BASE}/sherpa-onnx-whisper-medium.tar.bz2",
        "archive_format": "tar.bz2",
        "extracted_dir": "sherpa-onnx-whisper-medium",
        "files": {
            "encoder": "medium-encoder.int8.onnx",
            "decoder": "medium-decoder.int8.onnx",
            "tokens": "medium-tokens.txt",
        },
        "needs_term_replace": False,
        "needs_punctuation": False,
        "description": (
            "Whisper Medium. Лучшее качество среди Whisper-вариантов, "
            "требует мощный ЦП и >2 ГБ ОЗУ."
        ),
        "tag": "Тяжёлая",
    },

    # ---------------- SenseVoice (East Asian + English) ----------------
    "sense-voice": {
        "name": "SenseVoice (zh/en/ja/ko/yue)",
        "engine": "sherpa-onnx",
        "engine_subtype": "sense-voice",
        "language": "multi",
        "size_mb": 230,
        "url": f"{_SHERPA_BASE}/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09.tar.bz2",
        "archive_format": "tar.bz2",
        "extracted_dir": "sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09",
        "files": {
            "model": "model.int8.onnx",
            "tokens": "tokens.txt",
        },
        "needs_term_replace": False,
        "needs_punctuation": False,
        "description": (
            "Быстрая модель для китайского, английского, японского, "
            "корейского и кантонского."
        ),
    },
}


DEFAULT_MODEL_ID = "vosk-ru-small"
RECOMMENDED_MODEL_ID = "gigaam-v3-ctc-punct"


def model_dir(model_id: str) -> str:
    """Absolute path where the model's extracted folder should live."""
    return os.path.join(get_models_dir(), MODELS[model_id]["extracted_dir"])


def is_installed(model_id: str) -> bool:
    """A model is installed if its extracted_dir exists on disk."""
    if model_id not in MODELS:
        return False
    return os.path.isdir(model_dir(model_id))


def resolved_files(model_id: str) -> dict[str, str]:
    """Return absolute paths for the model's files dict."""
    base = model_dir(model_id)
    return {key: os.path.join(base, rel) for key, rel in MODELS[model_id]["files"].items()}
