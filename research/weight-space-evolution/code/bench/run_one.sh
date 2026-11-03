#!/usr/bin/env bash
# Run one benchmark configuration on one GPU with all caches inside the topic work/ directory.
# Usage: GPU=<uuid> CAMPAIGN=<id> run_one.sh <name> '<engine json>' <workloads> [extra bench.vllm_bench args...]
# Env: MODEL (default: text-only Gold export), CACHE (vLLM compile cache root; default work/cache/vllm-bench).
set -uo pipefail
TOPIC=$(cd "$(dirname "$0")/../.." && pwd)
W=${WSE_WORK_ROOT:-$TOPIC/work}
NAME=$1; ENGINE=$2; WL=$3; shift 3
CAMPAIGN=${CAMPAIGN:?set CAMPAIGN}
MODEL=${MODEL:-$W/derived/qwen3.5-0.8B-text-gold}
export TMPDIR=$W/tmp HF_HOME=$W/cache/hf XDG_CACHE_HOME=${XDG_CACHE_HOME:-$W/cache} \
  TRITON_CACHE_DIR=${TRITON_CACHE_DIR:-$W/cache/triton} FLASHINFER_WORKSPACE_BASE=${FLASHINFER_WORKSPACE_BASE:-$W/cache} \
  TORCHINDUCTOR_CACHE_DIR=${TORCHINDUCTOR_CACHE_DIR:-$W/cache/inductor}
export VLLM_CACHE_ROOT=${CACHE:-$W/cache/vllm-bench}
export CUDA_VISIBLE_DEVICES=${GPU:?set GPU uuid} OMP_NUM_THREADS=${OMP_NUM_THREADS:-8}
RAW=$W/raw/$CAMPAIGN; LOG=$W/logs/$CAMPAIGN
mkdir -p "$RAW" "$LOG" "$TMPDIR"
cd "$TOPIC/code"
setsid "$W/envs/vllm/bin/python" -m bench.vllm_bench --model "$MODEL" --name "$NAME" --engine "$ENGINE" \
  --workloads "$WL" --out "$RAW" "$@" > "$LOG/$NAME.log" 2>&1 &
PID=$!
wait $PID; rc=$?
# reap anything left in the job's own session (e.g. an orphaned engine core); never touches other processes
pkill -s $PID 2>/dev/null; sleep 1; pkill -9 -s $PID 2>/dev/null
echo "$NAME rc=$rc"
exit $rc
