"""Lazy Comments GUI with language selector and API key settings."""
from __future__ import annotations
import threading, tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable
import os, sys
from lazy_comments.downloader import download_model, uninstall_model
from lazy_comments.registry import MODELS, RECOMMENDED_MODEL_ID, is_installed

LANGS = [
    ("Russian", "ru"), ("English", "en"), ("Ukrainian", "uk"),
    ("German", "de"), ("French", "fr"), ("Spanish", "es"),
    ("Italian", "it"), ("Portuguese", "pt"), ("Polish", "pl"),
    ("Czech", "cs"), ("Dutch", "nl"), ("Hungarian", "hu"),
    ("Romanian", "ro"), ("Turkish", "tr"), ("Greek", "el"),
    ("Hebrew", "he"), ("Arabic", "ar"), ("Hindi", "hi"),
    ("Chinese Simplified", "zh-CN"), ("Chinese Traditional", "zh-TW"),
    ("Japanese", "ja"), ("Korean", "ko"), ("Thai", "th"),
    ("Vietnamese", "vi"), ("Indonesian", "id"), ("Malay", "ms"),
    ("Filipino", "tl"), ("Finnish", "fi"), ("Swedish", "sv"),
    ("Norwegian", "no"), ("Danish", "da"), ("Bulgarian", "bg"),
    ("Serbian", "sr"), ("Croatian", "hr"), ("Slovak", "sk"),
    ("Slovenian", "sl"), ("Estonian", "et"), ("Latvian", "lv"),
    ("Lithuanian", "lt"),
]

def _lang_display(code):
    for name, c in LANGS:
        if c == code:
            return name + " (" + c + ")"
    return code

def _human_size(mb):
    return f"{mb/1024:.1f} GB" if mb >= 1024 else f"{mb} MB"

def _status(model_id, active):
    if model_id == active: return "[active]"
    if is_installed(model_id): return "[installed]"
    return ""

class _ProgressDialog:
    def __init__(self, parent, title):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("420x140")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        self.lbl = tk.StringVar(value="Preparing...")
        tk.Label(self.top, textvariable=self.lbl, anchor="w", wraplength=400).pack(
            padx=16, pady=(16, 8), fill="x")
        self.pb = ttk.Progressbar(self.top, mode="determinate", length=380, maximum=1000)
        self.pb.pack(padx=16, pady=4)
        self.detail = tk.StringVar()
        tk.Label(self.top, textvariable=self.detail, fg="#666").pack(
            padx=16, pady=(4, 12), fill="x")

    def update(self, done, total, stage):
        def _a():
            pct = int(done * 1000 / total) if total else 0
            self.pb["value"] = pct
            detail = (f"{stage}: {done//1024//1024:.1f}/{total//1024//1024:.1f} MB ({pct/10:.0f}%)"
                       if stage == "Download" else f"{stage}: {done}/{total}")
            self.lbl.set(stage + "...")
            self.detail.set(detail)
        try: self.top.after(0, _a)
        except tk.TclError: pass

    def close(self):
        try: self.top.grab_release(); self.top.destroy()
        except tk.TclError: pass

class ModelWindow:
    def __init__(self, active_id, first_run, on_apply):
        self.active_id = active_id
        self.first_run = first_run
        self.on_apply = on_apply
        self._chosen = active_id or RECOMMENDED_MODEL_ID
        self._cancelled = True
        self.root = tk.Tk()
        self.root.title("Lazy Comments - Model Selection" if first_run else "Lazy Comments - Models")
        self.root.geometry("680x560")
        self._build()
        self._refresh()

    def _build(self):
        tk.Label(self.root, text="Select speech recognition model. All models work offline.",
                 wraplength=640, justify="left", anchor="w").pack(padx=16, pady=(14, 8), fill="x")
        outer = tk.Frame(self.root)
        outer.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        c = tk.Canvas(outer, borderwidth=0, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=c.yview)
        self.lf = tk.Frame(c)
        self.lf.bind("<Configure>", lambda e: c.configure(scrollregion=c.bbox("all")))
        c.create_window((0, 0), window=self.lf, anchor="nw", width=620)
