#!/usr/bin/env bash
set -euo pipefail
exec /srv/ai/benchmarks/qwen-hardware-characterization/.venv/bin/python /srv/ai/benchmarks/qwen-hardware-characterization/fio_launcher.py "$@"
