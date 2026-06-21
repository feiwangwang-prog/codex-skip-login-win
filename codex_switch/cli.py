"""CLI 入口：codex-switch local/official/status/adapter/gui"""
import argparse
import sys

from .config import apply_local_config, apply_official_config, write_config_raw, read_config_raw
from .auth import save_auth
from .state import update_state, read_state
from .adapter import start_adapter, stop_adapter, adapter_status, run_adapter_forever
from .constants import ADAPTER_PORT, CONFIG_PATH
from .i18n import t, init_lang


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

    print(t("cli_applied"))
    print(f"   {t('cli_model')}: {args.model}")
    print(f"   {t('cli_api')}: {args.base_url}")
    print(f"   {t('cli_adapter')}: {t('cli_enabled') if use_adapter else t('cli_disabled')}")
    print(f"   {t('cli_skip_login')}: {t('cli_yes') if skip_login else t('cli_no')}")
    print(f"   {t('cli_config_file')}: {CONFIG_PATH}")

    if use_adapter:
        print(f"\n{t('cli_adapter_hint')}")
        print(f"   python -m codex_switch.cli adapter --base-url {args.base_url} --model {args.model} --api-key {args.api_key}")


def cmd_official(args):
    """恢复官方登录配置"""
    text = apply_official_config(model=args.model)
    write_config_raw(text)

    update_state({
        "mode": "official",
        "model": args.model,
    })

    print(t("cli_restored"))
    print(f"   {t('cli_model')}: {args.model}")
    print(f"   {t('cli_config_file')}: {CONFIG_PATH}")


def cmd_status(args):
    """显示当前状态"""
    state = read_state()
    config = read_config_raw()

    print(t("cli_status_title"))
    print(f"{t('cli_mode')}: {state.get('mode', t('cli_not_set'))}")
    if state.get('mode') == 'local':
        print(f"{t('cli_model')}: {state.get('model', '-')}")
        print(f"{t('cli_api')}: {state.get('base_url', '-')}")
        print(f"{t('cli_adapter')}: {t('cli_enabled') if state.get('chat_adapter') else t('cli_disabled')}")
        print(f"{t('cli_skip_login')}: {t('cli_yes') if state.get('skip_login') else t('cli_no')}")
    elif state.get('mode') == 'official':
        print(f"{t('cli_model')}: {state.get('model', '-')}")

    print(f"\n--- config.toml ({CONFIG_PATH}) ---")
    if config:
        print(config)
    else:
        print(t("cli_file_missing"))

    print(f"\n{t('cli_adapter_status')}")
    a_status = adapter_status()
    print(f"{t('cli_running')}: {a_status['running']}")
    if a_status['running']:
        print(f"{t('cli_upstream')}: {a_status['base_url']}")
        print(f"{t('cli_model')}: {a_status['model']}")
        print(f"{t('cli_request_count')}: {a_status['request_count']}")
        print(f"{t('cli_error_count')}: {a_status['error_count']}")


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
    # 全局 --lang 参数
    # 先解析 --lang，再传给子命令
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--lang", choices=["zh", "en"], help="界面语言 / UI language (zh or en)")
    pre_args, remaining = pre_parser.parse_known_args()
    init_lang(pre_args.lang)

    parser = argparse.ArgumentParser(
        prog="codex-switch",
        description=t("cli_desc"),
        parents=[pre_parser],
    )
    sub = parser.add_subparsers(dest="command")

    # local
    p_local = sub.add_parser("local", help=t("cli_help_local"))
    p_local.add_argument("--base-url", required=True, help=t("cli_arg_base_url"))
    p_local.add_argument("--model", required=True, help=t("cli_arg_model"))
    p_local.add_argument("--api-key", required=True, help=t("cli_arg_api_key"))
    p_local.add_argument("--chat-adapter", action="store_true", help=t("cli_arg_chat_adapter"))
    p_local.add_argument("--skip-login", action="store_true", help=t("cli_arg_skip_login"))
    p_local.add_argument("--adapter-port", type=int, default=ADAPTER_PORT, help=t("cli_arg_adapter_port"))
    p_local.set_defaults(func=cmd_local)

    # official
    p_official = sub.add_parser("official", help=t("cli_help_official"))
    p_official.add_argument("--model", default="o3", help=t("cli_arg_official_model"))
    p_official.set_defaults(func=cmd_official)

    # status
    p_status = sub.add_parser("status", help=t("cli_help_status"))
    p_status.set_defaults(func=cmd_status)

    # adapter
    p_adapter = sub.add_parser("adapter", help=t("cli_help_adapter"))
    p_adapter.add_argument("--base-url", required=True, help=t("cli_arg_base_url"))
    p_adapter.add_argument("--model", required=True, help=t("cli_arg_model"))
    p_adapter.add_argument("--api-key", required=True, help=t("cli_arg_api_key"))
    p_adapter.add_argument("--port", type=int, default=ADAPTER_PORT, help=t("cli_arg_adapter_port"))
    p_adapter.set_defaults(func=cmd_adapter)

    # gui
    p_gui = sub.add_parser("gui", help=t("cli_help_gui"))
    p_gui.set_defaults(func=cmd_gui)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
