import re, time, yaml, logging
from apps.gateway.infer import run as llm
from apps.curator.curatord import craft_prompt
from apps.validator.validate import is_valid_json

rules = yaml.safe_load(open("apps/router/rules.yaml"))
routes = yaml.safe_load(open("configs/routes.yaml"))
decoding = yaml.safe_load(open("configs/decoding.yaml"))

def classify(text:str) -> str:
    for task, pats in rules["task_patterns"].items():
        if any(re.search(p, text, re.I|re.M) for p in pats): return task
    return "analysis"

def handle(user_input:str):
    task = classify(user_input)
    chain = routes[task]["models"]
    for i, m in enumerate(chain):
        prompt = craft_prompt(task, user_input, m)
        opts   = decoding.get(task, {})
        t0=time.time()
        out = llm(m["name"], prompt, options=opts)
        ok  = (not m.get("expects_json")) or is_valid_json(out, task)
        if ok: return {"task":task, "model":m["name"], "latency_ms":int(1000*(time.time()-t0)), "output":out}
    return {"task":task, "model":chain[-1]["name"], "output":out, "warning":"low confidence; review"}
