# Independent h28 shared complex witness

The unchanged reviewed even-ground D/E construction at h28 passes complete
independent finite replay. It uses 97,586 side roles and supports the simple
strict complex saving `3794/10^11`. Its applicability follows from the
previously reviewed all-even-ground proof, not from assuming the new h25
upstream network has the same frames. The complete compact multiplication
assembly remains a separate conditional transfer.

## Finite and exact evidence

[Run 20261008T013158Z](../runs/20261008T013158Z-review-complex28/)
reconstructed the full DAG supports, labels and physical timeline using
the unchanged independent [reviewer](../code/review_complex_frames.py).
It never invokes the producer's frame checker. The immutable producer
record is copied byte for byte, SHA256
`ddd974155f8ddbdf3efe7ed4c85fe122138def40314702c98f023ae996e38ea8`.

| Independent check | Count |
|---|---:|
| Nonzero output coefficients, with all required zeros also checked | 7,780,500 |
| Logical source/gate frames | 94,310 |
| Distinct nonzero residual norm-one witnesses | 152,984 |
| Distinct terminal-complement norm-one witnesses | 63,602 |
| Forward and reverse physical transitions | 559,308 |
| Exact partner-matching images | 3,276 |

The h28 replay took 2.022 seconds including the wrapper. The timed process
used 1.70 seconds user CPU and 0.14 seconds system CPU, with peak RSS
256,088 KiB, zero swaps and zero major page faults. There was one CPU
worker and one BLAS/OMP thread.

A separate [64-term exact count/log audit](../runs/20261008T014008Z-review-complex28-counts/)
recomputed these values and the retained coefficient guard without importing
the producer's count or logarithm routine:

```
v=3276, m=21952, N=35158608576, R=97586,
W=2165559937632, L=26143580736,
D=18030055680, s=47538353720841984,
eta=15/39549272.
```

The reconstruction uses `W=2N+2v^2(R+h+1)`, `L=3v^2*h*(h+1)` and
`s=W*m-2N+2L`. Four mixer passes and source/target groups give
`3v^2(4R+4)<6W`; saved-input elementary coefficient evaluation remains
below `E=64(W+m+1)^3`. Exact atanh series with rigorous tails enclose
`-log(1-eta)/log(m)` more tightly than the saved producer enclosure and
place it strictly above `3794/10^11`. Source:
[review_even_complex_counts.py](../code/review_even_complex_counts.py).

## Transferred proof and limits

The existing [all-even-ground review](review-complex-transfer.md) proves
the cancellation-free D/E recursion, transparent arbitrary-scratch scalar
shear, nonalternating binary residuals, every terminal complement, Cartesian
bank joins, signed three-stage exchange, rank budget and new grouped-gate
guard argument for every even h>=8. The h28 sources are exactly the same
ones as that review: circuit SHA256
`5773617bf59ae7287080ae2b4d2c3ddf019670143197571507b7377c9c3f3bd3`,
reviewer SHA256
`336e241f6cf25a525c94e06bece87bc686e45e4383346ca5fdc29f93640023b7`.
The complete h8 dirty scalar basis and actual dirty three-stage exchange
remain the finite calibration of that all-size algebraic proof. A dense
h28 dirty scalar matrix or a full physical h28^9 bank exchange was not
repeated; neither is inferred from the h28 binary frame checks.

The independently reviewed compact construction accepts different bit and
complex arities. Its new [generic composition](downstream-generic-compact-composition.md)
uses the already promoted 484,264-role bit primitive and this h28 witness.
The tight kappa remains `3111277520532267774488444782831/(2*10^39)`
because the prefix/bit branch is limiting, while the displayed common
numeric parameter cutoff drops from97,328 to1,021. Additional eventual
prime, descriptor/record and strict logarithm-absorption thresholds remain;
this number is not a complete all-input cutoff.

## Reproduction

Use fresh output paths from the RaD root:

```bash
python3 -B research/integer-multiplication-bounds/code/review_complex_frames.py \
  --h 28 --output "$FRESH_FRAMES"
python3 -B research/integer-multiplication-bounds/code/review_even_complex_counts.py \
  --candidate research/integer-multiplication-bounds/runs/20261008T013158Z-review-complex28/results/producer-copy.json \
  --independent-frames "$FRESH_FRAMES" --saving 3794/100000000000 \
  --output "$FRESH_COUNTS"
```

The h28 producer recipe is deterministic and uses the pinned original input
and preserved authored source. New compact input/proof identities remain
separate in the composition protocol. No broad novelty or unconditional
multiplication theorem is claimed.
