import os
from pathlib import Path

CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
CONFIG_PATH = CODEX_HOME / "config.toml"
AUTH_PATH = CODEX_HOME / "auth.json"
STATE_PATH = CODEX_HOME / "codex-switch-state.json"
MODEL_CATALOG_PATH = CODEX_HOME / "codex-switch-model-catalog.json"
BACKUP_DIR = CODEX_HOME / "backups"

ADAPTER_HOST = "127.0.0.1"
ADAPTER_PORT = 17638
ADAPTER_BASE_URL = f"http://{ADAPTER_HOST}:{ADAPTER_PORT}/v1"
