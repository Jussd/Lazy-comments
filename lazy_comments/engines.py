"""
Speech recognition engines.

Two backends: Vosk (Kaldi-based, classic) and sherpa-onnx (covers Whisper,
NeMo CTC/Transducer like GigaAM and Parakeet, SenseVoice, Moonshine).

Both engines take int16 PCM mono at SAMPLE_RATE Hz and return text.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from abc import ABC, abstractmethod

import numpy as np

from lazy_comments.config import SAMPLE_RATE
from lazy_comments.registry import MODELS, model_dir, resolved_files


# ---------------------------------------------------------------------------
# Path safety helper (Vosk + sherpa-onnx both can choke on non-ASCII paths
# on Windows because their C cores receive narrow-char strings).
# ---------------------------------------------------------------------------

def _ascii_safe_path(original_path: str, cache_subdir: str) -> str:
    """If `original_path` is non-ASCII, mirror it into %TEMP%/<cache_subdir>."""
    try:
        original_path.encode("ascii")
        return original_path
    except UnicodeEncodeError:
        pass

    cache_base = os.path.join(tempfile.gettempdir(), cache_subdir)
    safe_path = os.path.join(cache_base, os.path.basename(original_path))

    if os.path.isdir(safe_path):
        # Assume it's valid if a marker file is present; lightweight check.
        return safe_path

    print(f"[INIT] Path contains non-ASCII; copying model to {safe_path}")
    if os.path.exists(safe_path):
        shutil.rmtree(safe_path)
    shutil.copytree(original_path, safe_path)
    return safe_path


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class Engine(ABC):
    """Stateful recognizer wrapping one loaded model."""

    name: str = "base"

    @abstractmethod
    def transcribe(self, pcm_int16: np.ndarray) -> str:
        """Take 1-D int16 PCM @ SAMPLE_RATE Hz and return recognised text."""

    def unload(self) -> None:
        """Release resources. Default: no-op (GC handles it)."""


# ---------------------------------------------------------------------------
# Vosk
# ---------------------------------------------------------------------------

class VoskEngine(Engine):
    name = "vosk"

    def __init__(self, model_dir_path: str):
        from vosk import KaldiRecognizer, Model, SetLogLevel  # lazy import
        SetLogLevel(-1)
        safe = _ascii_safe_path(model_dir_path, "vosk_models")
        print(f"[INIT] Loading Vosk model: {safe}")
        self._Model = Model
        self._KaldiRecognizer = KaldiRecognizer
        self._model = Model(safe)
        print("[INIT] Vosk model loaded")

    def transcribe(self, pcm_int16: np.ndarray) -> str:
        recognizer = self._KaldiRecognizer(self._model, SAMPLE_RATE)
        recognizer.AcceptWaveform(pcm_int16.tobytes())
        final = json.loads(recognizer.FinalResult())
        return final.get("text", "").strip()

    def unload(self) -> None:
        self._model = None


# ---------------------------------------------------------------------------
# sherpa-onnx
# ---------------------------------------------------------------------------

class SherpaEngine(Engine):
    name = "sherpa-onnx"

    def __init__(self, model_id: str):
        import sherpa_onnx  # lazy import

        info = MODELS[model_id]
        subtype = info["engine_subtype"]
        base = _ascii_safe_path(model_dir(model_id), "sherpa_models")
        # Build a `files` dict with paths inside the safe-copied base.
        files = {key: os.path.join(base, rel)
                 for key, rel in info["files"].items()}

        print(f"[INIT] Loading sherpa-onnx model ({subtype}): {model_id}")

        cpu_threads = max(1, (os.cpu_count() or 4) // 2)

        if subtype == "nemo-ctc":
            self._recognizer = sherpa_onnx.OfflineRecognizer.from_nemo_ctc(
                model=files["model"],
                tokens=files["tokens"],
                num_threads=cpu_threads,
                sample_rate=SAMPLE_RATE,
                feature_dim=80,
                provider="cpu",
            )
        elif subtype == "nemo-transducer":
            self._recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
                encoder=files["encoder"],
                decoder=files["decoder"],
                joiner=files["joiner"],
                tokens=files["tokens"],
                num_threads=cpu_threads,
                sample_rate=SAMPLE_RATE,
                feature_dim=80,
                model_type="nemo_transducer",
                provider="cpu",
            )
        elif subtype == "whisper":
            self._recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
                encoder=files["encoder"],
                decoder=files["decoder"],
                tokens=files["tokens"],
                num_threads=cpu_threads,
                provider="cpu",
                language="",      # auto-detect
                task="transcribe",
            )
        elif subtype == "sense-voice":
            self._recognizer = sherpa_onnx.OfflineRecognizer.from_sense_voice(
                model=files["model"],
                tokens=files["tokens"],
                num_threads=cpu_threads,
                use_itn=True,
                language="auto",
                provider="cpu",
            )
        elif subtype == "moonshine":
            self._recognizer = sherpa_onnx.OfflineRecognizer.from_moonshine(
                preprocessor=files["preprocessor"],
                encoder=files["encoder"],
                uncached_decoder=files["uncached_decoder"],
                cached_decoder=files["cached_decoder"],
                tokens=files["tokens"],
                num_threads=cpu_threads,
                provider="cpu",
            )
        else:
            raise ValueError(f"Unsupported sherpa-onnx subtype: {subtype}")

        print(f"[INIT] sherpa-onnx model loaded ({subtype})")

    def transcribe(self, pcm_int16: np.ndarray) -> str:
        # sherpa-onnx expects float32 normalised to [-1, 1]
        samples = pcm_int16.astype(np.float32) / 32768.0
        stream = self._recognizer.create_stream()
        stream.accept_waveform(SAMPLE_RATE, samples)
        self._recognizer.decode_stream(stream)
        return (stream.result.text or "").strip()

    def unload(self) -> None:
        self._recognizer = None


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_engine(model_id: str) -> Engine:
    """Construct the right Engine instance for the given catalog entry."""
    if model_id not in MODELS:
        raise KeyError(f"Unknown model id: {model_id}")
    info = MODELS[model_id]
    eng_type = info["engine"]
    if eng_type == "vosk":
        return VoskEngine(model_dir(model_id))
    if eng_type == "sherpa-onnx":
        return SherpaEngine(model_id)
    raise ValueError(f"Unknown engine type: {eng_type}")
