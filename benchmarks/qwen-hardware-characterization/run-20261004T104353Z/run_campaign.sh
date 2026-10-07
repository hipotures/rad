#!/usr/bin/env bash
set -euo pipefail
exec /srv/ai/benchmarks/qwen-hardware-characterization/.venv/bin/python /srv/ai/benchmarks/qwen-hardware-characterization/launcher.py --resume /srv/ai/benchmarks/qwen-hardware-characterization/run-20261004T104353Z "$@"
