# Common-background orientation and the literal three-shear swap

Right and left multiplication of a common background have different effects
on nongraph frames. The synthesis track's three-shear swap uses a **right**
background and is algebraically valid. Its repeated helper traversals still
prevent a capacity gain. Neither result excludes a different joint swap
chronology with shared transitions.

## Exact orientation distinction

For actual frames F_E and F_G and an arbitrary common unitary B,

```text
(F_G*B)*(F_E*B)^-1 = F_G*F_E^-1.
(B*F_G)*(B*F_E)^-1 = B*(F_G*F_E^-1)*B^-1.
```

Thus the right background preserves every relative coefficient, while the
left background conjugates the physical operator. A full C background is
not monomial and can change the mixing rank. Generic intermediate F_E need
not be convolution operators; commuting the background through them is
invalid.

For the canonical generic representative
`F_E=D^-1*P*Htilde_r*P^-1*D^-1`, let C_E be P's routing complement of E.
The inverse-Z Lagrangian of `C_n*F_E` is L_C_E. This follows by mapping
the full diagonal Lagrangian through the partial Fourier: the complement
becomes the X projection and its annihilator becomes the Z kernel.
For a pinned odd source line span(U), its left-background span instead is
L_U-perp because C_U commutes with C_n.

For U in E, dimE=r, the left-background line-to-E distance is r-1 if
`C_E subset U-perp`, and r+1 otherwise. If E is degenerate, a complement
C_E cannot annihilate every vector of E: that would force
`C_E=E-perp`, which intersects E. This observation applies to the declared
left lift. It does not reject the right lift used by the synthesis agent.

[The exact control](../../code/complex/frame_background_orientation.py)
imports only the frozen canonical frame generator and compares actual
Gaussian coefficient matrices on common integer grids. It reconstructs
both left and right relative normal forms, including their affine maps and
quadratic fourth-root phases.

| n | Odd source U | Intermediate E | Original/right rank | Left rank |
| ---: | ---: | --- | ---: | ---: |
| 3 | 4 | span(3,4) | 1 | 1 |
| 3 | 7 | span(3,4) | 1 | 3 |
| 4 | 1 | span(1,7) | 1 | 1 |
| 4 | 7 | span(1,7) | 1 | 3 |

[The actual-time run](../../runs/20261009T015842Z-complex-frame-backgrounds/report.md)
passes all four controls. The right matrices agree exactly with the original
ones, while two left lifts require two additional C factors per selected
column. All examples include the actual phase gauges; distances alone are
not substituted for coefficients.

## Signed-swap physical target and the remaining bill

Put A=C_T and F=C_n. For virtual
`S=[[0,I],[-I,0]]`, input frames diag(A,I) and output frames
diag(F,F*A^-1), the physical target is

```text
diag(F,F*A^-1)*S*diag(A^-1,I)
 = F * [[0,I],[-X_T,0]],
```

because `A^2=X_T`. The remaining signed bank exchange and address
translation are monomial; they do not require another C child. This makes
a joint signed-swap chronology a meaningful route to a canonical primitive.

Three independently completed framed identity shears do not attain that
route's capacity saving. If one body uses W=2v+R actual banks and costs
`Wh-2v+2qh`, three bodies cost

```text
3Wh-6v+6qh.
```

The physical stock remains W if the same R helpers are reused. Three
geodesics per helper are three paid traversals, even when full-background
endpoint translations match exactly. Against one Wh capacity, the deficit
is `-2Wh+6v-6qh`, strictly negative for h>=3. Adding new helper copies
instead changes the real stock and still leaves the repeated data paths
to be counted; it is not a free remedy.

The synthesis agent retains an exact right-background wrapper and helper
return corrections. This review accepts its background algebra and agrees
with its scoped negative rank bill. It does not assert a lower bound for
all swaps, all frames or interleaved center/side circuits. The next useful
mechanism must share phase progress across the three virtual shears, or
realize the swap by another complete joint chronology.

```bash
python3 -B research/integer-mult-breakthrough/code/complex/frame_background_orientation.py
python3 -B research/integer-mult-breakthrough/code/complex/frame_background_orientation.py --output research/integer-mult-breakthrough/work/complex/<fresh-run>/receipt.json
```

Both commands use the standard library and
`canonical_subspace_frames.py`; the optional receipt is created exclusively.
No larger kappa or global swap obstruction is asserted.
