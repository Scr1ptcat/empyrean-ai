import yaml, json, pathlib

LIB = pathlib.Path("services/curator/library")

def _load(pid): return yaml.safe_load((LIB/pid).read_text())

def craft_prompt(task, user_text, model_cfg):
    pid = model_cfg.get("prompt_id") or f"{task}.v1.yaml"
    T   = _load(pid)
    sys = T["system"]
    inst= T["instructions"]
    fmt = T.get("format_constraints","")
    # Optional stakes/role cues when flagged (Evidence: EmotionPrompts). :contentReference[oaicite:11]{index=11}
    cues = T.get("cues","")
    return f"[SYSTEM]\n{sys}\n\n[INSTRUCTIONS]\n{inst}\n\n[CUES]\n{cues}\n\n[USER]\n{user_text}\n\n[OUTPUT]\n{fmt}".strip()
