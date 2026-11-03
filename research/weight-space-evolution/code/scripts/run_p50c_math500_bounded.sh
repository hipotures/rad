#!/usr/bin/env bash
# Bounded MATH-500 check of Gold vs reconstructed p50c, one model per GPU, in parallel.
# Requires: work root (default <topic>/work) with envs/vllm, inputs/math500/test.jsonl, derived/qwen3.5-0.8B-text-{gold,p50c},
# repos/lm_understand-logs (pinned). GPU_GOLD / GPU_P50C: GPU UUIDs or indices (discover with nvidia-smi -L).
set -euo pipefail
TOPIC=$(cd "$(dirname "$0")/../.." && pwd)
W=${WSE_WORK_ROOT:-$TOPIC/work}
RUN=${RUN:-20261103T-p50c-math500-bounded}
STRIDE=${STRIDE:-5}; SAMPLES=${SAMPLES:-2}
export TMPDIR=$W/tmp HF_HOME=$W/cache/hf VLLM_CACHE_ROOT=$W/cache/vllm XDG_CACHE_HOME=$W/cache TRITON_CACHE_DIR=$W/cache/triton \
  FLASHINFER_WORKSPACE_BASE=$W/cache UV_CACHE_DIR=$W/cache/uv TORCHINDUCTOR_CACHE_DIR=$W/cache/inductor   # keep every cache inside the topic
mkdir -p "$W/logs/$RUN" "$W/raw/$RUN" "$TMPDIR"
cd "$TOPIC/code"
nvidia-smi --query-gpu=timestamp,index,memory.used,utilization.gpu --format=csv -l 30 > "$W/logs/$RUN/nvidia_smi.csv" &
SMI=$!
pids=()
for spec in "gold:${GPU_GOLD:-0}" "p50c:${GPU_P50C:-1}"; do
  lab=${spec%%:*}; gpu=${spec#*:}
  CUDA_VISIBLE_DEVICES=$gpu "$W/envs/vllm/bin/python" -m wse.qwen_bounded_eval \
    --ckpt "$W/derived/qwen3.5-0.8B-text-$lab" --label "$lab" --math500 "$W/inputs/math500/test.jsonl" \
    --upstream-code "$W/repos/lm_understand-logs/exp8_math/code" --stride "$STRIDE" --samples "$SAMPLES" \
    --out "$TOPIC/runs/$RUN/results" --raw "$W/raw/$RUN" > "$W/logs/$RUN/$lab.log" 2>&1 &
  pids+=($!)
done
rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done
kill $SMI || true
exit $rc
