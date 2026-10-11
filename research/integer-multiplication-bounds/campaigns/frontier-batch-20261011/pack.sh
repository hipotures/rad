#!/usr/bin/env bash
# Pack the compact text evidence of finished runs as gzip copies under evidence/<run-id>.
# Local only: nothing is staged, committed or pushed. Originals stay unchanged.
#
#   export RAD_WORK_ROOT=<task-owned work directory>
#   ./pack.sh                 # every finished run not yet packed
#   ./pack.sh <run-dir>...    # selected runs
#
# Selected: protocol, configs, job logs and results, per-replay records and logs,
# job 2 SUMMARY.json and the receipt/result/audit/failure JSON of each replay output.
# Not selected: worktrees (pinned upstream source) and bulky intermediate outputs,
# which stay in RAD_WORK_ROOT and are listed in each run's records.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOP="$(git -C "$HERE" rev-parse --show-toplevel)"
: "${RAD_WORK_ROOT:?set RAD_WORK_ROOT}"
PY="$RAD_WORK_ROOT/envs/batch/bin/python"
runs=("$@")
[ ${#runs[@]} -gt 0 ] || runs=("$RAD_WORK_ROOT"/runs/*-job*)
for run in "${runs[@]}"; do
  run="$(cd "$run" && pwd)"; id="$(basename "$run")"
  dest="$HERE/evidence/$id"
  if [ -e "$dest" ]; then echo "skip $id (already packed)"; continue; fi
  if ! "$PY" -c 'import json,sys; sys.exit(0 if "finished_utc" in json.load(open(sys.argv[1])) else 1)' "$run/protocol.json"; then
    echo "skip $id (not finished)"; continue
  fi
  list="$(mktemp)"
  "$PY" - "$run" "$list" <<'EOF'
import json, re, sys
from pathlib import Path
run, out = Path(sys.argv[1]), sys.argv[2]
keep = []
for p in sorted(run.rglob('*')):
    if not p.is_file() or p.suffix not in ('.json', '.jsonl', '.log', '.txt'):
        continue
    rel = p.relative_to(run)
    parts = rel.parts[1:] if rel.parts[0] == 'repair' else rel.parts  # job 5 repair attempts
    top = parts[0]
    if top in ('trees', 'tmp', 'pr370'):
        continue
    if top == 'out':
        if not re.search(r'(RECEIPT|RESULT|AUDIT|FAILURE)', p.name, re.I) or p.stat().st_size > 5_000_000:
            continue
    keep.append(rel.as_posix())
json.dump(keep, open(out, 'w'))
print(f'{len(keep)} files selected')
EOF
  mkdir -p "$HERE/evidence"
  ( cd "$TOP" && python3 tools/archive_workspace.py pack-text --source "$run" --destination "${dest#$TOP/}" --paths-from "$list" | tail -6 )
  rm -f "$list"
done
