#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
uvicorn empyrean_ai.server:app --host 127.0.0.1 --port 8080
