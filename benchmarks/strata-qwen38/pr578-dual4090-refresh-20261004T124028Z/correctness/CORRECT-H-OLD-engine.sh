#!/bin/bash
set -o pipefail
/srv/ai/strata-pr578-refresh-20261004-control/build-default/strata "$@" | tee /srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/correctness/CORRECT-H-OLD-protocol.txt
