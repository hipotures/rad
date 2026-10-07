# Inspect, regenerate and validate the Atlas

These commands run static serving or CPU analysis. They never invoke Strata, record a new tape, fit a predictor or update a serving configuration. Run them from this review directory unless stated otherwise. A portable Git clone contains the complete selected browser representation; raw binary inputs have the recovery limitations in [artifact-manifest.json](artifact-manifest.json).

## Serve the published evidence

```bash
python3 code/serve.py --host 0.0.0.0 --port 8765
```

The server refuses an occupied port, prints discovered IPv4 URLs and records its command, PID, process start ticks and UTC in ignored `server-status.json`. It serves the local Plotly distribution and complete gzip JSON assets with the appropriate MIME type and Content-Encoding. Test with `curl -I http://127.0.0.1:8765/` and open its printed LAN URL from a desktop browser. No original model, tape or analysis environment is required. Do not start a second instance on the already running campaign port. A historical PID receipt does not authorize stopping an unrelated live process.

## Dependencies for analysis

Use a new external work directory; these examples use a shell variable without changing HOME or any serving setting.

```bash
atlas_work=/srv/ai/work/rad/golden-swap-experiment-atlas/reproduction-new
mkdir -p "$atlas_work"
python3 -m venv "$atlas_work/envs/atlas"
"$atlas_work/envs/atlas/bin/pip" install numpy==2.3.3
export RAD_WORK_ROOT="$atlas_work"
```

Python 3.10+ is required. The recorded environment used Python 3.14.4 and NumPy 2.3.3. Serving uses only the standard library. Browser validation additionally used Playwright 1.55.0 and system Chromium 154.0.8037.97; installing Playwright does not require downloading a browser if a compatible local Chromium is available.

## Bounded exact regeneration: exercised

The retained receipt [reproduction-validation.json](results/reproduction-validation.json) documents a fresh regeneration of Phase 2 math-inventory block 1, history+TC. It verified required original sizes/SHA256, reproduced all **48 normalized layer files byte-for-byte** and reproduced the full run summary exactly. The wrapper refuses an existing output directory and enforces a 240-second subprocess timeout.

```bash
"$atlas_work/envs/atlas/bin/python" code/reproduce.py --output "$atlas_work/derived/bounded-new"
```

This check requires its original immutable tape/journals at the manifest locations. If those bytes are unavailable, the command reports the missing input; it does not regenerate a natural capture or substitute another run. Full binary originals are intentionally absent from Git.

For inputs moved to another host, the lower-level parser supports recorded-prefix relocation. The frozen shared profile can be supplied with `--profile`; otherwise the lossless retained ranked-pair snapshot is used. The Q4 blob sizes come from the small hashed fixture, without loading model weights.

```bash
"$atlas_work/envs/atlas/bin/python" code/build_atlas.py --only golden-swap-phase2--math-inventory-block1-ORACLE_IN_HISTORY_TC --output "$atlas_work/derived/relocated-new" --map-path /srv/ai/research=/replacement/rad --map-path /srv/ai/work/rad=/replacement/work
```

A relocation changes absolute provenance strings, so compare normalized service/lifecycle values rather than promising the unchanged provenance-containing summary hash. The strict bounded wrapper above deliberately tests the original manifest paths.

## Full derivation: frozen selection

The readable selection document points to the complete configuration in `evidence/analysis-detail-v1`; the parser verifies its uncompressed SHA256 before loading it. Full layer-audit and reference window-series records also have complete gzip copies there, with small readable receipts in `results/`.

Do this in a **working copy of the review** if changing published metadata or validation receipts. Keep completed original evidence and completed derivation directories immutable. The supplied `configs/source-selection.json` freezes identity selection; do not choose a new subset from favorable timings. `catalog.py` is the original inventory builder, not a requirement to replace that selection.

```bash
"$atlas_work/envs/atlas/bin/python" code/build_atlas.py --output "$atlas_work/derived/browser-v1"
"$atlas_work/envs/atlas/bin/python" code/predictor.py --output "$atlas_work/derived/browser-v1"
"$atlas_work/envs/atlas/bin/python" code/finish_data.py
"$atlas_work/envs/atlas/bin/python" code/visual_findings.py --data-root "$atlas_work/derived/browser-v1"
"$atlas_work/envs/atlas/bin/python" code/resident_comparisons.py --data-root "$atlas_work/derived/browser-v1"
"$atlas_work/envs/atlas/bin/python" code/compact_assets.py --source "$atlas_work/derived/browser-v1" --destination "$atlas_work/derived/browser-compact-new"
```

`build_atlas.py` reads the existing counter snapshot from its retained archive if the historical external snapshot is absent. It checks source-byte provenance and retains exceptions in a separate failures directory. `--resume` is only for a task-owned interrupted derivation and checks original source hashes before reuse. The full original run took approximately 25 minutes of CPU analysis; it is not a timing benchmark. The predictor stage recomputes weighted empirical ROC from saved predictions, without model inference or retraining. Compaction validates exact service-row round trips and refuses an existing destination.

From the repository root, package the new complete text files into a fresh evidence directory:

```bash
python3 tools/archive_workspace.py pack-text --source "$atlas_work/derived/browser-compact-new" --destination iq3s-residency-20261004T230051Z/reviews/golden-swap-experiment-atlas-20261007T215621Z/evidence/reproduction-new
```

The checked-in site intentionally points to the frozen `browser-v1` namespace. A newly published data version needs explicit URL changes and another validation, not replacement of those original gzip files. Each complete gzip remains strictly below 10 MiB; no binary capture or large source tree is included. The Plotly library manifest pins version, complete-file hashes, source URL and license.

Full regenerated row-level validation/reference JSON should use the same `pack-text` workflow into a **fresh** analysis-detail namespace. Keep the complete originals outside Git, publish their whole gzip copies, and retain readable count/hash references. The publication validator rejects ordinary JSON with nested arrays over its row limit; renaming or weakening that guard is not part of this workflow.

## Checks

```bash
"$atlas_work/envs/atlas/bin/python" code/test_parsers.py
"$atlas_work/envs/atlas/bin/python" code/validate.py --data-root evidence/browser-v1
node --check site/app.js
```

The full data check validates all selected rows, partitions and generation use totals. Its seven original-record lifecycle spot checks additionally require original Phase 1/2 journals. The retained validation receipt records those checks as actually passed; a clone without originals cannot claim to repeat them.

Optional browser validation through the running HTTP server:

```bash
"$atlas_work/envs/atlas/bin/pip" install playwright==1.55.0
"$atlas_work/envs/atlas/bin/python" code/browser_validate.py --url http://127.0.0.1:8765/ --chromium /snap/bin/chromium
```

The validator uses the exact published representation when the uncompressed local reference is absent. It visits all ten pages, changes selectors, checks linked zoom/pan/hover, same-tape current/full-oracle comparison, exact decoding, provenance and PNG/SVG export. Chromium is launched with GPU rendering disabled; no GPU inference occurs. Screenshots and receipts are written in the working review, so preserve earlier receipts before a new validation.

The archive checker was tested with 27 repository tests. Before publication, stage only reviewed task paths and use the indexed scoped evidence decision:

```bash
python3 -m unittest discover -s tools -p test_archive_workspace.py
python3 tools/archive_workspace.py audit --staged-only --budget-policy iq3s-residency-20261004T230051Z/reviews/golden-swap-experiment-atlas-20261007T215621Z/configs/evidence-budget.json
```

Inspect `progress.json`, `STATUS.md`, the append-only `progress.jsonl`, validation receipts and `completion-audit.json` for the actual exercised scope. No old campaign regeneration command is run in place.
