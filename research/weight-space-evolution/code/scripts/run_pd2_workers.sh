#!/usr/bin/env bash
# One wse.pd2_eval worker per GPU on a shared job queue (jobs submitted with `python -m wse.pd2_eval submit`).
# Env: CAMPAIGN, QUEUE (dir), GPUS (e.g. "0 1"), SWAP_MODE (direct|reload|restart), PROFILE (profile3|default), FOLLOW.
set -uo pipefail
TOPIC=$(cd "$(dirname "$0")/../.." && pwd); W=$TOPIC/work
CAMPAIGN=${CAMPAIGN:?}; QUEUE=${QUEUE:?}; GPUS=${GPUS:-"0 1"}; SWAP_MODE=${SWAP_MODE:-direct}; PROFILE=${PROFILE:-profile3}
export TMPDIR=$W/tmp HF_HOME=$W/cache/hf XDG_CACHE_HOME=$W/cache TRITON_CACHE_DIR=$W/cache/triton \
  FLASHINFER_WORKSPACE_BASE=$W/cache TORCHINDUCTOR_CACHE_DIR=$W/cache/inductor VLLM_CACHE_ROOT=$W/cache/vllm-bench \
  PYTHONPATH=$TOPIC/code
L=$W/logs/$CAMPAIGN; mkdir -p "$L"; cd "$TOPIC/code"
pids=()
for g in $GPUS; do
  CUDA_VISIBLE_DEVICES=$g setsid "$W/envs/vllm/bin/python" -m wse.pd2_eval worker --queue "$QUEUE" --campaign "$CAMPAIGN" \
    --swap-mode "$SWAP_MODE" --engine-profile "$PROFILE" ${FOLLOW:+--follow} > "$L/worker-gpu$g-$SWAP_MODE-$(date +%s).log" 2>&1 &
  pids+=($!)
done
rc=0; for p in "${pids[@]}"; do wait $p || rc=1; done
for p in "${pids[@]}"; do pkill -s $p 2>/dev/null; done
echo "workers done rc=$rc"; ls "$QUEUE"/done | wc -l; ls "$QUEUE"/failed
