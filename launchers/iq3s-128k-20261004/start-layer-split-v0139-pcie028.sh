#!/usr/bin/env bash
set -euo pipefail
export CUDA_VISIBLE_DEVICES=0,1
unset STRATA_SPLIT_OWN STRATA_KV_ROT STRATA_REFILL_SERIAL STRATA_SPEC_COUPLED STRATA_REMOTE_EXPERT_DEBUG
cd /srv/ai/strata-pr578-refresh-20261004-control
exec /srv/ai/strata-pr578-refresh-20261004-control/.venv/bin/python -m serve.server --engine strata --config /srv/ai/launchers/iq3s-128k-20261004/configs/layer-split-v0139-pcie028.json --host 0.0.0.0 --port 8080 "$@"
