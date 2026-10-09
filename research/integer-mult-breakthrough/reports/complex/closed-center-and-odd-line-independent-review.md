# Independent physical center review and the odd-line affine extension

The exact Gaussian operator of the synthesis track's closed center component
passes an import-free review. The component adds `Kx`, restores every virtual
dirty auxiliary and ends that physical auxiliary in `F*z_initial`, where
`F=C_h`. It is center-only. Its rank charge does not constitute a complete
multiplier recurrence or an exponent certificate.

The review also establishes an exact extension of the relative kernel
interface to **every odd-weight label**, including the weight-three labels
of the simpler integral triple-total basis. Such labels require an affine
quotient-bit flip and a phase `i` for each selected column. Both operations
are explicit paid obligations.

## Independent reconstruction and inputs

[The verifier](../../code/complex/closed_center_interface_review.py) uses only
the Python standard library. It imports no producer code. Gaussian values
are pairs of exact rational numbers; the normal-form comparison uses integer
numerators on common powers-of-two grids. Its independent GF(2) elimination
constructs a perpendicular basis and its dot-dual, including alternating
restricted forms.

Scalar basis gates are immutable input data from
[the single-total local word](../../fixtures/complex/total-center-local-words.json)
and [the triple-total local word](../../fixtures/complex/triple-total-local-word.json).
The decoder is reconstructed directly from the reported combinatorial
formula. Expected physical outputs instead use the intersection polynomial,
without the basis or decoder. The reviewed synthesis source is
`closed_center_release.py`, SHA256
`684cd04a567881dae1c117d9966bbd59a8f9b48f1cfa674bca91ac4968948252`;
its [component report](../synthesis/closed-center-release-component.md)
defines the original weight-five chronology. The producer hash is a reference
identity, not an imported dependency of this verifier.

## Exact relative kernel for every odd label

Write `alpha=(1+i)/2`, `beta=(1-i)/2`,
`C_T=alpha*I+beta*X^T`, and `F=C_h`. The coefficient of F at address
difference d is

```text
c(d) = alpha^h * (-i)^weight(d).
```

For an odd-norm label T, put
`ell=((weight(T)-1)/2) mod2`. The literal convolution gives

```text
(F*C_T^-1)(d) = beta*c(d) + alpha*c(d xor T)
              = 2*beta*c(d)  if d dot T = ell,
              = 0           otherwise.
```

Indeed `c(d xor T)/c(d)=(-i)^weight(T)*(-1)^(d dot T)`.
Thus a weight-one-modulo-four label has the homogeneous perpendicular
support, while a weight-three-modulo-four label has an affine perpendicular
coset. Treating both as homogeneous omits an observable translation.

Let S be any basis of `T-perp`. Its restricted dot form is nondegenerate:
its radical is `T-perp intersect span(T)`, which is zero since `T dot T=1`.
Let M be its dot-dual, so `S^T*M=I`. No orthonormal basis is assumed.
Route output and input addresses through columns `(S,T)` and `(M,T)`:

```text
output = S*a + c_out*T
input  = M*b + c_in*T
c_out  = c_in xor ell.
```

For `eta=S*a xor M*b`, `eta dot T=0`. If ell=1,
`weight(eta xor T)=weight(eta)+weight(T) mod4`, giving an extra factor i.
Since `2*beta*alpha^h=alpha^(h-1)`, the nonzero coefficient is exactly

```text
i^ell
  * i^(-(weight(S*a)-weight(a)))
  * C_(h-1)[a,b]
  * i^(-(weight(M*b)-weight(b))).
```

This is one rank `h-1` child, two fourth-root quadratic chirps, two linear
address maps, and the affine quotient translation when ell=1. For f selected
columns, use one bulk child with selected width `h-1` and f columns, hence
`(h-1)*f` total literal C factors, f quotient-bit flips and the global unit
`i^(ell*f)`. The retained tensor certificate's field `one_child_width`
denotes this total physical tensor dimension; its per-column recurrence rank
is `h-1`. Charging i once instead of once per selected column fails the
two-column control. The packed matrix check writes column-major
coordinates for convenience; the physical chronology separately uses the
repository's row-bit-major packing. Those layouts differ by an explicit
linear bit permutation and have identical tensor coefficients.

These identities are an analytic all-h derivation with finite exact checks,
not a formal proof package. Native fixed-tape implementation of the maps,
chirps, quotient translations, inverse full-frame translations and precision
guards still requires its own complete cost argument. Their units do not
add denominator or magnitude bits, but their operations are not free.