c.configure(yscrollcommand=sb.set)
        c.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        br = tk.Frame(self.root)
        br.pack(fill="x", padx=16, pady=(4, 14))
        if self.first_run:
            tk.Button(br, text="Cancel", width=12, command=self._cancel).pack(side="right", padx=(8, 0))
            tk.Button(br, text="Continue", width=18, command=self._confirm, default="active").pack(side="right")
        else:
            tk.Button(br, text="Close", width=12, command=self._close).pack(side="right")

    def _refresh(self):
        for w in self.lf.winfo_children(): w.destroy()
        for mid, info in MODELS.items(): self._row(mid, info)

    def _row(self, mid, info):
        fr = tk.Frame(self.lf, bd=1, relief="solid", padx=10, pady=8)
        fr.pack(fill="x", pady=4)
        hf = tk.Frame(fr); hf.pack(fill="x")
        if self.first_run:
            tk.Radiobutton(hf, text=info["name"], variable=self._rv(), value=mid,
                           command=lambda m=mid: self._set(m),
                           font=("Segoe UI", 10, "bold")).pack(side="left")
        else:
            tk.Label(hf, text=info["name"], font=("Segoe UI", 10, "bold")).pack(side="left")
        if info.get("tag"): tk.Label(hf, text="  ["+info["tag"]+"]", fg="#0a7").pack(side="left")
        st = _status(mid, self.active_id)
        if st: tk.Label(hf, text="  "+st, fg="#06c").pack(side="left")
        tk.Label(fr, text="Engine: "+info["engine"]+"   Lang: "+(info.get("language","---"))+"   Size: "+_human_size(info["size_mb"]),
                 fg="#666", anchor="w").pack(fill="x", pady=(4, 0))
        tk.Label(fr, text=info.get("description",""), wraplength=580, anchor="w", justify="left").pack(fill="x", pady=(4, 0))
        if not self.first_run:
            af = tk.Frame(fr); af.pack(fill="x", pady=(8, 0))
            ins = is_installed(mid)
            if not ins:
                tk.Button(af, text="Download", command=lambda m=mid: self._dl(m)).pack(side="left")
            else:
                if mid != self.active_id:
                    tk.Button(af, text="Activate", command=lambda m=mid: self._act(m)).pack(side="left")
                tk.Button(af, text="Delete", command=lambda m=mid: self._del(m)).pack(side="left", padx=(6, 0))

    def _rv(self):
        if not hasattr(self,"_rv_"): self._rv_ = tk.StringVar(value=self._chosen or "")
        return self._rv_

    def _set(self, mid): self._chosen = mid

    def _dl(self, mid, activate=False):
        dlg = _ProgressDialog(self.root, "Downloading: "+MODELS[mid]["name"])
        rh = {}
        def w():
            try:
                download_model(mid, on_progress=dlg.update, on_log=lambda m: print(m))
                rh["ok"] = True
            except Exception as e:
                rh["error"] = str(e); import traceback; traceback.print_exc()
            finally: self.root.after(0, self._finish_dl)
        def _finish_dl():
            dlg.close()
            if "error" in rh: messagebox.showerror("Download error","Failed:\n\n"+rh["error"])
            elif activate: self._act(mid, skip_check=True)
            self._refresh()
        threading.Thread(target=w, daemon=True, name="DL").start()

    def _act(self, mid, skip_check=False):
        if not skip_check and not is_installed(mid): self._dl(mid, activate=True); return
        try:
            self.on_apply(mid)
            self.active_id = mid
            self._refresh()
        except Exception as e: messagebox.showerror("Activation error", str(e))

    def _del(self, mid):
        if mid == self.active_id: messagebox.showinfo("Cannot delete","Switch Lazy Comments to another model first."); return
        if not messagebox.askyesno("Delete?", "Delete model files for '" + MODELS[mid]["name"] + "'?"):
            return

        uninstall_model(mid); self._refresh()

    def _confirm(self):
        if not self._chosen: messagebox.showinfo("Select model","Pick a model from the list."); return
        if not is_installed(self._chosen):
