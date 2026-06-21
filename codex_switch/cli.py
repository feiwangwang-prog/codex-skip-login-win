"""CLI 入口：codex-switch local/official/status/adapter/gui"""
import argparse
import sys

from .config import apply_local_config, apply_official_config, write_config_raw, read_config_raw
from .auth import save_auth
from .state import update_state, read_state
from .adapter import start_adapter, stop_adapter, adapter_status, run_adapter_forever
from .constants import ADAPTER_PORT, CONFIG_PATH


def cmd_local(args):
    """应用自定义模型免登配置"""
    use_adapter = args.chat_adapter
    skip_login = args.skip_login

    # 写 config.toml
    text = apply_local_config(
        base_url=args.base_url,
        model=args.model,
        api_key=args.api_key,
        use_chat_adapter=use_adapter,
        skip_login=skip_login,
    )
    write_config_raw(text)

    # 保存 api_key 到 auth.json
    if args.api_key:
        save_auth(access_token="", api_key=args.api_key)

    # 保存状态
    update_state({
        "mode": "local",
        "base_url": args.base_url,
        "model": args.model,
        "chat_adapter": use_adapter,
        "skip_login": skip_login,
        "adapter_port": args.adapter_port,
    })

    print(f"✅ 已应用自定义模型配置")
    print(f"   模型: {args.model}")
    print(f"   API: {args.base_url}")
    print(f"   适配器: {'启用' if use_adapter else '关闭'}")
    print(f"   跳过登录: {'是' if skip_login else '否'}")
    print(f"   配置文件: {CONFIG_PATH}")

    if use_adapter:
        print(f"\n💡 请运行以下命令启动适配器:")
        print(f"   python -m codex_switch.cli adapter --base-url {args.base_url} --model {args.model} --api-key {args.api_key}")


def cmd_official(args):
    """恢复官方登录配置"""
    text = apply_official_config(model=args.model)
    write_config_raw(text)

    update_state({
        "mode": "official",
        "model": args.model,
    })

    print(f"✅ 已恢复官方配置")
    print(f"   模型: {args.model}")
    print(f"   配置文件: {CONFIG_PATH}")


def cmd_status(args):
    """显示当前状态"""
    state = read_state()
    config = read_config_raw()

    print("=== Codex Switch 状态 ===")
    print(f"模式: {state.get('mode', '未设置')}")
    if state.get('mode') == 'local':
        print(f"模型: {state.get('model', '-')}")
        print(f"API: {state.get('base_url', '-')}")
        print(f"适配器: {'启用' if state.get('chat_adapter') else '关闭'}")
        print(f"跳过登录: {'是' if state.get('skip_login') else '否'}")
    elif state.get('mode') == 'official':
        print(f"模型: {state.get('model', '-')}")

    print(f"\n--- config.toml ({CONFIG_PATH}) ---")
    if config:
        print(config)
    else:
        print("（文件不存在或为空）")

    print(f"\n--- 适配器状态 ---")
    a_status = adapter_status()
    print(f"运行中: {a_status['running']}")
    if a_status['running']:
        print(f"上游: {a_status['base_url']}")
        print(f"模型: {a_status['model']}")
        print(f"请求数: {a_status['request_count']}")
        print(f"错误数: {a_status['error_count']}")


def cmd_adapter(args):
    """启动协议适配器（阻塞式）"""
    run_adapter_forever(
        base_url=args.base_url,
        model=args.model,
        api_key=args.api_key,
        port=args.port,
    )


def cmd_gui(args):
    """启动 GUI"""
    from .gui import run_gui
    run_gui()


def main():
    parser = argparse.ArgumentParser(
        prog="codex-switch",
        description="Codex Desktop Windows 免登 + 国产模型接入工具",
    )
    sub = parser.add_subparsers(dest="command", help="子命令")

    # local
    p_local = sub.add_parser("local", help="应用自定义模型免登配置")
    p_local.add_argument("--base-url", required=True, help="上游 API 地址")
    p_local.add_argument("--model", required=True, help="模型 ID")
    p_local.add_argument("--api-key", required=True, help="API Key")
    p_local.add_argument("--chat-adapter", action="store_true", help="上游仅支持 Chat Completions，启用协议适配器")
    p_local.add_argument("--skip-login", action="store_true", help="跳过 ChatGPT 登录")
    p_local.add_argument("--adapter-port", type=int, default=ADAPTER_PORT, help="适配器端口")
    p_local.set_defaults(func=cmd_local)

    # official
    p_official = sub.add_parser("official", help="恢复官方登录")
    p_official.add_argument("--model", default="o3", help="官方模型（默认 o3）")
    p_official.set_defaults(func=cmd_official)

    # status
    p_status = sub.add_parser("status", help="查看当前状态")
    p_status.set_defaults(func=cmd_status)

    # adapter
    p_adapter = sub.add_parser("adapter", help="启动协议适配器")
    p_adapter.add_argument("--base-url", required=True, help="上游 API 地址")
    p_adapter.add_argument("--model", required=True, help="模型 ID")
    p_adapter.add_argument("--api-key", required=True, help="API Key")
    p_adapter.add_argument("--port", type=int, default=ADAPTER_PORT, help="适配器端口")
    p_adapter.set_defaults(func=cmd_adapter)

    # gui
    p_gui = sub.add_parser("gui", help="启动 GUI 界面")
    p_gui.set_defaults(func=cmd_gui)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
