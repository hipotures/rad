#!/usr/bin/env bash
set -euo pipefail
cd /srv/ai/research/iq3s-residency-20261004T230051Z
exec /srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python /srv/ai/research/iq3s-residency-20261004T230051Z/scripts/collect_traces.py episodes --variant diagnostic-gpu-router-v2 --experiment E017-gpu-router --attempt v2 "$@"
