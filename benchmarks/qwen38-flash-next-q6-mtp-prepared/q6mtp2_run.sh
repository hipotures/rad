#!/usr/bin/env bash
set -euo pipefail
exec python3 "$(dirname "$0")/q6mtp2_sweep.py" "$@"
