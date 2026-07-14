"""
System tray icon, menus, and the bridge between the worker and the GUI.
"""

from __future__ import annotations

import os
import sys
import threading

from lazy_comments.config import (
    HOTKEY_CHOICES,
    VALID_HOTKEYS,
    get_hotkey_display,
    get_models_dir,
    update_config,
)
from lazy_comments.registry import MODELS, is_installed
from lazy_comments import worker


def _get_icon_image():
    from PIL import Image
    icon_path = (
        os.path.join(sys._MEIPASS, "lazy_comments.ico")
        if getattr(sys, "frozen", False)
        else os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "lazy_comments.ico")
    )
    if os.path.exists(icon_path):
        return Image.open(icon_path)
    return Image.new("RGB", (64, 64), color=(59, 130, 246))


def setup_tray(log_dir: str) -> None:
    """Build and run the tray icon (blocks the calling thread)."""
    import pystray

    # ---- callbacks ------------------------------------------------------

    def on_open_logs(icon, item):
        try:
            os.startfile(log_dir)
        except Exception as e:
            print(f"[TRAY] Failed to open logs: {e}")

    def on_open_models(icon, item):
        try:
            models_dir = get_models_dir()
            os.makedirs(models_dir, exist_ok=True)
            os.startfile(models_dir)
        except Exception as e:
            print(f"[TRAY] Failed to open models: {e}")

    def on_manage_models(icon, item):
        """Open the tkinter manager window in its own thread."""
        def _run():
            from lazy_comments.gui import run_manager
            run_manager(active_id=worker.get_active_model_id(),
                        on_apply=_apply_model)
        threading.Thread(target=_run, daemon=True,
                         name="Lazy CommentsModelManager").start()

    def _apply_model(model_id: str):
        """Hot-swap engine + persist choice. Called from GUI thread."""
        print(f"[TRAY] Switching active model to {model_id}")
        worker.set_engine(model_id)
        update_config(active_model=model_id)
        try:
            icon.update_menu()
        except Exception:
            pass

    def on_set_hotkey(icon, event_name: str):
        if event_name not in VALID_HOTKEYS or event_name == worker.HOTKEY:
            return
        worker.set_hotkey(event_name)
        update_config(hotkey=event_name)
        print(f"[TRAY] Hotkey changed to {get_hotkey_display(event_name)}")
        icon.update_menu()


    def on_settings(icon, item):
        """Open the settings window (API key + languages)."""
        def _run():
            from lazy_comments.config import load_config, update_config
            import tkinter as tk

            cfg = load_config()
            saved_key = cfg.get("deepl_api_key", "")
            saved_source = cfg.get("source_lang", "ru")
            saved_target = cfg.get("target_lang", "en")

            LANGS = [
                ("Russian", "ru"), ("English", "en"), ("Ukrainian", "uk"),
                ("German", "de"), ("French", "fr"), ("Spanish", "es"),
                ("Italian", "it"), ("Portuguese", "pt"), ("Polish", "pl"),
                ("Czech", "cs"), ("Dutch", "nl"), ("Hungarian", "hu"),
                ("Romanian", "ro"), ("Turkish", "tr"), ("Greek", "el"),
                ("Hebrew", "he"), ("Arabic", "ar"), ("Hindi", "hi"),
                ("Chinese (Simplified)", "zh-CN"), ("Chinese (Traditional)", "zh-TW"),
                ("Japanese", "ja"), ("Korean", "ko"), ("Thai", "th"),
                ("Vietnamese", "vi"), ("Indonesian", "id"), ("Malay", "ms"),
                ("Finnish", "fi"), ("Swedish", "sv"), ("Norwegian", "no"),
                ("Danish", "da"), ("Bulgarian", "bg"), ("Serbian", "sr"),
                ("Croatian", "hr"), ("Slovak", "sk"), ("Slovenian", "sl"),
                ("Estonian", "et"), ("Latvian", "lv"), ("Lithuanian", "lt"),
            ]

            win = tk.Tk()
            win.title("Lazy Comments — Настройки")
            win.geometry("580x440")
            win.resizable(False, False)

            tk.Label(win, text="Lazy Comments — Настройки",
                     font=("Segoe UI", 13, "bold")).pack(pady=(18, 4))
            tk.Label(win, text="Выбор языков и API-ключа перевода (DeepL).",
                     fg="#666").pack(pady=(0, 12))

            # Language selection
            lang_frame = tk.LabelFrame(win, text="Языки", padx=12, pady=8)
            lang_frame.pack(fill="x", padx=20, pady=(0, 8))

            src_var = tk.StringVar(value=saved_source)
            tgt_var = tk.StringVar(value=saved_target)

            lang_options = [f"{n} ({c})" for n, c in LANGS]

            src_lbl = tk.Label(lang_frame, text="Исходный:")
            tgt_lbl = tk.Label(lang_frame, text="Целевой:")

            src_menu = tk.OptionMenu(lang_frame, src_var, *lang_options)
            src_menu.config(width=22)
            tgt_menu = tk.OptionMenu(lang_frame, tgt_var, *lang_options)
            tgt_menu.config(width=22)

            src_lbl.grid(row=0, column=0, sticky="w", pady=4)
            src_menu.grid(row=0, column=1, padx=(8, 8), pady=4)
            tgt_lbl.grid(row=1, column=0, sticky="w", pady=4)
            tgt_menu.grid(row=1, column=1, padx=(8, 8), pady=4)

            def swap_langs():
                sv = src_var.get(); tv = tgt_var.get()
                src_var.set(tv); tgt_var.set(sv)

            tk.Button(lang_frame, text="< > поменять", command=swap_langs,
                      width=12).grid(row=0, column=2, rowspan=2, padx=(4, 0))

            # DeepL API Key
            key_frame = tk.LabelFrame(win, text="DeepL API Key", padx=12, pady=8)
            key_frame.pack(fill="x", padx=20, pady=(0, 8))

            tk.Label(key_frame, text="API Key:",
                     width=10, anchor="w").grid(row=0, column=0, sticky="w")
            key_var = tk.StringVar(value=saved_key)
            tk.Entry(key_frame, textvariable=key_var, width=42).grid(
                row=0, column=1, padx=(4, 0), sticky="ew")
            tk.Label(key_frame, text="Получить бесплатный ключ: deepl.com/pro-api — 500k знаков/мес бесплатно",
                     fg="#06c", wraplength=400).grid(
                         row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

            bf = tk.Frame(win)
            bf.pack(pady=14)

            def get_lang_code(var):
                val = var.get()
                for n, c in LANGS:
                    if f"({c})" in val:
                        return c
                return "en"

            def save_all():
                update_config(
                    deepl_api_key=key_var.get().strip(),
                    source_lang=get_lang_code(src_var),
                    target_lang=get_lang_code(tgt_var),
                )
                win.destroy()

            tk.Button(bf, text="Отмена", width=12, command=win.destroy).pack(side="left", padx=8)
            tk.Button(bf, text="Сохранить", width=18, command=save_all).pack(side="left")
            win.bind("<Return>", lambda e: save_all())
            win.mainloop()

        threading.Thread(target=_run, daemon=True, name="Lazy CommentsSettings").start()

    def on_quit(icon, item):
        print("[TRAY] Quit requested")
        icon.stop()
        os._exit(0)

    # ---- menu builders --------------------------------------------------

    def make_hotkey_item(display, evt):
        def _action(icon, item):
            on_set_hotkey(icon, evt)
        def _checked(item):
            return worker.HOTKEY == evt
        return pystray.MenuItem(
            display,
            _action,
            radio=True,
            checked=_checked,
        )

    modifier_items = [make_hotkey_item(d, e) for d, e in HOTKEY_CHOICES[:6]]
    lock_items     = [make_hotkey_item(d, e) for d, e in HOTKEY_CHOICES[6:9]]
    fkey_items     = [make_hotkey_item(d, e) for d, e in HOTKEY_CHOICES[9:]]

    hotkey_submenu = pystray.Menu(
        *modifier_items,
        pystray.Menu.SEPARATOR,
        *lock_items,
        pystray.Menu.SEPARATOR,
        *fkey_items,
    )

    def make_model_quickswitch_item(model_id: str, info: dict):
        """Quick-switch radio item; greyed out if model isn't installed."""
        def _action(icon, item):
            _apply_model(model_id)
        def _checked(item):
            return worker.get_active_model_id() == model_id
        def _enabled(item):
            return is_installed(model_id)
        return pystray.MenuItem(
            info["name"],
            _action,
            radio=True,
            checked=_checked,
            enabled=_enabled,
        )

    model_quick_items = [
        make_model_quickswitch_item(mid, info) for mid, info in MODELS.items()
    ]
    model_submenu = pystray.Menu(
        *model_quick_items,
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Скачать ещё / Управление…", on_manage_models),
    )

    def model_label(item):
        mid = worker.get_active_model_id()
        if mid and mid in MODELS:
            return f"Модель: {MODELS[mid]['name']}"
        return "Модель: —"

    menu = pystray.Menu(
        pystray.MenuItem("Lazy Comments — Голосовой ввод", None,
                         default=True, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(lambda item: f"Клавиша: {get_hotkey_display(worker.HOTKEY)}",
                         None, enabled=False),
        pystray.MenuItem("Сменить клавишу", hotkey_submenu),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(model_label, None, enabled=False),
        pystray.MenuItem("Сменить модель", model_submenu),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Открыть логи", on_open_logs),
        pystray.MenuItem("Открыть папку с моделями", on_open_models),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Настройки...", on_settings),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Выход", on_quit),
    )

    icon = pystray.Icon("Lazy Comments", _get_icon_image(),
                        "Lazy Comments — Голосовой ввод", menu)
    icon.run()
