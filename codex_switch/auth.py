"""auth.json 读写"""
import json
from .constants import AUTH_PATH


def read_auth() -> dict:
    if not AUTH_PATH.exists():
        return {}
    try:
        return json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_auth(access_token: str, api_key: str = ""):
    data = read_auth()
    if access_token:
        data["codex_access_token"] = access_token
    if api_key:
        data["api_key"] = api_key
    AUTH_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
