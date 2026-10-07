# Exact bounded reproduction

The frozen binary/checkpoint, existing tapes, model backing and effective configuration are verified before replay. Replay never rebuilds, updates dependencies, changes ordinary serving or writes into prior campaigns. These commands use this host execution profile; external artifact recovery and the explicit source rebuild are recorded in `artifact-manifest.json` and `configs/dependencies.json`.

```bash
cd /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase2-20261007T093357Z
PY=/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python
$PY code/quick_status.py
$PY code/reproduce.py --prepare-only --task math-rational --arm ORACLE_IN_HISTORY_TC
$PY code/reproduce.py --task math-rational --arm ORACLE_IN_HISTORY_TC
```

Supported retained modes are `REPLAY_CURRENT`, `ORACLE_FULL`, `ORACLE_IN_HISTORY_TC`, `ORACLE_IN_LOGISTIC_TC`, `HISTORY_OFF`, and `LOGISTIC_OFF`. Use a development task for reproduction; do not accidentally create a fourth campaign attempt on a main task. The independent continuous-tail tape is `text-json-rfc8259`. Its public-source execution payload and token IDs regenerate into an explicit new directory with frozen-hash checks:

```bash
$PY code/independent_inputs.py --output-dir /srv/ai/work/rad/golden-swap-phase2/public-input-reproduction-UNIQUE
$PY code/reproduce.py --prepare-only --task text-json-rfc8259 --arm ORACLE_FULL \
  --input-dir /srv/ai/work/rad/golden-swap-phase2/public-input-reproduction-UNIQUE
```

The public excerpt and exact serializer/tokenizer recipe are durable source. Generated request payloads/IDs remain local/external under repository role policy. The original tape is irreplaceable; regenerated natural output is not promised identical. Every execution creates a fresh printed `REPRODUCTION_DIRECTORY`, refuses GPU/port conflict, caps startup plus saved warmup at180 seconds and request at240 seconds, validates complete fixed work and initial state, then stops only identity-checked owned processes. The original campaign clock is not reset. A later explicitly invoked reproduction has its own isolated600-second cap.

Offline single-point reproduction uses an explicitly separate output root and fails if the point already exists:

```bash
RAD_OFFLINE_OUTPUT_ROOT=/srv/ai/work/rad/golden-swap-phase2/offline-reproduction-UNIQUE \
  $PY code/offline_campaign.py --single-task math-rational --policy native --tc 1 --post 0 --threshold 0.5
```

This computes modeled demand/transfer accounting, never measured TG. The campaign evaluated each unchanged deterministic policy once per tape. Do not run `select.py` to retune the frozen operating point. All calibration comparisons and hashes are retained.

Analysis is read-only with respect to raw input and prior campaigns, but explicitly regenerates this campaign's derived result files. Run after owned GPU work stops:

```bash
$PY code/diagnose_phase1.py
$PY code/summarize.py
$PY code/protection_costs.py
$PY code/resources.py
$PY code/final_diagnostics.py
$PY code/render_report.py
```

The exact ordinary transaction byte partition and admission-generation linkage are asserted during regeneration. Unknown native completion/staging/target information is not zero. Prefix observation-span timing differs from native whole-decode timing; mandatory tail, drain and restoration remain charged to whole-run wall. Tested command outcomes and any repair are recorded in the attempt ledger and completion audit.

Source rebuild is an explicit separate operation. Use the retained cumulative source patch against the obtainable pinned upstream base, preserve the pinned ggml base (no dependency patch was required), and follow the recorded configure/build commands in `configs/dependencies.json`. Do not use preliminary `implement.py` as the authoritative final source reconstruction: the checked cumulative patch preserves subsequent bounded active-key bookkeeping repairs. A newly rebuilt binary must be treated as a new identity and must pass semantic/safety checks before timing; no rebuilt hash is assumed to match the measured executable.

## Explicit source acquisition and build

Use a fresh task-owned external namespace. The public pinned bases were verified with `gh api`; cumulative-patch application reproduced the entire source tree, and every ggml source file matched the pinned official archive. The measured runtime was built with these flags; this source-recovery check did not perform a second fresh build or repeat a main point.

```bash
set -euo pipefail
RAD_CASE=/srv/ai/work/rad/golden-swap-phase2/rebuild-UNIQUE
test ! -e "$RAD_CASE"
mkdir -p "$RAD_CASE/repos" "$RAD_CASE/inputs" "$RAD_CASE/builds"
gh repo clone Niko1221/Strata "$RAD_CASE/repos/strata" -- --no-checkout
git -C "$RAD_CASE/repos/strata" checkout --detach 6f32ec070f23ced9f50e704d854d775da52591ab
git -C "$RAD_CASE/repos/strata" apply "$PWD/patches/cumulative-from-original.diff"
gh api repos/ggml-org/llama.cpp/tarball/3cf03257f219afbe7334045ff7c6a06ac68c627d > "$RAD_CASE/inputs/ggml.tar.gz"
# SHA256 must be fbd160d892ea5aab531dff303c2f281fbcd496ba61ed858004fa913e546a9cb4
mkdir "$RAD_CASE/repos/ggml"
tar -xzf "$RAD_CASE/inputs/ggml.tar.gz" -C "$RAD_CASE/repos/ggml" --strip-components=1
cmake -S "$RAD_CASE/repos/strata" -B "$RAD_CASE/builds/runtime" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DSTRATA_ENABLE_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=89 -DSTRATA_BUILD_TESTS=ON \
  -DSTRATA_GGML_DIR="$RAD_CASE/repos/ggml"
cmake --build "$RAD_CASE/builds/runtime" -j 8
gcc -O3 -shared -fPIC code/fnv64.c -o "$RAD_CASE/builds/libfnv64.so"
g++ -O3 -std=c++20 -pthread -I"$RAD_CASE/repos/strata/include" \
  -I/usr/local/cuda/include code/offline.cpp -L/usr/local/cuda/lib64 \
  -Wl,-rpath,/usr/local/cuda/lib64 -lcudart -o "$RAD_CASE/builds/offline"
```

Do not silently substitute another binary into the frozen identity manifest. A rebuilt executable requires a separate identity/configuration, safety verification and explicitly separate measurement namespace. The original measured binary remains the retained replay default. Configure/build versions, pinned Python dependencies, source/checkpoint hashes and actual configure commands are in `configs/dependencies.json`. Large backing weights and tapes must exist at the recorded manifest locations or be explicitly restored/rebased; no automatic weight relocation occurs.

Artifact inventory excludes its own `storage-manifest-*.log` bookkeeping logs to avoid self-referential hashes. Those logs remain external. All scientific engine/request/tape/journal evidence is inventoried. Exact irreplaceable observations have no identified independent backup; this local-host-loss recovery gap is explicitly retained.

The exact cumulative snapshot includes an inherited host-only `.venv` symlink entry. It is metadata, contains no environment payload and is not required by the explicit CMake build. Exact tree recovery preserves it; a portable rebuild may exclude that entry with `git apply --exclude=.venv` and use a separately provisioned environment.
