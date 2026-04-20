from pathlib import Path
from typing import Any, Dict

import yaml

from app.models import AppConfig


DEFAULT_CONFIG_PATH = Path("config/engines.yaml")


def load_config(config_path: str | None = None) -> AppConfig:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found at {path}. Copy config/engines.sample.yaml to config/engines.yaml first."
        )

    with path.open("r", encoding="utf-8") as f:
        payload: Dict[str, Any] = yaml.safe_load(f) or {}

    return AppConfig.model_validate(payload)

