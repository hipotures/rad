# Exact physical-role cutoff and ordering experiments

The strongest result in these completed cohorts is the cutoff-two graph
with **472,885 physical roles**, 100 fewer than the independently reviewed
cutoff-four graph. The singleton vector is `[0]*6 + [23]*26 + [0]*18` at
ground 50. It has 447,868 additions, 58,800 designated partial outputs,
506,668 roles before controller reuse, and 33,783 selected controller links
from 40,006 candidates. Its source spans and physical target pairings use
the unchanged positive support-envelope transfer.

The exact candidate ID is
`f49b6b448c76fb29cb36514a81022e20659b094464cd9b7e114ee38e6f9ec3e4`.
Its logical DAG hash is
`0c93c27743962921d6dd68cb0328b5136d40091b4fe63280f6f9d016caa1979d`
and compiled hash is
`0119f56ac55b12ee03d204857a470f95243591a2f86dae2ec9325bc03f96a44a`.
The winner JSON is preserved in the cutoff run's durable results. A fresh
independent promotion in `20261008T030515Z-review-singleton-cutoff2` passed
all 63,562,800 nonzero coefficients, physical coefficients, envelope and
controller transitions, complete small dirty bases, and four shared
exchanges. The independent review took 98.48 seconds and peaked at
3,112,140 KiB. No new downstream exponent is claimed by this report.

| Cohort | Completed configurations | Distinct logical DAG hashes | Distinct compiled hashes | Best roles | Wall seconds |
|---|---:|---:|---:|---:|---:|
| Paired block order | 307 | 307 | 307 | 472,985 | 774.796 |
| Retained-controller schedule | 140 | 1 | 139 | 472,985 | 415.417 |
| Recursion cutoff | 320 | 120 | 120 | **472,885** | 783.360 |
| Four-term association | 400 | 200 | 200 | 472,885 | 951.365 |

These are exact full-circuit screens, including the original formal maps,
physical scalar compiler, both frame directions, and every physical target.
Throughput counts completed configurations; they are not counts of unique
mathematical graphs where the table records aliases. Different cohorts use
different candidate distributions and are not identical-input speedups.

The pair-order cohort retains all global pairs and changes only their local
order. Its 307 configurations cover deterministic permutations, rotations,
affine orders and seeded orders. The best reversed order ties the original
role count. The schedule cohort uses exact topological relabelings of one
fixed DAG, covering twelve deterministic priorities and 128 seeded rank ties;
none improves the rank-and-node-ID schedule. Small canonical regressions and
dirty-scratch controls precede both cohorts.

Cutoffs 2 and 3 coincide on the examined ground-50 recipes. Cutoffs 5 and 6
coincide with the cutoff-four leaf recipe, and cutoffs 7 through 10 coincide
with a larger leaf recipe. Their respective best role counts are 472,885,
472,985, and 477,935. The source interner and all checkers remained unchanged.
The initial small cutoff run failed when a direct top-level leaf retained
permuted output-pair keys outside the global adapter's supported interface.
The repaired small controls restrict `base<n`; all ground-50 candidates
satisfy this restriction. The failed attempt is retained.

Four-term rule 1 exactly equals rule 0: the existing balanced `total` on four
entries constructs the same two pair sums and final sum, including the
precomputed left sum. This explains the association aliases. After normalizing
rule 1 to 0, the best counts for early/late rules `(0,0)`, `(0,2)`, `(2,0)`,
and `(2,2)` are respectively 472,885, 489,797, 489,339 and 510,171. The
association family therefore gives a scoped negative. Its original fresh
worker run failed before science because reference imports were unavailable
when the local class was constructed. The fresh repair installs the immutable
reference first; two independent spawn controls passed. Neither original
source nor failed evidence was overwritten. Future queues normalize recipe
aliases before expensive evaluation.

Reproduction uses the topic's pinned Python 3.14.7 math environment, upstream
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`, and one BLAS thread per process.
Each durable run protocol records its exact command, source hashes, controls,
deadline, candidate seed and external output path. The external protocol adds
all candidate definitions; rerunning the recorded command with a fresh output
path regenerates the complete evidence. Completed per-case JSON files remain
external; the durable export retains compact statistics, exact winners, and
hashes/paths to complete summaries. It does not imply the full row files are
present in an ordinary clone.

Sources: [pair-order constructor](../code/finite_pair_block_orders.py),
[pair-order cohort](../code/finite_pair_order_batch.py),
[schedule cohort](../code/finite_retained_schedule_variants.py),
[cutoff cohort](../code/finite_singleton_cutoff_cohort.py),
[association cohort](../code/finite_singleton_sum_rules.py), and
[cold-worker repair](../code/finite_singleton_sum_rules_ready.py).
Runs: [pair-order](../runs/20261008T020031Z-finite-pair-block-orders/),
[schedules](../runs/20261008T021514Z-finite-retained-schedule-repair/),
[cutoffs](../runs/20261008T022630Z-finite-cutoff-cohort/), and
[association repair](../runs/20261008T024520Z-finite-association-repair/).
