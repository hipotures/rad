# Independent promotion of the terminal 219-case singleton winner

Campaign clock: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.
Pinned input: `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

The terminal 219-case winner passes complete independent uncached promotion
to 484,264 physical side roles, improving the previously promoted 485,237
witness by 973 roles. No intermediate successor candidate is promoted by
this review. A separately checked analytic composition is required to turn
the finite improvement into a new conditional multiplication exponent.

The immutable candidate is
`6a112b577b3feb05a94dcdfee41c449777edf0894e7fb73513ad805a5b141bd4`,
with base4 and the exact position vector `[22,22] + [23]*46 + [0,24]`.
Its [preserved input](../runs/20261008T010700Z-review-singleton-final219/results/candidate-input.json)
has SHA256 `02f86b24c896d6764b059853dcdaf113fc26f4589a30ddce973e5d48a8cb5641`.
The last global pair is asymmetric: common48 puts its unmatched mate first,
while common49 places it last. Complete global pairs remain intact.

The frozen [generic position reviewer](../code/review_singleton_positions.py)
was executed unchanged, rebuilding all50 local circuits without the search
cache. The independent proof and verifier interfaces are those detailed in
[the earlier position review](review-singleton-positions.md). All logical
coefficients are reconstructed from DAG arguments and compared against
fresh source-triple enumeration; every physical addition has disjoint
coefficient supports, and every extra copy has an empty destination.

| Quantity | Complete exact check |
|---|---:|
| Logical additions | 435,855 |
| Designated partial outputs | 58,800 |
| Nonzero partial coefficients | 63,562,800 |
| Fresh physical copies | 464,664 |
| Logical rational frames | 455,455 |
| Forward/reverse physical transitions | 2,711,948 |
| Retained controller links | 10,391 |
| Physical roles | 484,264 |

Each retained link is independently checked for source identity,
chronology, one-input gate capacity and envelope inclusion. There are
930,510 directed source uses and 920,119 resulting chain starts. Subtracting
one terminating pivot per435,855 binary gate yields484,264 physical roles.
Every physical output frame is exact and orthogonal to its designated
target. Source frames are original triple lines; all forward labels and
reverse complements nest. The positive rational envelope proof, unchanged
central losses, terminal endpoints, arbitrary-dirty argument and stage
joining hypotheses are therefore all retained.

The independently reconstructed compiled SHA256 equals the immutable
producer `91788d65aebb8fc9fb12a20350004f6cd766f5c36b6a226e9495bdd8a3ac55b5`.
All19,600 stage-matching images are independently checked for bijectivity
and intersection one.

The new graph has1,067 more additions than the previous promoted graph,
but2,040 more valid retained links. Consequently its true physical count
is973 lower. This is direct evidence that an addition-only screening
objective can reject a better frame-aware construction.

Both generic small position controls pass again. Their complete side
bases have190 and795 coordinates, while the complete invocation bases
including central registers have196 and803 coordinates. Both invocation
directions and all four equal-ground three-stage seed exchanges restore
arbitrary dirty scratch. These bounded checks are distinct from the full
h50 coefficient/frame census; no full h50 dirty matrix is claimed.

The [completed result](../runs/20261008T010700Z-review-singleton-final219/results/certificate.json)
records full witness time82.18 seconds, total work97.56 seconds and fresh
process peak3,052,716 KiB RSS. It uses Python3.14.7, NumPy2.5.3 and
SciPy1.18.1 with one CPU worker and one BLAS thread, while15 successor
evaluations continue in the campaign queue. The actual start/completion
times, source hashes, input identity and raw external timing output are
preserved in the [run](../runs/20261008T010700Z-review-singleton-final219/protocol.json).
There were no failed attempts and no frozen source edits.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  "$MATH_PY" -B research/integer-multiplication-bounds/code/review_singleton_positions.py \
  --reference "$REFERENCE" --candidate "$FINAL_219_CANDIDATE" \
  --small-controls --output "$FRESH_OUTPUT"
```
