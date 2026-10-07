#!/usr/bin/env bash
set -euo pipefail
cd /srv/ai/strata
export CUDA_VISIBLE_DEVICES=0,1
exec /srv/ai/strata/.venv/bin/python -m serve.server --engine strata --config /srv/ai/benchmarks/strata-qwen38/q4-max-sweep/configs/IQ3_S-best-runtime.json --host 127.0.0.1 --port 18084
