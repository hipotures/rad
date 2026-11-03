#!/usr/bin/env bash
# Two engines in parallel: GPU0 = Profile 3 (FlashInfer, mns 1024, mnbt 16384); GPU1 = vLLM defaults.
set -uo pipefail
TOPIC=$(cd "$(dirname "$0")/../.." && pwd); W=$TOPIC/work; C=20261103T-persistent-swap-evaluator
export TMPDIR=$W/tmp HF_HOME=$W/cache/hf XDG_CACHE_HOME=$W/cache TRITON_CACHE_DIR=$W/cache/triton \
  FLASHINFER_WORKSPACE_BASE=$W/cache TORCHINDUCTOR_CACHE_DIR=$W/cache/inductor VLLM_CACHE_ROOT=$W/cache/vllm-bench PYTHONPATH=$TOPIC/code
cd "$TOPIC/code"; mkdir -p $W/raw/$C $W/logs/$C
P3='{"max_model_len": 32768, "gpu_memory_utilization": 0.85, "attention_backend": "FLASHINFER", "max_num_seqs": 1024, "max_num_batched_tokens": 16384}'
DF='{"max_model_len": 32768, "gpu_memory_utilization": 0.85}'
CUDA_VISIBLE_DEVICES=0 setsid $W/envs/vllm/bin/python -m wse.determinism_probe --engine-json "$P3" --out $W/raw/$C/det_profile3.json > $W/logs/$C/det_profile3.log 2>&1 &
A=$!
CUDA_VISIBLE_DEVICES=1 setsid $W/envs/vllm/bin/python -m wse.determinism_probe --engine-json "$DF" --out $W/raw/$C/det_default.json > $W/logs/$C/det_default.log 2>&1 &
B=$!
wait $A; wait $B; grep -h "^[0-9] [SG]" $W/logs/$C/det_profile3.log; echo ---; grep -h "^[0-9] [SG]" $W/logs/$C/det_default.log
