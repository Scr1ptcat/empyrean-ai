from __future__ import annotations
import re
from typing import Dict, List

UNCERTAINTY = re.compile(r"\b(not sure|uncertain|unsure|might be|maybe)\b", re.I)

class Router:
    def __init__(self, routing_cfg: dict, aliases: Dict[str, str] | None = None):
        self.cfg = routing_cfg
        self.aliases = aliases or {}

    def classify(self, text: str, hint: str | None = None) -> str:
        if hint:
            return hint
        t = text.lower()
        if any(k in t for k in ["bug", "stack trace", "traceback", "exception"]):
            return "bug_triage"
        if any(k in t for k in ["diff", "implement", "code", "function", "class "]):
            return "code_assist"
        if any(k in t for k in ["design", "rfc", "architecture", "trade-off", "tradeoff"]):
            return "design_rfc"
        if any(k in t for k in ["extract", "fields", "json only", "key:"]):
            return "extraction"
        if any(k in t for k in ["story", "blog", "creative"]):
            return "creative"
        return "analytical"

    def initial_model(self, task_family: str) -> str:
        return self.cfg["task_map"][task_family]["initial"]

    def escalation_chain(self, task_family: str) -> List[str]:
        return list(self.cfg["task_map"][task_family]["chain"])

    def needs_escalation(self, signals: List[str]) -> bool:
        allowed = set(self.cfg["defaults"]["escalate_on"])
        return any(s in allowed for s in signals)

    def alias(self, model_name: str) -> str:
        return self.aliases.get(model_name, model_name)
