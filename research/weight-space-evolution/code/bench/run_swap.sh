#!/usr/bin/env bash
# Weight-swap check: GPU0 = one engine Gold -> p50c -> Gold (in-place reload); GPU1 = fresh engine on p50c.
set -uo pipefail
TOPIC=$(cd "$(dirname "$0")/../.." && pwd); W=$TOPIC/work
CAMPAIGN=${CAMPAIGN:?}; ENGINE=${ENGINE:-'{}'}; TAG=${TAG:-base}
G0=${G0:-GPU-6c849b47-7111-9265-9d42-ff8eddc05a2d}; G1=${G1:-GPU-81ac6e96-0bfe-390d-beb1-241466569d6b}
export TMPDIR=$W/tmp HF_HOME=$W/cache/hf XDG_CACHE_HOME=$W/cache TRITON_CACHE_DIR=$W/cache/triton \
  FLASHINFER_WORKSPACE_BASE=$W/cache TORCHINDUCTOR_CACHE_DIR=$W/cache/inductor VLLM_CACHE_ROOT=$W/cache/vllm-bench
G=$W/derived/qwen3.5-0.8B-text-gold; P=$W/derived/qwen3.5-0.8B-text-p50c
mkdir -p "$W/raw/$CAMPAIGN" "$W/logs/$CAMPAIGN"; cd "$TOPIC/code"
CUDA_VISIBLE_DEVICES=$G0 setsid "$W/envs/vllm/bin/python" -m bench.weight_swap --models "$G,$P,$G" --engine "$ENGINE" \
  --out "$W/raw/$CAMPAIGN" --name "swap_${TAG}_gold_p50c_gold" > "$W/logs/$CAMPAIGN/swap_${TAG}.log" 2>&1 &
A=$!
CUDA_VISIBLE_DEVICES=$G1 setsid "$W/envs/vllm/bin/python" -m bench.weight_swap --models "$P" --engine "$ENGINE" \
  --out "$W/raw/$CAMPAIGN" --name "swap_${TAG}_fresh_p50c" > "$W/logs/$CAMPAIGN/swap_${TAG}_fresh.log" 2>&1 &
B=$!
wait $A; ra=$?; wait $B; rb=$?
pkill -s $A 2>/dev/null; pkill -s $B 2>/dev/null
echo "swap rc=$ra fresh rc=$rb"
