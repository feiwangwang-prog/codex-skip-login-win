"""tkinter GUI 界面"""
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


def run_gui():
    root = tk.Tk()
    root.title("Codex Switch - 免登工具")
    root.geometry("520x480")
    root.resizable(False, False)

    # 居中
    root.update_idletasks()

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=8, pady=8)

    # --- Tab 1: 自定义模型 ---
    tab1 = ttk.Frame(notebook, padding=10)
    notebook.add(tab1, text="自定义模型免登")
    _build_local_tab(tab1)

    # --- Tab 2: 恢复官方 ---
    tab2 = ttk.Frame(notebook, padding=10)
    notebook.add(tab2, text="恢复官方登录")
    _build_official_tab(tab2)

    root.mainloop()


def _build_local_tab(parent):
    state = read_state()
    auth = read_auth()

    # API 地址
    ttk.Label(parent, text="API 地址:").grid(row=0, column=0, sticky="w", pady=4)
    var_url = tk.StringVar(value=state.get("base_url", "http://127.0.0.1:8080"))
    ttk.Entry(parent, textvariable=var_url, width=45).grid(row=0, column=1, columnspan=2, sticky="we", pady=4)

    # 模型 ID
    ttk.Label(parent, text="模型 ID:").grid(row=1, column=0, sticky="w", pady=4)
    var_model = tk.StringVar(value=state.get("model", "MiMo-7B-RL"))
    ttk.Entry(parent, textvariable=var_model, width=45).grid(row=1, column=1, columnspan=2, sticky="we", pady=4)

    # API Key
    ttk.Label(parent, text="API Key:").grid(row=2, column=0, sticky="w", pady=4)
    var_key = tk.StringVar(value=auth.get("api_key", ""))
    ttk.Entry(parent, textvariable=var_key, width=45, show="*").grid(row=2, column=1, columnspan=2, sticky="we", pady=4)

    # 复选框
    var_chat_adapter = tk.BooleanVar(value=state.get("chat_adapter", True))
    ttk.Checkbutton(parent, text="上游仅支持 Chat Completions（启用协议适配器）", variable=var_chat_adapter).grid(
        row=3, column=0, columnspan=3, sticky="w", pady=4
    )

    var_skip_login = tk.BooleanVar(value=state.get("skip_login", True))
    ttk.Checkbutton(parent, text="跳过 ChatGPT 登录", variable=var_skip_login).grid(
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
            messagebox.showwarning("提示", "请填写完整信息")
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
            messagebox.showinfo("成功", f"配置已保存\n{CONFIG_PATH}")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _apply_and_restart():
        _apply()
        _restart_codex()

    def _restart_codex():
        try:
            subprocess.run(["taskkill", "/IM", "codex.exe", "/F"], capture_output=True)
            # 尝试常见安装路径
            for path in [
                os.path.expandvars(r"%LOCALAPPDATA%\Codex\codex.exe"),
                os.path.expandvars(r"%PROGRAMFILES%\Codex\codex.exe"),
            ]:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    return
            messagebox.showinfo("提示", "配置已保存，请手动重启 Codex Desktop")
        except Exception as e:
            messagebox.showwarning("提示", f"重启 Codex 失败: {e}\n请手动重启")

    ttk.Button(btn_frame, text="应用并重启 Codex", command=_apply_and_restart).pack(side="left", padx=4)
    ttk.Button(btn_frame, text="仅保存配置", command=_apply).pack(side="left", padx=4)

    # 适配器控制
    adapter_frame = ttk.LabelFrame(parent, text="协议适配器", padding=8)
    adapter_frame.grid(row=6, column=0, columnspan=3, sticky="we", pady=8)

    lbl_adapter_status = ttk.Label(adapter_frame, text="状态: 未运行")
    lbl_adapter_status.pack(side="left", padx=4)

    def _update_adapter_label():
        s = adapter_status()
        if s["running"]:
            lbl_adapter_status.config(text=f"状态: 运行中 (请求:{s['request_count']} 错误:{s['error_count']})")
        else:
            lbl_adapter_status.config(text="状态: 未运行")
        parent.after(2000, _update_adapter_label)

    _update_adapter_label()

    def _toggle_adapter():
        s = adapter_status()
        if s["running"]:
            stop_adapter()
            messagebox.showinfo("适配器", "适配器已停止")
        else:
            base_url = var_url.get().strip()
            model = var_model.get().strip()
            api_key = var_key.get().strip()
            if not base_url or not model or not api_key:
                messagebox.showwarning("提示", "请先填写 API 地址、模型 ID 和 API Key")
                return
            msg = start_adapter(base_url, model, api_key, ADAPTER_PORT)
            messagebox.showinfo("适配器", msg)

    ttk.Button(adapter_frame, text="启动/停止适配器", command=_toggle_adapter).pack(side="right", padx=4)


def _build_official_tab(parent):
    state = read_state()

    ttk.Label(parent, text="官方模型:").grid(row=0, column=0, sticky="w", pady=8)
    var_model = tk.StringVar(value=state.get("model", "o3"))
    ttk.Entry(parent, textvariable=var_model, width=30).grid(row=0, column=1, sticky="w", pady=8)

    def _restore():
        model = var_model.get().strip()
        if not model:
            messagebox.showwarning("提示", "请输入模型名称")
            return
        try:
            text = apply_official_config(model=model)
            write_config_raw(text)
            update_state({"mode": "official", "model": model})
            messagebox.showinfo("成功", f"已恢复官方配置\n模型: {model}\n{CONFIG_PATH}")
        except Exception as e:
            messagebox.showerror("错误", str(e))

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
            messagebox.showinfo("提示", "配置已恢复，请手动重启 Codex Desktop")
        except Exception as e:
            messagebox.showwarning("提示", f"重启失败: {e}\n请手动重启 Codex")

    btn_frame = ttk.Frame(parent)
    btn_frame.grid(row=1, column=0, columnspan=2, pady=16, sticky="w")
    ttk.Button(btn_frame, text="恢复官方并重启 Codex", command=_restore_and_restart).pack(side="left", padx=4)
    ttk.Button(btn_frame, text="仅恢复配置", command=_restore).pack(side="left", padx=4)
