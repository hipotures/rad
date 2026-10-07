# Phase 3 reproduction

Use frozen local tapes/backing and the recorded binary identity. No automatic engine update, model training, rebuild or ordinary launcher change occurs. Reproduction writes a fresh namespace and refuses GPU/port conflict. Hashes and exact commands are in `configs/runtime-identity.json`, `inputs/manifest.json`, and the input/artifact manifests.

```bash
cd /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase3-20261007T150955Z
PY=/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python
$PY code/quick_status.py
$PY code/reproduce.py --prepare-only --task math-rational --arm PLANNER_OPT
$PY code/reproduce.py --task math-rational --arm PLANNER_OPT
```

Retained headline modes: `PLANNER_BASELINE`, `PLANNER_OPT`, `REPLAY_CURRENT`. Frozen logistic with minimum TC is retained as `ORACLE_IN_LOGISTIC_TC`; only deterministic OFF/ON parity was required/tested for its common planner path. Do not interpret this as a new live scorer competition. Use development tasks for a bounded reproducer, not a fourth primary point. Startup plus saved warmup is capped at180s; replay at240s; owned parent subprocess at440s plus cleanup. A later explicitly invoked reproduction after completion gets a separate600s clock; the scientific campaign clock is never reset.

The `reproduce.py` command tests its binary, frozen checkpoint, configuration, tape and exact work/initial-state identities before claiming a valid request. All outputs are separate from the original campaign. Owned PID/create-time checks precede termination; archived ownership records are never used to stop unrelated live processes.

Result regeneration (read-only prior campaigns, writes only Phase 3 derived results) must run with GPUs idle:

```bash
$PY code/summarize.py
$PY code/live_trajectory.py
$PY code/relative_mechanism.py
$PY code/phase_resources.py
$PY code/render_report.py
```

Existing-data analysis is reproducible without new inference:

```bash
$PY code/existing_analysis.py
```

It reads Phase 2 binary journals at their original locations. It does not rerun old regeneration scripts in place. Deterministic parity requires a fresh execution namespace, frozen source and CUDA user-space headers/runtime but no inference GPU work. `code/parity.py` preserves completed identical points and verifies their journals/logs rather than repeating a deterministic policy because elapsed simulation time differed. `tests/deterministic-parity.json` preserves candidate hashes, admission/lifecycle hashes and results for all13 tapes x2 scorers.

# Explicit source rebuild

The public base and cumulative patch reconstruct experimental source; local Phase 2/3 engine commit SHAs alone are not portable recovery. `code/source_recovery_check.py` was actually exercised: 858 source files match the measured checkout bytes, executable modes and canonical Git blobs, excluding the machine-local `.venv` link. Public `.gitattributes` CRLF conversion for Windows scripts is honored. Keep rebuild separate from frozen replay, use a fresh task-owned path, and require safety/parity gates for any new binary identity.

```bash
set -euo pipefail
RAD_CASE=/srv/ai/work/rad/golden-swap-phase3/rebuild-UNIQUE
test ! -e "$RAD_CASE"
mkdir -p "$RAD_CASE/repos" "$RAD_CASE/inputs" "$RAD_CASE/builds"
gh repo clone Niko1221/Strata "$RAD_CASE/repos/strata" -- --no-checkout
git -C "$RAD_CASE/repos/strata" checkout --detach 6f32ec070f23ced9f50e704d854d775da52591ab
git -C "$RAD_CASE/repos/strata" apply --exclude=.venv "$PWD/patches/cumulative-from-original.diff"
gh api repos/ggml-org/llama.cpp/tarball/3cf03257f219afbe7334045ff7c6a06ac68c627d > "$RAD_CASE/inputs/ggml.tar.gz"
# Expected upstream archive SHA256 fbd160d892ea5aab531dff303c2f281fbcd496ba61ed858004fa913e546a9cb4.
mkdir "$RAD_CASE/repos/ggml"
tar -xzf "$RAD_CASE/inputs/ggml.tar.gz" -C "$RAD_CASE/repos/ggml" --strip-components=1
cmake -S "$RAD_CASE/repos/strata" -B "$RAD_CASE/builds/runtime" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DSTRATA_ENABLE_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89 \
  -DSTRATA_BUILD_TESTS=ON -DSTRATA_GGML_DIR="$RAD_CASE/repos/ggml"
cmake --build "$RAD_CASE/builds/runtime" -j 8
gcc -O3 -shared -fPIC code/fnv64.c -o "$RAD_CASE/builds/libfnv64.so"
```

Dependency bases, original model revision and ordinary settings are inherited and remain frozen. The measured binary was actually built; a source reconstruction check is distinct from rebuilding a second supposedly identical executable. No build output or model weights belong in Git. Irreplaceable binary tapes/journals remain local; gzip text evidence does not recover them. Artifact manifests state this recovery gap.

# Progress, ledger and publication evidence

`progress.json` is atomic; `progress.jsonl` and `attempt-ledger.jsonl` are append-only. `STATUS.md` is readable current state. Inspect a retained compressed log with `gzip -dc`. Verify complete text evidence with the root tools:

```bash
python3 /srv/ai/research/tools/archive_workspace.py verify-text --destination "$PWD/evidence/completed-text-v1"
```

Each gzip is a complete source file strictly smaller than10MiB; originals remain unchanged. The manifest lists omissions, source paths, bytes and hashes. Reports/configs/source stay readable. Tested reproduction/analysis paths and the final indexed audit are recorded in `completion-audit.json`; skipped or failed paths are not blanket PASS claims.

Four completed namespaces were packed and verified against originals: main/offline/development raw text, runner logs, isolated reproduction text and fixture text. `code/publish_text.py` records their exact pack/verification commands; it refuses to overwrite these namespaces. Raw binary journals/tapes are not in Git. The publication manifest and `artifact-manifest.json` state every non-text omission and the host-local recovery gap.

The root publication suite was actually run: 26 tests passed. The initial analysis field-name mismatch and source comparison of Git LF blobs with declared CRLF checkouts are retained, with the exact minimal repairs. No request was rerun to repair those analysis/reconstruction issues.

## Post-hoc chronology correction

Without inference, run `code/live_trajectory.py --output <fresh-output.json>` using the recorded NumPy environment, then `tests/chronology_regression.py`. The original analysis and outputs are retained under `corrections/publication-chronology-20261007/original/`. This exercises retained admission/layer journals, not new GPU requests. See the correction summary for unchanged timing-result hashes.
