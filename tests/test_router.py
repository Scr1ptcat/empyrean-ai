from agentic_ai_ops.config import load_configs
from agentic_ai_ops.curator.router import Router

def test_classify_and_alias():
    cfg = load_configs(None)
    r = Router(cfg["routing"], aliases=cfg["models"].get("aliases", {}))
    assert r.classify("Please implement a function") == "code_assist"
    assert r.classify("Design an architecture") == "design_rfc"
    assert r.alias("quen3:30b") == "qwen3:30b"
