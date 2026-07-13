"""
Per-language slang dictionaries (IT + crypto).

For every supported language ``xx`` there are two modules inside this
package:

    it_xx.py       - Russian/native -> English IT/dev slang
    crypto_xx.py   - Russian/native -> English crypto slang

Each module exposes a ``translate(text)`` function (regex-based, word-boundary
safe, case-insensitive). ``apply_terms(text)`` reads the user's ``source_lang``
from the app config and applies BOTH dictionaries for that language (IT first,
then crypto). Languages without a dictionary pass through unchanged.
"""

from __future__ import annotations

import importlib
import sys

from lazy_comments.config import load_config

# Map app language codes (config.source_lang / GUI LANGS list) to the
# language suffix used in the module file names (it_xx.py / crypto_xx.py).
_LANG_SUFFIX = {
    "ru": "ru",
    "ru-ru": "ru",
    "de": "de",
    "es": "es",
    "fr": "fr",
    "zh": "zh",
    "zh-cn": "zh",
    "zh-tw": "zh",
}

# (it_module, crypto_module) per language suffix
_PAIRS = {
    "ru": ("it_ru", "crypto_ru"),
    "de": ("it_de", "crypto_de"),
    "es": ("it_es", "crypto_es"),
    "fr": ("it_fr", "crypto_fr"),
    "zh": ("it_cn", "crypto_cn"),
}

_cache: dict[str, list] = {}


def _load_pair(lang: str):
    """Return a list of ``translate`` callables for `lang` (may be empty)."""
    if lang in _cache:
        return _cache[lang]
    suffix = _LANG_SUFFIX.get(lang.lower())
    funcs = []
    if suffix:
        for mod_name in _PAIRS.get(suffix, ()):
            try:
                mod = importlib.import_module(f"lazy_comments.terms.{mod_name}")
                fn = getattr(mod, "translate", None)
                if fn is not None:
                    funcs.append(fn)
            except Exception as e:  # pragma: no cover - defensive
                print(f"[TERMS] Failed to load dict '{mod_name}': {e}")
    _cache[lang] = funcs
    return funcs


def apply_terms(text: str) -> str:
    """
    Apply the IT + crypto slang dictionaries for the user's configured
    source language. No-op (returns text unchanged) when the language has
    no dictionaries or text is empty.
    """
    if not text:
        return text
    cfg = load_config()
    lang = (cfg.get("source_lang") or "ru").lower()
    funcs = _load_pair(lang)
    if not funcs:
        return text
    result = text
    try:
        for fn in funcs:
            result = fn(result)
    except Exception as e:  # pragma: no cover - defensive
        print(f"[TERMS] translate failed: {e}")
        return text
    return result


def clear_cache() -> None:
    """Drop cached modules (e.g. after a config/language change)."""
    _cache.clear()
    for name in list(sys.modules):
        if name.startswith("lazy_comments.terms.") and name != __name__:
            del sys.modules[name]
