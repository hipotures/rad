# Q4 live oracle residency laboratory

The completed fixed-work experiment tests physical residency feasibility with future knowledge, not learned prediction or ordinary generated quality. Read [report.md](report.md), [summary.json](summary.json), and the three phase reports first.

The unchanged Q4/100us serving baseline remains the real-use configuration. Its normal launchers are under `launchers/control/`. Experimental capture/replay commands are separate under `launchers/experimental/`; they verify the frozen identities, refuse conflicts, have finite timeouts and create a new isolated reproduction campaign.

## Recompute preserved evidence

Run from this directory. These are CPU-only analysis commands; use them after GPU inference is finished.

```bash
PY=/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python
timeout 900s "$PY" scripts/refresh_audits.py
timeout 60s "$PY" scripts/extra_summary.py
timeout 30s "$PY" scripts/render_report.py
timeout 600s "$PY" scripts/inventory.py
```

The preserved residual-miss and distinct persistent-use analyses can be recomputed with `scripts/residual_misses.py LABEL` and `scripts/persistent_lifetimes.py LABEL`. They operate only on transaction logs; they do not modify runtime behavior.

Plotting is isolated from the frozen runtime environment:

```bash
python3 -m venv .analysis-venv
.analysis-venv/bin/python -m pip install -r requirements-plotting.txt
timeout 60s .analysis-venv/bin/python scripts/plots.py
```

## Artifacts and interpretation

- `raw/`: every request, including superseded pilots, failures and the retained timing anomaly.
- `tapes/`: schema, fixed input/window/route/mixture/QSA data and initial-state sidecars.
- `analysis/`: count/byte/ownership audits, interval timing, selected numerical samples, hardware telemetry, persistent lifetimes and file-hash inventory.
- `patches/`, `src/`, `builds/`, `git/`: isolated locally committed source, exact cumulative diffs, binaries, build commands and provenance.
- `configs/`, `inputs/`, `phase-a/`, `phase-b/`, `phase-c/`, `tests/`: fixed protocol, inputs, feasibility models, final matrix and safety evidence.
- `ledger.jsonl` and `DECISIONS.md`: failures, protocol repairs, exclusions and bounded decisions.

Large tapes, raw records, builds and source clones are retained on disk and intentionally Git-ignored. The evidence inventory records hashes and sizes. The tracked cumulative patch reproduces the experimental source from the frozen base without fetching a moving upstream. Build commands are in the identity-linked `git/builds/` logs, which are retained and inventoried even when Git-ignored.

The primary table reports replay-equivalent output tokens/s. Forced emission and MTP equality are part of the workload contract, not a correctness or quality claim. Real expert math and copy/publication safety are separately tested. Exact KV DMA service at streamed contexts and finite tape-end privileges remain explicit limitations.
