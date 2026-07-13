# -*- coding: utf-8 -*-
"""
RU -> EN улучшенный словарь крипто-сленга.

Логика разделена на 3 уровня:
1. NUMERIC_PATTERNS — обработка связок чисел и активов от STT (например, "5 иксов" -> "5x gains").
2. TICKERS_AND_ACRONYMS — строгий регистрозависимый перевод (ATH, NFT), чтобы не ломать обычные английские слова.
3. SLANG — регистронезависимый перевод русского крипто-сленга с защитой границ слов.
"""

import re

# === УРОВЕНЬ 1: Паттерны для числительных от STT (Число + Ассет) ===
NUMERIC_PATTERNS = {
    r'(\d+)\s*икс(?:а|ов)?': r'\1x gains',
    r'(\d+)\s*битк(?:а|ов|и)?': r'\1 BTC',
    r'(\d+)\s*эфир(?:а|ов|ка)?': r'\1 ETH',
}

# === УРОВЕНЬ 2: Строго регистрозависимые тикеры и аббревиатуры (Только точное совпадение) ===
TICKERS_AND_ACRONYMS = {
    'ATH': 'ATH',
    'BTC': 'BTC',
    'ETH': 'ETH',
    'SOL': 'SOL',  # Теперь не превратит испанское/обычное слово "sol" (солнце) в токен
    'DOT': 'DOT',  # Не превратит английское слово "dot" (точка) в токен
}

