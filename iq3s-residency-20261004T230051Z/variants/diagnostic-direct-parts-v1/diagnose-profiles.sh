#!/usr/bin/env bash
set -euo pipefail
cd /srv/ai/research/iq3s-residency-20261004T230051Z
exec /srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python scripts/collect_traces.py profiles --variant diagnostic-direct-parts-v1 --experiment E023-direct-parts --attempt diagnostic-v1 "$@"
