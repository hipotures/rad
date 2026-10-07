# Reproduce Golden Swap Phase 4 evidence

Run from the RaD repository root. The completed campaign is immutable for live
attempts: do not invoke its historical matrix or extend its clock. Analysis and
restoration create fresh external namespaces and require Python3 plus NumPy;
future live preparation additionally requires psutil, the frozen model, original
tape/sidecar/reference observations, CUDA runtime, two4090s and the exact binary.
No automatic update, runtime rebuild, launcher modification or dependency push occurs.
The frozen small FNV checksum helper is copied with hash verification into a
future reproducer; its authored C source and explicit build command are retained.

On the original host, the Python environment exercised was
`/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python`.
Use a compatible user-space environment elsewhere and record its identity.

## Restore journals and regenerate results without inference

Choose fresh output paths. The gzip exports recover all original admission,
layer, native, lifecycle, publication, producer and GPU journal bytes. Each
restored original is checked against its SHA256. Historical PID metadata is
read-only evidence and never process-control authority.

```bash
RAD_CAMPAIGN=iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase4-publication-wait-20261007T184009Z
RAD_REPRO=/srv/ai/work/rad/golden-swap-phase4-publication-wait/repro-UNIQUE
python3 "$RAD_CAMPAIGN/code/restore_evidence.py" --output "$RAD_REPRO/raw"
python3 "$RAD_CAMPAIGN/code/analyze.py" --raw-root "$RAD_REPRO/raw" --output "$RAD_REPRO/results"
cmp "$RAD_REPRO/results/analysis.json" "$RAD_CAMPAIGN/results/final/analysis.json"
cmp "$RAD_REPRO/results/requests.csv" "$RAD_CAMPAIGN/results/final/requests.csv"
python3 "$RAD_CAMPAIGN/code/render_report.py" --output "$RAD_REPRO/report.md"
python3 "$RAD_CAMPAIGN/tests/graph_fixture.py"
```

All eight point journals and all four final compact result files were actually
restored/regenerated from committed-format gzip copies with exact equality.
Report rendering was exercised. This does not recover the full natural tape or
numerical activation journals; [artifact-manifest.json](artifact-manifest.json)
states that recovery gap. No GPU request is needed for result regeneration.

## Frozen plan and Phase 3 correction

```bash
python3 "$RAD_CAMPAIGN/code/check_plan.py" --local-inputs
python3 iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase3-20261007T150955Z/tests/chronology_regression.py
```

The plan check validates the preserved planning contract and local frozen inputs;
its `experiment_started:false` field describes its own check scope, not today's
campaign status. Actual execution clock and version identities are in runs/.
It refuses GPU conflicts during input hashing. The correction's standalone
live_trajectory.py can write a fresh diagnostic from retained Phase3 journals;
old Phase3 full regeneration writers must not be invoked in place. No Phase3
GPU rerun was needed.

## Source recovery and explicit build

Use GitHub CLI for public dependency acquisition. Select a fresh external root.
The tracked cumulative patch reconstructs all experiment source from the public
0.1.39 base, without depending on a local-only derivative commit.

```bash
gh repo clone Niko1221/Strata "$RAD_REPRO/public-strata" -- --no-checkout
python3 "$RAD_CAMPAIGN/code/reproduce_source.py" \
  --clone-source "$RAD_REPRO/public-strata" --output "$RAD_REPRO/runtime"
gh api repos/ggml-org/llama.cpp/tarball/3cf03257f219afbe7334045ff7c6a06ac68c627d > "$RAD_REPRO/ggml.tar.gz"
# Pinned archive SHA256: fbd160d892ea5aab531dff303c2f281fbcd496ba61ed858004fa913e546a9cb4.
mkdir "$RAD_REPRO/ggml"
tar -xzf "$RAD_REPRO/ggml.tar.gz" -C "$RAD_REPRO/ggml" --strip-components=1
cmake -S "$RAD_REPRO/runtime" -B "$RAD_REPRO/build" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DSTRATA_ENABLE_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89 \
  -DSTRATA_BUILD_TESTS=ON -DSTRATA_GGML_DIR="$RAD_REPRO/ggml"
cmake --build "$RAD_REPRO/build" -j 8
```

Source recovery was tested using the local clone as acquisition source and
checking the obtainable public base plus patch against final tracked tree
`14c6ad63924d2f3916526bf55a4c3938978ac890`. Public download was inherited pinned
provenance, not redownloaded during this goal. The measured binary was built and
fixtures executed; a second rebuild was not performed. Exact binary bytes may
vary on another toolchain. A new binary requires new identity/safety gates;
never substitute it for the frozen binary in old timing records.

## Retained replay modes in a separate namespace

The reproducer checks exact binary/source/config/model/checkpoint/tape identities,
GPU and port conflicts, then prepares an isolated copy of the runner and a new
30-minute clock. It never edits the completed campaign. Without `--execute` it
only prepares and verifies; this bounded path was tested for CONTROL, including
isolated runner import and native FNV tape validation. Both
CONTROL and TRACE runner paths were exercised in the six actual measurements.
An additional execution of this wrapper was not performed under the attempt cap.

```bash
python3 "$RAD_CAMPAIGN/code/reproduce_replay.py" \
  --output "$RAD_REPRO/prepare-control" --arm CONTROL
# A future separately authorized reproduction, fresh output only:
python3 "$RAD_CAMPAIGN/code/reproduce_replay.py" \
  --output "$RAD_REPRO/live-trace" --arm TRACE --execute
```

The wrapper allows one measured attempt, 440s outer request budget, finite
startup/warmup/request timeouts, flushed heartbeats and identity-checked owned
process cleanup. It does not launch inference during preparation. It preserves
failed/slow results. It is host-specific until artifact paths are explicitly
relocated in a new manifest. STRATA_VERIFY_PROFILE must be unset, including no
value0; scheduling-changing profiling is forbidden. No extra replay was run in
this completed campaign merely to test a launcher.

## Progress, ledger and publication

```bash
cat "$RAD_CAMPAIGN/STATUS.md"
python3 -m json.tool "$RAD_CAMPAIGN/progress.json"
cat "$RAD_CAMPAIGN/runs/20261007T194914Z/attempt-ledger.jsonl"
python3 tools/archive_workspace.py verify-text --destination "$RAD_CAMPAIGN/evidence/requests-20261007T194914Z"
python3 tools/archive_workspace.py verify-text --destination "$RAD_CAMPAIGN/evidence/journals-20261007T194914Z"
```

Completed text and one whole export per original journal are gzip-published;
combined TRACE exports above10MiB are explicitly skipped, not chunked. A scoped
one-time evidence budget is [configs/evidence-budget.json](configs/evidence-budget.json).
The final staged audit used that exact indexed decision. Normal authored source,
configs and compact report remain readable. Source patches retain upstream
context whitespace. See completion-audit.json for actual tests, deviations,
missing graph/clock coverage, cleanup, elapsed time and publication status.
