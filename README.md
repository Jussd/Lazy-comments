# Lazy Comments — voice input & translator for Windows

Speak in your language — publish in any. Voice dictation and instant translation for social media.

> Hold **right Ctrl**, speak, release — the text appears right where your cursor is.

In any window: chat, browser, notepad, search box, terminal, IDE, CLI.

---

## 🎯 Why you'll want it

🎤 **Voice input** — dictate text instead of typing it by hand.
🌍 **Built-in translator** — speak in your native language and the app automatically types the text in your chosen target language.
⚡ **Saves time** — no need to switch between a translation app and the social network.
💬 **Great for international communication** — ideal for posts, comments and messages in foreign languages.
🔤 **Translation runs on the DeepL API**, delivering high-quality results.
🔒 **Privacy** — speech recognition runs locally on your device; your voice is never sent to third parties.
🌍 **Crypto & IT terminology support** — the app automatically normalizes crypto/IT slang and local terms from several languages into standard English tech wording.
🗣️ **Works as plain voice typing too** — no API key needed. If you skip the DeepL key, Lazy Comments still transcribes your speech locally and pastes it as-is. A free offline dictation tool with zero setup.

---

## 🚀 Install in a minute

### 1. [Download the installer](https://github.com/Jussd/Lazy-comments/releases/download/v1.2.0/lazy_comments-setup.exe)

Run `lazy_comments-setup.exe` (~29 MB).

### 2. Run the setup wizard

1. Click **Next**.
2. Tick options as you like:
   - 🖥️ Create a desktop shortcut
   - ⚡ Launch Lazy Comments at Windows startup *(recommended)*
3. Click **Install**, confirm the UAC prompt.
4. Keep **"Launch Lazy Comments"** checked and click **Finish**.

### 3. Pick a model *(first run only!)*

On first launch Lazy Comments opens the **"Select model"** window with a list of offline recognition engines. All models run locally, on your PC.

- 🇷🇺 **GigaAM v3 (recommended for Russian)** — best choice for Russian speech. ~215 MB, adds punctuation and writes numbers as digits.
- 🪶 **Vosk Russian Small** — lightest model (~45 MB), runs even on weak PCs.
- 🌍 **Whisper Small / Medium** — multilingual (99+ languages), good quality.
- ⚡ **Parakeet TDT v3** — fast multilingual model from NVIDIA, 25 European languages.

Pick one model and click **Continue** — Lazy Comments downloads it (30 seconds to a couple of minutes, depending on the model and your connection). You can switch models anytime from the tray.

> 🇷🇺 **For users in Russia:** Vosk models download from `alphacephei.com` and work reliably. The other models (GigaAM v3, Whisper, Parakeet, SenseVoice) live on **GitHub Releases**, which Russian providers often throttle. If the download sticks at 0% or drops — **turn on a VPN** and try again.

### 4. Set up languages and the DeepL API key *(first run)*

Right after the model, Lazy Comments opens the **Settings** window where you:

- choose the **source language** (what you speak) and the **target language** (what gets typed),
- paste your **DeepL API key** (needed only for translation — see below).

If you leave the API key empty, the app still works as a **plain voice typer**: it transcribes your speech locally and pastes it unchanged.

### 5. You're done 🎉

A Lazy Comments icon appears in the tray (next to the clock) — that means it's running.

---

## 🔑 Getting started with the DeepL API

Translation uses the **DeepL API**. Recognition is free and offline; translation needs a free DeepL key.

