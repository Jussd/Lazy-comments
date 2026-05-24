"""
Tkinter UI: first-run model picker + model manager (download / delete /
switch active).

Both windows reuse the same model list widget.
"""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from voxapp.downloader import download_model, uninstall_model
from voxapp.registry import (
    DEFAULT_MODEL_ID,
    MODELS,
    RECOMMENDED_MODEL_ID,
    is_installed,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _human_size(mb: int) -> str:
    if mb >= 1024:
        return f"{mb / 1024:.1f} ГБ"
    return f"{mb} МБ"


def _status_label(model_id: str, active_id: str | None) -> str:
    if model_id == active_id:
        return "● активна"
    if is_installed(model_id):
        return "✓ установлена"
    return ""


class _ProgressDialog:
    """Modal-ish progress window with status text + progressbar."""

    def __init__(self, parent: tk.Tk, title: str):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("420x140")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        self.label_var = tk.StringVar(value="Подготовка...")
        tk.Label(self.top, textvariable=self.label_var, anchor="w",
                 justify="left", wraplength=400).pack(
                     padx=16, pady=(16, 8), fill="x")

        self.pb = ttk.Progressbar(self.top, mode="determinate",
                                  length=380, maximum=1000)
        self.pb.pack(padx=16, pady=4)

        self.detail_var = tk.StringVar(value="")
        tk.Label(self.top, textvariable=self.detail_var, anchor="w",
                 fg="#666").pack(padx=16, pady=(4, 12), fill="x")

    def update_progress(self, done: int, total: int, stage: str) -> None:
        def _apply():
            if total > 0:
                pct = int(done * 1000 / total)
                self.pb["value"] = pct
                if stage == "Загрузка":
                    self.detail_var.set(
                        f"{stage}: {done / 1024 / 1024:.1f} / "
                        f"{total / 1024 / 1024:.1f} МБ ({pct / 10:.0f}%)")
                else:
                    self.detail_var.set(f"{stage}: {done} / {total}")
            else:
                self.pb["value"] = 0
                self.detail_var.set(
                    f"{stage}: {done / 1024 / 1024:.1f} МБ")
            self.label_var.set(stage + "...")
        # Marshal back to the Tk thread; safe to call from worker threads.
        try:
            self.top.after(0, _apply)
        except tk.TclError:
            pass

    def close(self) -> None:
        try:
            self.top.grab_release()
            self.top.destroy()
        except tk.TclError:
            pass


# ---------------------------------------------------------------------------
# Model picker / manager window
# ---------------------------------------------------------------------------

class ModelWindow:
    """
    A reusable window listing all catalog models.

    Modes:
        first_run=True  -> the user must pick exactly one model and
                           confirm; on_apply receives the chosen id.
                           Cancelling exits the whole app.
        first_run=False -> manage mode; user can install/remove any
                           model and pick which one is active.
    """

    def __init__(self, active_id: str | None, first_run: bool,
                 on_apply: Callable[[str], None]):
        self.active_id = active_id
        self.first_run = first_run
        self.on_apply = on_apply
        self._chosen_id: str | None = active_id or RECOMMENDED_MODEL_ID
        self._cancelled = True  # set False on successful apply

        self.root = tk.Tk()
        self.root.title("Vox — Выбор модели"
                        if first_run else "Vox — Модели распознавания")
        self.root.geometry("680x560")
        try:
            import os, sys
            icon_dir = (sys._MEIPASS if getattr(sys, "frozen", False)
                        else os.path.dirname(os.path.dirname(
                            os.path.abspath(__file__))))
            self.root.iconbitmap(os.path.join(icon_dir, "vox.ico"))
        except Exception:
            pass

        self._build_ui()
        self._refresh_list()

    # -- UI construction --------------------------------------------------

    def _build_ui(self) -> None:
        intro_text = (
            "Выбери модель распознавания речи. Все модели работают "
            "офлайн, на твоём компьютере."
            if self.first_run else
            "Управление моделями распознавания. Активная — это та, "
            "которой Vox распознаёт твою речь."
        )
        tk.Label(self.root, text=intro_text, wraplength=640,
                 justify="left", anchor="w").pack(
                     padx=16, pady=(14, 8), fill="x")

        # Scrollable list
        outer = tk.Frame(self.root)
        outer.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        canvas = tk.Canvas(outer, borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical",
                                 command=canvas.yview)
        self.list_frame = tk.Frame(canvas)
        self.list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.list_frame, anchor="nw",
                             width=620)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bottom buttons
        btn_row = tk.Frame(self.root)
        btn_row.pack(fill="x", padx=16, pady=(4, 14))

        if self.first_run:
            tk.Button(btn_row, text="Отмена", width=12,
                      command=self._on_cancel).pack(side="right", padx=(8, 0))
            tk.Button(btn_row, text="Продолжить", width=18,
                      command=self._on_confirm_first_run,
                      default="active").pack(side="right")
        else:
            tk.Button(btn_row, text="Закрыть", width=12,
                      command=self._on_close).pack(side="right")

    def _refresh_list(self) -> None:
        for w in self.list_frame.winfo_children():
            w.destroy()

        for mid, info in MODELS.items():
            self._render_model_row(mid, info)

    def _render_model_row(self, model_id: str, info: dict) -> None:
        frame = tk.Frame(self.list_frame, bd=1, relief="solid", padx=10, pady=8)
        frame.pack(fill="x", pady=4)

        # Header row: radio (first-run) or name + status
        header = tk.Frame(frame)
        header.pack(fill="x")

        if self.first_run:
            rb = tk.Radiobutton(
                header, text=info["name"],
                variable=self._radio_var(), value=model_id,
                command=lambda mid=model_id: self._set_chosen(mid),
                font=("Segoe UI", 10, "bold"))
            rb.pack(side="left")
        else:
            tk.Label(header, text=info["name"],
                     font=("Segoe UI", 10, "bold")).pack(side="left")

        tag = info.get("tag")
        if tag:
            tk.Label(header, text=f"  [{tag}]", fg="#0a7").pack(side="left")

        status = _status_label(model_id, self.active_id)
        if status:
            tk.Label(header, text=f"  {status}", fg="#06c").pack(side="left")

        meta = (f"Движок: {info['engine']}   "
                f"Язык: {info.get('language', '—')}   "
                f"Размер: {_human_size(info['size_mb'])}")
        tk.Label(frame, text=meta, fg="#666",
                 anchor="w", justify="left").pack(fill="x", pady=(4, 0))

        tk.Label(frame, text=info.get("description", ""), wraplength=580,
                 anchor="w", justify="left").pack(fill="x", pady=(4, 0))

        # Action buttons (only in manage mode)
        if not self.first_run:
            actions = tk.Frame(frame)
            actions.pack(fill="x", pady=(8, 0))
            installed = is_installed(model_id)
            is_active = (model_id == self.active_id)

            if not installed:
                tk.Button(actions, text="Скачать",
                          command=lambda mid=model_id:
                              self._download_then_refresh(mid)).pack(side="left")
            else:
                if not is_active:
                    tk.Button(actions, text="Сделать активной",
                              command=lambda mid=model_id:
                                  self._activate(mid)).pack(side="left")
                tk.Button(actions, text="Удалить",
                          command=lambda mid=model_id:
                              self._delete(mid)).pack(side="left", padx=(6, 0))

    # -- State helpers ----------------------------------------------------

    def _radio_var(self) -> tk.StringVar:
        if not hasattr(self, "_radio_state"):
            self._radio_state = tk.StringVar(value=self._chosen_id or "")
        return self._radio_state

    def _set_chosen(self, model_id: str) -> None:
        self._chosen_id = model_id

    # -- Actions ----------------------------------------------------------

    def _download_then_refresh(self, model_id: str,
                               then_activate: bool = False) -> None:
        dlg = _ProgressDialog(self.root,
                              f"Загрузка: {MODELS[model_id]['name']}")
        result_holder: dict = {}

        def worker():
            try:
                download_model(model_id,
                               on_progress=dlg.update_progress,
                               on_log=lambda m: print(m))
                result_holder["ok"] = True
            except Exception as e:
                result_holder["error"] = str(e)
                print(f"[DL] Failed: {e}")
                import traceback
                traceback.print_exc()
            finally:
                self.root.after(0, _finish)

        def _finish():
            dlg.close()
            if "error" in result_holder:
                messagebox.showerror(
                    "Ошибка загрузки",
                    f"Не удалось скачать модель:\n\n{result_holder['error']}")
            elif then_activate:
                self._activate(model_id, skip_install_check=True)
            self._refresh_list()

        threading.Thread(target=worker, daemon=True,
                         name="VoxModelDownload").start()

    def _activate(self, model_id: str, skip_install_check: bool = False) -> None:
        if not skip_install_check and not is_installed(model_id):
            self._download_then_refresh(model_id, then_activate=True)
            return
        try:
            self.on_apply(model_id)
            self.active_id = model_id
            self._refresh_list()
        except Exception as e:
            messagebox.showerror(
                "Не удалось активировать",
                f"Не получилось переключить модель:\n\n{e}")

    def _delete(self, model_id: str) -> None:
        if model_id == self.active_id:
            messagebox.showinfo(
                "Нельзя удалить активную",
                "Сначала переключи Vox на другую модель.")
            return
        if not messagebox.askyesno(
                "Удалить модель?",
                f"Удалить файлы модели «{MODELS[model_id]['name']}»?\n"
                f"Их можно будет скачать заново в любой момент."):
            return
        uninstall_model(model_id)
        self._refresh_list()

    def _on_confirm_first_run(self) -> None:
        if not self._chosen_id:
            messagebox.showinfo("Выбери модель", "Сначала выбери модель в списке.")
            return
        self._cancelled = False
        mid = self._chosen_id
        if not is_installed(mid):
            # Download, then apply, then close.
            dlg = _ProgressDialog(self.root,
                                  f"Загрузка: {MODELS[mid]['name']}")
            result_holder: dict = {}

            def worker():
                try:
                    download_model(mid,
                                   on_progress=dlg.update_progress,
                                   on_log=lambda m: print(m))
                    result_holder["ok"] = True
                except Exception as e:
                    result_holder["error"] = str(e)
                    print(f"[DL] Failed: {e}")
                finally:
                    self.root.after(0, _finish)

            def _finish():
                dlg.close()
                if "error" in result_holder:
                    messagebox.showerror(
                        "Ошибка загрузки",
                        f"Не удалось скачать модель:\n\n{result_holder['error']}")
                    return
                try:
                    self.on_apply(mid)
                    self._cancelled = False
                    self.root.destroy()
                except Exception as e:
                    messagebox.showerror(
                        "Не удалось активировать",
                        f"Скачивание прошло, но запустить не получилось:\n\n{e}")

            threading.Thread(target=worker, daemon=True,
                             name="VoxModelDownload").start()
        else:
            self.on_apply(mid)
            self.root.destroy()

    def _on_cancel(self) -> None:
        # First-run cancel = exit the whole app.
        if messagebox.askyesno(
                "Выйти из Vox?",
                "Без модели Vox не сможет распознавать речь.\n"
                "Закрыть программу?"):
            self.root.destroy()

    def _on_close(self) -> None:
        self.root.destroy()

    def run(self) -> bool:
        """Block until window closed. Returns True if a model was applied."""
        self.root.mainloop()
        return not self._cancelled


# ---------------------------------------------------------------------------
# Convenience wrappers
# ---------------------------------------------------------------------------

def run_first_run_wizard(on_apply: Callable[[str], None]) -> bool:
    """Show the picker. Returns True if user picked & confirmed a model."""
    win = ModelWindow(active_id=None, first_run=True, on_apply=on_apply)
    return win.run()


def run_manager(active_id: str | None,
                on_apply: Callable[[str], None]) -> None:
    """Show the model manager (non-modal style; this blocks until closed)."""
    win = ModelWindow(active_id=active_id, first_run=False, on_apply=on_apply)
    win.run()
