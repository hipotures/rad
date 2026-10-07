#!/usr/bin/env bash
set -euo pipefail
exec "/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python" "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-residency-v2-20261005T202441Z/scripts/launch.py" stop --variant control "$@"