**Sign up:** go to the official [DeepL API](https://www.deepl.com/pro-api) site and create a developer account.
**Get your key:** log in, open **My Account** and go to the **API Keys** section.
**Use the key:** paste it into Lazy Comments — either in the first-run **Settings** window, or later via the tray menu (**Настройки…**).
**DeepL API Free:** free with a limit of **500 000 characters per month**.

---

## 🎙 How to use it

1. Open any window where you want to type something.
2. **Click** with the mouse into the input field.
3. **Hold right Ctrl** — you'll hear a short beep.
4. **Speak** — calmly, as to a person.
5. **Release Ctrl** — a second later the text lands in the field.

> If auto-paste didn't fire (some apps block it) — the text is always in the clipboard, just press **Ctrl+V**.

---

## 💡 Examples

| You say | You get |
|---------|---------|
| "Создай функцию которая возвращает массив" | Создай функцию которая возвращает array |
| "Запушь в гитхаб ветку фича логин" | Запушь в GitHub ветку feature login |
| "Добавь юзстейт для счётчика" | Добавь useState для счётчика |
| "Сделай реакт компонент" | Сделай React компонент |
| "Закоммить и запушь в мейн" | Закоммить и запушь в main |

Lazy Comments knows **over a thousand IT terms** — React, Python, Docker, Kubernetes, AWS, and so on. It also understands **crypto slang** — wallet, gas, mint, airdrop, DeFi, HODL, bridge, staking, and more.

The IT + crypto slang base covers **five languages: Russian, Chinese, Spanish, German and French**. Speak your local slang and Lazy Comments normalizes it into standard English tech wording.

---

## 🔧 Tray menu

Right-click the Lazy Comments tray icon:

| Item | What it does |
|------|--------------|
| **Key: …** | Current hotkey (updates automatically) |
| **Change key ▸** | Submenu to pick another key: Right/Left Ctrl, Right/Left Shift, Right/Left Alt, Caps Lock, Scroll Lock, Pause, F1–F12 |
| **Model: …** | Currently active recognition model |
| **Change model ▸** | Submenu for quick switching between downloaded models + **"Download more / Manage…"** opens the model manager |
| **Open logs** | Opens the logs folder |
| **Open models folder** | Opens the models folder |
| **Settings…** | Opens the settings window — change source/target language and add or update the DeepL API key |
| **Exit** | Closes Lazy Comments |

> The default hotkey is **right Ctrl**. Change it via the tray submenu **Change key ▸**; the choice is saved in `%APPDATA%\lazy_comments\config.json` and applies instantly, no restart needed.

---

## 🧠 Recognition models

Lazy Comments works with several offline engines. The catalog is built in — pick and download right from the app:

| Model | Size | Lang | For whom |
|-------|------|------|----------|
| **Vosk Russian Small** | 45 MB | RU | Lightest, for weak PCs |
| **Vosk Russian 0.42** | 1.8 GB | RU | Max quality among Vosk |
| **GigaAM v3 (with punctuation)** | 215 MB | RU | **Recommended for Russian** |
| **GigaAM v3 (no punctuation)** | 215 MB | RU | If you want uniform punctuation from Lazy Comments |
| **Parakeet TDT v3** | 670 MB | 25 EU | Fast + accurate, RU/EN/EU |
| **Whisper Tiny** | 230 MB | multi | 99+ languages, fast |
| **Whisper Base** | 290 MB | multi | Better quality than Tiny |
| **Whisper Small** | 640 MB | multi | Good balance of quality and speed |
| **Whisper Medium** | 1.9 GB | multi | Best quality, needs a strong CPU |
| **SenseVoice** | 230 MB | zh/en/ja/ko/yue | East Asia + English |

> Switch between downloaded models in two clicks: **tray → Change model ▸**. Download a new one or delete an old one via **"Download more / Manage…"** in the same submenu.
>
> Models live in `%APPDATA%\lazy_comments\models\`; the active one is stored in `%APPDATA%\lazy_comments\config.json` as the `active_model` field.

---

## ❓ If something goes wrong

<details>
<summary><b>Hotkey doesn't work</b></summary>

Close Lazy Comments from the tray (right-click → **Exit**) and run it as administrator:
right-click the shortcut → **"Run as administrator"**.

> Windows requires administrator rights for the app to intercept right Ctrl at the system level.
</details>

<details>
<summary><b>Lazy Comments doesn't hear me</b></summary>

1. Check the microphone: **Windows Settings** → **Sound** → check the mic level.
2. Speak louder and clearer, closer to the mic.
3. Open the logs via the tray menu (**Open logs**) — details are there.
</details>

<details>
<summary><b>Tray icon didn't appear</b></summary>

1. Open `%APPDATA%\lazy_comments\logs\lazy_comments.log` (paste this into the Explorer address bar).
2. Look at the last lines — the error is there.
3. If it's unclear — bring this log and ask for help.
</details>

<details>
<summary><b>Text isn't pasted automatically</b></summary>

Some apps block auto-paste. The text is still in the clipboard — just press **Ctrl+V** manually.
</details>

<details>
<summary><b>Windows Defender warns about the installer</b></summary>

In the SmartScreen window click **"More info"** → **"Run anyway"**.

The installer isn't code-signed yet, so Windows is suspicious of it. That's normal for open-source software.
</details>

<details>
<summary><b>Model won't download / sticks at 0%</b></summary>

Vosk models download from `alphacephei.com` and work reliably. The other models (GigaAM v3, Whisper, Parakeet, SenseVoice) live on **GitHub Releases**, which Russian providers often throttle. If the download sticks at 0% or drops — **turn on a VPN** and try again.
</details>

---

## 📁 Where Lazy Comments stores files

| Where | What |
|-------|------|
| `C:\Program Files\Lazy Comments\` | The app itself |
| `%APPDATA%\lazy_comments\models\` | Recognition model (~70 MB) |
| `%APPDATA%\lazy_comments\logs\` | Runtime logs |

To quickly open `%APPDATA%\lazy_comments\` — press **Win+R**, type `%APPDATA%\lazy_comments` and Enter.

---

## ⚡ Launch at Windows startup

The simplest way is to tick **"Launch Lazy Comments at Windows startup"** right in the installer.

If you forgot — no need to reinstall:

1. **Win+R** → `shell:startup` → Enter.
2. Drag the Lazy Comments shortcut from the desktop there.
3. Right-click the shortcut → **Properties** → **Advanced** → tick **"Run as administrator"**.

---

## 🗑 How to uninstall

**Windows Settings** → **Apps** → find **Lazy Comments** → **Uninstall**.

The folders `%APPDATA%\lazy_comments\models` and `%APPDATA%\lazy_comments\logs` aren't removed automatically — delete them manually if you don't need them.

---

## 🛠 For developers

Sources are in this repo. Lazy Comments is written in Python using [Vosk](https://alphacephei.com/vosk/) for offline speech recognition. Build `lazy_comments-setup.exe` via `build.bat` (PyInstaller + Inno Setup 6).

License — MIT, see [LICENSE](LICENSE).

---

---

# Lazy Comments — голосовой ввод и переводчик для Windows

Говорите на своём языке — публикуйте на любом. Голосовой ввод и мгновенный перевод для социальных сетей.

> Зажми **правый Ctrl**, говори, отпусти — и текст появится прямо там, где курсор.

В любом окне: чат, браузер, блокнот, поле поиска, терминал, IDE, CLI.

---

## 🎯 Зачем это нужно

🎤 **Голосовой ввод** — диктуйте текст вместо ручного набора.
🌍 **Встроенный переводчик** — говорите на своём родном языке, а программа автоматически печатает текст на выбранном языке перевода.
⚡ **Экономия времени** — не нужно переключаться между приложением для перевода и социальной сетью.
💬 **Удобно для международного общения** — идеально для постов, комментариев и сообщений на иностранных языках.
🔤 **Перевод выполняется через API DeepL**, обеспечивающий высокое качество перевода.
🔒 **Приватность** — распознавание речи работает локально на устройстве, голосовые данные не передаются третьим лицам.
🌍 **Поддержка крипто и IT-терминологии** — приложение автоматически нормализует крипто-IT-сленг и локальные термины из разных языков в стандартную англоязычную терминологию.
🗣️ **Работает и как обычный голосовой набор** — без API-ключа. Если не вставлять ключ DeepL, Lazy Comments всё равно распознаёт речь на вашем ПК и вставляет её как есть. Бесплатный офлайн-диктофон, которому не нужна никакая настройка.

---

## 🚀 Установка за минуту

### 1. [Скачай установщик](https://github.com/Jussd/Lazy-comments/releases/download/v1.2.0/lazy_comments-setup.exe)

Запусти `lazy_comments-setup.exe` (≈29 МБ).

### 2. Пройди мастер установки

1. Жми **Далее**.
2. Поставь галочки по желанию:
   - 🖥️ Создать ярлык на рабочем столе
   - ⚡ Запускать Lazy Comments при старте Windows *(рекомендуем)*
3. Жми **Установить**, подтверди UAC.
4. Оставь галочку **«Запустить Lazy Comments»** и жми **Завершить**.

### 3. Подожди модель *(только в первый раз!)*

При первом запуске Lazy Comments откроет окно **«Выбор модели»** со списком доступных движков распознавания. Все модели работают офлайн, на твоём компьютере.

- 🇷🇺 **GigaAM v3 (рекомендуется для русского)** — лучший выбор для русской речи. ~215 МБ, сама ставит пунктуацию и пишет цифры цифрами.
- 🪶 **Vosk Russian Small** — самая лёгкая модель (~45 МБ), запустится даже на слабом ПК.
- 🌍 **Whisper Small / Medium** — мультиязычно (99+ языков), хорошее качество.
- ⚡ **Parakeet TDT v3** — быстрая мультимодель от NVIDIA, 25 европейских языков.

Выбери одну модель, нажми **«Продолжить»** — Lazy Comments её скачает (от 30 секунд до пары минут, зависит от модели и интернета). Модель можно сменить в любой момент из трея.

> 🇷🇺 **Пользователям из России:** модели Vosk качаются с `alphacephei.com` и работают стабильно. Остальные модели (GigaAM v3, Whisper, Parakeet, SenseVoice) лежат на **GitHub Releases**, который в РФ нередко режется провайдерами. Если загрузка зависает на 0% или обрывается — **включи VPN** и попробуй снова.

### 4. Выбери языки и вставь ключ DeepL *(при первом запуске)*

Сразу после выбора модели Lazy Comments откроет окно **«Настройки»**, где ты:

- выбираешь **исходный язык** (на чём говоришь) и **язык перевода** (что печатается),
- вставляешь свой **API-ключ DeepL** (нужен только для перевода — см. ниже).

Если ключ оставить пустым, приложение всё равно работает как **обычный голосовой набор**: распознаёт речь локально и вставляет её без изменений.

### 5. Готово 🎉

В трее (рядом с часами) появится иконка Lazy Comments — значит всё работает.

---

## 🔑 Как начать работу с DeepL API

Перевод использует **API DeepL**. Распознавание бесплатное и офлайн; для перевода нужен бесплатный ключ DeepL.

**Регистрация:** перейди на официальный сайт [DeepL API](https://www.deepl.com/pro-api) и создай аккаунт разработчика.
**Получение ключа:** войди в свой профиль, открой **«Учётная запись» (My Account)** и перейди в раздел **API Keys**.
**Где вставить ключ:** в окне **«Настройки»** при первом запуске либо позже через меню в трее (**Настройки…**).
**DeepL API Free:** бесплатно с лимитом **500 000 символов в месяц**.

---

## 🎙 Как пользоваться

1. Открой любое окно, где хочешь что-то напечатать.
2. **Кликни мышкой** в поле для ввода.
3. **Зажми правый Ctrl** — услышишь короткий «бип».
4. **Говори** — спокойно, как с человеком.
5. **Отпусти Ctrl** — через секунду текст окажется в поле.

> Если автовставка не сработала (некоторые приложения её блокируют) — текст всегда в буфере обмена, просто нажми **Ctrl+V**.

---

## 💡 Примеры

| Скажи | Получится |
|-------|-----------|
| «Создай функцию которая возвращает массив» | Создай функцию которая возвращает array |
| «Запушь в гитхаб ветку фича логин» | Запушь в GitHub ветку feature login |
| «Добавь юзстейт для счётчика» | Добавь useState для счётчика |
| «Сделай реакт компонент» | Сделай React компонент |
| «Закоммить и запушь в мейн» | Закоммить и запушь в main |

Lazy Comments знает больше тысячи айтишных терминов — React, Python, Docker, Kubernetes, AWS, и так далее. А ещё понимает **крипто-сленг** — wallet, gas, mint, airdrop, DeFi, HODL, bridge, staking и многое другое.

База IT- и крипто-сленга охватывает **пять языков: русский, китайский, испанский, немецкий и французский**. Говори на своём сленге — Lazy Comments приведёт его к стандартной англоязычной терминологии.

---

## 🔧 Меню в трее

Правый клик на иконке Lazy Comments:

| Пункт | Что делает |
|-------|------------|
| **Клавиша: …** | Текущая горячая клавиша (обновляется автоматически) |
| **Сменить клавишу ▸** | Подменю для выбора другой клавиши: Правый/Левый Ctrl, Правый/Левый Shift, Правый/Левый Alt, Caps Lock, Scroll Lock, Pause, F1–F12 |
| **Модель: …** | Текущая активная модель распознавания |
| **Сменить модель ▸** | Подменю с быстрым переключением между уже скачанными моделями + пункт **«Скачать ещё / Управление…»** открывает менеджер моделей |
| **Открыть логи** | Открывает папку с логами |
| **Открыть папку с моделями** | Открывает папку с моделями |
| **Настройки…** | Открывает окно настроек — смена языков и добавление/обновление API-ключа DeepL |
| **Выход** | Закрывает Lazy Comments |

> По умолчанию горячая клавиша — **правый Ctrl**. Можно сменить через подменю **Сменить клавишу ▸** в трее: выбор сохраняется в `%APPDATA%\lazy_comments\config.json` и применяется сразу, без перезапуска.

---

## 🧠 Модели распознавания

Lazy Comments умеет работать с несколькими офлайн-движками. Каталог встроен — выбирай и качай прямо из приложения:

| Модель | Размер | Язык | Для кого |
|--------|--------|------|----------|
| **Vosk Russian Small** | 45 МБ | RU | Самая лёгкая, для слабых ПК |
| **Vosk Russian 0.42** | 1.8 ГБ | RU | Максимум качества среди Vosk |
| **GigaAM v3 (с пунктуацией)** | 215 МБ | RU | **Рекомендуется для русского** |
| **GigaAM v3 (без пунктуации)** | 215 МБ | RU | Если хочется единый стиль пунктуации от Lazy Comments |
| **Parakeet TDT v3** | 670 МБ | 25 EU | Быстро + точно, RU/EN/EU |
| **Whisper Tiny** | 230 МБ | мульти | 99+ языков, быстро |
| **Whisper Base** | 290 МБ | мульти | Качество выше Tiny |
| **Whisper Small** | 640 МБ | мульти | Хороший баланс качества и скорости |
| **Whisper Medium** | 1.9 ГБ | мульти | Лучшее качество, нужен мощный ЦП |
| **SenseVoice** | 230 МБ | zh/en/ja/ko/yue | Восточная Азия + английский |

> Переключиться между скачанными моделями — два клика: **трей → Сменить модель ▸**. Скачать новую или удалить старую — пункт **«Скачать ещё / Управление…»** в том же подменю.
>
> Модели лежат в `%APPDATA%\lazy_comments\models\`, активная сохраняется в `%APPDATA%\lazy_comments\config.json` как поле `active_model`.

---

## ❓ Если что-то идёт не так

<details>
<summary><b>Горячая клавиша не работает</b></summary>

Закрой Lazy Comments через трей (правый клик → **Выход**) и запусти от имени администратора:
правый клик на ярлыке → **«Запуск от имени администратора»**.

> Windows требует прав администратора, чтобы программа могла перехватывать правый Ctrl на системном уровне.
</details>

<details>
<summary><b>Lazy Comments не слышит голос</b></summary>

1. Проверь микрофон: **Параметры Windows** → **Звук** → проверь уровень микрофона.
2. Говори громче и чётче, ближе к микрофону.
3. Открой логи через трей-меню (**Открыть логи**) — там подробности.
</details>

<details>
<summary><b>Иконка в трее не появилась</b></summary>

1. Открой `%APPDATA%\lazy_comments\logs\lazy_comments.log` (можно вставить эту строку в адресную строку Проводника).
2. Посмотри последние строки — там будет ошибка.
3. Если непонятно — приходи с этим логом за помощью.
</details>

<details>
<summary><b>Текст не вставляется автоматически</b></summary>

Некоторые приложения блокируют автовставку. Текст всё равно в буфере обмена — просто нажми **Ctrl+V** вручную.
</details>

<details>
<summary><b>Защитник Windows ругается на установщик</b></summary>

В окне SmartScreen нажми **«Подробнее»** → **«Выполнить в любом случае»**.

Установщик пока не подписан сертификатом, поэтому Windows подозрительно к нему относится. Это нормально для open-source программ.
</details>

<details>
<summary><b>Модель не скачивается / висит на 0%</b></summary>

Модели Vosk качаются с `alphacephei.com` и работают стабильно. Остальные модели (GigaAM v3, Whisper, Parakeet, SenseVoice) лежат на **GitHub Releases**, который в РФ нередко режется провайдерами. Если загрузка зависает на 0% или обрывается — **включи VPN** и попробуй снова.
</details>

---

## 📁 Где Lazy Comments хранит файлы

| Где | Что |
|-----|-----|
| `C:\Program Files\Lazy Comments\` | Сама программа |
| `%APPDATA%\lazy_comments\models\` | Модель распознавания (≈70 МБ) |
| `%APPDATA%\lazy_comments\logs\` | Логи работы |

Чтобы быстро открыть `%APPDATA%\lazy_comments\` — нажми **Win+R**, введи `%APPDATA%\lazy_comments` и Enter.

---

## ⚡ Автозапуск при старте Windows

Самый простой способ — поставить галочку **«Запускать Lazy Comments при старте Windows»** прямо в установщике.

Если забыл — переустанавливать не нужно:

1. **Win+R** → `shell:startup` → Enter.
2. Перетащи туда ярлык Lazy Comments с рабочего стола.
3. Правый клик на ярлыке → **Свойства** → **Дополнительно** → галочка **«Запуск от имени администратора»**.

---

## 🗑 Как удалить

**Параметры Windows** → **Приложения** → найди **Lazy Comments** → **Удалить**.

Папки `%APPDATA%\lazy_comments\models` и `%APPDATA%\lazy_comments\logs` не удаляются автоматически — если они тебе не нужны, удали вручную.

---

## 🛠 Для разработчиков

Исходники — в этом репозитории. Lazy Comments написан на Python с использованием [Vosk](https://alphacephei.com/vosk/) для офлайн распознавания речи. Сборка `lazy_comments-setup.exe` — `build.bat` (PyInstaller + Inno Setup 6).

Лицензия — MIT, см. [LICENSE](LICENSE).
