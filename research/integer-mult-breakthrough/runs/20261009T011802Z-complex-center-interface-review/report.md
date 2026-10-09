# Independent closed center interface review

Status: PASS INDEPENDENT EXACT PHYSICAL CENTER AND ODD-LINE REVIEW. Actual start: 2026-10-09T01:18:02.789815+00:00; elapsed 62.090 seconds.

The exact full result and immutable input/source identities are retained under results/. See [the cross-run report](../../reports/complex/closed-center-and-odd-line-independent-review.md) for proofs, coverage and limitations.

Reproduce into a fresh ignored output directory:

```bash
python3 -B research/integer-mult-breakthrough/code/complex/closed_center_interface_review.py --workers 4 --output research/integer-mult-breakthrough/work/complex/<fresh-run>/results
```

This verifies a center-only Kx component and exact odd-label Gaussian normal forms. It does not certify a complete integer multiplier, native fixed-tape routing or a larger exponent.
