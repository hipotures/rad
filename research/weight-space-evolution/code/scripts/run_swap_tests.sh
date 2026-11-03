#!/usr/bin/env bash
# Persistent-evaluator transition tests on both GPUs (B4). GPU0: direct sequence, then extended random cycles.
# GPU1: restart sequence (fresh-engine reference for every state), then reload sequence.
set -uo pipefail
TOPIC=$(cd "$(dirname "$0")/../.." && pwd); W=$TOPIC/work
CAMPAIGN=${CAMPAIGN:?}; SEQ=${SEQ:-gold,p50c,gold,p25c,p50c,gold,p10c,rand-dir-0,rand-fused,chain-p50c,gold}
EXT=${EXT:-80}; P=${P:-}   # P: name prefix for a repeated round
export TMPDIR=$W/tmp HF_HOME=$W/cache/hf XDG_CACHE_HOME=$W/cache TRITON_CACHE_DIR=$W/cache/triton \
  FLASHINFER_WORKSPACE_BASE=$W/cache TORCHINDUCTOR_CACHE_DIR=$W/cache/inductor VLLM_CACHE_ROOT=$W/cache/vllm-bench \
  PYTHONPATH=$TOPIC/code
R=$W/raw/$CAMPAIGN; L=$W/logs/$CAMPAIGN; mkdir -p "$R" "$L"; cd "$TOPIC/code"
PY=$W/envs/vllm/bin/python
g0() { CUDA_VISIBLE_DEVICES=0 setsid $PY -m wse.swap_test --mode direct --sequence "$SEQ" --out "$R" --name ${P}seq_direct > "$L/${P}seq_direct.log" 2>&1
       [ "$EXT" -gt 0 ] && CUDA_VISIBLE_DEVICES=0 setsid $PY -m wse.swap_test --mode direct --extended "$EXT" --seed ${EXTSEED:-1} ${EXTFULL:-} --out "$R" --name ${P}ext_direct > "$L/${P}ext_direct.log" 2>&1; }
g1() { CUDA_VISIBLE_DEVICES=1 setsid $PY -m wse.swap_test --mode restart --sequence "$SEQ" --out "$R" --name ${P}seq_restart > "$L/${P}seq_restart.log" 2>&1
       CUDA_VISIBLE_DEVICES=1 setsid $PY -m wse.swap_test --mode reload --sequence "$SEQ" --out "$R" --name ${P}seq_reload > "$L/${P}seq_reload.log" 2>&1; }
g0 & A=$!; g1 & B=$!
wait $A; wait $B
echo done; ls "$R"
