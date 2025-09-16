from __future__ import annotations
import asyncio, json, sys
from pathlib import Path
import typer
from .config import load_configs
from .curator.registry import ModelRegistry
from .curator.router import Router
from .curator.engine import CuratorEngine
from .logging_utils import setup_logging

app = typer.Typer(add_completion=False, no_args_is_help=True, help="Empyrean AI CLI")


@app.command()
def curate(task: str = typer.Option(None, "--task", help="task family"),
           model: str = typer.Option("auto", "--model", help="model key|auto"),
           user_input: str = typer.Option(..., "--input", help="text or @/path/to/file"),
           candidates: int = typer.Option(2, "--candidates", min=1, max=4)):
    setup_logging()
    base = Path(__file__).resolve().parents[2]
    cfg = load_configs(base / "configs")
    registry = ModelRegistry(cfg); registry.set_routing(cfg["routing"])
    router = Router(cfg["routing"], aliases=cfg["models"].get("aliases", {}))
    engine = CuratorEngine(cfg, base)

    if user_input.startswith("@"):
        p = Path(user_input[1:]); text = p.read_text(encoding="utf-8")
    else:
        text = user_input

    tf = task or router.classify(text)
    mk = registry.routing_initial(tf) if model == "auto" else model
    mi = registry.resolve(router.alias(mk))

    async def _run():
        out = await engine.curate(tf, text, mi.ollama_name, n_candidates=candidates, run_dir=base / "data" / "runs")
        print(json.dumps({"task_family": tf, "model": mi.key, "output": out["text"], "validation": out["validation"]}, ensure_ascii=False))
    asyncio.run(_run())


@app.command()
def eval(run: Path = typer.Option(None, "--run", help="unused placeholder for v1")):
    """Run tiny golden-set eval (local, offline)."""
    base = Path(__file__).resolve().parents[2]
    gfile = base / "data" / "golden" / "tasks.jsonl"
    lines = gfile.read_text(encoding="utf-8").strip().splitlines()
    by_family: dict[str,int] = {}
    for ln in lines:
        import json; t = json.loads(ln)
        by_family[t["task_family"]] = by_family.get(t["task_family"], 0) + 1
    print(json.dumps({"golden_counts": by_family, "file": str(gfile)}, indent=2))

if __name__ == "__main__":
    app()
