
from __future__ import annotations

import os
import sys
import threading
import time
import traceback

from lazy_comments.config import (
    get_log_dir,
    load_config,
    update_config,
)
from lazy_comments.registry import (
    DEFAULT_MODEL_ID,
    MODELS,
    RECOMMENDED_MODEL_ID,
    is_installed,
)


def _setup_logging() -> tuple[str, str]:
    log_dir = get_log_dir()
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "lazy_comments.log")

    if os.path.exists(log_file) and os.path.getsize(log_file) > 5 * 1024 * 1024:
        os.remove(log_file)

    log_fp = open(log_file, "a", encoding="utf-8", buffering=1)

    if getattr(sys, "frozen", False):
        sys.stdout = log_fp
        sys.stderr = log_fp
    else:
        class _Tee:
            def __init__(self, *streams):
                self._streams = streams
            def write(self, data):
                for s in self._streams:
                    try:
                        s.write(data)
                        s.flush()
                    except Exception:
                        pass
            def flush(self):
                for s in self._streams:
                    try:
                        s.flush()
                    except Exception:
                        pass

        sys.stdout = _Tee(sys.__stdout__, log_fp)
        sys.stderr = _Tee(sys.__stderr__, log_fp)

    return log_dir, log_file


def _resolve_initial_model() -> str | None:
    cfg = load_config()
    active = cfg.get("active_model")
    if active and active in MODELS and is_installed(active):
        return active

    for candidate in (RECOMMENDED_MODEL_ID, DEFAULT_MODEL_ID):
        if is_installed(candidate):
            return candidate

    for mid in MODELS:
        if is_installed(mid):
            return mid

    return None


def _show_first_run_wizard() -> str | None:
    from lazy_comments.gui import run_first_run_wizard

    chosen: dict[str, str] = {}

    def _on_apply(model_id: str) -> None:
        chosen["id"] = model_id
        update_config(active_model=model_id)

    ok = run_first_run_wizard(on_apply=_on_apply)
    if not ok or "id" not in chosen:
        return None
    return chosen["id"]


def main() -> None:
    log_dir, log_file = _setup_logging()
    print(f'\n=== Lazy Comments started at {time.strftime("%Y-%m-%d %H:%M:%S")} ===')

    model_id = _resolve_initial_model()
    if model_id is None:
        print("[INIT] No model installed — showing first-run wizard")
        model_id = _show_first_run_wizard()
        if model_id is None:
            print("[INIT] First-run cancelled, exiting")
            return

    from lazy_comments import worker
    t = threading.Thread(
        target=worker.run, args=(model_id,), daemon=True, name="Lazy CommentsWorker",
    )
    t.start()

    try:
        from lazy_comments.tray import setup_tray
        setup_tray(log_dir)
    except Exception as e:
        print(f"[FATAL] Tray failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
