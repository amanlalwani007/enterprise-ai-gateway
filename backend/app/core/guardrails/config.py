import os
import yaml
from typing import Any
from app.core.config import settings

DEFAULT_CONFIG = {
    "input": [],
    "output": [],
}


def load_guardrail_config(config_path: str | None = None) -> dict[str, Any]:
    path = config_path or settings.GUARDRAILS_CONFIG_PATH
    if not path or not os.path.isfile(path):
        return dict(DEFAULT_CONFIG)
    try:
        with open(path) as f:
            return yaml.safe_load(f) or dict(DEFAULT_CONFIG)
    except Exception:
        return dict(DEFAULT_CONFIG)
