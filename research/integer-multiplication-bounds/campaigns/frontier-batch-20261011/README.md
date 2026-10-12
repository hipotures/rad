# Frontier batch, 2026-10-11

Status: **complete (2026-10-11).** All three jobs ran on the shared host; see
the [results report](report.md). In brief:
- 34 of 39 pinned claims reproduce. The 5 failures are integrity-check
  failures of one author's browser-uploaded packages.
- The follow-up job 4 reproduced those 5 packages when the one absent
  manifest file was tolerated. #493 (1.30353e-3) is therefore the top claim
  without cross-copy, and its binding complex input (#471) reproduces.
- Every cross-copy claim splits 22-34% of its hosted residuals across two
  copies, and job 1 shows that a split is not a program of the fixed local
  word under single-stream registers. The author of #448, #480 and #494
  accepted this and retitled the three as "not established"
  ([replies](upstream-comments/README.md#replies-checked-2026-10-11-2140-utc)).
- Only E8 (and implausibly Leech) can drive #370's template.

Follow-up **job 5** replayed the nine frontier packages opened after job 2
was pinned: #484 and #495-#502, at heads pinned 2026-10-11 21:54 UTC
([report section 6](report.md#6-fresh-replays-of-the-newer-frontier-job-5)).
- 8 of 9 pass with the exact claimed value. #498 needs job 4's
  `.gitattributes` repair.
- #502 at 1.343518e-3 is the top reproduced claim without cross-copy. It is
  conditional on #484's Lemma A and Lemma G.
- #501 claims the same value, but it fails from fresh sources: its frame map
  pins a #484 source word that six identical builds here do not produce.
- Our ledger finds the hosting clean, including #496's cross-replica pooling
  and #471's complex template.

Follow-up **job 6** (2026-10-12) moved from verification to search
([report section 7](report.md#7-where-the-complex-cost-sits-agent-2026-10-12)).
- The asynchronous whole-owner allocation of the newest claims is already solver-optimal. It governs only 4.7% of
  the first-order complex cost; 95% sits in the local word, which is repeated 72 times.
- #523 and #527 reproduce exactly from fresh sources. At 1.467289e-3, #527 (a draft) is the highest claim
  reproduced here.
- 13 billion annealing moves over 5.3 h found no cheaper frame timing for the #514, #522, #523 or #527 words.
  Frame retiming with a fixed gate sequence is exhausted in this lineage.

See [GOAL.md](GOAL.md) for the brief and completion criteria.

This campaign continues the
[upstream frontier inventory](../../runs/20261011T1916Z-upstream-frontier-inventory/report.md)
and the
[mechanism comparison](../../runs/20261011T1945Z-upstream-mechanism-comparison/report.md).

## How to run (operator)

Run from this directory, on the shared host, one job after another:

```bash
export RAD_WORK_ROOT=/srv/ai/work/rad/integer-multiplication-bounds/frontier-batch-20261011
./run.sh setup     # once: venv, upstream clone, pinned commits, preflight of all jobs
./run.sh 1         # about 1 minute
./run.sh 2         # about 1-3 hours, uses all cores
./run.sh 3         # about 2 minutes, CPU + one GPU
./run.sh 4         # follow-up: repair replays of 5 packages, about 30 minutes
./run.sh 5         # follow-up: fresh replays of the 9 newer frontier packages, about 1 hour
./run.sh status
```

- **Separate work root.** `RAD_WORK_ROOT` must be outside the Git checkout.
  Each job writes a fresh `runs/<UTC>-job<N>/` there and never removes earlier
  runs.
- **Fast preflight.** Each job checks its environment, pinned commits,
  compiler, Boost and disk space first, and stops within seconds if something
  is missing. After the preflight it always runs to completion. A failing part
  (for example a replay) is recorded, and the job continues.
- **Job 2 parallelism.** `JOBS=<n>` overrides the number of parallel replays
  (default: cores - 1). `TIMEOUT_MIN=<m>` sets the per-replay timeout (default
  150).
- **Resuming job 2.** If job 2 is interrupted, rerun it with the same `--work`
  directory to continue. That is an advanced use; by default a rerun creates a
  fresh run.
- **Packing results.** `./pack.sh` later packs the compact text evidence of
  finished runs into `evidence/<run-id>` as gzip copies. It is local only and
  never stages, commits or pushes.

## Jobs

| Job | Question | Code | Hardware |
|---|---|---|---|
| 1 | Is cross-copy hosting (#448) a program of the fixed local word when each register is bound to one stream? | [job1_stream_model.py](code/job1_stream_model.py) | 1 core, seconds |
| 2 | Do 39 pinned frontier claims reproduce from a fresh checkout with their authors' own verifiers? | [job2_replays.py](code/job2_replays.py), [config](configs/job2-replays.json) | all cores; replays are single-threaded and run concurrently |
| 3 | Can any other root system or lattice replace E8 in #370's five-stage bit template? | [job3_lattice_screen.py](code/job3_lattice_screen.py) | CPU; the exact Leech span check uses a free GPU, else CPU |
| 5 (follow-up) | Do the 9 frontier claims opened after job 2's pinning (#484, #495-#502) reproduce with their authors' verifiers? Which complex supplier b does each bind to? A repair attempt runs only under job 4's condition (#498 lists an absent `.gitattributes`). | [job5_replays.py](code/job5_replays.py), [config](configs/job5-replays.json), [smoke test](code/test_job5_smoke.py) | 9 replays in parallel |
| 6 (follow-up) | Can a different frame timing of the newest complex words (#514/#522/#523/#527, built fresh) lower their paid recursive cost Phi, keeping every gate, coefficient and fixed frame? | [job6_retime_search.py](code/job6_retime_search.py), [config](configs/job6-builds.json), [smoke test](code/test_job6_smoke.py) | 2 builds in parallel, then all cores annealing until the hour budget ends |
| 4 (follow-up) | Do #471/#476/#478/#483/#492 reproduce when the one missing manifest key (`.gitattributes`) is tolerated? #471's complex b caps #493 and feeds #473/#490/#491. | [job4_repair_replays.py](code/job4_repair_replays.py), [job4_launcher.py](code/job4_launcher.py) | 5 cores, one replay each |

## Pre-run smoke tests (agent, 2026-10-11)

These smoke tests are not the results; the operator's runs are authoritative.

- **Job 1.** Full run took 9.6 s. Whole hosting equalled the original program
  in every case. 0 of 152 single-register cross-copy programs did. The
  two-register control (a different word with one more helper) was valid.
- **Job 2.** 12 of the 39 replays were exercised through the harness: #376,
  #433, #434, #436, #438, #439, #442, #444, #461, #464, #465 and #493 passed.
  8 of them ran concurrently in 6.5 min, single-threaded each, with peak RSS up
  to 0.7 GB. Most of them reproduced the title kappa exactly, the rest to the
  title's rounding. The large r715/r740 chains were not pre-run.
- **Job 3.** The quick screen (without Leech) took 2.6 s. Our price function
  reproduces #370's R865 saving exactly. Leech: the F_2 span of the correction
  masks has rank 2599, confirmed by an exact check of all 98,280 rows on the GPU
  (38 s in total).

- **Job 5** (2026-10-11, before the operator run):
  - `code/test_job5_smoke.py` passes 12 of 12 checks on a synthetic repository. They cover the as-is pass, the
    `.gitattributes` repair, a declined repair, a computational failure, exact versus 1e-19-close decimals,
    `a/10^k` strings, JSON numbers parsed exactly, and the `{BOOST}` substitution.
  - On the real packages, #498 failed as-is at its integrity assertion, as predicted. Its repair attempt passed
    in 225 s with the exact title kappa, and its `complex_lower` is #471's b. #496 passed as-is in 522 s with the
    substituted `--boost-include`, exact title kappa, and `complex_lower` = 133385415620840915601/10^23 (its own
    pooled supplier). The operator's run remains authoritative.
  - `code/job5_hosting_ledger.py` on the job 4 outputs now parses #471's complex template, the one template
    job 2's ledger could not read: 43,120 slots, 0 cross-copy, 0 overlaps, windows re-derived 12 of 12.

- **Job 6** (2026-10-12, before the operator run):
  - `code/test_job6_smoke.py` passes 12 of 12 checks. On two toy words, the replay reproduces hand-computed
    profiles and the annealer's best equals the brute-force optimum over all 16^4 timings. `validate_state` rejects
    a decreasing frame and a target that leaves its level before the centres phase. 1,687 random cascaded moves on
    #502's word keep every chain admissible, and incremental Phi equals from-scratch Phi.
  - A 108 s search over the 7 distinct words of job 5 shows that the model reproduces every word's own profile.
    Unretimed #484-lineage words drop by 180-252 Phi; one reaches 23,249.83, the value of the retimed #495 word.
    The retimed words (#495, #502) gain nothing. The operator's run remains authoritative.

## Layout

- `run.sh`, `pack.sh`: operator entry points
- `code/`: job sources
- `configs/`: pinned replays, Python requirements
- `evidence/`: created by `pack.sh` after the runs
- `code/job2_hosting_ledger.py`: agent's post-hoc independent ledger of the hosted templates
- `code/job5_hosting_ledger.py`: its extension for job 5 (#471's layouts, per-call owner summary)
- `code/test_job5_ledger_mutations.py`: mutation controls of the pooled-slot audit
- `code/job5_pr501_word_check.py`: diagnosis of #501's source-word pin
- `code/job6_retime_search.py`, `code/test_job6_smoke.py`: job 6 frame-timing search and its smoke test
- `report.md`: results and interpretation
