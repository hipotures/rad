#!/usr/bin/env bash
set -euo pipefail
cd /srv/ai/research/iq3s-residency-20261004T230051Z
exec /srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python /srv/ai/research/iq3s-residency-20261004T230051Z/scripts/collect_traces.py profiles --variant diagnostic-skip-local-host-plan-v1 --experiment E019-skip-local-host-plan --attempt diagnostic-v1 "$@"
