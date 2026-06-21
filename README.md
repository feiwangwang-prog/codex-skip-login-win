# Codex Switch - Windows 版

让 Codex Desktop 跳过 ChatGPT 登录，直接接入国产模型（如小米 MiMo API）。

## 功能

- **免登接入**：修改 `~/.codex/config.toml`，绕过 ChatGPT OAuth 登录
- **协议适配**：本地 HTTP 代理，将 Codex 的 Responses API 转成 Chat Completions 格式
- **GUI 界面**：tkinter 图形界面，支持中英文切换，操作简单
- **CLI 命令行**：适合脚本和高级用户，支持 `--lang en` 切换语言
- **开机自启**：适配器可注册为开机启动
- **一键还原**：随时恢复官方登录配置

## 环境要求

- Windows 10/11
- Python 3.8+（需在 PATH 中）
- Codex Desktop 已安装

## 快速开始

### 方式一：GUI（推荐）

双击 `run_gui.bat`，在界面中填写：

1. **API 地址**：你的模型服务地址（如 `http://127.0.0.1:8080`）
2. **模型 ID**：模型名称（如 `MiMo-7B-RL`）
3. **API Key**：你的 API 密钥
4. 勾选「上游仅支持 Chat Completions」（大多数国产模型需要）
5. 点击「应用并重启 Codex」

右上角按钮可随时切换中英文界面。

### 方式二：CLI

```bash
# 应用自定义模型配置（启用适配器 + 跳过登录）
python -m codex_switch.cli local \
  --base-url http://127.0.0.1:8080 \
  --model MiMo-7B-RL \
  --api-key sk-xxx \
  --chat-adapter \
  --skip-login

# 英文输出
python -m codex_switch.cli --lang en local \
  --base-url http://127.0.0.1:8080 \
  --model MiMo-7B-RL \
  --api-key sk-xxx \
  --chat-adapter \
  --skip-login

# 启动协议适配器（另开一个终端）
python -m codex_switch.cli adapter \
  --base-url http://127.0.0.1:8080 \
  --model MiMo-7B-RL \
  --api-key sk-xxx

# 查看当前状态
python -m codex_switch.cli status

# 恢复官方登录
python -m codex_switch.cli official
```

### 方式三：一键安装

```bash
scripts\install.bat
```

## 工作原理

Codex Desktop 默认使用 OpenAI Responses API 并要求 ChatGPT OAuth 登录。本工具：

1. 修改 `config.toml`，将 `model_provider` 设为 `custom`，指向你的模型 API
2. 设置 `preferred_auth_method = "none"` 跳过登录
3. 如果你的模型只支持 Chat Completions 格式，启动本地适配器做协议转换

```
Codex Desktop
    ↓ Responses API (POST /v1/responses)
适配器 (127.0.0.1:17638)
    ↓ Chat Completions (POST /v1/chat/completions)
你的模型 API（MiMo、DeepSeek 等）
```

## 文件说明

| 文件 | 用途 |
|------|------|
| `~/.codex/config.toml` | Codex 配置，本工具会修改此文件 |
| `~/.codex/auth.json` | 存储 API Key |
| `~/.codex/codex-switch-state.json` | 工具运行状态 |
| `~/.codex/backups/` | 配置自动备份 |

## 语言切换

| 方式 | 用法 |
|------|------|
| GUI | 点击窗口右上角的 EN / 中文 按钮，界面实时切换 |
| CLI 参数 | `codex-switch --lang en status` |
| 环境变量 | `set CODEX_SWITCH_LANG=en` 后运行 CLI 命令 |

---

# Codex Switch - Windows Edition

Skip the ChatGPT login requirement in Codex Desktop and connect to any OpenAI-compatible model API directly.

## Features

- **Login Bypass**: Modify `~/.codex/config.toml` to bypass ChatGPT OAuth login
- **Protocol Adapter**: Local HTTP proxy that converts Codex Responses API to Chat Completions format
- **GUI**: tkinter interface with bilingual support (Chinese / English)
- **CLI**: Command-line interface with `--lang en` for English output
- **Auto-start**: Adapter can register as a startup item
- **One-click Restore**: Revert to official Codex login config anytime

## Requirements

- Windows 10/11
- Python 3.8+ (must be in PATH)
- Codex Desktop installed

## Quick Start

### Option 1: GUI (Recommended)

Double-click `run_gui.bat` and fill in:

1. **API URL**: Your model service address (e.g. `http://127.0.0.1:8080`)
2. **Model ID**: Model name (e.g. `MiMo-7B-RL`)
3. **API Key**: Your API key
4. Check "Upstream only supports Chat Completions" (required for most non-OpenAI providers)
5. Click "Apply & Restart Codex"

Use the EN / 中文 button in the top-right corner to switch the interface language.

### Option 2: CLI

```bash
# Apply custom model config (with adapter + skip login)
python -m codex_switch.cli --lang en local \
  --base-url http://127.0.0.1:8080 \
  --model MiMo-7B-RL \
  --api-key sk-xxx \
  --chat-adapter \
  --skip-login

# Start protocol adapter (in a separate terminal)
python -m codex_switch.cli adapter \
  --base-url http://127.0.0.1:8080 \
  --model MiMo-7B-RL \
  --api-key sk-xxx

# Check current status
python -m codex_switch.cli --lang en status

# Restore official login
python -m codex_switch.cli official
```

### Option 3: One-click Install

```bash
scripts\install.bat
```

## How It Works

Codex Desktop uses the OpenAI Responses API by default and requires ChatGPT OAuth login. This tool:

1. Modifies `config.toml` to set `model_provider` to `custom`, pointing to your API
2. Sets `preferred_auth_method = "none"` to skip login
3. If your model only supports Chat Completions format, a local adapter handles protocol conversion

```
Codex Desktop
    ↓ Responses API (POST /v1/responses)
Adapter (127.0.0.1:17638)
    ↓ Chat Completions (POST /v1/chat/completions)
Your Model API (MiMo, DeepSeek, etc.)
```

## File Overview

| File | Purpose |
|------|---------|
| `~/.codex/config.toml` | Codex config, modified by this tool |
| `~/.codex/auth.json` | Stores API key |
| `~/.codex/codex-switch-state.json` | Tool runtime state |
| `~/.codex/backups/` | Auto backups of config |

## Language Switching

| Method | Usage |
|--------|-------|
| GUI | Click the EN / 中文 button in the top-right corner; the UI updates instantly |
| CLI flag | `codex-switch --lang en status` |
| Environment variable | `set CODEX_SWITCH_LANG=en` then run any CLI command |

## Acknowledgments

Ported from the macOS version of [codex-skip-login](https://github.com/huangama666/codex-skip-login).

## License

MIT
