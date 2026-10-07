#!/usr/bin/env bash
set -euo pipefail
exec "/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python" "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-multigpu-20261005T164628Z/scripts/q4_multigpu.py" --campaign "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-multigpu-20261005T164628Z" start --profile 32k "$@"
