#!/usr/bin/env bash
# Bounded MATH-500 check of Gold vs p50c with problem sharding: GPU k runs Gold then p50c on problems k, k+2, ...
# Both GPUs carry the same mix of work and finish together (the per-model split of run_p50c_math500_bounded.sh left
# one GPU idle while the other finished the slower model). Usage: GPUS="<uuid0> <uuid1>" RUN=<run-id> this script.
set -euo pipefail
TOPIC=$(cd "$(dirname "$0")/../.." && pwd)
W=${WSE_WORK_ROOT:-$TOPIC/work}
RUN=${RUN:?set RUN to a fresh run id}
STRIDE=${STRIDE:-5}; SAMPLES=${SAMPLES:-2}; MAX_TOKENS=${MAX_TOKENS:-32768}
read -r -a G <<< "${GPUS:-0 1}"; K=${#G[@]}
export TMPDIR=$W/tmp HF_HOME=$W/cache/hf VLLM_CACHE_ROOT=$W/cache/vllm XDG_CACHE_HOME=$W/cache TRITON_CACHE_DIR=$W/cache/triton \
  FLASHINFER_WORKSPACE_BASE=$W/cache UV_CACHE_DIR=$W/cache/uv TORCHINDUCTOR_CACHE_DIR=$W/cache/inductor
mkdir -p "$W/logs/$RUN" "$W/raw/$RUN" "$TMPDIR"
cd "$TOPIC/code"
nvidia-smi --query-gpu=timestamp,index,memory.used,utilization.gpu --format=csv -l 30 > "$W/logs/$RUN/nvidia_smi.csv" &
SMI=$!
pids=()
for i in "${!G[@]}"; do
  (
    for lab in gold p50c; do
      CUDA_VISIBLE_DEVICES=${G[$i]} "$W/envs/vllm/bin/python" -m wse.qwen_bounded_eval \
        --ckpt "$W/derived/qwen3.5-0.8B-text-$lab" --label "$lab" --shard "$i/$K" --max-tokens "$MAX_TOKENS" \
        --math500 "$W/inputs/math500/test.jsonl" --upstream-code "$W/repos/lm_understand-logs/exp8_math/code" \
        --stride "$STRIDE" --samples "$SAMPLES" --out "$TOPIC/runs/$RUN/results" --raw "$W/raw/$RUN" \
        > "$W/logs/$RUN/${lab}_s${i}of${K}.log" 2>&1
    done
  ) &
  pids+=($!)
done
rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done
kill $SMI || true
exit $rc
