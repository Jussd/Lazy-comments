# -*- coding: utf-8 -*-
"""
DE -> EN улучшенный словарь крипто-сленга (Немецкий язык).

Логика разделена на 3 уровня:
1. NUMERIC_PATTERNS — обработка связок чисел от STT (например, "5 x" -> "5x gains").
2. TICKERS_AND_ACRONYMS — строгий регистрозависимый перевод (SOL, DOT, ATH), чтобы не ломать обычные немецкие слова.
3. SLANG — регистронезависимый перевод немецкого крипто-сленга и Denglisch-глаголов (holden, shorten, gepumpt).
"""

import re

# === УРОВЕНЬ 1: Паттерны для числительных от STT (Число + Множитель) ===
NUMERIC_PATTERNS = {
    r'(\d+)\s*fach': r'\1x gains',
    r'(\d+)\s*x': r'\1x gains',
}

# === УРОВЕНЬ 2: Строго регистрозависимые тикеры и аббревиатуры ===
TICKERS_AND_ACRONYMS = {
    'SOL': 'SOL',  # Защита от пересечений в нижнем регистре
    'DOT': 'DOT',  # Защищает английское/немецкое слово "dot" (точка)
    'ATH': 'ATH',
    'BTC': 'BTC',
    'ETH': 'ETH',
    'FUD': 'FUD',
    'FOMO': 'FOMO',
}

# === УРОВЕНЬ 3: Регистронезависимый немецкий крипто-сленг и Denglisch ===
SLANG = {
    # --- hold / HODL ---
    'geholdet': 'held',
    'gehodlet': 'HODLed',
    'holden': 'hold',
    'hodlen': 'HODL',
    'hodler': 'HODLer',
    'holder': 'HODLer',
    'hodl': 'HODL',

    # --- dump ---
    'abverkauf': 'sell-off',
    'gedumpt': 'dumped',
    'dumpen': 'dump',
    'dump': 'dump',

    # --- pump ---
    'pump and dump': 'pump and dump',
    'gepumpt': 'pumped',
    'pumpen': 'pump',
    'pump': 'pump',

    # --- short / long ---
    'geshortet': 'shorted',
    'gelongt': 'longed',
    'shorten': 'short',
    'longen': 'long',
    'short': 'short',
    'long': 'long',

    # --- market participants ---
    'kleinanleger': 'retail investors',
    'bagholder': 'bagholder',
    'walen': 'whales',
    'wale': 'whales',
    'wal': 'whale',
    'degen': 'degen',

    # --- bull / bear ---
    'bärenmarkt': 'bear market',
    'bullenmarkt': 'bull market',
    'bärenfalle': 'bear trap',
    'bullenfalle': 'bull trap',
    'bullrun': 'bull run',
    'bearish': 'bearish',
    'bullish': 'bullish',
    'bullen': 'bulls',
    'bären': 'bears',
    'bulle': 'bull',
    'bär': 'bear',

    # --- hands ---
    'diamantenhände': 'diamond hands',
    'papierhände': 'paper hands',

    # --- hype / scam ---
    'teppichzieher': 'rug pull',  # Шутливый дословный перевод мем-термина
    'rugpull': 'rug pull',
    'betrug': 'scam',
    'scam': 'scam',

    # --- moon / crash slang ---
    'allzeithoch': 'ATH',
    'zum mond': 'to the moon',
    'shitcoin': 'shitcoin',
    'memecoin': 'memecoin',
    'lambo': 'lambo',
    'rekt': 'rekt',

    # --- TA ---
    'korrektur': 'correction',
    'widerstand': 'resistance',
    'unterstützung': 'support',
    'ausbruch': 'breakout',
    'pullback': 'pullback',
    'boden': 'bottom',
    'top': 'top',

    # --- leverage / liquidation ---
    'geliquidiert': 'liquidated',
    'liquidiert': 'liquidated',
    'margin call': 'margin call',
    'hebel': 'leverage',
    'all in': 'all in',
    'liquidierung': 'liquidation',

    # --- earn / farm ---
    'gestakt': 'staked',
    'staken': 'stake',
    'staking': 'staking',
    'farming': 'farming',
    'farmen': 'farm',

    # --- airdrop / listing ---
    'gelistet': 'listed',
    'delistet': 'delisted',
    'airdrop': 'airdrop',
    'listing': 'listing',
    'presale': 'presale',

    # --- infra ---
    'cold wallet': 'cold wallet',
    'hot wallet': 'hot wallet',
    'smart contract': 'smart contract',
    'seed phrase': 'seed phrase',
    'private key': 'private key',
    'halving': 'halving',
    'wallet': 'wallet',
    'gebühr': 'fee',
    'gebühren': 'fees',
    'gas': 'gas',

    # --- project / meta ---
    'insider-infos': 'insider info',
    'market maker': 'market maker',
    'tokenomik': 'tokenomics',
    'tokenomics': 'tokenomics',
    'roadmap': 'roadmap',
    'weißbuch': 'whitepaper',
    'whitepaper': 'whitepaper',
    'unlock': 'unlock',
    'manipulation': 'manipulation',
    'volatilität': 'volatility',
    'profit': 'profit',
    'verlust': 'losses',
    'vesting': 'vesting',
}


def translate(text: str) -> str:
    """Заменяет немецкий крипто-сленг на английские термины с защитой контекста."""
    result = text

    # Этап 1: Обработка паттернов количества от STT (safest)
    for pattern, replacement in NUMERIC_PATTERNS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Этап 2: Строго регистрозависимые тикеры и аббревиатуры (БЕЗ ignorecase)
    for ticker, full_name in TICKERS_AND_ACRONYMS.items():
        pattern = r'(?<!\w)' + re.escape(ticker) + r'(?!\w)'
        result = re.sub(pattern, full_name, result)

    # Этап 3: Регистронезависимый общий немецкий сленг (сортировка по длине)
    for slang, replacement in sorted(SLANG.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r'(?<!\w)' + re.escape(slang) + r'(?!\w)'
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


if __name__ == '__main__':
    # Тестовые сценарии
    test_1 = "Ich werde meine BTC holden, weil die wale den Markt gepumpt haben."
    test_2 = "Gestern haben wir ein neues Allzeithoch erreicht, jetzt haben die degen FOMO."
    
    print("Тест 1:")
    print(translate(test_1))
    print("\nТест 2:")
    print(translate(test_2))