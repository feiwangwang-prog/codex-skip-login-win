"""Responses API → Chat Completions 协议适配器

本地 HTTP 服务 (127.0.0.1:17638)，将 Codex 发出的 OpenAI Responses API 请求
转换为 Chat Completions 格式转发给上游（如 MiMo API），
再将上游响应转换回 Responses 格式返回给 Codex。
"""
import json
import re
import threading
import time
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any

from .constants import ADAPTER_HOST, ADAPTER_PORT


# ---------------------------------------------------------------------------
# Responses → Chat Completions 转换
# ---------------------------------------------------------------------------

def responses_input_to_chat_messages(input_data: list) -> list:
    """把 Responses API 的 input 数组转成 Chat Completions messages"""
    messages = []
    for item in input_data:
        role = item.get("role", "user")
        content = item.get("content", "")
        item_type = item.get("type", "")

        if item_type == "message":
            if isinstance(content, list):
                # 多模态：取文本部分
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "input_text":
                        text_parts.append(part.get("text", ""))
                    elif isinstance(part, dict) and part.get("type") == "text":
                        text_parts.append(part.get("text", ""))
                    elif isinstance(part, str):
                        text_parts.append(part)
                content = "\n".join(text_parts)
            messages.append({"role": role, "content": content})

        elif item_type == "function_call":
            fn_name = item.get("name", "")
            fn_args = item.get("arguments", "{}")
            call_id = item.get("call_id", "")
            msg = {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": call_id,
                    "type": "function",
                    "function": {"name": fn_name, "arguments": fn_args},
                }],
            }
            messages.append(msg)

        elif item_type == "function_call_output":
            call_id = item.get("call_id", "")
            output = item.get("output", "")
            messages.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": output,
            })

    return messages


def responses_tools_to_chat_tools(tools: list) -> list:
    """把 Responses tools 转成 Chat Completions tools"""
    chat_tools = []
    for tool in tools:
        if tool.get("type") == "function":
            chat_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {}),
                },
            })
    return chat_tools


def responses_request_to_chat_payload(req: dict) -> dict:
    """把 Responses API 请求转成 Chat Completions 请求"""
    model = req.get("model", "")
    messages = responses_input_to_chat_messages(req.get("input", []))
    payload = {"model": model, "messages": messages}

    if req.get("tools"):
        payload["tools"] = responses_tools_to_chat_tools(req["tools"])

    if req.get("temperature") is not None:
        payload["temperature"] = req["temperature"]
    if req.get("max_output_tokens") is not None:
        payload["max_tokens"] = req["max_output_tokens"]
    if req.get("stream"):
        payload["stream"] = True

    return payload


def chat_response_to_responses(chat_resp: dict, req: dict) -> dict:
    """把 Chat Completions 响应转回 Responses API 格式"""
    choice = chat_resp.get("choices", [{}])[0]
    message = choice.get("message", {})
    content = message.get("content", "") or ""
    finish_reason = choice.get("finish_reason", "stop")

    # 构造 output
    output = []

    # 检查 tool_calls
    tool_calls = message.get("tool_calls", [])
    if tool_calls:
        for tc in tool_calls:
            fn = tc.get("function", {})
            output.append({
                "type": "function_call",
                "id": tc.get("id", ""),
                "name": fn.get("name", ""),
                "arguments": fn.get("arguments", "{}"),
                "call_id": tc.get("id", ""),
                "status": "completed",
            })

    # 文本内容
    if content:
        output.append({
            "type": "message",
            "id": f"msg_{int(time.time() * 1000)}",
            "role": "assistant",
            "content": [{"type": "output_text", "text": content}],
            "status": "completed",
        })

    # 如果既没 tool_calls 也没 content，给个空消息
    if not output:
        output.append({
            "type": "message",
            "id": f"msg_{int(time.time() * 1000)}",
            "role": "assistant",
            "content": [{"type": "output_text", "text": ""}],
            "status": "completed",
        })

    usage = chat_resp.get("usage", {})
    return {
        "id": chat_resp.get("id", f"resp_{int(time.time() * 1000)}"),
        "object": "response",
        "created_at": int(time.time()),
        "model": chat_resp.get("model", req.get("model", "")),
        "output": output,
        "usage": {
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        },
        "status": "completed",
    }


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------

class AdapterState:
    """适配器运行状态（单例）"""
    def __init__(self):
        self.base_url: str = ""
        self.model: str = ""
        self.api_key: str = ""
        self.running: bool = False
        self.server: HTTPServer | None = None
        self.thread: threading.Thread | None = None
        self.request_count: int = 0
        self.error_count: int = 0
        self.last_error: str = ""


_adapter_state = AdapterState()


