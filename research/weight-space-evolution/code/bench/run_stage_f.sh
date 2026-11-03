#!/usr/bin/env bash
# Workload F (two GPUs): baseline config solo on GPU0 (GPU1 idle), then the same config on both GPUs at once,
# then one tensor-parallel (TP=2) engine over both GPUs. Run with no other GPU work.
set -uo pipefail
TOPIC=$(cd "$(dirname "$0")/../.." && pwd)
PY=$TOPIC/work/envs/vllm/bin/python
G0=${G0:-GPU-6c849b47-7111-9265-9d42-ff8eddc05a2d}; G1=${G1:-GPU-81ac6e96-0bfe-390d-beb1-241466569d6b}
export CAMPAIGN=${CAMPAIGN:?}
cd "$TOPIC/code"
$PY -m bench.queue "$TOPIC/configs/vllm_perf/stage_f_solo.json" --campaign "$CAMPAIGN" --gpus "$G0"
$PY -m bench.queue "$TOPIC/configs/vllm_perf/stage_f_pair.json" --campaign "$CAMPAIGN" --gpus "$G0,$G1"
GPU="$G0,$G1" "$TOPIC/code/bench/run_one.sh" f_tp2 '{"tensor_parallel_size": 2}' A,B,D --repeats 2 --d-levels 1,8,32
