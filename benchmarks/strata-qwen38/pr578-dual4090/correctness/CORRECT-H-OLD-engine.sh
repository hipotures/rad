#!/bin/bash
set -o pipefail
/srv/ai/strata-pr578-control/build-default/strata "$@" | tee /srv/ai/benchmarks/strata-qwen38/pr578-dual4090/correctness/CORRECT-H-OLD-protocol.txt
