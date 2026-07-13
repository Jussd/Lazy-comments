# -*- coding: utf-8 -*-
"""
ES -> EN улучшенный словарь крипто-сленга (Испанский язык).

Логика разделена на 3 уровня:
1. NUMERIC_PATTERNS — обработка связок чисел от STT (например, "5 equis" -> "5x gains").
2. TICKERS_AND_ACRONYMS — строгий регистрозависимый перевод (SOL, DOT, ATH), чтобы не ломать обычные испанские слова.
3. SLANG — регистронезависимый перевод испанского крипто-сленга и Spanglish-глаголов (holdear, dumpear).
"""

import re

# === УРОВЕНЬ 1: Паттерны для числительных от STT (Число + Множитель) ===
NUMERIC_PATTERNS = {
    r'(\d+)\s*equis': r'\1x gains',
    r'(\d+)\s*veces': r'\1x gains',
}

# === УРОВЕНЬ 2: Строго регистрозависимые тикеры и аббревиатуры (Только точное совпадение) ===
TICKERS_AND_ACRONYMS = {
    'SOL': 'SOL',  # Защищает испанское слово "sol" (солнце) от ложной замены
    'DOT': 'DOT',  # Защищает английское слово "dot" (точка)
    'ATH': 'ATH',
    'BTC': 'BTC',
    'ETH': 'ETH',
    'FUD': 'FUD',
    'FOMO': 'FOMO',
}

# === УРОВЕНЬ 3: Регистронезависимый испанский крипто-сленг и Spanglish ===
SLANG = {
    # --- hold / HODL ---
    'holdeando': 'holding',
    'hodleando': 'HODLing',
    'holdear': 'hold',
    'hodlear': 'HODL',
    'aguantar': 'hold',
    'aguante': 'hold',
    'hodler': 'HODLer',
    'holder': 'HODLer',
    'hodl': 'HODL',
    'jodl': 'HODL',

    # --- dump ---
    'dumpeado': 'dumped',
    'tirar la moneda': 'dump',
    'dumpear': 'dump',
    'dumpeo': 'dump',
    'dump': 'dump',

    # --- pump ---
    'pump and dump': 'pump and dump',
    'inflar y deshacerse': 'pump and dump',
    'pumpear': 'pump',
    'pumpeo': 'pump',
    'bombeo': 'pump',
    'inflar': 'pump',
    'pump': 'pump',

    # --- short / long ---
    'vender en corto': 'short',
    'prendre corto': 'short',
    'position corta': 'short position',
    'shortear': 'short',
    'shorteo': 'short',
    'en corto': 'short',
    'ir largo': 'go long',
    'irse largo': 'go long',
    'en largo': 'long',

    # --- market participants ---
    'quedarse con la bolsa': 'bagholding',
    'degenerado': 'degen',
    'pececillo': 'minnow',
    'bagholder': 'bagholder',
    'ballenas': 'whales',
    'camarón': 'shrimp',
    'camaron': 'shrimp',
    'ballena': 'whale',
    'delfín': 'dolphin',
    'delfin': 'dolphin',
    'dege': 'degen',
    'pez': 'fish',

    # --- bull / bear ---
    'mercado bajista': 'bear market',
    'mercado alcista': 'bear market',
    'trampa para osos': 'bear trap',
    'trampa para toros': 'bull trap',
    'corrida de toro': 'bull run',
    'bull run': 'bull run',
    'bajista': 'bearish',
    'alcista': 'bullish',
    'toros': 'bulls',
    'osos': 'bears',
    'toro': 'bull',
    'oso': 'bear',

    # --- hands ---
    'manos de diamante': 'diamond hands',
    'manos de papel': 'paper hands',

    # --- hype / scam ---
    'tiron de alfombra': 'rug pull',
    'tirón de alfombra': 'rug pull',
    'rugpull': 'rug pull',
    'estafa': 'scam',
    'scam': 'scam',

    # --- moon / crash slang ---
    'maximo historico': 'ATH',
    'máximo histórico': 'ATH',
    'me rektearon': 'got rekt',
    'moneda basura': 'shitcoin',
    'a la luna': 'to the moon',
    'shitcoin': 'shitcoin',
    'memecoin': 'memecoin',
    'moonear': 'moon',
    'despegar': 'moon',
    'lambo': 'lambo',
    'rekt': 'rekt',
    'volar': 'moon',

    # --- TA ---
    'correccion': 'correction',
    'corrección': 'correction',
    'resistencia': 'resistance',
    'retroceso': 'pullback',
    'ruptura': 'breakout',
    'soporte': 'support',
    'rebote': 'bounce',
    'fondo': 'bottom',
    'techo': 'top',

    # --- leverage / liquidation ---
    'llamada de margen': 'margin call',
    'apalancamiento': 'leverage',
    'me liquidaron': 'got liquidated',
    'todo dentro': 'all in',
    'apostar todo': 'all in',
    'ir all in': 'go all in',
    'liquidacion': 'liquidation',
    'liquidación': 'liquidation',

    # --- earn / farm ---
    'staking': 'staking',
    'stakear': 'stake',
    'stakeo': 'staking',
    'farmear': 'farm',
    'farmeo': 'farming',

    # --- airdrop / listing ---
    'airdropear': 'airdrop',
    'delistado': 'delisted',
    'airdrop': 'airdrop',
    'listado': 'listing',
    'preventa': 'presale',

    # --- infra ---
    'billetera fria': 'cold wallet',
    'billetera fría': 'cold wallet',
    'billetera caliente': 'hot wallet',
    'contrato inteligente': 'smart contract',
    'reduccion a la mitad': 'halving',
    'reducción a la mitad': 'halving',
    'frase semilla': 'seed phrase',
    'clave privada': 'private key',
    'billetera': 'wallet',
    'monedero': 'wallet',
    'comision': 'fee',
    'comisión': 'fee',

    # --- project / meta ---
    'informacion privilegiada': 'insider info',
    'información privilegiada': 'insider info',
    'creador de mercado': 'market maker',
    'tokenomica': 'tokenomics',
    'tokenómica': 'tokenomics',
    'hoja de ruta': 'roadmap',
    'libro blanco': 'whitepaper',
    'desbloqueo': 'unlock',
    'manipulacion': 'manipulation',
    'manipulación': 'manipulation',
    'volatilidad': 'volatility',
    'ganancias': 'profit',
    'perdidas': 'losses',
    'pérdidas': 'losses',
    'vesting': 'vesting',
}


def translate(text: str) -> str:
    """Заменяет испанский крипто-сленг на английские термины с защитой контекста."""
    result = text

    # Этап 1: Обработка паттернов количества от STT (safest)
    for pattern, replacement in NUMERIC_PATTERNS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Этап 2: Строго регистрозависимые тикеры и аббревиатуры (БЕЗ ignorecase)
    for ticker, full_name in TICKERS_AND_ACRONYMS.items():
        pattern = r'(?<!\w)' + re.escape(ticker) + r'(?!\w)'
        result = re.sub(pattern, full_name, result)

    # Этап 3: Регистронезависимый общий испанский сленг (сортировка по длине)
    for slang, replacement in sorted(SLANG.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r'(?<!\w)' + re.escape(slang) + r'(?!\w)'
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


if __name__ == '__main__':
    # Тестовые сценарии
    test_1 = "Voy a holdear mi bitcoin, las ballenas estan pumpeando el alt y los peces tienen manos de papel."
    test_2 = "El sol está brillando hoy, pero yo prefiero comprar un poco de SOL y esperar que suba a la luna."
    
    print("Тест 1:")
    print(translate(test_1))
    print("\nТест 2:")
    print(translate(test_2))