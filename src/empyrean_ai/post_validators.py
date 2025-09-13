from __future__ import annotations
import json
import re
from pathlib import Path
from jsonschema import validate, Draft202012Validator
from jsonschema.exceptions import ValidationError

UNCERTAINTY = re.compile(r"\b(not sure|uncertain|unsure|might be|maybe)\b", re.I)
REFUSAL = re.compile(r"\b(i can't|i cannot|cannot comply|refuse)\b", re.I)

class ValidationResult:
    def __init__(self, ok: bool, signals: list[str] | None = None, errors: str | None = None):
        self.ok = ok
        self.signals = signals or []
        self.errors = errors

def parse_json_strict(text: str) -> tuple[dict | None, str | None]:
    try:
        # Strip accidental markdown fences
        t = text.strip()
        if t.startswith("```"):
            t = t.strip("` ")
        return json.loads(t), None
    except Exception as e:
        return None, str(e)

def load_schema(path: Path) -> dict:
    import json, sys
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def validate_output(task_family: str, raw_text: str, schema_dir: Path) -> ValidationResult:
    data, err = parse_json_strict(raw_text)
    signals: list[str] = []
    if err:
        signals.append("invalid_json")
        return ValidationResult(False, signals, f"json parse error: {err}")
    # refusal / uncertainty checks
    text = json.dumps(data)
    if UNCERTAINTY.search(text):
        signals.append("uncertainty_markers")
    if REFUSAL.search(text):
        signals.append("refusal_detected")
    # schema
    schema_path = schema_dir / f"{task_family}.schema.json"
    try:
        schema = load_schema(schema_path)
        Draft202012Validator(schema).validate(data)
    except ValidationError as ve:
        signals.append("schema_fail")
        return ValidationResult(False, signals, f"schema: {ve.message}")
    return ValidationResult(True, signals, None)
