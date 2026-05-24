"""
System tray icon, menus, and the bridge between the worker and the GUI.
"""

from __future__ import annotations

import os
import sys
import threading

from voxapp.config import (
    HOTKEY_CHOICES,
    VALID_HOTKEYS,
    get_hotkey_display,
    get_models_dir,
    update_config,
)
from voxapp.registry import MODELS, is_installed
from voxapp import worker


def _get_icon_image():
    from PIL import Image
    icon_path = (
        os.path.join(sys._MEIPASS, "vox.ico")
        if getattr(sys, "frozen", False)
        else os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "vox.ico")
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
            from voxapp.gui import run_manager
            run_manager(active_id=worker.get_active_model_id(),
                        on_apply=_apply_model)
        threading.Thread(target=_run, daemon=True,
                         name="VoxModelManager").start()

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
        pystray.MenuItem("Vox — Голосовой ввод", None,
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
        pystray.MenuItem("Выход", on_quit),
    )

    icon = pystray.Icon("Vox", _get_icon_image(),
                        "Vox — Голосовой ввод", menu)
    icon.run()
