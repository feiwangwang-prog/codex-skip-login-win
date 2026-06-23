# Codex Switch · Windows 版

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

> **中文** | [English](#codex-switch--windows-edition)

让 Codex Desktop 跳过 ChatGPT 登录，直接接入国产模型（如小米 MiMo API）或任何 OpenAI 兼容 API。

## 功能

- **免登接入** — 修改 `~/.codex/config.toml`，绕过 ChatGPT OAuth 登录
- **协议适配** — 本地 HTTP 代理，将 Codex 的 Responses API 转成 Chat Completions 格式
- **GUI 界面** — tkinter 图形界面，支持中英文切换
- **CLI 命令行** — 适合脚本和高级用户，`--lang en` 切换语言
- **一键启动** — `start-adapter.bat` 从已保存配置启动适配器，无需重复输入参数
- **一键还原** — 随时恢复官方登录配置

## 环境要求

- Windows 10/11
- Python 3.8+（需在 PATH 中）
- Codex Desktop 已安装

## 快速开始

### 方式一：GUI（推荐）

双击 `run_gui.bat`，在界面中填写：

1. **API 地址** — 你的模型服务地址（如 `http://127.0.0.1:8080`）
2. **模型 ID** — 模型名称（如 `MiMo-7B-RL`）
3. **API Key** — 你的 API 密钥
4. 勾选「上游仅支持 Chat Completions」（大多数国产模型需要）
5. 点击「应用并重启 Codex」

右上角按钮可随时切换中英文界面。

### 方式二：CLI

```bash
# 应用自定义模型配置（启用适配器 + 跳过登录）
codex-switch local \
  --base-url http://127.0.0.1:8080 \
  --model MiMo-7B-RL \
  --api-key sk-xxx \
  --chat-adapter \
  --skip-login

# 英文输出
codex-switch --lang en local \
  --base-url http://127.0.0.1:8080 \
  --model MiMo-7B-RL \
  --api-key sk-xxx \
  --chat-adapter \
  --skip-login

# 查看当前状态
codex-switch status

# 恢复官方登录
codex-switch official
```

### 方式三：启动适配器

配置保存后，可以用 bat 一键启动适配器（无需重复输入参数）：

```bash
# 双击或命令行运行
start-adapter.bat

# 或手动指定参数
python -m codex_switch.adapter http://127.0.0.1:8080 MiMo-7B-RL sk-xxx
```

### 方式四：一键安装

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

## 语言切换

| 方式 | 用法 |
|------|------|
| GUI | 点击窗口右上角的 EN / 中文 按钮 |
| CLI 参数 | `codex-switch --lang en status` |
| 环境变量 | `set CODEX_SWITCH_LANG=en` 后运行 CLI |

## 文件说明

| 文件 | 用途 |
|------|------|
| `~/.codex/config.toml` | Codex 配置，本工具会修改此文件 |
| `~/.codex/auth.json` | 存储 API Key |
| `~/.codex/codex-switch-state.json` | 工具运行状态 |
| `~/.codex/backups/` | 配置自动备份 |

---

# Codex Switch · Windows Edition

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

> **English** | [中文](#codex-switch--windows-版)

Skip the ChatGPT login requirement in Codex Desktop and connect to any OpenAI-compatible model API directly.

## Features

- **Login Bypass** — Modify `~/.codex/config.toml` to bypass ChatGPT OAuth login
- **Protocol Adapter** — Local HTTP proxy that converts Codex Responses API to Chat Completions format
- **GUI** — tkinter interface with bilingual support (Chinese / English)
- **CLI** — Command-line interface with `--lang en` for English output
- **One-click Start** — `start-adapter.bat` launches adapter from saved config, no need to re-enter params
- **One-click Restore** — Revert to official Codex login config anytime

## Requirements

- Windows 10/11
- Python 3.8+ (must be in PATH)
- Codex Desktop installed

## Quick Start

### Option 1: GUI (Recommended)

Double-click `run_gui.bat` and fill in:

1. **API URL** — Your model service address (e.g. `http://127.0.0.1:8080`)
2. **Model ID** — Model name (e.g. `MiMo-7B-RL`)
3. **API Key** — Your API key
4. Check "Upstream only supports Chat Completions" (required for most non-OpenAI providers)
5. Click "Apply & Restart Codex"

Use the EN / 中文 button in the top-right corner to switch the interface language.

### Option 2: CLI

```bash
# Apply custom model config (with adapter + skip login)
codex-switch local \
  --base-url http://127.0.0.1:8080 \
  --model MiMo-7B-RL \
  --api-key sk-xxx \
  --chat-adapter \
  --skip-login

# Check current status
codex-switch --lang en status

# Restore official login
codex-switch official
```

### Option 3: Start Adapter

After saving config, launch the adapter with one click (no need to re-enter params):

```bash
# Double-click or run from command line
start-adapter.bat

# Or specify params manually
python -m codex_switch.adapter http://127.0.0.1:8080 MiMo-7B-RL sk-xxx
```

### Option 4: One-click Install

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

## Language Switching

| Method | Usage |
|--------|-------|
| GUI | Click the EN / 中文 button in the top-right corner |
| CLI flag | `codex-switch --lang en status` |
| Env variable | `set CODEX_SWITCH_LANG=en` then run any CLI command |

## File Overview

| File | Purpose |
|------|---------|
| `~/.codex/config.toml` | Codex config, modified by this tool |
| `~/.codex/auth.json` | Stores API key |
| `~/.codex/codex-switch-state.json` | Tool runtime state |
| `~/.codex/backups/` | Auto backups of config |

## Acknowledgments

Ported from the macOS version of [codex-skip-login](https://github.com/huangama666/codex-skip-login).

## License

MIT
