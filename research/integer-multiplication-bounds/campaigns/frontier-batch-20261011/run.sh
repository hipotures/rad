#!/usr/bin/env bash
# Frontier batch 2026-10-11: offline jobs run by the operator, one after another.
#
#   export RAD_WORK_ROOT=<task-owned work directory>   # required, outside the Git checkout
#   ./run.sh setup     # environment, upstream clone and pinned commits (network); preflight
#   ./run.sh 1         # stream-model check of whole vs cross-copy hosting   (~1 min, CPU)
#   ./run.sh 2         # parallel fresh replays of 39 pinned upstream claims (~1-3 h, all cores)
#   ./run.sh 3         # exact lattice/root-system screen incl. Leech          (~2 min, CPU+GPU)
#   ./run.sh 4         # repair replays of #471/#476/#478/#483/#492, one documented deviation (~30 min)
#   ./run.sh 5         # fresh replays of #484 and #495-#502 (new frontier), repair only if job 4's condition (~1 h)
#   ./run.sh status    # what has finished
#
# Every job writes to a fresh $RAD_WORK_ROOT/runs/<UTC>-job<N>/ and never deletes
# earlier runs. A job's preflight stops it within seconds if something is missing;
# after preflight a job always runs to completion and records failures per part.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODE="$HERE/code"
CONF="$HERE/configs"
: "${RAD_WORK_ROOT:?set RAD_WORK_ROOT to a task-owned work directory outside the Git checkout}"
ROOT="$(mkdir -p "$RAD_WORK_ROOT" && cd "$RAD_WORK_ROOT" && pwd)"
case "$ROOT/" in "$(git -C "$HERE" rev-parse --show-toplevel)/"*) echo "RAD_WORK_ROOT must be outside the Git checkout" >&2; exit 2;; esac
PY="$ROOT/envs/batch/bin/python"
CLONE="$ROOT/repos/upstream"
UPSTREAM=https://github.com/CrocSwap/integer-mult-bounds
PR370_SHA=b7fe9cdf2da009c947ff6b334c562bc190b30373   # E8 bit word producer (job 3 validation)

stamp() { date -u +%Y%m%dT%H%M%SZ; }
say() { printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*"; }
die() { say "PREFLIGHT FAILED: $*" >&2; exit 3; }

pinned_shas() {  # $1 = replay config (default: job 2's, plus the #370 producer)
  "$PY" -c 'import json,sys; print("\n".join(r["sha"] for r in json.load(open(sys.argv[1]))["replays"]))' "${1:-$CONF/job2-replays.json}"
  [ -n "${1:-}" ] || echo "$PR370_SHA"
}
config_prs() {  # $1 = replay config
  "$PY" -c 'import json,sys; print(" ".join(str(r["pr"]) for r in json.load(open(sys.argv[1]))["replays"]))' "$1"
}

preflight() {  # $1 = job
  [ -x "$PY" ] || die "missing $PY (run ./run.sh setup)"
  "$PY" - "$1" <<'EOF' || die "python environment"
import sys, importlib
mods = {'1': ['numpy'], '2': ['numpy', 'scipy', 'sympy', 'mpmath'], '3': ['numpy'],
        '5': ['numpy', 'scipy', 'sympy', 'mpmath']}[sys.argv[1]]
for m in mods:
    importlib.import_module(m)
assert sys.version_info >= (3, 11), sys.version
EOF
  [ -d "$CLONE/.git" ] || die "missing upstream clone $CLONE (run ./run.sh setup)"
  if [ "$1" != 1 ]; then
    for s in $(pinned_shas); do git -C "$CLONE" cat-file -e "$s^{commit}" 2>/dev/null || die "commit $s not in clone (run ./run.sh setup)"; done
  fi
  if [ "$1" = 5 ]; then
    for s in $(pinned_shas "$CONF/job5-replays.json"); do git -C "$CLONE" cat-file -e "$s^{commit}" 2>/dev/null || die "commit $s not in clone (run ./run.sh setup)"; done
  fi
  if [ "$1" = 2 ] || [ "$1" = 5 ]; then
    command -v g++ >/dev/null || die "g++ not found (some upstream packages compile C++)"
    [ -d "${BOOST_INCLUDE:-/usr/include}/boost" ] || die "Boost headers not found; set BOOST_INCLUDE"
    free_gb=$(df -Pk "$ROOT" | awk 'NR==2{print int($4/1048576)}')
    [ "$free_gb" -ge 60 ] || die "only ${free_gb} GiB free under $ROOT; need >= 60"
  fi
  say "preflight job $1 OK ($("$PY" -V), $(nproc) cores)"
}

new_run() {  # $1 = job; prints run dir
  local d="$ROOT/runs/$(stamp)-job$1"
  mkdir -p "$d"
  {
    echo "{"
    echo "  \"job\": $1,"
    echo "  \"started_utc\": \"$(date -u +%FT%TZ)\","
    echo "  \"campaign_commit\": \"$(git -C "$HERE" rev-parse HEAD)\","
    echo "  \"campaign_dirty\": $( [ -z "$(git -C "$HERE" status --porcelain -- .)" ] && echo false || echo true ),"
    echo "  \"python\": \"$("$PY" -V 2>&1)\","
    echo "  \"host_cores\": $(nproc),"
    echo "  \"gpus\": \"$(nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader 2>/dev/null | tr '\n' ';')\""
    echo "}"
  } > "$d/protocol.json"
  cp -r "$CONF" "$d/configs"
  echo "$d"
}

finish() {  # $1 = run dir, $2 = exit code
  "$PY" - "$1" "$2" <<'EOF'
import json, sys, datetime
p = sys.argv[1] + '/protocol.json'; d = json.load(open(p))
d.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), exit_code=int(sys.argv[2]))
json.dump(d, open(p, 'w'), indent=2)
EOF
  say "finished $(basename "$1") exit=$2  ->  $1"
}

