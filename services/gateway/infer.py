import requests, json

OLLAMA="http://localhost:11434/api/generate"

def run(model, prompt, options=None):
    body = {"model": model, "prompt": prompt, "stream": False}
    if options: body["options"] = options
    r = requests.post(OLLAMA, json=body, timeout=120)
    r.raise_for_status()
    return r.json()["response"]
