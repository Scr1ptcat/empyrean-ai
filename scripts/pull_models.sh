#!/usr/bin/env bash
set -euo pipefail
# Pull upstream base models once; they may be large.
models=(
  "devstral:24b"
  "qwen3-coder:30b"
  "qwen3:30b"
  "gemma3:27b"
  "gemma3:27b-it-qat"
  "nemotron:70b"
  "gpt-oss:20b"
  "gpt-oss:120b"
)
for m in "${models[@]}"; do
  echo "Pulling $m"
  ollama pull "$m" || true
done