case "${1:-}" in
  setup)
    command -v uv >/dev/null || { echo "uv is required (https://docs.astral.sh/uv/)"; exit 2; }
    mkdir -p "$ROOT/envs" "$ROOT/repos" "$ROOT/runs"
    [ -x "$PY" ] || uv venv -q "$ROOT/envs/batch" --python 3.14
    uv pip install -q --python "$PY" -r "$CONF/requirements.txt"
    [ -d "$CLONE/.git" ] || git clone -q --no-checkout "$UPSTREAM" "$CLONE"
    for n in $(config_prs "$CONF/job2-replays.json") 370 $(config_prs "$CONF/job5-replays.json"); do
      git -C "$CLONE" fetch -q origin "pull/$n/head:refs/remotes/pr/$n" || say "warning: could not fetch PR $n head"
    done
    for s in $(pinned_shas) $(pinned_shas "$CONF/job5-replays.json"); do
      git -C "$CLONE" cat-file -e "$s^{commit}" 2>/dev/null || git -C "$CLONE" fetch -q origin "$s" || say "warning: pinned $s unavailable"
    done
    for j in 1 2 3 5; do preflight "$j"; done
    ;;
  1)
    preflight 1; RUN=$(new_run 1); set +e
    "$PY" -B "$CODE/job1_stream_model.py" --out "$RUN/job1-stream-model.json" 2>&1 | tee "$RUN/job1.log"
    rc=${PIPESTATUS[0]}; set -e; finish "$RUN" "$rc"
    ;;
  2)
    preflight 2; RUN=$(new_run 2); set +e
    "$PY" -B "$CODE/job2_replays.py" --config "$CONF/job2-replays.json" --clone "$CLONE" --work "$RUN" \
      --python "$PY" --jobs "${JOBS:-$(( $(nproc) - 1 ))}" --timeout-min "${TIMEOUT_MIN:-150}" 2>&1 | tee "$RUN/job2.log"
    rc=${PIPESTATUS[0]}; set -e; finish "$RUN" "$rc"
    ;;
  3)
    preflight 3; RUN=$(new_run 3); set +e
    mkdir -p "$RUN/pr370" && git -C "$CLONE" archive "$PR370_SHA" research/e8-bit/code/bit/producer | tar -x -C "$RUN/pr370"
    "$PY" -B "$CODE/job3_lattice_screen.py" --out "$RUN/job3-lattice-screen.json" \
      --e8-producer "$RUN/pr370/research/e8-bit/code/bit/producer" 2>&1 | tee "$RUN/job3.log"
    rc=${PIPESTATUS[0]}; set -e; finish "$RUN" "$rc"
    ;;
  4)
    preflight 2; RUN=$(new_run 4); set +e
    "$PY" -B "$CODE/job4_repair_replays.py" --config "$CONF/job2-replays.json" --clone "$CLONE" --work "$RUN" \
      --python "$PY" --timeout-min "${TIMEOUT_MIN:-150}" ${ONLY:+--only "$ONLY"} 2>&1 | tee "$RUN/job4.log"
    rc=${PIPESTATUS[0]}; set -e; finish "$RUN" "$rc"
    ;;
  5)
    preflight 5; RUN=$(new_run 5); set +e
    "$PY" -B "$CODE/job5_replays.py" --config "$CONF/job5-replays.json" --clone "$CLONE" --work "$RUN" \
      --python "$PY" --timeout-min "${TIMEOUT_MIN:-180}" ${ONLY:+--only "$ONLY"} 2>&1 | tee "$RUN/job5.log"
    rc=${PIPESTATUS[0]}; set -e; finish "$RUN" "$rc"
    ;;
  test5)
    "$PY" -B "$CODE/test_job5_smoke.py"
    ;;
  status)
    for d in "$ROOT"/runs/*-job*; do
      [ -d "$d" ] || continue
      "$PY" -c 'import json,sys; d=json.load(open(sys.argv[1]+"/protocol.json")); print(sys.argv[1].rsplit("/",1)[-1], "finished" if "finished_utc" in d else "RUNNING/INTERRUPTED", "exit=%s" % d.get("exit_code"))' "$d"
    done
    ;;
  *) sed -n '2,15p' "$0"; exit 2;;
esac
