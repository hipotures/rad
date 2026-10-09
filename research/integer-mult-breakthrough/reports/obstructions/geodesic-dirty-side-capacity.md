# A geodesic dirty side and its unresolved primitive transfer

## Proposed complete framed word

For triple labels U,T, set K[T,U]=(intersection(T,U)-1)/2 and Q=I-K.
Every nonzero side edge has U dot T=0. Give each such edge its own arbitrary
dirty helper z[T,U]. Before any sink leaves the identity frame, subtract
Q[T,U]*z[T,U] from sink T. Move each edge helper to the line-U frame and add
source U there. Sources retain their original line frames until all injections.

Process sources in lexicographic order. Sink T follows the nested span E_T
of its processed nonzero neighbors, always contained in T-perp. For an edge,
move its helper from line U to the same actual E_T representative as the sink,
add Q[T,U] times the helper, and move it to full. The earlier dirty subtraction
has traveled through the sink's own frame path, so the late addition cancels
it in virtual coordinates. Finally move the sink to T-perp, sources to full,
and subtract each full source from its edge helpers. Those helpers end F*z.

The central component's zero-frame scatters precede the growing side sinks.
Its helpers remain at full until the shared source cleanup. Assuming consistent
actual L_E representatives and their correctly priced relative operators, the
combined word adds x to each virtual sink and restores every virtual dirty
helper. It is a framed identity shear, not automatically a canonical C_h call.

## Complete geometric charges and exact conditional moments

An edge helper follows widths1,dim(E_T)-1,h-dim(E_T), totaling h. Every sink
follows nested extensions and a charged final residual, totaling h-1. With v
sources, v sinks, v center helpers, q=h center features and M edge helpers,

```text
W=3v+M, total rank=Wh-2v+2qh.
```

The [independent enumerator](../../code/obstructions/geodesic_side_capacity.py)
retains every source/target edge, actual binary span update, zero-rank omission,
final sink completion and full-width feature return. Exact rational logarithm
and exponential bounds enclose the roots of these conditional profiles:

| h | v | M | W | Rank deficit | Conditional complex root |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 9 | 84 | 3,192 | 3,444 | 6 | (262601438,262601439)/10^12 |
| 10 | 120 | 6,720 | 7,080 | 40 | (810401054,810401055)/10^12 |
| 12 | 220 | 24,420 | 25,080 | 152 | (811625163,811625164)/10^12 |
| 16 | 560 | 182,000 | 183,680 | 608 | (408477357,408477358)/10^12 |

All exceed the necessary complex threshold 20/189981 in the old assumed
assembly. None is an attained native characteristic root or a kappa bound.
The [four-worker run](../../runs/20261009T013835Z-geodesic-side-capacity/report.md)
uses only small binary span states and compact histograms; it does not allocate
the enormous physical arrays suggested by the h16 helper stock. Larger sweeps
are unnecessary before the unresolved primitive transfer is addressed.

## Why the obvious canonical use fails

The actual inputs are x=A_T*X,y=Y and the data outputs are x=F*X,
y=F*A_T^-1*(Y+X), with A_T=C_line(T), F=C_h. On raw arbitrary source and sink
data, the operator is therefore

```text
F * [[A_T^-1,0], [X_T,A_T^-1]],     A_T^2=X_T.
```

Separate source encoding by A_T, followed by sink return by A_T and subtraction
of the returned full source, repairs this to uniform F on both banks. The two
extra width-one calls per label cancel the apparent 2v saving. The corrected
total is Wh+2qh and its target moment exceeds one. Exact literal wrapper and
moment controls are in the [canonical boundary report](canonical-framed-shear-boundary.md).
Treating source/sink banks as zero instead also changes the active-data baseline;
their allocated stock is not an automatic extra rank-saving allowance.

## Surviving hypotheses and reproduction

A complete joint virtual signed swap is a distinct candidate: with the same
initial and final frames its physical map has only monomial corrections to F.
Three separately restored shear bodies have large repeated costs, so their
joint chronology must be derived rather than assumed. A two-axis embedding
could instead reuse encodings already paid elsewhere. Actual common frames,
native affine/chirp routes, complete guards and stock, same-width recursion and
the canonical primitive/assembly transfer all remain required.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/geodesic_side_capacity.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/canonical_framed_shear_boundary.py --workers 1 --bounded
```

Complete commands, source hashes and unchanged compact outcomes are in the
run protocol. These are exact geometric and conditional arithmetic results,
with internal model-assisted research analysis, not formal verification.
