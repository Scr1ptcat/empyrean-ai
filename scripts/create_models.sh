#!/usr/bin/env bash
set -euo pipefail
# Create curated models with fixed SYSTEM + parameters.
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
declare -A map=(
  ["devstral-24b"]="devstral:24b curated/devstral-24b:curated"
  ["qwen3-coder-30b"]="qwen3-coder:30b curated/qwen3-coder-30b:curated"
  ["qwen3-30b"]="qwen3:30b curated/qwen3-30b:curated"
  ["gemma3-27b"]="gemma3:27b curated/gemma3-27b:curated"
  ["gemma3-27b-it-qat"]="gemma3:27b-it-qat curated/gemma3-27b-it-qat:curated"
  ["nemotron-70b"]="nemotron:70b curated/nemotron-70b:curated"
  ["gpt-oss-20b"]="gpt-oss:20b curated/gpt-oss-20b:curated"
  ["gpt-oss-120b"]="gpt-oss:120b curated/gpt-oss-120b:curated"
)
for d in "${!map[@]}"; do
  src="$root/models/$d/Modelfile"
  IFS=' ' read -r base name <<< "${map[$d]}"
  echo "Creating ${name} from $base"
  ollama create "$name" -f "$src"
done
echo "Created curated models."
