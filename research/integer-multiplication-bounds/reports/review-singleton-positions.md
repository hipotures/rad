# Independent promotion of an arbitrary singleton-position vector

Campaign clock: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.
Pinned input: `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

The new h50 candidate passes complete independent logical and physical
scalar reconstruction, rational frame transitions, controller accounting,
and bounded complete dirty-scratch controls. Its 485,237 physical side roles
improve the previously promoted gap23 witness by 123 roles. This is a
conditional finite-construction improvement; its multiplication exponent
requires a separate analytic composition.

## Candidate and independent checks

The immutable throughput candidate is
`abda739268bd6b9473e6b5d05fa63c4e7ca721783ecc2e4c3c1289635f261563`.
It uses base4 and singleton positions 23 for common points 0–47 and 22 for
48–49. The previous gap23 witness placed the latter pair at 24. Every intact
global pair remains intact; only the local location of the unmatched mate
changes. The input certificate is preserved in
[the run](../runs/20261008T005350Z-review-singleton-positions/results/candidate-input.json).

The [fresh reviewer](../code/review_singleton_positions.py) constructs all
50 local circuits independently, without the throughput worker's local
cache. It imports the frozen independent coefficient, envelope, and dirty
reviewers and does not call the producer's scalar verifier. All logical
coefficients are reconstructed from DAG arguments and original triples;
each designated partial output is compared with a fresh enumeration.
The physical mixer independently checks every disjoint addition and every
fresh copy, so the verified coefficient identities hold over ordinary
integers as well as the characteristic-two scalar field used by the bit
invocation.

| Quantity | Exact full-candidate check |
|---|---:|
| Logical additions | 434,788 |
| Designated partial outputs | 58,800 |
| Nonzero partial coefficients | 63,562,800 |
| Fresh physical copies | 465,637 |
| Logical rational frames | 454,388 |
| Forward and reverse physical frame transitions | 2,709,626 |
| Retained controller links | 8,351 |
| Physical side roles | 485,237 |

Each selected link is independently checked to retain the same logical
source, move forward in the use order, obey at most one retained input per
previous gate, and satisfy the envelope inclusion equations. Counting
928,376 directed source uses and subtracting 8,351 links gives 920,025 chain
starts. Each of the 434,788 binary gates supplies a terminating input pivot,
so the number of allocated roles is independently
`920025 - 434788 = 485237`. This verifies the witness even without relying
on the optimizer's maximum-cardinality claim. That claim is scoped to this
fixed DAG, schedule, and controller-chain ansatz.

The independently reconstructed compiled serialization equals the immutable
producer SHA256
`1c977516b156233960e65894a416fd1c2416fd9963827a019363f117c221033f`.
The independent logical and physical digests use different serializers and
are retained in the complete result.

## Frames and arbitrary dirty scratch

The envelope checker derives the intersection core and support union from
the logical arguments. It verifies source copies are exactly the original
triple lines; every output frame is exact and orthogonal to its designated
target; and all physical labels nest forward, with their complements
nesting in reverse. The universal positive norm proof is the unchanged
[rational envelope proof](review-rational-envelopes.md). The full h50 run
uses constraint equations rather than performing dense rational elimination
of every label. All 19,600 stage-matching images are independently checked
for bijectivity and intersection one.

Two new small controls vary singleton positions independently. They are
h6 `[1,1,1,1,0,0]` and h8 `[0,3,1,2,3,0,1,1]`; the second does not require
the two members of a global pair to choose the same position. This checks
that the proof does not accidentally depend on a uniform gap or paired
position equality.

| Small boundary | h6 | h8 |
|---|---:|---:|
| Side roles | 150 | 683 |
| Complete side-invocation basis, excluding central registers | 190 | 795 |
| Complete invocation basis, including central registers | 196 | 803 |
| Distinct dense rational envelope checks | 122 | 603 |
| Physical forward and reverse transitions | 708 | 3,910 |

Both complete side bases pass the neighbor shear, arbitrary dirty side
restoration, and transposed opposite shear. The pinned complete invocation
routine additionally checks both forward and inverse chronology on every
basis coordinate including the central registers. The complete equal-ground
three-stage exchange passes seeds1 and109 for each small ground, restoring
both arbitrary dirty banks. These are explicit bounded tests; no full
h50 dirty matrix or complete multiplication machine is claimed.

The [controller proof](review-frame-reuse.md) and
[stage-joining proof](review-asymmetric-motifs.md) apply because every
new frame and controller transition satisfies their exact hypotheses.
The central-return losses and terminal auxiliary endpoints are unchanged.
The rational label argument remains separate from the characteristic-two
scalar bit invocation.

## Reproduction and measurements

The [complete result](../runs/20261008T005350Z-review-singleton-positions/results/certificate.json)
and protocol preserve input identities, every source hash, interpreter,
library versions, commands, and raw timing output. The successful process
used Python3.14.7, NumPy2.5.3, SciPy1.18.1, one CPU worker, and one BLAS
thread. The 16-process campaign queue reserved one evaluation slot for this
audit and continued 15 evaluations concurrently.

The full h50 witness took 81.01 seconds; all work including small controls
took 97.89 seconds. External `/usr/bin/time` measured 101.20 elapsed seconds,
95.75 user seconds, 2.06 system seconds, and 3,059,216 KiB peak RSS. The
RSS measurement covers one fresh process, including all three cases.
It must not be compared directly with a reused throughput worker's lifetime
high-water mark or a warm-cache per-case timer.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  "$MATH_PY" -B research/integer-multiplication-bounds/code/review_singleton_positions.py \
  --reference "$REFERENCE" --candidate "$CANDIDATE" \
  --small-controls --output "$FRESH_OUTPUT"
```

There were no failed attempts in this new run. Prior frozen singleton
review files were neither modified nor reused as output destinations.
