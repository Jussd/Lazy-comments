"""
Push-to-talk worker: keyboard hook + microphone capture + transcription.
"""
from __future__ import annotations
import queue, sys, threading, time, requests
import keyboard, numpy as np, pyperclip, sounddevice as sd, winsound
from lazy_comments.config import (AUTO_PASTE, ENABLE_BEEPS, MIN_RECORD_MS, SAMPLE_RATE,
                           get_hotkey_display, initial_hotkey, load_config)
from lazy_comments.engines import build_engine
from lazy_comments.punctuation import add_punctuation, replace_terms
from lazy_comments.registry import MODELS

_engine: object = None
_engine_lock = threading.Lock()
_active_model_id: str | None = None
_audio_queue: queue.Queue = queue.Queue()
_recording = False
_record_start_time = 0.0
_suppress_until = 0.0
HOTKEY = initial_hotkey()

# ──────────────────────────────────────────
# Translation
# ──────────────────────────────────────────
TRANSLATE_ENABLED = True

def translate_text(text: str, source_lang: str = None, target_lang: str = None) -> str:
    """Translate text using DeepL API with configurable languages."""
    cfg = load_config()
    api_key = cfg.get("deepl_api_key", "").strip()

    if not api_key:
        print("[TRANS] No DeepL API key configured, skipping translation")
        return text

    if not TRANSLATE_ENABLED:
        return text

    if source_lang is None:
        source_lang = cfg.get("source_lang", "ru")
    if target_lang is None:
        target_lang = cfg.get("target_lang", "en")

    # DeepL language code mapping
    DEEPL_LANGS = {
        "ru": "RU", "uk": "UK", "en": "EN-US", "en-gb": "EN-GB",
        "de": "DE", "fr": "FR", "es": "ES", "it": "IT", "nl": "NL",
        "pl": "PL", "pt": "PT", "ja": "JA", "zh": "ZH",
    }
    deep_src = DEEPL_LANGS.get(source_lang.lower(), source_lang.upper())
    deep_tgt = DEEPL_LANGS.get(target_lang.lower(), target_lang.upper())

    try:
        url = "https://api-free.deepl.com/v2/translate"
        headers = {"Authorization": f"DeepL-Auth-Key {api_key}", "Content-Type": "application/json"}
        data = {
            "text": [text],
            "source_lang": deep_src,
            "target_lang": deep_tgt,
        }
        r = requests.post(url, headers=headers, json=data, timeout=15)
        print(f"[TRANS] HTTP {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            translations = result.get("translations", [])
            if translations:
                return translations[0].get("text", text)
        else:
            print(f"[TRANS] API error: {r.text}")
    except Exception as e:
        print(f"[TRANS] Exception: {e}")
    return text


# ──────────────────────────────────────────
# Engine management
# ──────────────────────────────────────────
def set_engine(model_id: str) -> None:
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
    global HOTKEY
    HOTKEY = event_name

# ──────────────────────────────────────────
# Audio
# ──────────────────────────────────────────
def _beep_start():
    if ENABLE_BEEPS:
        winsound.Beep(800, 80)

def _beep_stop():
    if ENABLE_BEEPS:
        winsound.Beep(500, 80)

def _audio_callback(indata, frames, time_info, status):
    if status:
        print(f"[AUDIO] {status}", file=sys.stderr)
    if _recording:
        _audio_queue.put(indata.copy())

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

# ──────────────────────────────────────────
# Keyboard hook
# ──────────────────────────────────────────
def _on_event(event):
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

    # Post-processing
    info = MODELS.get(_active_model_id or "", {})
    if info.get("needs_term_replace", True):
        text = replace_terms(text)
    if info.get("needs_punctuation", True):
        text = add_punctuation(text)

    print(f'[STT] "{text}"')

    # ── TRANSLATE HERE ──
    text_en = translate_text(text)
    print(f'[TRANS] Final: "{text_en}"')

    pyperclip.copy(text_en)
    print("[CLIP] Copied to clipboard")

    if AUTO_PASTE:
        _suppress_until = time.time() + 0.2
        time.sleep(0.05)
        keyboard.send("ctrl+v")
        print("[PASTE] Pasted")

# ──────────────────────────────────────────
# Worker entry point
# ──────────────────────────────────────────
def run(initial_model_id: str) -> None:
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
            samplerate=SAMPLE_RATE, blocksize=4000, dtype="int16",
            channels=1, callback=_audio_callback,
        ):
            print("=" * 50)
            print(" Lazy Comments — Voice Input + Translation")
            print("=" * 50)
            print(f" Model:      {initial_model_id}")
            print(f" Hotkey:     [{get_hotkey_display(HOTKEY).upper()}] (hold to record)")
            print(f" Auto-paste: {AUTO_PASTE}")
            print(f" Beeps:      {ENABLE_BEEPS}")
            print("=" * 50)
            print("Ready. Hold the hotkey and speak.")
            keyboard.wait()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
