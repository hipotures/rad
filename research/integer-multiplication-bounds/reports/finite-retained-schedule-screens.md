# Retained-controller schedule and graph screens

The purpose is to compare actual compiled role counts rather than additions
alone. These experiments import the coordinating agent's
`frame_reuse.py` without changing it. For each schedule, they explicitly
reindex a legal topological order, preserve all physical input/output names,
run the same exact maximum-flow controller-chain optimizer, and check the
whole scalar map and both rational frame directions.

## Fixed graph orders

At h=8 and h=12, fourteen rank-prioritized tie variants were tested: original
and reversed IDs, high/low fanout, high/low support size, canonical span,
span/fanout, high/low downstream depth, incoming fanout pressure, and three
seeded random tie orders (seeds 1, 109, 20261007). All ties yielded the same
best count. Every one of the thirty cases, including old-ID order, passed
dirty scratch with both orientations on every basis input.

| h | Precompile R | Old-ID compiled R | Rank compiled R | Retained links |
|---:|---:|---:|---:|---:|
| 8 | 792 | 792 | 768 | 24 |
| 12 | 4140 | 4110 | 3936 | 204 |
| 50 | 494250 | 493650 (coordinator) | 487650 | 6600 |

The full h=50 follow-up covered six rank tie variants: original IDs, reversed
IDs, canonical span, largest support first, highest fanout first, and random
seed 109. All six compiled to 487650 roles with 6600 selected links out of
11100 candidates. Each passed the complete scalar coefficients and forward
and reverse frame checks. This is a bounded negative result for tie choices;
it is not a proof that the count is optimal over arbitrary schedules.

The complete finite results are
[small dirty checks](../runs/20261007T230730Z-finite-schedule-small/results/certificate.json)
and [h50 tie checks](../runs/20261007T230930Z-finite-schedule50/results/certificate.json).
The graph reindexing gives different serialized compiled hashes from the
coordinator's original graph IDs, even when the role count is equal.

## Recursion thresholds

Paired recursion with threshold 2 has the same precompile role count as
threshold 4 at h=8, h=12, and h=50, but can change the available source
spans. At h=8 it increases retained links from 24 to 72, reducing compiled
roles from 768 to 720. The h=12 and h=50 results remain 3936 and 487650,
respectively. Both original-ID rank ties and random seed 109 agree.

The [threshold-2 finite witnesses](../runs/20261007T230945Z-finite-schedule-base2/results/certificate.json)
check all scalar maps and both frame directions. Dirty scratch was checked
for the original threshold-4 small comparison; the threshold-2 comparison
does not claim an independent dirty-stage certificate.

## Block graph alternatives

The 252-case screen evaluated ground sizes 8, 12, 16, 20, seven block patterns
`2`, `2,3`, `2,4`, `3,2`, `4,2`, `3`, `4`, thresholds 2/4/6, and all three
disjoint recombination choices 0/1/2. Every complete graph map and both
compiled frame directions were checked. The best actual counts were:

| h | Best compiled R | Representative pattern | Threshold | Recombination |
|---:|---:|---|---:|---:|
| 8 | 720 | 2 | 2 | 0 |
| 12 | 3936 | 2 | 2 | 0 |
| 16 | 11344 | 2 | 2 | 0 |
| 20 | 24560 | 2 | 2 | 0 |

The h=8 pattern `2,3` also reaches 720. Larger blocks can permit more
retained links, but their extra additions outweigh those savings in this
bounded exact-span screen. The screen took 59.5592 seconds with two CPU
workers. Its [compact summary](../runs/20261007T231200Z-finite-reuse-graph-small/results/summary.json)
contains the exact versions, source hashes, settings, row hash and row path.
The full deterministic rows are external text evidence under
`derived/finite/reuse-graph-small-20261007T231200Z.jsonl`; the console log is
`logs/finite/reuse-graph-small-20261007T231200Z.log`.

## Reproduction

Use the topic's pinned math environment (Python 3.14.7, NumPy 2.5.3,
SciPy 1.18.1), or recreate it from `configs/math-requirements.txt`. Set
`OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and `MKL_NUM_THREADS=1`.
The immutable reference argument is a checkout at
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

```bash
python code/finite_schedule_search.py --reference "$REF" --h 8 12 \
  --workers 2 --dirty --output "$FRESH_RUN/results/certificate.json"
python code/finite_schedule_search.py --reference "$REF" --h 50 \
  --base 4 --workers 1 \
  --modes rank_id,rank_reverse_id,rank_span_id,rank_support_hi,rank_fanout_hi,rank_random \
  --seeds 109 --output "$FRESH_RUN/results/certificate.json"
python code/finite_schedule_search.py --reference "$REF" --h 8 12 50 \
  --base 2 --workers 1 --modes rank_id,rank_random --seeds 109 \
  --output "$FRESH_RUN/results/certificate.json"
python code/finite_reuse_graph_scan.py --reference "$REF" --h 8 12 16 20 \
  --workers 2 --rows "$FRESH_ROWS" --summary "$FRESH_RUN/results/summary.json"
```

The first system-Python invocation failed before constructing a candidate
because NumPy was unavailable; its
[failure record](../runs/20261007T231000Z-finite-schedule-env-failure/report.md)
is retained. New frame families may change these conclusions and should be
screened separately with fresh run IDs.
