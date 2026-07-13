# -*- coding: utf-8 -*-
"""
FR -> EN улучшенный словарь крипто-сленга (Французский язык).

Логика разделена на 3 уровня:
1. NUMERIC_PATTERNS — обработка связок чисел от STT (например, "5 fois" -> "5x gains").
2. TICKERS_AND_ACRONYMS — строгий регистрозависимый перевод (SOL, DOT, ATH), чтобы не ломать обычные французские слова.
3. SLANG — регистронезависимый перевод французского крипто-сленга и Franglais-глаголов (holder, shorter, liquidé).
"""

import re

# === УРОВЕНЬ 1: Паттерны для числительных от STT (Число + Множитель) ===
NUMERIC_PATTERNS = {
    r'(\d+)\s*fois': r'\1x gains',
    r'(\d+)\s*x': r'\1x gains',
}

# === УРОВЕНЬ 2: Строго регистрозависимые тикеры и аббревиатуры ===
TICKERS_AND_ACRONYMS = {
    'SOL': 'SOL',  # Защищает обычные слова от ложной замены токеном Solana
    'DOT': 'DOT',  # Защищает английское/французское слово "dot" (точка)
    'ATH': 'ATH',
    'BTC': 'BTC',
    'ETH': 'ETH',
    'FUD': 'FUD',
    'FOMO': 'FOMO',
}

# === УРОВЕНЬ 3: Регистронезависимый французский крипто-сленг и Franglais ===
SLANG = {
    # --- hold / HODL ---
    'holdé': 'held',
    'hodlé': 'HODLed',
    'holder': 'hold',
    'hodler': 'HODL',
    'hodl': 'HODL',
    'garder': 'hold',

    # --- dump ---
    'dumpé': 'dumped',
    'dumper': 'dump',
    'vente massive': 'sell-off',
    'dump': 'dump',

    # --- pump ---
    'pump and dump': 'pump and dump',
    'pumpé': 'pumped',
    'pumper': 'pump',
    'gonfler': 'pump',
    'pump': 'pump',

    # --- short / long ---
    'shorter': 'short',
    'shorté': 'shorted',
    'longer': 'long',
    'longé': 'longed',
    'en court': 'short',
    'en long': 'long',

    # --- market participants ---
    'petits investisseurs': 'retail investors',
    'bagholder': 'bagholder',
    'baleines': 'whales',
    'crevette': 'shrimp',
    'baleine': 'whale',
    'degen': 'degen',

    # --- bull / bear ---
    'marché baissier': 'bear market',
    'marché haussier': 'bull market',
    'piège à ours': 'bear trap',
    'piège à taureaux': 'bull trap',
    'bullrun': 'bull run',
    'bearish': 'bearish',
    'bullish': 'bullish',
    'taureaux': 'bulls',
    'ours': 'bears',

    # --- hands ---
    'mains de diamant': 'diamond hands',
    'mains de papier': 'paper hands',

    # --- hype / scam ---
    'tirage de tapis': 'rug pull',  # Дословный перевод мем-термина
    'rugpull': 'rug pull',
    'arnaque': 'scam',
    'scam': 'scam',

    # --- moon / crash slang ---
    'plus haut historique': 'ATH',
    'jusqu\'à la lune': 'to the moon',
    'shitcoin': 'shitcoin',
    'memecoin': 'memecoin',
    'lambo': 'lambo',
    'rekt': 'rekt',

    # --- TA ---
    'correction': 'correction',
    'résistance': 'resistance',
    'support': 'support',
    'cassure': 'breakout',
    'pullback': 'pullback',
    'bas': 'bottom',
    'sommet': 'top',

    # --- leverage / liquidation ---
    'appel de marge': 'margin call',
    'liquidé': 'liquidated',
    'effet de levier': 'leverage',
    'liquidation': 'liquidation',
    'all in': 'all in',

    # --- earn / farm ---
    'staké': 'staked',
    'staker': 'stake',
    'staking': 'staking',
    'farming': 'farming',
    'farmer': 'farm',

    # --- airdrop / listing ---
    'listé': 'listed',
    'déréférencé': 'delisted',
    'airdrop': 'airdrop',
    'listing': 'listing',
    'presale': 'presale',

    # --- infra ---
    'cold wallet': 'cold wallet',
    'hot wallet': 'hot wallet',
    'contrat intelligent': 'smart contract',
    'phrase de récupération': 'seed phrase',
    'phrase graine': 'seed phrase',
    'clé privée': 'private key',
    'halving': 'halving',
    'portefeuille': 'wallet',
    'frais': 'fee',
    'gas': 'gas',

    # --- project / meta ---
    'délit d\'initié': 'insider info',
    'teneur de marché': 'market maker',
    'tokenomics': 'tokenomics',
    'roadmap': 'roadmap',
    'livre blanc': 'whitepaper',
    'whitepaper': 'whitepaper',
    'unlock': 'unlock',
    'manipulation': 'manipulation',
    'volatilité': 'volatility',
    'profit': 'profit',
    'pertes': 'losses',
    'vesting': 'vesting',
}


def translate(text: str) -> str:
    """Заменяет французский крипто-сленг на английские термины с защитой контекста."""
    result = text

    # Этап 1: Обработка паттернов количества от STT (safest)
    for pattern, replacement in NUMERIC_PATTERNS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Этап 2: Строго регистрозависимые тикеры и аббревиатуры (БЕЗ ignorecase)
    for ticker, full_name in TICKERS_AND_ACRONYMS.items():
        pattern = r'(?<!\w)' + re.escape(ticker) + r'(?!\w)'
        result = re.sub(pattern, full_name, result)

    # Этап 3: Регистронезависимый общий французский сленг (сортировка по длине)
    for slang, replacement in sorted(SLANG.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r'(?<!\w)' + re.escape(slang) + r'(?!\w)'
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


if __name__ == '__main__':
    # Тестовые сценарии
    test_1 = "Je vais holder mes tokens parce que les baleines ont pumper le marché."
    test_2 = "Hier on a atteint un nouveau plus haut historique, j'ai hâte d'acheter du SOL."
    
    print("Тест 1:")
    print(translate(test_1))
    print("\nТест 2:")
    print(translate(test_2))