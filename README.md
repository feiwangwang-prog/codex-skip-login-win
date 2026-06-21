# Codex Switch - Windows 版

让 Codex Desktop 跳过 ChatGPT 登录，直接接入国产模型（如小米 MiMo API）。

## 功能

- **免登接入**：修改 `~/.codex/config.toml`，绕过 ChatGPT OAuth 登录
- **协议适配**：本地 HTTP 代理，将 Codex 的 Responses API 转成 Chat Completions 格式
- **GUI 界面**：tkinter 图形界面，操作简单
- **CLI 命令行**：适合脚本和高级用户
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

### 方式二：CLI

```bash
# 应用自定义模型配置（启用适配器 + 跳过登录）
python -m codex_switch.cli local \
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

## 卸载

```bash
scripts\uninstall.bat
```

或手动：删除开机自启项 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\codex-adapter.bat`

## 致谢

基于 [codex-skip-login](https://github.com/huangama666/codex-skip-login) 的 macOS 版移植。

## License

MIT
