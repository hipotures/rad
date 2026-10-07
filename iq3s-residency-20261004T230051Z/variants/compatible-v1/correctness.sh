#!/usr/bin/env bash
set -euo pipefail
cd /srv/ai/research/iq3s-residency-20261004T230051Z
exec /srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python /srv/ai/research/iq3s-residency-20261004T230051Z/scripts/correctness_battery.py --variant compatible-v1 --experiment E010-compatible-runtime --attempt v1 --reference /srv/ai/research/iq3s-residency-20261004T230051Z/experiments/E006-frequency/correctness-r2/correctness/control "$@"
