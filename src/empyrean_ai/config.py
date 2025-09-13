from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import yaml

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "configs"

def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_configs(base_dir: Path | None = None) -> dict:
    base = Path(base_dir) if base_dir else DEFAULT_DIR
    models = load_yaml(base / "models.yml")
    routing = load_yaml(base / "routing.yml")
    decoding = load_yaml(base / "decoding.yml")
    return {"models": models, "routing": routing, "decoding": decoding}