## Actual dirty chronology and the component ledger

The independent execution uses physical inputs `C_T*x`, `y`, `z` and
compares them against

```text
source final = F*x
sink final   = (F*C_T^-1)*(y + K*x)
dirty final  = F*z.
```

It reconstructs the early zero-frame B/negative-scatter/B-inverse word,
source injections at each line frame, the common full-frame late basis,
lowering of exactly q feature banks, positive scatter, their full-frame
return, basis inverse, full-frame source cleanup and final sink kernel.
All scalar B operations act between identical actual address operators.
The independent expected output uses only K's polynomial and literal
convolutions. This checks actual operator equality, rather than equality
of abstract frame labels.

Removing the first feature's full-frame return changes a dirty output even
though the positive scatter has already occurred. That is a meaningful
counterexample for this declared word: its subsequent basis inverse mixes
incompatible actual operators. It is not a lower bound on every possible
center chronology. Requiring raw dirty identity also fails; applying F
inverse to each final dirty bank recovers every original value.

For v source, v sink and v dirty banks, the stock is `W=3v`. The actual
per-column child histogram is v at width 1, 3v at width h-1 and 2q at width h.
Its total is

```text
rank charge = 3*v*h - 2*v + 2*q*h
endpoint floor = 3*v*h - 2*v
closed feature release = 2*q*h.
```

The tensor count multiplies each width by f. All full-width calls remain
explicit. This ledger applies to Kx alone; it cannot replace an old complete
center/side cost until the old calls are removed in an actual joint word.
The v helper banks are real dirty stock, distinct from a scalar addition
count used as a provisional role proxy. Small bases need not save rank:
the triple h4 example has charge72 versus capacity48.

## Completed exact evidence

[The four-worker run](../../runs/20261009T011802Z-complex-center-interface-review/report.md)
started at `2026-10-09T01:18:02.789815+00:00` and completed in 62.090 seconds.
Its run ID was derived from the actual clock immediately before launch.
The complete unchanged certificate and protocol are retained, with original
ignored paths, sizes and hashes in the run's persistence receipt.

| Check | Explicit coverage |
| --- | --- |
| Every odd label at h1 through h7 | 127 interfaces; 1,198,372 exact matrix coefficients |
| Weight-three and weight-one two-column normal forms | 8,192 complete packed matrix coefficients |
| Orthogonal color, h3, f1 | All72 physical basis columns; two full dirty Gaussian fields |
| Orthogonal color, h3, f2 | Nine origin-bank columns; two full dirty Gaussian fields |
| Triple-total, h4, f1 | All192 physical basis columns; two full dirty Gaussian fields |
| Single-total, h7, f1 | All63 origin-bank columns; one full dirty Gaussian field |

The physical tests compare 565,008 output values. Origin-bank coverage uses
a separate exact covariance argument: every C-line/full operation is a
convolution, and every scalar bank gate has fixed address-independent
coefficients. Their composition commutes with simultaneous address XOR on
all banks. Hence an origin column determines every translated column.
The 63 single-total origin columns determine its 8,064 basis columns; those
8,064 columns were not individually recomputed. Gaussian complex linearity
then covers arbitrary payloads.

Negative controls reject even-norm labels under the rank h-1 contract,
missing affine offsets, missing i phases, one-time instead of per-column
phase charging, omitted feature returns and the wrong raw dirty endpoint.

[The bounded single-worker receipt](../../runs/20261009T012009Z-complex-center-interface-ci/report.md)
passes in 0.746 seconds. It checks every odd label through h4, both complete
two-column normal forms, color f1/f2 origins and triple h4 origins, including
full dirty fields and all applicable negative controls. It omits the full
h7 physical replay. The bounded command is suitable for the existing CI
registry; registry publication is owned by the campaign coordinator.

```bash
python3 -B research/integer-mult-breakthrough/code/complex/closed_center_interface_review.py --workers 1 --bounded --output research/integer-mult-breakthrough/work/complex/<fresh-ci>/results
python3 -B research/integer-mult-breakthrough/code/complex/closed_center_interface_review.py --workers 4 --output research/integer-mult-breakthrough/work/complex/<fresh-full>/results
```

The center-only operator is independently accepted within this scope. The
weight-three affine extension makes the integral triple-total basis a viable
candidate for a paid center component. A joint I-K side chronology, complete
dirty/helper accounting, native routing and asymptotic transfer remain open.
No larger kappa is asserted.
