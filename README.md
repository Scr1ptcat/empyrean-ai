# empyrean-ai

Local prompt **curator + router** for software‑engineering workflows over Ollama models on a single workstation (Intel i9‑14900K, RTX 4090 24 GB, 96 GB RAM).

**Key features**

- Versioned prompt library (YAML) + JSON‑schema outputs
- Curator engine: generate → rank/score → refine → finalize
- Deterministic decoding defaults; router escalates only on failure signals
- Guardrails: injection defense, refusal/format checks, JSON auto‑repair
- FastAPI server (`/v1/curate`, `/v1/eval`, `/healthz`) + Typer CLI
- Eval/analytics logs with tiny golden set
- Ollama integration with retries + metrics

> This scaffold follows the deployment and curation guidance in the attached plans. :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3}

## Quickstart

## API

GET /healthz → {"status":"ok"}

POST /v1/curate → body: {"task_family":"code_assist","input":"...", "model":"auto"}

POST /v1/eval → run golden‑set A/B and report metrics

## Router policy

Start with the smallest capable model; escalate on: invalid JSON, schema failure, explicit uncertainty markers ("unsure", "not certain"), or quick‑check failure. Deterministic tasks use low temperature; creative tasks use higher temperature. See configs/decoding.yml and configs/routing.yml.

## Determinism

Fixed decoding defaults per task family

Prompt versioning with PromptID and PROMPT_CANARY:v1

Validated JSON against schemas/outputs/*.schema.json

## Notes

One heavy model at a time. 70B/120B use partial CPU offload; see modelfiles/*/Modelfile for gpu_layers guidance.

Alias: users typing quen3:30b are routed to qwen3:30b.

Development
make lint     # ruff check + mypy
make test     # unit tests
make eval     # run golden-set eval (local)