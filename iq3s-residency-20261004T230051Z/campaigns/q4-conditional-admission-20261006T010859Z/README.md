# Q4 conditional admission laboratory

This directory is a separate continuation of the immutable Q4 residency-v2 campaign. Read `report.md`, `STATUS.json` and `DECISIONS.md` for the final recommendation and protocol changes. No normal user launcher is replaced.

## Retained source and model

Control: `../../builds/control/strata`, source `6f32ec070f23ced9f50e704d854d775da52591ab`.
Conditional: `builds/conditional-v1/strata`, source `0266e540087acb98acd183546edeab3164aee8fd`.
Exact binary hashes, CUDA/compiler/options, local commits and model manifests are in `git/`, `configs/` and `patches/`. Source worktrees are under `src/`; useful research code is under `scripts/` and `tests/`, not `/tmp`. All weights remain in their existing model directories.

## Reproduce the analysis without inference

Use the preserved control Python environment:

```bash
PY=/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python
"$PY" scripts/analyze_live.py
"$PY" scripts/live_costs.py
"$PY" scripts/analyze_ablations.py
"$PY" scripts/render_report.py
.plotvenv/bin/python scripts/plot_results.py
```

These scripts read the saved raw requests and traces; they do not fit a new model, choose a different threshold, change weights, or start an engine. `analyze_live.py` regenerates the raw-derived summary and temporarily sets its recommendation to pending; `render_report.py` then restores the frozen `decision.json` recommendation. Running the scripts after completion updates this campaign's derived artifacts, so archive its existing artifact manifest first if preserving a bit-for-bit report snapshot.

Training and holdout scripts are retained for inspection. Do not rerun them over the completed campaign: overwrite guards preserve the original frozen checkpoints and decisions. Task-level development/calibration/holdout splits were made before fitting. The logistic checkpoint threshold is frozen at 0.12; no live refit is performed.

## Reproduce inference after completion

Each launcher supports `--check`, `--host` and `--port`. The reproducer is enabled only after campaign completion or the original absolute deadline. It uses one fresh server and one fixed warmup per measured request, serially, with no automatic retries.

```bash
launchers/control/reproduce.sh --profile 32k --port 18144
launchers/conditional/reproduce.sh --profile 32k --port 18144
```

Run only one command at a time. Additional reproductions are user-invoked runs stored separately, not additions to the completed three-repeat research matrix.

## Raw evidence

- `raw/`: 18 primary fixed-4096 requests, plus the separate exploratory screen.
- `independent/`: whole held-out application tasks, separate from context benchmarks.
- `traces/`: Phase A and training-data diagnostic events/demand/native changes.
- `diagnostics/`: matched ablations and the one candidate-OFF timing guard.
- `tests/`: native suite, real CUDA scheduler fixture, byte checks and repairs.
- `manual/`: six advertised launcher smoke checks.
- `analysis/`: paired IDs/trajectories, exact routing accounting, hardware phases, costs, funnels and plots.

Unknown metrics remain unknown. Offline transaction attribution is not a counterfactual native-adaptation oracle. Diagnostic full traces/readbacks never enter headline timing runs. The artifact manifest hashes raw data after all owned processes stop.
