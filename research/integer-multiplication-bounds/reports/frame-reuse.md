# Increasing-frame retained controllers

The pinned paired compiler uses each circuit use as a separate occurrence,
with one result-pivot identification per addition. An input used only as a
controller retains its scalar value. This campaign chains later uses of that
same value when their rational gate frames contain its preceding gate frame.
At every addition at least one incoming chain terminates; that input provides
the overwritten result pivot. Every other outgoing copy gets a fresh role.

For a fixed graph and topological schedule, a unit-capacity maximum flow
selects the largest admissible link set. A source capacity of one per gate
allows at most one retained input there, and every incoming use has capacity
one. Time order rules out cycles. With c additions, q designated partial
outputs and l retained links, the role count is `R=c+q-l`. This is an optimum
within the stated chain ansatz, not among all reversible circuits.

## Exact frame and scalar obligations

The original rational form is `H=I-J/9`. Every node's source triple indicators
share a common coordinate i. For their span, `sum x=3x_i`, hence
`x^T H x=sum_(j!=i) x_j^2`; the span is positive and nondegenerate.
Removing coordinate i gives signless edge vectors. Connected bipartite
components have one signed-sum constraint; odd components span all their
coordinates. The compiler encodes this span exactly over Q. Odd cycles use
characteristic-zero algebra, independent of the bit scalar field.

A retained role carries the same logical wire value while its frames grow
through successive gates. Reversing the sequence and taking orthogonal
complements gives increasing frames in the reverse mixer. Every designated
output frame is orthogonal to its physical target; an output may end a
controller chain only if the final frame still lies in that output span.
The transparent schedule restores arbitrary dirty scratch because
`JLz+JL(z+Vx)=JLVx` over F2, and L is invertible.

Input and output labels, the rank-one negative source correction, central
returns, and the complete stage-1/stage-3 auxiliary-bank matching are
retained. Thus `W=2v^3+2v^2(R+h)`, `L=3v^2 h^2`, and
`s=Wm-v^3+2L`, with `v=binom(h,3)`, `m=h^3`. New controller chains add
no decreasing edge.

## Measured witnesses and falsification

At h=50, aligned pairing starts from c=435450, q=58800, R=494250.
Node-ID order admits only 600 links, giving 493650 roles. Sorting by exact
source-span dimension (then node ID) gives 6600 links and 487650 roles.
The latter graph has 11,100 eligible links. The compiled scalar identity is
`b4e846f16448379f0383ff1216308068a2239dfcd2c6d59d041e4b549d9b570f`.
The full corrected certificate used 56.24 wall seconds and 3,143,692 KiB
peak RSS, with no swap. Local unmodified ID-order graphs yielded no links;
a small positive control verifies five roles reduce to four with one link.

The [complete certificate](../runs/20261007T2302Z-frame-reuse/results/certificate.json)
passes full-size exact scalar/frame checks, both orientations of exhaustive
dirty-scratch tests at h=6 and h=8, stage exchange at seeds 1/109, all
19,600 joining matches, strict primitive logarithms, and the original
Gaussian assembly. It supports `kappa=18962736562719/10^31`.

[Independent review](review-frame-reuse.md) adds 3,315 rational span checks,
37,225 exact containment comparisons, and full-basis scalar/frame checks
at h=6,8,10. It audits role accounting and output endpoints separately.
Combining with the reviewed blocked Gaussian model is certified in
[the parameter report](downstream-parameter-optimum.md). The complete
upstream algorithmic theorem stays conditional; no formalization or complete
multiplication-machine implementation is claimed.

An initial certificate attempt incorrectly called the original c+q helper
with a replacement physical-role program. It failed rather than certifying
the preferred result. A new attempt uses the explicit proven count formula
and first checks equality with the original helper in its own model.

## Reproduction

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$MATH_PY" code/frame_reuse_positive_control.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$MATH_PY" code/frame_reuse_certificate.py --reference "$REF" --output "$OUT"
```

The paths above are relative to the topic directory. Source versions and
commands are pinned in the run protocol; the math lock is in configs/.
The first validation exercises exact rational elimination on the positive
control. The full certificate is the executed reproduction path. Next: test
broader positive support envelopes and graph/schedule changes, while
optimizing the actual transferred exponent rather than a gate proxy.
