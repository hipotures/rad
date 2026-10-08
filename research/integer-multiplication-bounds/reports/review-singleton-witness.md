# Independent dense review of the h50 singleton witness

Campaign clock: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.
Pinned input: `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

The singleton gap23 construction passes independent dense logical and
physical scalar reconstruction and all rational frame checks. It uses
485,360 physical side roles and 8,170 retained controller links, improving
the previously reviewed 486,200-role envelope construction by 840 roles.
The smaller role count is a conditional finite construction improvement;
its effect on an integer multiplication exponent requires a separately
checked analytic composition.

## Exact map and physical execution

The recipe `finite_singleton_certificate.build(50,23)` places the unmatched
mate at position 23 for common points 0–47 and position 24 for 48–49. It retains
all complete global pairs and changes their local recursion order only.
The complete input promotion certificate is
`runs/20261008T000730Z-finite-singleton-transfer/results/certificate.json`,
SHA256 `f13437859a4626b2ee84d9d483dd24eaeda3e7900d2c80ba9724d5c7864a443c`.

The [new independent reviewer](../code/review_singleton_witness.py) reads
only physical input triples, DAG arguments, and output labels for the
dense logical map. It does not use the builder's provenance support lookup
or either producer map verifier. Every node is reconstructed by disjoint
union of input-variable bitsets. Each output is compared against a freshly
enumerated sum of the common-point source triples avoiding the target's
other points.

It then independently executes the compiled physical mixer. Every binary
addition must have disjoint nonzero coefficient supports. Every extra
copy must have a previously empty destination. All result coefficients
must equal the independently reconstructed logical node, including every
physical designated output. This verifies ordinary cancellation-free
integer coefficient identities, stronger than checking parity alone. It
does not turn the rational bit-label family into a binary complex-label
family.

The [completed full result](../runs/20261008T002315Z-review-singleton-witness/results/singleton50-gap23-independent.json)
records:

| Quantity | Independently checked |
|---|---:|
| Active logical additions | 434,730 |
| Designated partial outputs | 58,800 |
| Nonzero partial coefficients | 63,562,800 |
| Physical fresh copies | 465,760 |
| Logical rational frames | 454,330 |
| Forward and reverse physical frame transitions | 2,709,640 |
| Retained controller links | 8,170 |
| Physical side roles | 485,360 |

The dense logical digest is
`31717eb8496249a48cce309ca0a172a13cc6dbee9592a57d82965d5b2e6b697b`;
the independent physical schedule digest is
`a5ca532aec8761c77a93650465d6adba075a2e3b6ab110bbb25246a05dcf0ff1`.
These digests intentionally differ from the producer's serializers.
The full replay took 68.57 seconds and peaked at 2,883,404 KiB RSS with one
CPU worker and one BLAS thread.

## Frames, dirty boundary, and transfer

The constraint-based checker independently derives each envelope's common
core and coordinate union from the DAG arguments. It verifies source copies
use exactly the original triple lines, each logical dimension is correct,
every synthetic generator satisfies the equations, every designated target
is orthogonal, every output physical frame is exact, and both physical frame
directions nest. The universal positive norm proof and independent rational
basis census remain those in [the envelope review](review-rational-envelopes.md).
No dense rational elimination of every h50 label is claimed or needed.

The [small h8 gap2 control](../runs/20261008T002315Z-review-singleton-witness/results/singleton8-gap2-independent.json)
uses 684 side roles and passes all 796 coordinates of the complete
side-invocation basis, including arbitrary dirty scratch and both opposite
bank shears. It checks 602 distinct envelope bases by exact rational
elimination and all 3,888 physical frame transitions. The side basis excludes
the central h registers. The finite agent's separate promotion certificate
checks complete invocations including central registers and complete equal
and unequal three-stage exchanges; those are different test boundaries.

All 19,600 h50 stage-matching images are independently reconstructed and
checked for bijectivity and intersection one. The proof of controller role
accounting, arbitrary scratch restoration, the unchanged central-return
rank loss, terminal frames, and first/third bank joins is unchanged from
the [controller](review-frame-reuse.md), [envelope](review-rational-envelopes.md),
and [asymmetric motif](review-asymmetric-motifs.md) reviews. Since every new
logical and physical frame obeys those hypotheses, no new decreasing-rank
cost is introduced. The original full multiplication and unaffected lifting
interfaces remain conditional inputs.

## Reproduction and failure provenance

Use the campaign math environment or install the topic's pinned math
requirements. System Python lacks NumPy on this host: the first h50 and
h8 attempts completed logical reconstruction, then stopped before physical
compilation with `ModuleNotFoundError`. Their environment failure and
unchanged source hash are retained in the run's `failed-v1/` directory.
The successful attempts used Python 3.14.7, NumPy 2.5.3 and SciPy 1.18.1,
with fresh output names. No successful result or immutable input was
overwritten.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  "$MATH_PY" -B research/integer-multiplication-bounds/code/review_singleton_witness.py \
  --reference "$REFERENCE" --h 50 --gap 23 --output "$FRESH_FULL"

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  "$MATH_PY" -B research/integer-multiplication-bounds/code/review_singleton_witness.py \
  --reference "$REFERENCE" --h 8 --gap 2 --small --output "$FRESH_SMALL"
```

The protocol records source and input hashes, dependency versions, the
immutable campaign clock, commands, resource allocation, and precise scope.
