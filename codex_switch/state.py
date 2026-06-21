"""codex-switch-state.json 读写"""
import json
from .constants import STATE_PATH


def read_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(data: dict):
    STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def update_state(updates: dict):
    data = read_state()
    data.update(updates)
    save_state(data)
