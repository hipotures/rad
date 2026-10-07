#!/usr/bin/env bash
set -euo pipefail

repo=/srv/ai/buun-llama-cpp
server="$repo/build/bin/llama-server"
target=/srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q6/UD-Q6_K_XL/Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf
mtp=/srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260901-unsloth-MTP-Q8_0/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf
log_dir=/srv/ai/benchmarks/buun-logs
log="$log_dir/buun-$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$log_dir"

cmd=(
  "$server"
  -m "$target"
  -c 131072
  -np 1
  -fa on
  -ctk q8_0
  -ctv q8_0
  -b 512
  -ub 128
  -t 16
  -tb 16
  -dev CUDA0,CUDA1
  -sm layer
  -ngl all
  --no-warmup
  -ot 'exps=CPU'
  --fit on
  --moe-cache soft
  --moe-cache-expert-parallel auto
  --spec-type draft-mtp
  --spec-draft-model "$mtp"
  --spec-draft-n-max 3
  --host 0.0.0.0
  --port 18089
)

{
  printf 'git commit buun: '
  git -C "$repo" rev-parse HEAD
  printf 'llama-server --version: '
  "$server" --version
  printf 'start command: '
  printf '%q ' "${cmd[@]}"
  printf '\n'
  exec "${cmd[@]}"
} 2>&1 | tee "$log"
