from __future__ import annotations

from pathlib import Path
import json


def golden_counts(base: Path | None = None) -> dict[str, int]:
    root = Path(base) if base else Path(__file__).resolve().parents[1]
    f = root / "data" / "golden" / "tasks.jsonl"
    if not f.exists():
        return {}
    counts: dict[str, int] = {}
    for ln in f.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        t = json.loads(ln)
        fam = t.get("task_family")
        if fam:
            counts[fam] = counts.get(fam, 0) + 1
    return counts

