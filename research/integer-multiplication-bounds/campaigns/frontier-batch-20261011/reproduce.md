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
./run.sh 4          # TIMEOUT_MIN=<m>, ONLY=<pr,pr> optional
```

Follow-up job 5 (fresh replays of #484 and #495-#502; repair attempt only under job 4's condition):

```bash
./run.sh test5      # synthetic smoke test of the harness, under a second, no network
./run.sh 5          # TIMEOUT_MIN=<m> (default 180), ONLY=<pr,pr> optional
```

Expected checks: `SUMMARY.json` has 9 rows and `harness_errors: 0`. Each
`checks/pr-N.json` states whether the claimed value (the title kappa, or #484's
configured b) occurs exactly in the passing attempt's outputs. A repair attempt
appears only under `repair/`, with its own worktree, output directory and record.

Post-hoc ledger of job 5's templates (agent analysis; job 2's checks plus #471's 9-field slots, replica-pooled
pieces and a per-call owner summary). Pass the job 4 runs as well to include #471:

```bash
python3 code/job5_hosting_ledger.py --run "$RAD_WORK_ROOT/runs/<UTC>-job5" \
  --run "$RAD_WORK_ROOT/runs/20261011T211954Z-job4" --run "$RAD_WORK_ROOT/runs/20261011T213109Z-job4" \
  --out "$RAD_WORK_ROOT/runs/<UTC>-job5/analysis/hosting-ledger.json"
```

Follow-up job 6 (build the #523 and #527 words, then search frame timings until the hour budget ends):

```bash
./run.sh test6      # smoke test, about 30 s; uses job 5's #502 word for the cascade check when present
./run.sh 6 7.5      # total wall-clock budget in hours; TIMEOUT_MIN caps the build stage (default 120,
                    # at most half the budget); JOBS sets the number of annealing processes (default cores - 1)
```

Console during the run: every 5 min of the build stage, the last line of each package's own log; then every
10 min of the search, one row per word with start Phi, best Phi so far, gain (% of local climbs) and moves tried.
The control word (job 5's #502) should stay at gain 0.

Expected checks: `job6-build.log` ends with both replays passed (their claimed kappa exact). `search/WORDS.json`
lists every distinct built word; `status: ok` means this model's replay reproduces that word's own
`local_profile`. `search/SUMMARY.json` gives, per word, the start and best first-order Phi of the paid climbs.
`search/BEST-<word>.json` holds the best timing (one canonical frame basis per A/B gate), which `validate_state`
re-checks from scratch. A positive gain is only a candidate: the agent then re-emits the word and runs the
package's own local replay, Clifford phase lowering, owner audit and moment engines before any value is stated.

Follow-up job 7 (gate orders and frame timings of the words job 6 built; needs a job 6 run, nothing is rebuilt):

```bash
./run.sh test7      # smoke test, about 20 s; uses job 6's #527 word for the exact-replay check when present
./run.sh 7 7.5      # wall-clock budget in hours; JOBS sets the number of annealing processes (default cores - 1)
```

Console: every 10 min one row per word (start Phi, best Phi, gain, moves tried, accepted gate moves). The newest
words (#527, #523) get two annealer slots per round. Expected checks: `search/SUMMARY.json` (or, if the run is
stopped, `job7_reorder_search.py --out <run>/search --summarize`). Every final record has
`exact_replay_checked: true`: its order passed the pairwise commutation check and an exact rational replay of
phases A and B. `BEST-<word>.json` holds the best order (`order_a_best`, `order_b_best`, original gate indices) and
one frame basis per original gate. A gain is a candidate only until the package's own checks pass on the re-emitted
word.

For job 4, expected check: each record has `eligible: true` (the package differs from its manifest only by the absent
`.gitattributes`) and a `# JOB4 DEVIATION ... remaining_equal=True` line in its log.
