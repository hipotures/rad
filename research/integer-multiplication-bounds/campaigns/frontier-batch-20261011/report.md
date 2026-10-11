# Frontier batch 2026-10-11: results

Operator runs on the shared host (16 cores, 2 x RTX 4090, Python 3.14.7),
campaign commit `01db37d2`, clean tree. All three jobs finished with exit 0.

| Run | Wall time | Outcome |
|---|---|---|
| `20261011T202316Z-job1` | 10 s | `MODEL_CONSISTENT` |
| `20261011T202331Z-job2` | 23.6 min (15 parallel) | 34 of 39 replays pass |
| `20261011T205141Z-job3` | 49 s | E8 price validation matches #370 |

The evidence is in [evidence/](evidence/) as gzip copies; the full outputs and
worktrees stay in `RAD_WORK_ROOT` (see [Evidence](#evidence)).

## 1. Cross-copy hosting under single-stream registers (job 1)

**Question.** Is splitting one dirty helper residual across two data copies
(#448 lineage) a program of the fixed local word, when each register is bound
to one physical stream and streams form a direct sum?

**Method.** Exact small models (bit side q = 3, 5; complex side q = 2;
m up to 8) of the original program, whole-residual hosting (#442), every
single-register placement of a split residual, and a two-register control.

**Measured.**
- Whole hosting equals the original program in all 13 cases where the residual
  fits on one copy.
- 0 of 152 single-register cross-copy programs equal the original program
  (18 split cases).
- The two-register control equals the original program in all 18 cases.
  It is a different local word that uses one more helper per split residual.

## 2. Fresh replays of 39 pinned claims (job 2)

Each replay ran the author's own verifier in a fresh detached worktree at the
pinned SHA, with a fresh output directory and no network access needed.

**Measured.**
- 34 of 39 pass. 33 of them print the title kappa exactly in a receipt or
  their log. #442 matches it to the title's printed rounding (within 1e-6).
- No verifier modified its worktree.
- Non-`PASS` receipt statuses are only informational negative-control labels
  (for example `EXACT_CLEAN_FULL_WORD_DISCOVERY_NOT_ADMITTED`).
- The longest replay was #462 (22.9 min); the largest peak RSS was 1.3 GB (#491).
- **#450 passed.** A PR comment had predicted that it would not replay from a
  fresh clone.
- **5 failures, all by one author (Dugongue):** #471, #476, #478, #483, #492.
  Each stops in 0.2 s at its own package integrity check:
  `MANIFEST.json` lists `.gitattributes`, but the pinned commit does not contain
  it. The commits are titled "Add files via upload", and a browser upload
  drops dotfiles. Every other listed file matches its hash byte for byte. The
  missing file's content could not be recovered: no blob in the upstream clone
  has that hash, and about 68k candidate attribute files did not match either.
  These are packaging failures at the pinned SHA, not evidence about the
  mathematics. The highest of these claims, #492 at 1.29738e-3, is below #493.

| Tier | Replayed and passing (title kappa) | Not reproduced |
|---|---|---|
| E8, no hosting | #376, #433, #436, #438, #439, #482 (max 1.16886e-3) | |
| Whole-residual hosting | #434, #442, #444, #445, #451, #454, #456-#463, #465-#467, #470, #472, #473, #490, #491, **#493 (1.30353e-3)** | #471, #476, #478, #483, #492 (integrity) |
| Cross-copy hosting | #448, #450, #464 (arithmetic only), #469, **#480 (1.37255e-3)** | |

A pass means that the author's verifier reproduces the claimed number from the
pinned bytes. It does not review the mathematics, and it does not discharge the
conditional supplier, hosting and compiler interfaces that the packages
declare.

### Independent hosting ledger (agent, post hoc)

[`code/job2_hosting_ledger.py`](code/job2_hosting_ledger.py) reads every
distinct hosted template produced by the replays (68 templates, 67 parsed). It
uses no upstream code. It checks:
- the split ledger: residuals whose coordinates lie on more than one data copy;
- coordinate intervals per child and copy: disjoint and within the child's rank;
- that each hosted stage lies in the stored window;
- the windows themselves, re-derived from each template's own schedule.

The one template not parsed is #473's `kernel-whole9-borrowed-spectator-v1`,
whose rows have nine fields.

| Template | Hosted residuals | Split across two copies |
|---|---|---|
| #448 bit / complex | 5770 / 5040 | 1562 (27%) / 1715 (34%) |
| #450 (both variants), #469 | 8140 | 1807 (22%) |
| #480 bit | 62920 | 14612 (23%) |
| all 61 other templates (whole hosting, #434 ... #493, incl. their parents) | 4320 - 660660 | 0 |

Across all 67 parsed templates there were 0 interval overlaps, 0 intervals
outside a child's rank and 0 rows outside the stored window. The windows
re-derived from the schedule match the stored windows in every template whose
schedule names pairs and child indices. The two nine-stage complex templates
(#434/#442 and #448) do not, so they were not re-derived.

**Interpretation.** Every cross-copy claim in the batch rests on 22-34% of its
hosted residuals being split across two copies. Job 1 shows that such a split
is not a program of the fixed local word when a register belongs to one stream.
It becomes valid with a second register, which costs one more helper per split
residual, and no package prices that helper. The whole-hosting templates
contain no split and pass all ledger checks.

**Confidence.** High for the measured counts and ledger checks. Medium-high for
the conclusion that the cross-copy tier is unsupported as priced. Job 1 is our
exact model of the declared execution model. An execution model in which one
helper register serves two streams at no cost would need its own justification.
The batch does not refute such a model.

## 3. Lattice screen for #370's five-stage template (job 3)

Our price function reproduces #370's R865 saving exactly
(9.040728210936710e-4, deficit 120). The deficit is 4V - 5 n_cent h, and
`s_ub` is the saving bound at R = 0.

| System | V | n_cent | Deficit | s_ub | Break-even helpers per line vs E8 |
|---|---|---|---|---|---|
| E8 roots | 120 | 9 | 120 | 4.37e-3 | 13.6 (actual word: 7.2) |
| E7 roots | 63 | 7 | 7 | 5.5e-4 (< E8's actual saving) | - |
| Leech minimal | 98280 | 2599 (exact, all rows on GPU) | 81240 | 1.24e-3 | **1.29** |
| E6; D4-D24; A4-A12; E8 norm-4, norm-6, norm-2+4; BW16 | | | negative | 0 | - |

**Conclusion.**
- Within this template, only E8 and Leech have a usable positive deficit.
- E7 is bounded below E8's actual saving.
- Leech would have to beat E8's saving with at most 1.29 helpers per line,
  where E8 needs 7.2. We consider this implausible, but the batch does not
  prove it impossible.
- We recommend no further work on replacing the lattice unless a cheap helper
  construction for Leech appears.

## Recommended next steps

1. Take #493 (1.30353e-3, whole-residual hosting, reproduced exactly) as the
   reproducible top claim without cross-copy. The idle-data hosting
   assumption itself is still unreviewed upstream and is the next audit target.
2. The cross-copy finding is suitable for an upstream review comment on
   #448/#480. Posting requires the user's authorization.
3. Optional: rerun the five Dugongue packages with a single documented
   deviation, tolerating exactly the missing `.gitattributes` key. Those
   verifiers call `integrity()` only inside their own package. None of the five
   claims exceeds #493.

## Evidence

- `evidence/<run-id>/` holds gzip copies of each run's protocol, configs and
  logs, plus `archive-manifest.jsonl.gz` with the original sizes and hashes.
  For job 2 it also holds `SUMMARY.json`, the 39 records, 39 replay logs, 1,125
  receipt/result/audit JSON files from `out/` and `analysis/hosting-ledger.json`.
- Not published:
  - the 39 worktrees (11 GB): pinned upstream source, regenerable from
    `configs/job2-replays.json`;
  - bulk replay outputs (2.6 GB), including the hosted templates: regenerable
    by `./run.sh 2`, and their SHA-256 hashes are in the records.

  Both stay under
  `/srv/ai/work/rad/integer-multiplication-bounds/frontier-batch-20261011/runs/`.
- Ledger regeneration:
  `python3 code/job2_hosting_ledger.py --run <job2 run> --out <file>` (17 s).