class AdapterHandler(BaseHTTPRequestHandler):
    """处理 /v1/responses 请求，转换后转发到上游 Chat Completions"""

    def log_message(self, fmt, *args):
        # 静默日志，避免刷屏
        pass

    def do_POST(self):
        if "/v1/responses" not in self.path and "/v1/chat/completions" not in self.path:
            self._send_error(404, "Not Found")
            return

        try:
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len)
            req = json.loads(body)
        except Exception as e:
            self._send_error(400, f"Bad request: {e}")
            return

        _adapter_state.request_count += 1

        try:
            if "/v1/responses" in self.path:
                self._handle_responses(req)
            else:
                self._handle_passthrough(req)
        except Exception as e:
            _adapter_state.error_count += 1
            _adapter_state.last_error = str(e)
            self._send_error(502, f"Upstream error: {e}")

    def _handle_responses(self, req: dict):
        """Responses API → Chat Completions → Responses"""
        chat_payload = responses_request_to_chat_payload(req)
        # 覆盖 model 为上游实际模型
        chat_payload["model"] = _adapter_state.model

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_adapter_state.api_key}",
        }

        chat_resp = self._upstream_request(
            f"{_adapter_state.base_url}/chat/completions",
            chat_payload,
            headers,
        )

        resp = chat_response_to_responses(chat_resp, req)
        self._send_json(200, resp)

    def _handle_passthrough(self, req: dict):
        """Chat Completions 直接透传"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_adapter_state.api_key}",
        }
        chat_resp = self._upstream_request(
            f"{_adapter_state.base_url}/chat/completions",
            req,
            headers,
        )
        self._send_json(200, chat_resp)

    def _upstream_request(self, url: str, payload: dict, headers: dict) -> dict:
        data = json.dumps(payload).encode("utf-8")
        http_req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(http_req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code}: {body}")

    def _send_json(self, code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, code: int, message: str):
        self._send_json(code, {"error": {"message": message, "type": "adapter_error"}})


# ---------------------------------------------------------------------------
# 启动/停止
# ---------------------------------------------------------------------------

def start_adapter(base_url: str, model: str, api_key: str, port: int = ADAPTER_PORT) -> str:
    """启动适配器，返回状态信息"""
    if _adapter_state.running:
        return f"适配器已在运行中（端口 {port}）"

    # 规范化 base_url：去掉尾部 /v1 之类的路径
    base_url = re.sub(r'/v\d+/?$', '', base_url.rstrip('/'))

    _adapter_state.base_url = base_url
    _adapter_state.model = model
    _adapter_state.api_key = api_key
    _adapter_state.request_count = 0
    _adapter_state.error_count = 0
    _adapter_state.last_error = ""

    try:
        server = HTTPServer((ADAPTER_HOST, port), AdapterHandler)
        _adapter_state.server = server
        _adapter_state.running = True

        def _run():
            try:
                server.serve_forever()
            except Exception:
                pass
            finally:
                _adapter_state.running = False

        t = threading.Thread(target=_run, daemon=True)
        _adapter_state.thread = t
        t.start()

        return f"适配器已启动: http://{ADAPTER_HOST}:{port}/v1"
    except OSError as e:
        return f"启动失败: {e}"


def stop_adapter() -> str:
    """停止适配器"""
    if not _adapter_state.running:
        return "适配器未在运行"
    if _adapter_state.server:
        _adapter_state.server.shutdown()
    _adapter_state.running = False
    return "适配器已停止"


def adapter_status() -> dict:
    """返回适配器状态"""
    return {
        "running": _adapter_state.running,
        "base_url": _adapter_state.base_url,
        "model": _adapter_state.model,
        "port": ADAPTER_PORT,
        "request_count": _adapter_state.request_count,
        "error_count": _adapter_state.error_count,
        "last_error": _adapter_state.last_error,
    }


def run_adapter_forever(base_url: str, model: str, api_key: str, port: int = ADAPTER_PORT):
    """阻塞式运行适配器（用于 CLI adapter 子命令）"""
    base_url = re.sub(r'/v\d+/?$', '', base_url.rstrip('/'))
    _adapter_state.base_url = base_url
    _adapter_state.model = model
    _adapter_state.api_key = api_key
    _adapter_state.request_count = 0
    _adapter_state.error_count = 0
    _adapter_state.last_error = ""
    _adapter_state.running = True

    try:
        server = HTTPServer((ADAPTER_HOST, port), AdapterHandler)
        _adapter_state.server = server
        print(f"适配器已启动: http://{ADAPTER_HOST}:{port}/v1")
        print(f"上游: {base_url}/chat/completions")
        print(f"模型: {model}")
        print("按 Ctrl+C 停止")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n适配器已停止")
    finally:
        _adapter_state.running = False


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 4:
        # 命令行参数模式: python -m codex_switch.adapter <base_url> <model> <api_key> [port]
        run_adapter_forever(sys.argv[1], sys.argv[2], sys.argv[3],
                            int(sys.argv[4]) if len(sys.argv) > 4 else ADAPTER_PORT)
    else:
        # 从 state 读取配置（供 start-adapter.bat 使用）
        from .state import read_state
        from .auth import read_auth

        state = read_state()
        auth = read_auth()
        base_url = state.get("base_url", "")
        model = state.get("model", "")
        api_key = auth.get("api_key", "")
        if not base_url or not model or not api_key:
            print("错误: 未找到配置。请先运行 codex-switch local 配置模型，或传参启动:")
            print("  python -m codex_switch.adapter <base_url> <model> <api_key> [port]")
            sys.exit(1)
        run_adapter_forever(base_url, model, api_key, state.get("adapter_port", ADAPTER_PORT))
