"""
Push-to-talk worker: keyboard hook + microphone capture + transcription.

The engine is held behind a lock so the tray can hot-swap models without
racing the transcribe path.
"""

from __future__ import annotations

import queue
import sys
import threading
import time

import keyboard
import numpy as np
import pyperclip
import sounddevice as sd
import winsound

from voxapp.config import (
    AUTO_PASTE,
    ENABLE_BEEPS,
    MIN_RECORD_MS,
    SAMPLE_RATE,
    get_hotkey_display,
    initial_hotkey,
)
from voxapp.engines import Engine, build_engine
from voxapp.punctuation import add_punctuation, replace_terms
from voxapp.registry import MODELS


# ---------------------------------------------------------------------------
# Module-level state (mutated by tray callbacks too)
# ---------------------------------------------------------------------------

_engine: Engine | None = None
_engine_lock = threading.Lock()
_active_model_id: str | None = None

_audio_queue: queue.Queue = queue.Queue()
_recording = False
_record_start_time = 0.0
_suppress_until = 0.0  # timestamp until which keyboard events are ignored

HOTKEY = initial_hotkey()


# ---------------------------------------------------------------------------
# Engine management (called from tray / GUI)
# ---------------------------------------------------------------------------

def set_engine(model_id: str) -> None:
    """Atomically swap the active engine. Blocks until the new one is loaded."""
    global _engine, _active_model_id
    new_engine = build_engine(model_id)
    with _engine_lock:
        old = _engine
        _engine = new_engine
        _active_model_id = model_id
    if old is not None:
        try:
            old.unload()
        except Exception:
            pass


def get_active_model_id() -> str | None:
    return _active_model_id


def set_hotkey(event_name: str) -> None:
    """Change the push-to-talk key at runtime."""
    global HOTKEY
    HOTKEY = event_name


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------

def _beep_start() -> None:
    if ENABLE_BEEPS:
        winsound.Beep(800, 80)


def _beep_stop() -> None:
    if ENABLE_BEEPS:
        winsound.Beep(500, 80)


def _audio_callback(indata, frames, time_info, status):
    if status:
        print(f"[AUDIO] {status}", file=sys.stderr)
    if _recording:
        _audio_queue.put(indata.copy())


# ---------------------------------------------------------------------------
# Transcription
# ---------------------------------------------------------------------------

def _drain_audio() -> np.ndarray | None:
    chunks = []
    while not _audio_queue.empty():
        try:
            chunks.append(_audio_queue.get_nowait())
        except queue.Empty:
            break
    if not chunks:
        return None
    audio = np.concatenate(chunks).flatten()
    if np.max(np.abs(audio)) < 100:
        return None
    return audio


def _transcribe() -> str:
    audio = _drain_audio()
    if audio is None:
        return ""
    with _engine_lock:
        engine = _engine
    if engine is None:
        print("[STT] No engine loaded")
        return ""
    return engine.transcribe(audio)


# ---------------------------------------------------------------------------
# Keyboard hook
# ---------------------------------------------------------------------------

def _on_event(event):
    """Dispatch only when event.name matches the configured HOTKEY."""
    if time.time() < _suppress_until:
        return
    if event.name != HOTKEY:
        return
    if event.event_type == keyboard.KEY_DOWN:
        _on_key_press(event)
    elif event.event_type == keyboard.KEY_UP:
        _on_key_release(event)


def _on_key_press(event):
    global _recording, _record_start_time
    if _recording:
        return
    # Drop stale audio
    while not _audio_queue.empty():
        try:
            _audio_queue.get_nowait()
        except queue.Empty:
            break
    _record_start_time = time.time()
    _recording = True
    _beep_start()
    print("[REC] Listening...")


def _on_key_release(event):
    global _recording, _suppress_until
    if not _recording:
        return
    _recording = False
    elapsed_ms = (time.time() - _record_start_time) * 1000
    _beep_stop()

    if elapsed_ms < MIN_RECORD_MS:
        print(f"[REC] Too short ({elapsed_ms:.0f}ms), ignored")
        return

    print(f"[REC] Stopped ({elapsed_ms:.0f}ms), transcribing...")
    text = _transcribe()
    if not text:
        print("[STT] No speech recognized")
        return

    # Per-model post-processing
    info = MODELS.get(_active_model_id or "", {})
    if info.get("needs_term_replace", True):
        text = replace_terms(text)
    if info.get("needs_punctuation", True):
        text = add_punctuation(text)

    print(f'[STT] "{text}"')

    pyperclip.copy(text)
    print("[CLIP] Copied to clipboard")

    if AUTO_PASTE:
        # Don't let the synthetic ctrl+v re-trigger PTT when HOTKEY is ctrl
        _suppress_until = time.time() + 0.2
        time.sleep(0.05)
        keyboard.send("ctrl+v")
        print("[PASTE] Pasted")


# ---------------------------------------------------------------------------
# Worker entry point (runs in background thread)
# ---------------------------------------------------------------------------

def run(initial_model_id: str) -> None:
    """Load the engine, hook keyboard, open the mic, block forever."""
    print(f"[INIT] Active model: {initial_model_id}")
    try:
        set_engine(initial_model_id)
    except Exception as e:
        print(f"[FATAL] Failed to load engine for {initial_model_id}: {e}")
        import traceback
        traceback.print_exc()
        return

    keyboard.hook(_on_event)
    print(f"[INIT] Opening microphone ({SAMPLE_RATE} Hz)")

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=4000,
            dtype="int16",
            channels=1,
            callback=_audio_callback,
        ):
            print("=" * 50)
            print(" Vox — Voice Input")
            print("=" * 50)
            print(f" Model:      {initial_model_id}")
            print(f" Hotkey:     [{get_hotkey_display(HOTKEY).upper()}] (hold to record)")
            print(f" Auto-paste: {AUTO_PASTE}")
            print(f" Beeps:      {ENABLE_BEEPS}")
            print("=" * 50)
            print("Ready. Hold the hotkey and speak.")
            keyboard.wait()  # blocks forever
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
