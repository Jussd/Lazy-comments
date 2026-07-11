"""
Paths, config.json read/write, and the hotkey choices list.

Lives in %APPDATA%\\lazy_comments\\ for frozen builds, next to the script otherwise.
"""

from __future__ import annotations

import json
import os
import sys


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_HOTKEY = "right alt"
DEFAULT_SOURCE_LANG = "ru"
DEFAULT_TARGET_LANG = "en"
SAMPLE_RATE = 16000
MIN_RECORD_MS = 250
ENABLE_BEEPS = True
AUTO_PASTE = True


# ---------------------------------------------------------------------------
# Hotkey catalog (display name, event.name as emitted by `keyboard` lib)
# ---------------------------------------------------------------------------

HOTKEY_CHOICES = [
    ("Правый Ctrl",  "right ctrl"),
    ("Левый Ctrl",   "ctrl"),
    ("Правый Shift", "right shift"),
    ("Левый Shift",  "shift"),
    ("Правый Alt",   "right alt"),
    ("Левый Alt",    "alt"),
    ("Caps Lock",    "caps lock"),
    ("Scroll Lock",  "scroll lock"),
    ("Pause",        "pause"),
    *[(f"F{i}", f"f{i}") for i in range(1, 13)],
]
VALID_HOTKEYS = {evt for _, evt in HOTKEY_CHOICES}


def get_hotkey_display(event_name: str) -> str:
    """Human-readable label for an event.name; falls back to upper()."""
    for display, evt in HOTKEY_CHOICES:
        if evt == event_name:
            return display
    return event_name.upper() if event_name else "<unknown>"


# ---------------------------------------------------------------------------
# Filesystem paths
# ---------------------------------------------------------------------------

def _appdata_root() -> str:
    """Per-user data root (frozen: %APPDATA%\\lazy_comments, otherwise: project dir)."""
    if getattr(sys, "frozen", False):
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "lazy_comments")
    # Dev mode: keep state right next to the source for easy inspection.
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_models_dir() -> str:
    return os.path.join(_appdata_root(), "models")


def get_log_dir() -> str:
    return os.path.join(_appdata_root(), "logs")


def get_config_path() -> str:
    return os.path.join(_appdata_root(), "config.json")


# ---------------------------------------------------------------------------
# Config I/O
# ---------------------------------------------------------------------------

def load_config() -> dict:
    """Read config from disk; return {} on missing/corrupt file."""
    path = get_config_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {}


def save_config(config: dict) -> None:
    """Atomically write config to disk."""
    path = get_config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, path)


def update_config(**changes) -> dict:
    """Read-modify-write helper. Returns the updated config dict."""
    cfg = load_config()
    cfg.update(changes)
    save_config(cfg)
    return cfg


# ---------------------------------------------------------------------------
# Resolved settings used by the worker on startup
# ---------------------------------------------------------------------------

def initial_hotkey() -> str:
    raw = load_config().get("hotkey", DEFAULT_HOTKEY)
    if isinstance(raw, str) and raw in VALID_HOTKEYS:
        return raw
    return DEFAULT_HOTKEY
