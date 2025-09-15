from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json


def now_ts() -> str:
    """Return current UTC timestamp in ISO-8601 with offset."""
    return datetime.now(timezone.utc).isoformat()


def proxy_score(ok: bool, signals: list[str]) -> float:
    """Very small scoring heuristic for MVP ranking.

    Prefer valid outputs; penalise by number of signals.
    """
    return 1.0 if ok else max(0.0, 0.6 - 0.1 * len(signals))


def log_run(run_dir: Path, payload: dict) -> Path:
    """Write a timestamped JSON payload under run_dir/YYYYMMDD and return the file path."""
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    out_dir = (Path(run_dir) / day)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = datetime.now(timezone.utc).strftime("run_%H%M%S_%f.json")
    path = out_dir / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


