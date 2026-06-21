"""tkinter GUI 界面（中英文双语）"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import os

from .config import apply_local_config, apply_official_config, write_config_raw, read_config_raw
from .auth import save_auth, read_auth
from .state import update_state, read_state
from .adapter import start_adapter, stop_adapter, adapter_status
from .constants import CONFIG_PATH, ADAPTER_PORT, CODEX_HOME
from .i18n import t, toggle_lang


def run_gui():
    root = tk.Tk()
    root.geometry("520x480")
    root.resizable(False, False)

    def _rebuild():
        """销毁所有子控件并重建 UI（语言切换时调用）"""
        for widget in root.winfo_children():
            widget.destroy()
        _build_ui(root, _rebuild)

    _rebuild(root)
    root.mainloop()


def _build_ui(root, rebuild_cb):
    """构建全部 UI 控件"""
    root.title(t("app_title"))

    # 语言切换按钮（右上角）
    lang_btn = ttk.Button(root, text=t("lang_switch"), command=lambda: _on_switch_lang(rebuild_cb))
    lang_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-8, y=4)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=8, pady=(28, 8))

    # --- Tab 1: 自定义模型 ---
    tab1 = ttk.Frame(notebook, padding=10)
    notebook.add(tab1, text=t("tab_custom"))
    _build_local_tab(tab1)

    # --- Tab 2: 恢复官方 ---
    tab2 = ttk.Frame(notebook, padding=10)
    notebook.add(tab2, text=t("tab_official"))
    _build_official_tab(tab2)


def _on_switch_lang(rebuild_cb):
    """切换语言后重建 UI"""
    toggle_lang()
    rebuild_cb()


def _build_local_tab(parent):
    state = read_state()
    auth = read_auth()

    # API 地址
    ttk.Label(parent, text=t("api_url")).grid(row=0, column=0, sticky="w", pady=4)
    var_url = tk.StringVar(value=state.get("base_url", "http://127.0.0.1:8080"))
    ttk.Entry(parent, textvariable=var_url, width=45).grid(row=0, column=1, columnspan=2, sticky="we", pady=4)

    # 模型 ID
    ttk.Label(parent, text=t("model_id")).grid(row=1, column=0, sticky="w", pady=4)
    var_model = tk.StringVar(value=state.get("model", "MiMo-7B-RL"))
    ttk.Entry(parent, textvariable=var_model, width=45).grid(row=1, column=1, columnspan=2, sticky="we", pady=4)

    # API Key
    ttk.Label(parent, text=t("api_key")).grid(row=2, column=0, sticky="w", pady=4)
    var_key = tk.StringVar(value=auth.get("api_key", ""))
    ttk.Entry(parent, textvariable=var_key, width=45, show="*").grid(row=2, column=1, columnspan=2, sticky="we", pady=4)

    # 复选框
    var_chat_adapter = tk.BooleanVar(value=state.get("chat_adapter", True))
    ttk.Checkbutton(parent, text=t("chat_adapter"), variable=var_chat_adapter).grid(
        row=3, column=0, columnspan=3, sticky="w", pady=4
    )

    var_skip_login = tk.BooleanVar(value=state.get("skip_login", True))
    ttk.Checkbutton(parent, text=t("skip_login"), variable=var_skip_login).grid(
        row=4, column=0, columnspan=3, sticky="w", pady=4
    )

    # 按钮区
    btn_frame = ttk.Frame(parent)
    btn_frame.grid(row=5, column=0, columnspan=3, pady=12, sticky="we")

    def _apply():
        base_url = var_url.get().strip()
        model = var_model.get().strip()
        api_key = var_key.get().strip()
        if not base_url or not model or not api_key:
            messagebox.showwarning(t("msg_hint"), t("msg_fill_all"))
            return
        try:
            text = apply_local_config(
                base_url=base_url,
                model=model,
                api_key=api_key,
                use_chat_adapter=var_chat_adapter.get(),
                skip_login=var_skip_login.get(),
            )
            write_config_raw(text)
            save_auth(access_token="", api_key=api_key)
            update_state({
                "mode": "local",
                "base_url": base_url,
                "model": model,
                "chat_adapter": var_chat_adapter.get(),
                "skip_login": var_skip_login.get(),
            })
            messagebox.showinfo(t("msg_success"), f"{t('msg_saved')}\n{CONFIG_PATH}")
        except Exception as e:
            messagebox.showerror(t("msg_error"), str(e))

    def _apply_and_restart():
        _apply()
        _restart_codex()

    def _restart_codex():
        try:
            subprocess.run(["taskkill", "/IM", "codex.exe", "/F"], capture_output=True)
            for path in [
                os.path.expandvars(r"%LOCALAPPDATA%\Codex\codex.exe"),
                os.path.expandvars(r"%PROGRAMFILES%\Codex\codex.exe"),
            ]:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    return
            messagebox.showinfo(t("msg_hint"), t("msg_restart_manual"))
        except Exception as e:
            messagebox.showwarning(t("msg_hint"), f"{t('msg_restart_fail')}: {e}\n{t('msg_manual_restart')}")

    ttk.Button(btn_frame, text=t("btn_apply_restart"), command=_apply_and_restart).pack(side="left", padx=4)
    ttk.Button(btn_frame, text=t("btn_save_only"), command=_apply).pack(side="left", padx=4)

    # 适配器控制
    adapter_frame = ttk.LabelFrame(parent, text=t("adapter_group"), padding=8)
    adapter_frame.grid(row=6, column=0, columnspan=3, sticky="we", pady=8)

    lbl_adapter_status = ttk.Label(adapter_frame, text=t("adapter_status_stopped"))
    lbl_adapter_status.pack(side="left", padx=4)

    def _update_adapter_label():
        s = adapter_status()
        if s["running"]:
            lbl_adapter_status.config(text=f"{t('adapter_status_running')} (req:{s['request_count']} err:{s['error_count']})")
        else:
            lbl_adapter_status.config(text=t("adapter_status_stopped"))
        parent.after(2000, _update_adapter_label)

    _update_adapter_label()

    def _toggle_adapter():
        s = adapter_status()
        if s["running"]:
            stop_adapter()
            messagebox.showinfo(t("msg_adapter"), t("msg_adapter_stopped"))
        else:
            base_url = var_url.get().strip()
            model = var_model.get().strip()
            api_key = var_key.get().strip()
            if not base_url or not model or not api_key:
                messagebox.showwarning(t("msg_hint"), t("msg_fill_api_first"))
                return
            msg = start_adapter(base_url, model, api_key, ADAPTER_PORT)
            messagebox.showinfo(t("msg_adapter"), msg)

    ttk.Button(adapter_frame, text=t("btn_adapter_toggle"), command=_toggle_adapter).pack(side="right", padx=4)


def _build_official_tab(parent):
    state = read_state()

    ttk.Label(parent, text=t("official_model")).grid(row=0, column=0, sticky="w", pady=8)
    var_model = tk.StringVar(value=state.get("model", "o3"))
    ttk.Entry(parent, textvariable=var_model, width=30).grid(row=0, column=1, sticky="w", pady=8)

    def _restore():
        model = var_model.get().strip()
        if not model:
            messagebox.showwarning(t("msg_hint"), t("msg_input_model"))
            return
        try:
            text = apply_official_config(model=model)
            write_config_raw(text)
            update_state({"mode": "official", "model": model})
            messagebox.showinfo(t("msg_success"), f"{t('msg_restored')}\n{t('cli_model')}: {model}\n{CONFIG_PATH}")
        except Exception as e:
            messagebox.showerror(t("msg_error"), str(e))

    def _restore_and_restart():
        _restore()
        try:
            subprocess.run(["taskkill", "/IM", "codex.exe", "/F"], capture_output=True)
            for path in [
                os.path.expandvars(r"%LOCALAPPDATA%\Codex\codex.exe"),
                os.path.expandvars(r"%PROGRAMFILES%\Codex\codex.exe"),
            ]:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    return
            messagebox.showinfo(t("msg_hint"), t("msg_restore_manual"))
        except Exception as e:
            messagebox.showwarning(t("msg_hint"), f"{t('msg_restart_fail')}: {e}\n{t('msg_manual_restart')}")

    btn_frame = ttk.Frame(parent)
    btn_frame.grid(row=1, column=0, columnspan=2, pady=16, sticky="w")
    ttk.Button(btn_frame, text=t("btn_restore_restart"), command=_restore_and_restart).pack(side="left", padx=4)
    ttk.Button(btn_frame, text=t("btn_restore_only"), command=_restore).pack(side="left", padx=4)
