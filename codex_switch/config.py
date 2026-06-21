"""config.toml 读写与备份"""
import shutil
import re
from datetime import datetime
from pathlib import Path
from .constants import CONFIG_PATH, BACKUP_DIR, CODEX_HOME


def backup_config():
    if not CONFIG_PATH.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = BACKUP_DIR / f"config.{ts}.toml"
    shutil.copy2(CONFIG_PATH, dst)
    return dst


def read_config_raw() -> str:
    if not CONFIG_PATH.exists():
        return ""
    return CONFIG_PATH.read_text(encoding="utf-8")


def write_config_raw(text: str):
    CODEX_HOME.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(text, encoding="utf-8")


def parse_toml_simple(text: str) -> dict:
    """简易 TOML 解析，返回 {section_key: {key: value}} 结构"""
    result = {}
    current_section = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = re.match(r'^\[(.+)\]$', stripped)
        if m:
            current_section = m.group(1).strip().strip('"')
            if current_section not in result:
                result[current_section] = {}
            continue
        m = re.match(r'^(\w+)\s*=\s*(.+)$', stripped)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip()
            if current_section is None:
                current_section = "__root__"
                if current_section not in result:
                    result[current_section] = {}
            result[current_section][key] = val
    return result


def set_root_keys(text: str, updates: dict) -> str:
    """在 TOML 文本的根段落设置/更新键值"""
    lines = text.splitlines()
    # 找到第一个 section header 的位置
    first_section_idx = len(lines)
    for i, line in enumerate(lines):
        if re.match(r'^\s*\[', line):
            first_section_idx = i
            break

    root_lines = lines[:first_section_idx]
    rest_lines = lines[first_section_idx:]

    existing_keys = set()
    new_root_lines = []
    for line in root_lines:
        m = re.match(r'^(\w+)\s*=', line)
        if m:
            key = m.group(1).strip()
            existing_keys.add(key)
            if key in updates:
                new_root_lines.append(f'{key} = {updates[key]}')
                continue
        new_root_lines.append(line)

    for key, val in updates.items():
        if key not in existing_keys:
            new_root_lines.insert(0, f'{key} = {val}')

    return "\n".join(new_root_lines + rest_lines)


def remove_root_keys(text: str, keys: list) -> str:
    """从根段落删除指定键"""
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        m = re.match(r'^(\w+)\s*=', line)
        if m and m.group(1).strip() in keys:
            continue
        new_lines.append(line)
    return "\n".join(new_lines)


def remove_section(text: str, section_name: str) -> str:
    """删除整个 TOML section"""
    lines = text.splitlines()
    new_lines = []
    in_section = False
    for line in lines:
        m = re.match(r'^\[(.+)\]$', line.strip())
        if m:
            if m.group(1).strip().strip('"') == section_name:
                in_section = True
                continue
            else:
                in_section = False
        elif in_section:
            # 跳过 section 内的键值对和空行
            if line.strip() and not line.strip().startswith("#"):
                continue
            # section 后的空行也跳过
            continue
        new_lines.append(line)
    return "\n".join(new_lines)


def ensure_custom_provider(text: str, base_url: str, model: str, api_key: str, use_chat_adapter: bool) -> str:
    """确保 [model_providers.custom] 段存在且正确"""
    section = '[model_providers.custom]'
    wire_api = "chat" if use_chat_adapter else "responses"
    block = (
        f'\n{section}\n'
        f'base_url = "{base_url}"\n'
        f'name = "custom"\n'
        f'requires_openai_auth = false\n'
        f'wire_api = "{wire_api}"\n'
        f'experimental_bearer_token = "{api_key}"\n'
    )

    # 删除旧的 section
    text = remove_section(text, "model_providers.custom")
    # 追加新的
    return text.rstrip() + "\n" + block


def apply_local_config(base_url: str, model: str, api_key: str, use_chat_adapter: bool, skip_login: bool) -> str:
    """应用自定义模型配置，返回最终 config.toml 内容"""
    text = read_config_raw()
    if not text:
        text = ""

    # 备份
    backup_config()

    # 删除旧的根键
    text = remove_root_keys(text, ["model_provider", "model", "preferred_auth_method", "model_catalog_json"])

    # 设置新根键
    root_updates = {
        "model_provider": '"custom"',
        "model": f'"{model}"',
    }
    if skip_login:
        root_updates["preferred_auth_method"] = '"none"'
    else:
        root_updates["preferred_auth_method"] = '"chatgpt"'
    text = set_root_keys(text, root_updates)

    # 适配器 URL
    from .constants import ADAPTER_BASE_URL
    provider_url = ADAPTER_BASE_URL if use_chat_adapter else base_url

    # 确保 provider 段
    text = ensure_custom_provider(text, provider_url, model, api_key, use_chat_adapter)

    return text


def apply_official_config(model: str = "o3") -> str:
    """恢复官方登录配置"""
    text = read_config_raw()
    if not text:
        text = ""

    backup_config()

    text = remove_root_keys(text, ["model_provider", "model", "preferred_auth_method", "model_catalog_json"])
    text = remove_section(text, "model_providers.custom")

    root_updates = {
        "model": f'"{model}"',
    }
    text = set_root_keys(text, root_updates)

    return text
