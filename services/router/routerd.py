import time
from pathlib import Path
import logging

from services.gateway.infer import run as llm
from services.curator.curatord import craft_prompt
from empyrean_ai.config import load_configs
from empyrean_ai.curator.router import Router
from empyrean_ai.curator.registry import ModelRegistry
from empyrean_ai.curator.engine import _decoding_for
from empyrean_ai.post_validators import validate_output


BASE = Path(__file__).resolve().parents[2]
CFG = load_configs(BASE / "configs")
REG = ModelRegistry(CFG); REG.set_routing(CFG["routing"])
ROUTER = Router(CFG["routing"], aliases=CFG["models"].get("aliases", {}))


def handle(user_input: str) -> dict:
    task = ROUTER.classify(user_input)
    initial = CFG["routing"]["task_map"][task]["initial"]
    chain = [initial] + list(CFG["routing"]["task_map"][task]["chain"])
    opts = _decoding_for(task, CFG["decoding"]) if CFG.get("decoding") else {}
    schema_dir = BASE / "schemas" / "outputs"

    last_out = None
    t_start = time.time()
    for key in chain:
        model_info = REG.resolve(ROUTER.alias(key))
        prompt = craft_prompt(task, user_input, {"prompt_id": f"{task}_v1.yml"})
        out = llm(model_info.ollama_name, prompt, options=opts)
        last_out = out
        vr = validate_output(task, out, schema_dir)
        if vr.ok:
            return {
                "task": task,
                "model": key,
                "latency_ms": int(1000 * (time.time() - t_start)),
                "output": out,
                "validation": {"ok": True, "signals": vr.signals},
            }
    return {
        "task": task,
        "model": chain[-1],
        "output": last_out,
        "warning": "low confidence; review",
        "validation": {"ok": False, "signals": ["escalation_exhausted"]},
    }
