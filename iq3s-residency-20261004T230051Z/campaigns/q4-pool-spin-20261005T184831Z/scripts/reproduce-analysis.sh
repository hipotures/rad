#!/usr/bin/env bash
set -euo pipefail
/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-pool-spin-20261005T184831Z/scripts/analyze_pool.py
/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-pool-spin-20261005T184831Z/scripts/finish_pool.py render
/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-pool-spin-20261005T184831Z/scripts/finish_pool.py audit
