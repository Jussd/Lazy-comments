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