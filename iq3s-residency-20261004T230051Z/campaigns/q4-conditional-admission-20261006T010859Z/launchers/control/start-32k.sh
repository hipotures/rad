#!/usr/bin/env bash
set -euo pipefail
exec "/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python" "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-conditional-admission-20261006T010859Z/scripts/launch.py" start --variant control --profile 32k "$@"
