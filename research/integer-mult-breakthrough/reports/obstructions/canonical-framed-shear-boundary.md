# Canonical wrapper boundary for a framed identity shear

Let A=C_line(T), F=C_h. They are commuting convolutions and A^2=X_T is an
address translation. The center-plus-geodesic-side candidate has physical
inputs x=A*X,y=Y and outputs

```text
x_out=F*X,
y_out=F*A^-1*(Y+X),
helper_out=F*Z.
```

For raw source p and sink q, its physical two-bank block is
F*[[A^-1,0],[X_T,A^-1]]. The following named wrapper gives canonical F:

1. Apply A to the raw source p.
2. Execute the complete framed word.
3. Apply A to its sink, then subtract the full returned source.

The outputs are exactly F*p,F*q,F*Z. Both A calls are paid width-one children,
and scalar subtraction is a separate local operation. Thus a framed profile
Wh-2v+2qh becomes Wh+2qh; its rank moment at zero already exceeds one. The
[checker](../../code/obstructions/canonical_framed_shear_boundary.py) verifies
complete Gaussian source/sink/address columns, A^2 translations, omitted
encoding/return/cleanup controls and exact outward corrected target moments.
It imports previously published Gaussian and characteristic arithmetic.

This is a failure of this named separate-wrapper reduction. It is not a
proof that every possible canonical adapter must pay2v or that the physical
framed word is incorrect. Global encoding reuse, a different primitive and a
joint signed-swap chronology remain hypotheses. Setting the data banks to zero
does not retain the same arbitrary-input row baseline.

A virtual signed swap S=[[0,I],[-I,0]] with initial diag(A,I) and final
diag(F,F*A^-1) would instead have physical operator

```text
F * [[0,I],[-X_T,0]].
```

Paid raw exchange, sign and address translation would then give uniform F
without the two recursive wrapper calls. This algebra alone supplies no
joint circuit. Executing three independent dirty-restoring shears introduces
repeated helper paths and data returns, which must be charged in a new complete
word. Tensor-column translations and scalar units also remain explicit.

Reproduce the bounded controls with Python's standard library:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/canonical_framed_shear_boundary.py --workers 1 --bounded
```

The source rejects an existing optional output directory. Complete discovery
uses four workers without bounded mode. No canonical native improvement or
larger kappa is certified; this is internal mathematical and exact finite
review, not a formal package or external peer review.
