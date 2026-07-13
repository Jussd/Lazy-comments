# -*- coding: utf-8 -*-
"""
ZH -> EN улучшенный словарь крипто-сленга (Китайский язык).

Особенности архитектуры для китайского языка:
1. NUMERIC_PATTERNS — обработка связок чисел от STT (например, "10倍" -> "10x gains").
2. TICKERS_AND_ACRONYMS — строгий регистр с границами по ЛАТИНСКИМ буквам (?<![a-zA-Z]). 
   Это позволяет корректно находить токены (SOL, BTC) внутри слитного китайского текста.
3. SLANG — поиск и замена иероглифического крипто-сленга без использования границ слов, 
   с жесткой сортировкой ключей по длине.
"""

import re

# === УРОВЕНЬ 1: Паттерны для числительных от STT (Число + Ассет/Множитель) ===
NUMERIC_PATTERNS = {
    r'(\d+)\s*倍': r'\1x gains',
    r'(\d+)\s*个大饼': r'\1 BTC',
    r'(\d+)\s*个以太': r'\1 ETH',
    r'(\d+)\s*倍币': r'\1x coin',
}

# === УРОВЕНЬ 2: Строго регистрозависимые тикеры и аббревиатуры ===
# Границы проверяются только по английским буквам, чтобы иероглифы вокруг не мешали распознаванию
TICKERS_AND_ACRONYMS = {
    'ATH': 'ATH',
    'BTC': 'BTC',
    'ETH': 'ETH',
    'SOL': 'SOL',
    'DOT': 'DOT',
    'NFT': 'NFT',
    'FUD': 'FUD',
    'FOMO': 'FOMO',
}

# === УРОВЕНЬ 3: Иероглифический китайский крипто-сленг ===
SLANG = {
    # --- HODL / Accumulate / All-in ---
    '长线持有': 'HODL',
    '屯币': 'hold coins',
    '囤币': 'hold coins',
    '梭哈': 'all-in',
    '压路机前捡钢蹦': 'picking up pennies in front of a steamroller',

    # --- Pump & Dump ---
    '拉盘': 'pump',
    '砸盘': 'dump',
    '暴涨': 'pump',
    '暴跌': 'dump',
    '插针': 'liquidation wick',  # Резкое движение цены ("игла"), сбривающее маржиналку
    '腰斩': 'drop 50%',         # Цена "перерезана пополам"

    # --- Coins & Tokens (Мемы и кальки названий) ---
    '大饼': 'Bitcoin',
    '二饼': 'Ethereum',
    '以太坊': 'Ethereum',
    '以太': 'Ethereum',
    '姨太': 'Ethereum',
    '山寨币': 'altcoins',
    '山寨': 'altcoin',
    '土狗': 'shitcoin',         # "Деревенская собака" — мемкоины / высокорисковые щитки
    '金狗': '100x memecoin',    # "Золотая собака" — успешный выстреливший мемкоин
    '空气币': 'shitcoin',       # "Воздушная монета" — скам без технологии
    '稳定币': 'stablecoin',
    '代币': 'token',

    # --- Market Participants (Участники рынка) ---
    '韭菜': 'retail investors', # "Лук-порей" — хомяки, которых постоянно "стригут"
    '割韭菜': 'harvesting retail investors',
    '巨鲸': 'whales',
    '庄家': 'market makers / whales',
    '科学家': 'crypto bots/developers', # "Ученые" — разработчики ботов и снайпер-скриптов

    # --- Market States (Состояние рынка) ---
    '牛市': 'bull market',
    '熊市': 'bear market',
    '猴市': 'highly volatile market', # "Обезьяний рынок" — прыгает туда-сюда без тренда
    '横盘': 'sideways market',

    # --- Trading Actions (Торговые операции) ---
    '割肉': 'cut losses',       # "Отрезать мясо" — зафиксировать убыток
    '止损': 'stop loss',
    '止盈': 'take profit',
    '现货': 'spot',
    '期货': 'futures',
    '杠杆': 'leverage',
    '开仓': 'open a position',
    '平仓': 'close a position',
    '加仓': 'add to position',
    '减仓': 'reduce position',

    # --- Liquidations & Scams (Ликвидации и Скам) ---
    '爆仓': 'liquidated',
    '穿仓': 'negative equity liquidation',
    '跑路': 'rug pull',         # "Убежать" — проект соскамился и ушел с деньгами
    '项目方跑路': 'project rug pull',
    '归零': 'go to zero',

    # --- Earn / DeFi (Заработок) ---
    '质押': 'staking',
    '流动性挖矿': 'yield farming',
    '挖矿': 'mining',

    # --- Events & Meta ---
    '空投': 'airdrop',
    '上线': 'listing',
    '下线': 'delisting',
    '众筹': 'ICO',
    '白名单': 'whitelist',

    # --- Docs & Tokenomics ---
    '代币经济学': 'tokenomics',
    '白皮书': 'whitepaper',
    '路线图': 'roadmap',
    '锁仓': 'lock-up',
    '解锁': 'unlock',

    # --- Sentiment ---
    '踏空': 'FOMO / missed the rally', # Упустил движение, остался в кэше вне рынка
    '恐慌贪婪指数': 'Fear and Greed Index',
    '山寨季': 'altseason',
}


def translate(text: str) -> str:
    """Заменяет китайский крипто-сленг на английские термины."""
    result = text

    # Этап 1: Обработка паттернов количества от STT
    for pattern, replacement in NUMERIC_PATTERNS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Этап 2: Строго регистрозависимые тикеры (Защита латинских границ)
    for ticker, full_name in TICKERS_AND_ACRONYMS.items():
        # Специфичный паттерн: игнорируем иероглифы, проверяем только отсутствие соседних английских букв
        pattern = r'(?<![a-zA-Z])' + re.escape(ticker) + r'(?![a-zA-Z])'
        result = re.sub(pattern, full_name, result)

    # Этап 3: Китайский иероглифический сленг (Прямая замена подстрок по длине)
    for slang, replacement in sorted(SLANG.items(), key=lambda x: len(x[0]), reverse=True):
        result = re.sub(re.escape(slang), replacement, result)

    return result


if __name__ == '__main__':
    # Тест 1: Слитный текст с токенами и числами
    test_1 = "我刚买了2个大饼和一些SOL，希望能拿到10倍。如果项目方跑路我就归零了。"
    # Тест 2: Сленг участников рынка и состояния цен
    test_2 = "现在是牛市吗？刚才大盘插针，很多杠杆爆仓了，巨鲸在砸盘，韭菜又被割肉。"
    
    print("Тест 1:")
    print(translate(test_1))
    print("\nТест 2:")
    print(translate(test_2))