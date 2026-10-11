# Frontier batch, 2026-10-11

Status: **complete (2026-10-11).** All three jobs ran on the shared host; see
the [results report](report.md). In brief:
- 34 of 39 pinned claims reproduce. The 5 failures are integrity-check
  failures of one author's browser-uploaded packages.
- #493 (1.30353e-3) is the top claim without cross-copy whose verifier
  passes, but it is capped by #471's complex supplier, and #471 did not
  replay.
- Every cross-copy claim splits 22-34% of its hosted residuals across two
  copies, and job 1 shows that a split is not a program of the fixed local
  word under single-stream registers.
- Only E8 (and implausibly Leech) can drive #370's template.

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

## Layout

- `run.sh`, `pack.sh`: operator entry points
- `code/`: job sources
- `configs/`: pinned replays, Python requirements
- `evidence/`: created by `pack.sh` after the runs
- `code/job2_hosting_ledger.py`: agent's post-hoc independent ledger of the hosted templates
- `report.md`: results and interpretation