# === УРОВЕНЬ 3: Регистронезависимый русский крипто-сленг ===
SLANG = {
    # --- hold / HODL ---
    'холдить': 'hold',
    'холднуть': 'hold',
    'холдим': 'holding',
    'холдеры': 'HODLers',
    'холдер': 'HODLer',
    'холд': 'hold',
    'ходлить': 'HODL',
    'ходлер': 'HODLer',
    'ходл': 'HODL',

    # --- dump ---
    'заdamпить': 'dump',
    'задампили': 'dumped',
    'дампить': 'dump',
    'задампить': 'dump',
    'слили': 'dumped',
    'слить': 'dump',
    'слив': 'sell-off',
    'дамп': 'dump',
    'думп': 'dump',

    # --- pump ---
    'запампили': 'pumped',
    'памп и дамп': 'pump and dump',
    'пампить': 'pump',
    'запампить': 'pump',
    'разогнать': 'pump',
    'разгон': 'pump',
    'памп': 'pump',
    'пид': 'P&D',

    # --- short / long ---
    'зашортить': 'short',
    'в шорте': 'short',
    'зайти в шорт': 'short',
    'шортить': 'short',
    'шорт': 'short',
    'лонговать': 'long',
    'залонговать': 'long',
    'в лонге': 'long',
    'закинуть в лонг': 'long',
    'кинуть в лонг': 'long',
    'лонг': 'long',

    # --- hype / scam ---
    'скам проект': 'scam project',
    'скамный': 'scammy',
    'рагпулл': 'rug pull',
    'раг пул': 'rug pull',
    'рагпул': 'rug pull',
    'хайп': 'hype',
    'скам': 'scam',

    # --- coins ---
    'альткоины': 'altcoins',
    'альткоин': 'altcoin',
    'шиткоин': 'shitcoin',
    'щиткоин': 'shitcoin',
    'стейблкоин': 'stablecoin',
    'стейбл': 'stablecoin',
    'альт': 'altcoin',
    'биток': 'Bitcoin',
    'битка': 'Bitcoin',
    'битки': 'Bitcoin',
    'сатоши': 'sats',
    'саты': 'sats',
    'шиток': 'shitcoin',
    'щиток': 'shitcoin',

    # --- market participants ---
    'хомячок': 'small retail investor',
    'хомяк': 'retail investor',
    'дегенерат': 'degen',
    'мешочник': 'bagholder',
    'киты': 'whales',
    'кит': 'whale',
    'деген': 'degen',
    'мешок': 'bag',

    # --- bull / bear ---
    'крабовый рынок': 'crab market',
    'боковик': 'sideways market',
    'бычий': 'bullish',
    'медвежий': 'bearish',
    'быки': 'bulls',
    'бык': 'bull',
    'медведи': 'bears',
    'медведь': 'bear',

    # --- hands ---
    'бриллиантовые руки': 'diamond hands',
    'алмазные руки': 'diamond hands',
    'бумажные руки': 'paper hands',
    'слабые руки': 'weak hands',

    # --- price action / TA ---
    'обновить хай': 'hit a new ATH',
    'рынок в крови': 'bloodbath',
    'хайpoit': 'ATH',
    'сопротивление': 'resistance',
    'поддержка': 'support',
    'коррекция': 'correction',
    'туземун': 'to the moon',
    'в космос': 'to the moon',
    'полетели': 'mooning',
    'пробой': 'breakout',
    'отскок': 'bounce',
    'откат': 'pullback',
    'пузырь': 'bubble',
    'ракета': 'rocket',
    'дно': 'bottom',
    'хай': 'high',

    # --- sentiment acronyms ---
    'дудосил': 'DYOR',
    'фомо': 'FOMO',
    'фад': 'FUD',
    'фуд': 'FUD',
    'дую': 'DYOR',
    'нфа': 'NFA',

    # --- gains ---
    'заиксовать': 'multiply Nx',
    'десятикс': '10x',
    'поймать лося': 'take a loss',
    'словить лося': 'take a loss',
    'профит': 'profit',
    'иксы': 'x gains',
    'икс': 'x',

    # --- leverage / liquidation ---
    'заликвидировали': 'got liquidated',
    'маржин колл': 'margin call',
    'маржинколл': 'margin call',
    'ликвиднули': 'got liquidated',
    'ливеридж': 'leverage',
    'ликвидация': 'liquidation',
    'плечо': 'leverage',

    # --- earn / farm ---
    'застейкать': 'stake',
    'стейкинг': 'staking',
    'стейкать': 'stake',
    'фармить': 'farming',
    'фарм': 'farm',

    # --- airdrop / listing ---
    'делистнули': 'got delisted',
    'залистили': 'got listed',
    'аирдроп': 'airdrop',
    'эирдроп': 'airdrop',
    'листинг': 'listing',
    'делистинг': 'delisting',
    'пресейл': 'presale',
    'пре сейл': 'presale',
    'дроп': 'airdrop',
    'айсио': 'ICO',

    # --- infra ---
    'холодный кошелек': 'cold wallet',
    'горячий кошелек': 'hot wallet',
    'смартконтракт': 'smart contract',
    'смарт контракт': 'smart contract',
    'метавселенная': 'metaverse',
    'приватный ключ': 'private key',
    'сидфраза': 'seed phrase',
    'сид фраза': 'seed phrase',
    'кошелек': 'wallet',
    'приватник': 'private key',
    'ноды': 'nodes',
    'нода': 'node',
    'газ': 'gas',
    'комса': 'fee',
    'комиссия': 'fee',
    'волет': 'wallet',
    'халвинг': 'halving',
    'дефи': 'DeFi',
    'нфт': 'NFT',

    # --- positions ---
    'набрать позицию': 'build a position',
    'закрыть позицию': 'close a position',
    'открыть позицию': 'open a position',
    'закупиться': 'buy in',
    'закупаться': 'buy in',
    'отбился': 'break even',
    'отбить': 'break even',

    # --- project / listing meta ---
    'маркетмейкер': 'market maker',
    '代币经济学': 'tokenomics',
    'токеномика': 'tokenomics',
    'токеника': 'tokenomics',
    'вайтпейпер': 'whitepaper',
    'вайт пейпер': 'whitepaper',
    'роадмап': 'roadmap',
    'роудмап': 'roadmap',
    'анлок': 'unlock',
    'вестинг': 'vesting',
    'клиф': 'cliff',
    'ммщик': 'market maker',
    'инсайд': 'insider info',
    'инсайдер': 'insider',
    'манипуляция': 'manipulation',
    'волатильность': 'volatility',
}


def translate(text: str) -> str:
    """Заменяет русский крипто-сленг на английские термины с защитой контекста."""
    result = text

    # Этап 1: Обработка паттернов количества от STT (safest)
    for pattern, replacement in NUMERIC_PATTERNS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Этап 2: Строго регистрозависимые тикеры и аббревиатуры (БЕЗ ignorecase)
    for ticker, full_name in TICKERS_AND_ACRONYMS.items():
        pattern = r'(?<!\w)' + re.escape(ticker) + r'(?!\w)'
        result = re.sub(pattern, full_name, result)

    # Этап 3: Регистронезависимый общий русский сленг (сортировка по длине)
    for slang, replacement in sorted(SLANG.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r'(?<!\w)' + re.escape(slang) + r'(?!\w)'
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


if __name__ == '__main__':
    # Тестовые сценарии
    test_1 = "Я решил купить 2 битка и сделать 10 иксов. Киты запампили альт, а хомяки словили лося."
    test_2 = "Вчера обновили ATH, но на рынке жесткий ФУД. Закинул деньги в SOL и зафиксировал профит."
    
    print("Тест 1:")
    print(translate(test_1))
    print("\nТест 2:")
    print(translate(test_2))