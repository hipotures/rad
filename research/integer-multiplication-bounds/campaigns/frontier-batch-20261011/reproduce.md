# Reproduction

Prerequisites: Linux, `uv`, Git, GitHub access for `./run.sh setup`, g++
(C++17), Boost headers, at least 60 GiB free under the work root. A CUDA GPU is
optional (job 3 falls back to the CPU).

```bash
cd research/integer-multiplication-bounds/campaigns/frontier-batch-20261011
export RAD_WORK_ROOT=<task-owned directory outside the checkout>
./run.sh setup
./run.sh 1
./run.sh 2          # JOBS=<n> TIMEOUT_MIN=<m> optional
./run.sh 3
./pack.sh           # gzip copies of compact text evidence into evidence/<run-id>
```

Expected checks:
- Job 1 status `MODEL_CONSISTENT`: whole hosting and the two-register control
  equal the original program in every case.
- Job 3 `e8_price_validation.matches_reference` is true.
- Job 2: every replay has a record in `records/` and the run has `SUMMARY.json`.
  Pass/fail of a replay is a measured outcome, not a harness error.

Pinned versions: Python 3.14 in a uv venv with `configs/requirements.txt`;
upstream commits in `configs/job2-replays.json`; the #370 producer at
`b7fe9cdf2da009c947ff6b334c562bc190b30373`.

Post-hoc ledger of the hosted templates (agent analysis, about 20 s, no upstream code):

```bash
python3 code/job2_hosting_ledger.py --run "$RAD_WORK_ROOT/runs/<UTC>-job2" \
  --out "$RAD_WORK_ROOT/runs/<UTC>-job2/analysis/hosting-ledger.json"
```

Follow-up job 4 (repair replays; one documented deviation applied in memory, worktrees unmodified):

```bash
./run.sh 4          # TIMEOUT_MIN=<m> optional
```

Expected check: each record has `eligible: true` (the package differs from its manifest only by the absent
`.gitattributes`) and a `# JOB4 DEVIATION ... remaining_equal=True` line in its log.
