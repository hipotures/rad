#!/usr/bin/env bash
set -euo pipefail
benchmark_root="${BENCH_ROOT:-/srv/ai/benchmarks/qwen-hardware-characterization}"
exec "$benchmark_root/.venv/bin/python" "$benchmark_root/campaign.py" "$@"