dlg = _ProgressDialog(self.root, "Downloading: "+MODELS[self._chosen]["name"])
            rh = {}
            def w():
                try:
                    download_model(self._chosen, on_progress=dlg.update, on_log=lambda m: print(m))
                    rh["ok"] = True
                except Exception as e: rh["error"] = str(e)
                finally: self.root.after(0, self._finish_confirm)
            def _finish_confirm():
                dlg.close()
                if "error" in rh: messagebox.showerror("Download error",rh["error"]); return
                self.on_apply(self._chosen)
                self._cancelled = False
                self.root.destroy()
                self.root.after(200, self._settings_window)
            threading.Thread(target=w, daemon=True, name="DL").start()
        else:
            self.on_apply(self._chosen)
            self._cancelled = False
            self.root.destroy()
            self._settings_window()

    def _settings_window(self):
        from lazy_comments.config import load_config, update_config
        cfg = load_config()
        saved_key = cfg.get("deepl_api_key", "")
        saved_source = cfg.get("source_lang", "ru")
        saved_target = cfg.get("target_lang", "en")

        win = tk.Tk()
        win.title("Lazy Comments - Settings")
        win.geometry("580x440")
        win.resizable(False, False)

        tk.Label(win, text="Lazy Comments Settings", font=("Segoe UI", 13, "bold")).pack(pady=(18, 4))
        tk.Label(win, text="Configure translation languages and API key.", fg="#666").pack(pady=(0, 12))

        # Languages
        lf = tk.LabelFrame(win, text="Languages", padx=12, pady=8)
        lf.pack(fill="x", padx=20, pady=(0, 8))

        src_var = tk.StringVar(value=_lang_display(saved_source))
        tgt_var = tk.StringVar(value=_lang_display(saved_target))
        lang_opts = [_lang_display(c) for _, c in LANGS]

        tk.Label(lf, text="From:").grid(row=0, column=0, sticky="w", pady=4)
        tk.OptionMenu(lf, src_var, *lang_opts).grid(row=0, column=1, padx=(8, 8), pady=4, sticky="w")
        tk.Label(lf, text="To:").grid(row=1, column=0, sticky="w", pady=4)
        tk.OptionMenu(lf, tgt_var, *lang_opts).grid(row=1, column=1, padx=(8, 8), pady=4, sticky="w")

        def swap():
            sv = src_var.get(); tv = tgt_var.get()
            src_var.set(tv); tgt_var.set(sv)
        tk.Button(lf, text="< > swap", command=swap, width=10).grid(
            row=0, column=2, rowspan=2, padx=(4, 0))

        # DeepL API Key
        kf = tk.LabelFrame(win, text="DeepL API Key", padx=12, pady=8)
        kf.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(kf, text="API Key:", width=10, anchor="w").grid(row=0, column=0, sticky="w")
        key_var = tk.StringVar(value=saved_key)
        tk.Entry(kf, textvariable=key_var, width=42).grid(row=0, column=1, padx=(4, 0), sticky="ew")
        tk.Label(kf, text="Get free key: deepl.com/pro-api — 500k chars/month free",
                 fg="#06c", wraplength=400).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

        bf = tk.Frame(win)
        bf.pack(pady=14)

        def get_code(var):
            val = var.get()
            for n, c in LANGS:
                if _lang_display(c) == val:
                    return c
            return "en"

        def save():
            update_config(
                deepl_api_key=key_var.get().strip(),
                source_lang=get_code(src_var),
                target_lang=get_code(tgt_var),
            )
            win.destroy()

        tk.Button(bf, text="Cancel", width=12, command=win.destroy).pack(side="left", padx=8)
        tk.Button(bf, text="Save", width=18, command=save).pack(side="left")
        win.bind("<Return>", lambda e: save())
        win.mainloop()

    def _cancel(self):
        if messagebox.askyesno("Exit?","Without a model Lazy Comments cannot recognize speech. Exit?"): self.root.destroy()

    def _close(self): self.root.destroy()
    def run(self): self.root.mainloop(); return not self._cancelled

def run_first_run_wizard(on_apply): return ModelWindow(None, True, on_apply).run()
def run_manager(active_id, on_apply): ModelWindow(active_id, False, on_apply).run()
