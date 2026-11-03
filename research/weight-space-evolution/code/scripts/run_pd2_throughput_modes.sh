#!/usr/bin/env bash
# Full-cycle throughput comparison of transition modes / GPU counts on the dev split (Workstream B/C).
# Each configuration is its own campaign (so pd2_report/pd2_throughput read only its jobs):
#   <base>-restart2 : restart mode, GPUs 0+1, editors SUB
#   <base>-reload2  : reload mode,  GPUs 0+1, editors SUB
#   <base>-direct1  : direct mode,  GPU 0 only, all editors (scaling vs the 2-GPU direct campaign <base>)
set -uo pipefail
TOPIC=$(cd "$(dirname "$0")/../.." && pwd); W=$TOPIC/work; cd "$TOPIC/code"
BASE=${BASE:-20261103T-phaseD-v2-e2e}
SUB=${SUB:-E0,p50c,p25c,p10c,rand-dir-0,rand-fused}
RUNS=${RUNS:-restart2 reload2 direct1}   # which configurations to run (names below)
RES=${RES:-$TOPIC/runs/$BASE/results}
ALL=$(python3 -c "import json;print(','.join(e['editor_id'] for e in json.load(open('$TOPIC/configs/phaseD_v2/editors.json'))['editors']))")
run() {  # name mode gpus editors
  local C=$BASE-$1 Q=$W/queues/$BASE-$1
  mkdir -p "$Q"
  PYTHONPATH=. "$W/envs/vllm/bin/python" -m wse.pd2_eval submit --queue "$Q" --editors "$4" --split dev --prefix "$1_" | tail -1
  date +%s > "$W/tmp/$C.start"
  CAMPAIGN=$C QUEUE=$Q GPUS="$3" SWAP_MODE=$2 "$TOPIC/code/scripts/run_pd2_workers.sh"
  "$W/envs/wse/bin/python" -m wse.pd2_throughput --campaign "$C" --label "$1" --since "$(cat "$W/tmp/$C.start")" \
    --out "$RES/throughput_$1.json" | head -30
}
for r in $RUNS; do case $r in
  restart2) run restart2 restart "0 1" "$SUB" ;;
  reload2) run reload2 reload "0 1" "$SUB" ;;
  direct1) run direct1 direct "0" "$ALL" ;;
  restart2-all) run restart2-all restart "0 1" "$ALL" ;;
  reload2-all) run reload2-all reload "0 1" "$ALL" ;;
esac; done
echo all done
