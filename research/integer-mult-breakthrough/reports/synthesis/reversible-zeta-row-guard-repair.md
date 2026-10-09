# Nonzero unit-domain repair for the bounded row verifier

Status: **VALIDATOR BOUNDARY REPAIR**. The historical exact controls and
all unresolved eleven-gate outcomes are unchanged.

Independent coordinator review found that the original scalar-domain
check only tested whether the norm numerator and denominator had
power-of-two bit patterns. At zero, `0 & (0-1)` is zero, so a zero scale
passed that test. None of the retained invertible words uses zero;
their full forward/inverse controls remain valid. The original
verifier, configs, manifest and receipts are preserved unchanged.

`code/synthesis/verify_zeta_row_controls_v2.py` adds a strictly positive
norm requirement before delegating arithmetic to the pinned original
verifier. It validates all retained forward and inverse words first.
The effective standard-library closure is the v2 source, the original
`verify_zeta_row_controls.py` and the small witness fixture.

Direct controls now reject scale0, scale3 (norm9) and scale(1+2i)
(norm5). They accept -1, i, (1+i), and (1+i)/2. The v2 receipt also
reproduces the original zero-scale acceptance explicitly, then reruns
all five exact forward/inverse words and the unchanged binary/ternary
exhaustive controls.

The first new v2 instrumentation predicate used `any(row)` on a row of
Gaussian coordinate pairs. Python treats each nonempty `(0,0)` tuple
as true, so that predicate incorrectly rejected the reproduced
all-zero row. The repaired predicate compares each pair to `(0,0)`.
The failed source is reconstructible by reversing
`code/synthesis/patches/zeta-unit-guard-control-repair.patch` against
the repaired v2 source. A fresh exact rerun preserves its failure
trace and source hash. The first uncaptured terminal attempt's exact
clock was not instrumented; the retained reproduction clock is exact.
This failure concerns the new negative-control instrumentation, not a
change to any accepted finite operator.

From the repository root:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_zeta_row_controls_v2.py
```

Expected status is `PASS NONZERO-UNIT ROW CONTROLS V2`. The v2 CI config
and publication manifest identify the exact closures and preserved
previous hashes. No historical raw bytes were overwritten.
