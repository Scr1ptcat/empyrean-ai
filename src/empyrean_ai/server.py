from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from .config import load_configs
from .curator.registry import ModelRegistry
from .curator.router import Router
from .curator.engine import CuratorEngine
from .logging_utils import setup_logging

setup_logging()

BASE = Path(__file__).resolve().parents[2]

cfg = load_configs(BASE / "configs")
registry = ModelRegistry(cfg)
registry.set_routing(cfg["routing"])
router = Router(cfg["routing"], aliases=cfg["models"].get("aliases", {}))
engine = CuratorEngine(cfg, BASE)

app = FastAPI()

class CurateRequest(BaseModel):
    task_family: str | None = None
    input: str
    model: str | None = "auto"
    n_candidates: int = 2

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/v1/curate")
async def curate(req: CurateRequest):
    task = req.task_family or router.classify(req.input)
    model_key = registry.routing_initial(task) if req.model in (None, "auto") else req.model
    model_info = registry.resolve(router.alias(model_key))
    out = await engine.curate(task, req.input, model_info.ollama_name, n_candidates=req.n_candidates, run_dir=BASE / "data" / "runs")
    # escalation loop: use configured signals policy
    chain = router.escalation_chain(task)
    i = 0
    signals = out["validation"].get("signals", [])
    while (not out["validation"]["ok"] or router.needs_escalation(signals)) and i < len(chain):
        m = registry.resolve(router.alias(chain[i]))
        out = await engine.curate(task, req.input, m.ollama_name, n_candidates=req.n_candidates, run_dir=BASE / "data" / "runs")
        signals = out["validation"].get("signals", [])
        i += 1
    return {"task_family": task, "model_used": model_info.key if out["meta"]["model"]==model_info.ollama_name else chain[i-1] if i>0 else model_info.key, "output": out["text"], "validation": out["validation"], "meta": out["meta"]}

class EvalRequest(BaseModel):
    limit: int | None = 10

@app.post("/v1/eval")
async def eval_endpoint(req: EvalRequest):
    # lightweight local eval over golden set without heavy inference
    import json
    g = (BASE / "data" / "golden" / "tasks.jsonl").read_text(encoding="utf-8").strip().splitlines()
    tasks = [json.loads(x) for x in g][: (req.limit or 10)]
    by_family = {}
    for t in tasks:
        by_family.setdefault(t["task_family"], 0)
        by_family[t["task_family"]] += 1
    return {"golden_counts": by_family, "note": "Run full A/B via CLI 'aan eval' to compare prompts"}
