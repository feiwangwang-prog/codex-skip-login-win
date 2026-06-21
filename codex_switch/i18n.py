"""国际化模块 — UI 字符串中英文支持"""
import os

STRINGS = {
    "zh": {
        # GUI - 窗口
        "app_title": "Codex Switch - 免登工具",
        # GUI - Tab
        "tab_custom": "自定义模型免登",
        "tab_official": "恢复官方登录",
        # GUI - 自定义模型 Tab
        "api_url": "API 地址:",
        "model_id": "模型 ID:",
        "api_key": "API Key:",
        "chat_adapter": "上游仅支持 Chat Completions（启用协议适配器）",
        "skip_login": "跳过 ChatGPT 登录",
        "btn_apply_restart": "应用并重启 Codex",
        "btn_save_only": "仅保存配置",
        # GUI - 适配器
        "adapter_group": "协议适配器",
        "adapter_status_running": "状态: 运行中",
        "adapter_status_stopped": "状态: 未运行",
        "btn_adapter_toggle": "启动/停止适配器",
        # GUI - 恢复官方 Tab
        "btn_restore_restart": "恢复官方并重启 Codex",
        "btn_restore_only": "仅恢复配置",
        "official_model": "官方模型:",
        # GUI - 消息
        "msg_saved": "配置已保存",
        "msg_restored": "已恢复官方配置",
        "msg_adapter_stopped": "适配器已停止",
        "msg_adapter_started": "适配器已启动",
        "msg_fill_all": "请填写完整信息",
        "msg_restart_manual": "配置已保存，请手动重启 Codex Desktop",
        "msg_restore_manual": "配置已恢复，请手动重启 Codex Desktop",
        "msg_restart_fail": "重启 Codex 失败",
        "msg_manual_restart": "请手动重启",
        "msg_fill_api_first": "请先填写 API 地址、模型 ID 和 API Key",
        "msg_restore_hint": "配置已恢复，请手动重启 Codex Desktop",
        "msg_input_model": "请输入模型名称",
        # GUI - 通用消息框标题
        "msg_error": "错误",
        "msg_success": "成功",
        "msg_hint": "提示",
        "msg_warning": "警告",
        "msg_adapter": "适配器",
        # GUI - 语言切换
        "lang_switch": "EN",

        # CLI - 子命令描述
        "cli_desc": "Codex Desktop Windows 免登 + 国产模型接入工具",
        "cli_help_local": "应用自定义模型免登配置",
        "cli_help_official": "恢复官方登录",
        "cli_help_status": "查看当前状态",
        "cli_help_adapter": "启动协议适配器",
        "cli_help_gui": "启动 GUI 界面",
        "cli_arg_base_url": "上游 API 地址",
        "cli_arg_model": "模型 ID",
        "cli_arg_api_key": "API Key",
        "cli_arg_chat_adapter": "上游仅支持 Chat Completions，启用协议适配器",
        "cli_arg_skip_login": "跳过 ChatGPT 登录",
        "cli_arg_adapter_port": "适配器端口",
        "cli_arg_official_model": "官方模型（默认 o3）",
        # CLI - 输出
        "cli_applied": "✅ 已应用自定义模型配置",
        "cli_model": "模型",
        "cli_api": "API",
        "cli_adapter": "适配器",
        "cli_enabled": "启用",
        "cli_disabled": "关闭",
        "cli_skip_login": "跳过登录",
        "cli_yes": "是",
        "cli_no": "否",
        "cli_config_file": "配置文件",
        "cli_adapter_hint": "💡 请运行以下命令启动适配器:",
        "cli_restored": "✅ 已恢复官方配置",
        "cli_status_title": "=== Codex Switch 状态 ===",
        "cli_mode": "模式",
        "cli_not_set": "未设置",
        "cli_upstream": "上游",
        "cli_request_count": "请求数",
        "cli_error_count": "错误数",
        "cli_adapter_status": "--- 适配器状态 ---",
        "cli_running": "运行中",
        "cli_file_missing": "（文件不存在或为空）",
    },
    "en": {
        # GUI - Window
        "app_title": "Codex Switch - Login Bypass Tool",
        # GUI - Tabs
        "tab_custom": "Custom Model",
        "tab_official": "Restore Official",
        # GUI - Custom Model Tab
        "api_url": "API URL:",
        "model_id": "Model ID:",
        "api_key": "API Key:",
        "chat_adapter": "Upstream only supports Chat Completions (enable adapter)",
        "skip_login": "Skip ChatGPT Login",
        "btn_apply_restart": "Apply & Restart Codex",
        "btn_save_only": "Save Only",
        # GUI - Adapter
        "adapter_group": "Protocol Adapter",
        "adapter_status_running": "Status: Running",
        "adapter_status_stopped": "Status: Stopped",
        "btn_adapter_toggle": "Start/Stop Adapter",
        # GUI - Restore Official Tab
        "btn_restore_restart": "Restore & Restart Codex",
        "btn_restore_only": "Restore Only",
        "official_model": "Official Model:",
        # GUI - Messages
        "msg_saved": "Config saved",
        "msg_restored": "Official config restored",
        "msg_adapter_stopped": "Adapter stopped",
        "msg_adapter_started": "Adapter started",
        "msg_fill_all": "Please fill in all fields",
        "msg_restart_manual": "Config saved. Please restart Codex Desktop manually.",
        "msg_restore_manual": "Config restored. Please restart Codex Desktop manually.",
        "msg_restart_fail": "Failed to restart Codex",
        "msg_manual_restart": "Please restart manually",
        "msg_fill_api_first": "Please fill in API URL, Model ID and API Key first",
        "msg_restore_hint": "Config restored. Please restart Codex Desktop manually.",
        "msg_input_model": "Please enter model name",
        # GUI - Common message box titles
        "msg_error": "Error",
        "msg_success": "Success",
        "msg_hint": "Hint",
        "msg_warning": "Warning",
        "msg_adapter": "Adapter",
        # GUI - Language switch
        "lang_switch": "中文",

        # CLI - Subcommand descriptions
        "cli_desc": "Codex Desktop Windows login bypass + custom model tool",
        "cli_help_local": "Apply custom model login-bypass config",
        "cli_help_official": "Restore official login config",
        "cli_help_status": "Show current status",
        "cli_help_adapter": "Start protocol adapter",
        "cli_help_gui": "Launch GUI",
        "cli_arg_base_url": "Upstream API URL",
        "cli_arg_model": "Model ID",
        "cli_arg_api_key": "API Key",
        "cli_arg_chat_adapter": "Upstream only supports Chat Completions, enable adapter",
        "cli_arg_skip_login": "Skip ChatGPT login",
        "cli_arg_adapter_port": "Adapter port",
        "cli_arg_official_model": "Official model (default: o3)",
        # CLI - Output
        "cli_applied": "✅ Custom model config applied",
        "cli_model": "Model",
        "cli_api": "API",
        "cli_adapter": "Adapter",
        "cli_enabled": "enabled",
        "cli_disabled": "disabled",
        "cli_skip_login": "Skip login",
        "cli_yes": "yes",
        "cli_no": "no",
        "cli_config_file": "Config file",
        "cli_adapter_hint": "💡 Run the following command to start the adapter:",
        "cli_restored": "✅ Official config restored",
        "cli_status_title": "=== Codex Switch Status ===",
        "cli_mode": "Mode",
        "cli_not_set": "not set",
        "cli_upstream": "Upstream",
        "cli_request_count": "Requests",
        "cli_error_count": "Errors",
        "cli_adapter_status": "--- Adapter Status ---",
        "cli_running": "Running",
        "cli_file_missing": "(file does not exist or is empty)",
    },
}

current_lang = "zh"


def t(key):
    """获取当前语言的翻译字符串"""
    return STRINGS.get(current_lang, STRINGS["zh"]).get(key, key)


def set_lang(lang):
    """设置语言"""
    global current_lang
    if lang in STRINGS:
        current_lang = lang


def toggle_lang():
    """切换语言"""
    global current_lang
    current_lang = "en" if current_lang == "zh" else "zh"


def init_lang(lang_arg=None):
    """初始化语言：优先命令行参数，其次环境变量，最后默认中文"""
    if lang_arg:
        set_lang(lang_arg)
    elif os.environ.get("CODEX_SWITCH_LANG", "").lower() in ("en", "zh"):
        set_lang(os.environ["CODEX_SWITCH_LANG"].lower())
