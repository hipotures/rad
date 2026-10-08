# Fine singleton schedules: 450 exact candidates

The completed cohort checked 450 new ground-50 position vectors with no
errors. Its best circuit uses 472,985 physical roles, 41 fewer than the
independently promoted 473,026-role anchor. The winner is
`[0]*6 + [23]*26 + [0]*18`, a cyclic early-position window. This establishes
a finite compiler result; independent uncached dirty and stage promotion
was requested after the cohort finished and is tracked separately.

The winner has 448,068 additions, 58,800 partial outputs, 42,832 merged
additions and 33,883 selected controller links from 40,106 candidates.
Its unoptimized role count is 506,868. Fewer additions outweigh the small
loss of retained links relative to the anchor. This is a maximum flow only
within the fixed graph, rank schedule and retained-controller ansatz.

Candidate ID:
`2af21b3008b368a4d6533a1fe5df2b4dc82979de24ac58260e708c2da8a16b04`.
Logical digest:
`9b2d5068b57826d8a224da45a6f41620b51d90724eb8d6c4dff48cb9a790e127`.
Compiled digest:
`a915626899ba308501e0abae7d187822fe29cd655941375996d0cbcfcaada077`.
The [exact winner](../runs/20261008T013948Z-finite-singleton-structured/results/winner.json)
has SHA-256
`6b1b790d03b8a946a1478ce8a64e45299e2325b139733cecc6ea198cb770dedb`.

The [source](../code/finite_singleton_structured.py), SHA-256
`8e3ed4b13fa25508e01834adef62b744fdfd84b908f2b9c01bd64d4aa09852a3`,
adds fine prefix, cyclic window, paired masks and seeded refinements
(seed 313) to the frozen dispatcher. It excludes all earlier planned
candidate IDs, including the live predecessor. The original immutable
upstream is pinned at `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.
The identical direct envelope constructor retains its earlier full
Space-field regression digest
`b95dc6a90713db358f2fe73cdf6feb4d8621d141ed51355ee86b49a388d5b021`.

Every candidate reruns the exact global map, positive-frame construction,
physical scalar/frame compilation and all physical target pairings.
Only independently verified immutable local DAGs are cached. Every retained
frame has the same positive common-point envelope proof, so this cohort
does not introduce an indefinite-frame hypothesis or weaken any checker.

The cohort finished in 1,201.290 seconds, 1,348.550 verified candidates per
hour. Average per-case phases were 15.142 seconds for physical compilation,
12.656 for envelopes, 5.536 for controller flow, 1.855 for the global map,
0.715 for construction/local checks and 0.213 for targets. The dynamic
worker pool used up to 16 aggregate campaign processes and subtracted
live predecessor and separately reserved proof workers. All capacity
changes are preserved in the compact summary. Different candidate sets
and reservations prevent treating throughput differences as a same-input
implementation speedup.

The [protocol](../runs/20261008T013948Z-finite-singleton-structured/protocol.json)
contains the exact command, source identity and deadline. The
[compact summary](../runs/20261008T013948Z-finite-singleton-structured/results/compact-summary.json)
retains measurements and the winner. All candidate definitions, all 450
case files and full logs remain deterministically regenerable under
`$RAD_WORK_ROOT/derived/finite/20261008T013948Z-finite-singleton-structured/`
and the corresponding `logs/finite/` directory. Reproduction uses the
pinned math environment, the recorded 473,026-role winner as anchor,
recorded exclusion protocols and a fresh output path. Complete row-level
evidence has the repository's intact gzip publication path; a compact
summary does not claim to contain every candidate row.

The improvement is small relative to the earlier prefix gain. The next
independent experiments vary paired block order and compiler schedule,
and investigate a different monotone whole intersection-one construction.
