#!/usr/bin/env bash
set -euo pipefail
exec "/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python" "/srv/ai/research/iq3s-residency-20261004T230051Z/scripts/lab.py" stop --variant "persistent-v2-off" "$@"
