from __future__ import annotations
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Tuple
from .templates import TemplateLibrary
from empyrean_ai.post_validators import validate_output, ValidationResult
from empyrean_ai.evaluators import log_run, proxy_score, now_ts
from .inference.ollama_client import OllamaClient

def _decoding_for(task_family: str, decoding_cfg: dict) -> dict:
    """Resolve decoding parameters for a task family with clear errors.

    Expected shape in decoding_cfg:
      profiles: {name: {...}}
      per_task: {task_family: {profile: name, ...overrides}}
      defaults: {...}  # optional
    """
    per_task = decoding_cfg.get("per_task") or {}
    defaults = decoding_cfg.get("defaults") or {}
    node = per_task.get(task_family)
    if not node:
        known = ", ".join(sorted(per_task)) or "<none>"
        raise KeyError(f"Unknown task_family {task_family!r} in decoding config. Known: {known}")
    # Support both new-style (profiles/defaults) and existing flat keys
    profiles = decoding_cfg.get("profiles")
    profile_name = node.get("profile")
    if not profile_name:
        raise KeyError(f"Task family {task_family!r} has no 'profile' entry in decoding config.")
    if profiles is not None:
        profile = profiles.get(profile_name)
        if profile is None:
            avail = ", ".join(sorted(profiles)) or "<none>"
            raise KeyError(
                f"Decoding profile {profile_name!r} not found in configs/decoding.yml. Available: {avail}"
            )
        base = {**defaults, **profile}
    else:
        # fallback to flat top-level profiles (e.g., 'deterministic', 'creative')
        flat_profiles = {k: v for k, v in decoding_cfg.items() if k not in {"per_task", "context_caps", "defaults"}}
        profile = flat_profiles.get(profile_name)
        if profile is None:
            avail = ", ".join(sorted(flat_profiles)) or "<none>"
            raise KeyError(
                f"Decoding profile {profile_name!r} not found. Available: {avail}"
            )
        base = {**defaults, **profile}
    # optional overrides
    for k in ("temperature", "top_p", "max_new_tokens"):
        if k in node:
            base[k] = node[k]
    return base

REPAIR_INSTR = """You output invalid or non-conforming JSON for task '{task_family}'. 
Fix ONLY the JSON structure to conform to the expected schema. 
Do not add commentary or fences. Here is your previous output:
---
{bad}
---
Return corrected JSON only.
"""

class CuratorEngine:
    def __init__(self, cfg: dict, base_dir: Path):
        self.cfg = cfg
        self.templates = TemplateLibrary(base_dir / "prompt_library")
        self.schema_dir = base_dir / "schemas" / "outputs"
        self.client = OllamaClient()

    async def _run_one(self, model_name: str, prompt: str, options: dict) -> Tuple[str, dict]:
        res = await self.client.generate(model_name, prompt, options)
        return res["text"], res

    async def _attempt_repair(self, task_family: str, model: str, bad_text: str, options: dict) -> Tuple[ValidationResult, str, dict]:
        prompt = REPAIR_INSTR.format(task_family=task_family, bad=bad_text)
        fixed, raw = await self._run_one(model, prompt, options)
        vr = validate_output(task_family, fixed, self.schema_dir)
        return vr, fixed, raw

    async def curate(self, task_family: str, user_input: str, model_ollama_name: str, n_candidates: int = 2, run_dir: Path | None = None) -> dict:
        tmpl = self.templates.load(f"{task_family}_v1")
        base_prompt = self.templates.render(tmpl, user_input)

        # simple prompt variants: add minor directive toggles
        variants = [base_prompt]
        if n_candidates > 1:
            variants.append(base_prompt + "\nConstraint: be concise yet complete.")
        options = _decoding_for(task_family, self.cfg["decoding"])
        results: List[Tuple[ValidationResult, str, dict]] = []

        for v in variants[:n_candidates]:
            text, raw = await self._run_one(model_ollama_name, v, options)
            vr = validate_output(task_family, text, self.schema_dir)
            if not vr.ok:
                # one-shot auto-repair
                vr2, text2, raw2 = await self._attempt_repair(task_family, model_ollama_name, text, options)
                if vr2.ok:
                    vr, text, raw = vr2, text2, raw2
                else:
                    # keep the original failure
                    pass
            results.append((vr, text, raw))

        # ranking: prefer valid JSON and fewer signals; fallback to first
        ranked = sorted(results, key=lambda r: (not r[0].ok, len(r[0].signals)))
        best = ranked[0]
        payload = {
            "ts": now_ts(),
            "task_family": task_family,
            "model": model_ollama_name,
            "options": options,
            "candidates": [ {"ok": r[0].ok, "signals": r[0].signals, "elapsed": r[2].get("elapsed")} for r in results ],
            "winner": {"ok": best[0].ok, "signals": best[0].signals},
            "score": proxy_score(best[0].ok, best[0].signals),
        }
        if run_dir:
            log_run(run_dir, payload)
        return {"text": best[1], "meta": payload, "validation": {"ok": best[0].ok, "signals": best[0].signals, "errors": best[0].errors}}
