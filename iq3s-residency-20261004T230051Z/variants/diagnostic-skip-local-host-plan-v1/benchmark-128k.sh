#!/usr/bin/env bash
set -euo pipefail
cd /srv/ai/research/iq3s-residency-20261004T230051Z
exec "/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python" "/srv/ai/research/iq3s-residency-20261004T230051Z/scripts/lab.py" benchmark --variant "diagnostic-skip-local-host-plan-v1" --profile "128k" "$@"
