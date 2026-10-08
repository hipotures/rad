# One-common-point target complements

This checkpoint establishes a small improvement from genuinely indefinite
frames on the fixed paired circuit. At ground 50 and global singleton gap 23,
the recovered circuit uses 485336 auxiliary roles, 24 fewer than its positive
support-envelope realization. The later positive-frame pairing search found
485237 roles on a different graph, so485336 is not the campaign headline.
Applying the complementary frames to that newer graph remains useful work.

## Mathematical family

The ambient rational form is H=9I-J. Its eigenvalues are9 on the coordinate
sum-zero subspace and 9-h on the all-ones line; it is nondegenerate for h!=9.
For h>9 it has exactly one negative direction.

For a circuit node n, let Desc(n) be all designated physical output targets
reachable from n. If their designated common point is a single c, every
target triple contains c. Their exact rational span T(n) is positive: on
the common-point incidence subspace, the H quadratic form is nine times
the squared norm of the outside coordinates. Consequently
K(n)=T(n)^perp is nondegenerate, contains the original positive source
envelope, and has one negative direction. Every vector of K(n) is
orthogonal to every designated downstream physical target.

For an original edge child->parent, Desc(child) contains Desc(parent), so
T(parent) is contained in T(child), and K(child) is contained in K(parent).
This is the correct direction. Nodes shared across two or more designated
common points keep their positive envelopes. Input copies remain exactly
the original triple lines. The executable builder asserts these properties
for every original edge before optimization.

Each eligible node chooses between its positive envelope and K(n). A
wide child conservatively forces a wide eligible parent. A binary integer
program jointly chooses these frames and retained-controller links under a
fixed topological schedule. Its returned integer vector is checked against
every integer constraint, then passed through the unchanged physical
compiler and a separate maximum-flow controller optimization. Feasibility
and the recovered role count are exact; solver optimality is reported by
HiGHS and is not a standalone exact dual certificate.

## Transfer obligation

Positivity is not required by the upstream projector identities. For any
nondegenerate rational U contained in nondegenerate V, orthogonal
projectors satisfy P_U P_V=P_U=P_V P_U, and P_V-P_U is an idempotent of
rank dim(V)-dim(U). Orthogonal complements reverse inclusion. Thus the
already reviewed forward/reverse mixer argument applies to the recovered
nondegenerate frames. The immutable upstream discussion is
build/sections/03-motifs.tex, lines 469-525, at
bcd4ebde8692383539f8a48734e5fbf3a18a32c2.

The physical compiler's inherited textual field
"Every retained frame has a common point" does not certify these indefinite
frames. The authoritative certificate is the common-point positivity of
T, ambient nondegeneracy, and the explicit inclusion/target checks. No
compiler assertion was removed. The exact inclusion predicate is bound
locally to the process during compilation.

All designated target orthogonality, source-line compatibility and both
frame directions have passed. Complete small dirty-basis checks have
passed. A new full independently reconstructed physical-frame timeline,
three-stage dirty exchange, and written final rank/join acknowledgement
are still required before the changed indefinite family is promoted into a
campaign exponent. No extra rank saving is claimed merely from the24
fewer roles.

## Exact finite evidence

| Ground / schedule | Positive comparator R | Complement R | Chosen wide nodes | Outcome |
|---|---:|---:|---:|---|
|12 / original IDs|3864|4081|see certificate|negative schedule comparator|
|12 / wide-frame rank|3864|3906|276|negative schedule comparator|
|12 / narrow-frame rank|3864|3858|276|6 roles saved|
|16 / alternating rank refinement|11200|11192|448 or496|8 roles saved; two-cycle|
|20 / alternating rank refinement|24320|24310|860|10 roles saved|
|50 / last singleton|486200|486200|0|no gain|
|50 / global gap 23|485360|485336|8448|24 roles saved|

The independent ground 12 family audit reconstructed all 5152 distinct frame
Gram matrices over Q, checked 2988 exact descendant-target spans, and
compared17536 inclusion decisions with dense rational matrix ranks, seed109.
All frames were nondegenerate with the expected inertia. This audit covers
the alternatives used by all three ground 12 schedules. Ground 12/16/20
complete forward and inverse dirty side-invocation basis checks passed.
Alternating scheduling did not improve the initial narrow-rank counts.

The full ground 50 gap 23 run checked 434730 additions and 58800 partial
outputs, 8194 selected links among 14324 candidates, 11544 relevant frame
variables and 10500 nesting constraints. HiGHS reported a closed optimum
in 5.664 seconds. Full elapsed time was143.115 seconds. The compiled
SHA256 is a7e8c550b62fc52ef73e33cbf9144813742733664c6875b23162df79c2175fb1.

## Recovery

Authored sources are [finite_adaptive_complements.py](../code/finite_adaptive_complements.py),
[finite_label_milp.py](../code/finite_label_milp.py) and
[finite_complement_schedule_refine.py](../code/finite_complement_schedule_refine.py).
All result certificates record complete chosen original-node IDs and retained
user pairs, source hashes, NumPy/SciPy versions, arguments, UTC times and
the pinned reference commit. Full graphs and physical programs are
deterministically regenerable from these witnesses; they are not stored as
large Git payloads. The associated external logs are listed in each run's
protocol.

Use the campaign math environment and set all BLAS/OMP threads to1.
Representative reproduction, always with a fresh output:

```bash
python -B code/finite_adaptive_complements.py --reference "$REFERENCE" \
  --h 12 --schedule wide_rank --independent --dirty --time-limit 60 \
  --output "$FRESH_RESULT"
python -B code/finite_adaptive_complements.py --reference "$REFERENCE" \
  --h 50 --gap 23 --schedule narrow_rank --time-limit 90 \
  --output "$FRESH_RESULT"
```

The decisive full certificate is
[gap23 result](../evidence/20261008T0058Z-phase-singleton-complex-compact/runs/20261008T002730Z-finite-adaptive-complements50-gap23/results/certificate.json.gz).
The independently dense family audit is
[ground12 result](../runs/20261008T002200Z-finite-adaptive-complements12/results/certificate.json).
The complete small schedule refinement is
[ground12/16/20 result](../evidence/20261008T0058Z-phase-singleton-complex-compact/runs/20261008T002400Z-finite-complement-schedule-small/results/certificate.json.gz).

## Next discriminating questions

First apply this family to the strongest newly verified pairing vector.
Second determine whether multiple-common target kernels create any new
retained-controller links, rather than merely larger positive frames. Third
test intermediate nondegenerate frames that admit the useful previous
controller while retaining more of the original source constraints. Each
requires actual physical role counts and the full nondegenerate transfer;
an additions proxy is insufficient.

Complete row-level certificates are published as intact gzip evidence.
Local original JSON remains unchanged. Follow the topic reproduction guide
to restore missing JSON before running certificate-consuming commands.
