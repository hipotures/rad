# Actual representatives for arbitrary subspace frames

Every binary subspace E now has a deterministic literal Gaussian frame F_E,
including degenerate E. Its inverse-Z Lagrangian is
`L_E={(a+b,b):a in E-perp,b in E}`. The zero, full, odd-line and odd-kernel
operators are pinned exactly. This supplies an actual common-operator API
for the proposed nested dirty side construction; sharing only a Lagrangian
label is insufficient for scalar additions.

## Explicit all-size operator

Let r=dimE, choose an invertible binary routing P whose first r columns
are a canonical basis of E, and write D=diag(i^weight). The generic frame is

```text
F_E = D^-1 * P * Htilde_r * P^-1 * D^-1,
Htilde_r = ((1+i)/2)^r * Hadamard_r = S_r*C_r*S_r.
```

The unselected coordinates of Htilde remain fixed. There is no irrational
normalization gate. The temporal word in
[frame_spec](../../code/complex/canonical_subspace_frames.py) includes both
linear maps, both all-bit diagonal phases and the selected dyadic Hadamard.
The API supports arbitrary dimensions without allocating an address cube.

The partial Fourier `P*Htilde_r*P^-1` has inverse-Z span
`(E-perp,0)+(0,E)`. Right conjugation by D adds x to the z component of a
Pauli label, yielding L_E. Left diagonal phases commute with Z and leave
this span intact. No nondegenerate completion of E is assumed.

Pinned overrides are actual matrices, not free replacements at runtime:

| E | Chosen F_E |
| --- | --- |
| Zero | I |
| Full space | C_n |
| Odd-norm line span(T) | C_T |
| Odd-norm hyperplane T-perp | C_n*C_T^-1 |

Each override has the same L_E as the generic construction. The line and
kernel cases are graph frames because the odd T gives an orthogonal direct
sum. The weight-three kernel's affine offset is included by its literal
operator, as established in the
[odd-line review](closed-center-and-odd-line-independent-review.md).
An even-norm line has a vertical direction in L_E and cannot be replaced
by the ordinary C_T graph frame; the executable negative control rejects
that tempting shortcut.

The published subspace geometry gives
`distance(L_E,L_F)=dimE+dimF-2*dim(E intersect F)`. For E contained in F,
the exact relative Clifford `F_F*F_E^-1` therefore has mixing rank
`dimF-dimE`, independently of its diagonal or monomial gauges. An actual
Clifford of mixing rank d has affine matrix support with2^d entries per
column and a quadratic phase. Choosing active input/output coordinates
that make their nondegenerate bilinear coupling the identity leaves one
dyadic C_d, two quadratic fourth-root gauges and two affine routers. Its
Gaussian dyadic, unitary coefficients force the remaining scalar phase
to be a fourth root. All gauges and offsets still need implementation and
cost accounting.

This is an all-size algebraic existence argument. The present executable
normal-form compiler uses exact coefficient matrices and is bounded at n5;
it is not a scalable native tape normal-form compiler. A tableau-based
compiler or another efficient explicit construction remains an obligation
before a large side word is accepted with its proposed native recurrence.

## Exact bounded API and evidence

`frame_matrix(E,n)` returns an integer Gaussian numerator matrix on grid
`2^-dimE`, plus its specification. `compile_nested(E,F,n)` reconstructs
`F_F*F_E^-1` and returns the selected rank, full input/output linear maps,
affine offset, fourth-root tables and fitted quadratic phases. It checks
every matrix coefficient. No producer source is imported.

[The completed two-worker run](../../runs/20261009T014550Z-complex-canonical-subspace-frames/report.md)
started at `2026-10-09T01:45:50.150971+00:00` and passed in0.698 seconds.

| Dimension | All subspaces | All nested ordered pairs | Pairs with a degenerate endpoint | Exact relative matrix entries |
| ---: | ---: | ---: | ---: | ---: |
| 3 | 16 | 66 | 33 | 4,224 |
| 4 | 67 | 513 | 306 | 131,328 |

For all83 frames, literal `F_E^-1*Z_j*F_E` Pauli matrices reconstruct the
claimed L_E. All579 nested transitions then pass one-child amplitude,
affine support, active coupling and quadratic phase reconstruction,
totaling135,552 matrix coefficients. Both endpoints of every scalar common
frame operation can therefore use the exact same returned representative.
The tests cover unchanged frames as well as nontrivial nested transitions.

```bash
python3 -B research/integer-mult-breakthrough/code/complex/canonical_subspace_frames.py --workers 2 --output research/integer-mult-breakthrough/work/complex/<fresh-run>/results
python3 -B research/integer-mult-breakthrough/code/complex/verify_phase_frame_primitives.py
```

The bounded CI wrapper checks every n3 frame/nested pair and the independent
h3 outer-axis kernels in fresh temporary directories. It leaves no output
unless an exclusive `--output` receipt is requested. The wrapper and the two
standalone sources form its complete standard-library closure.

## Side chronology implications and limits

For a target T, processed source labels U orthogonal to T generate a nested
span `E_T subset T-perp`. A sink and an edge helper can both use this exact
F_E_T; a virtual scalar addition then remains a literal addition of whole
physical banks. An odd source U contained in E_T can travel from C_U to
F_E_T and then to C_n with total geodesic rank n-1. A helper starting at zero
and passing through C_U has total rank n. The final sink frame is pinned to
the correct C_n*C_T^-1 rather than a merely equivalent graph label.

These are interface implications, not a verified whole dirty side word.
Every early dirty subtraction, changed common frame, helper retirement,
center scatter, source cleanup and physical dirty endpoint must still be
included. In particular the return cost of a copied center and the actual
number of edge helpers remain paid. Larger subspace lists, native routing,
precision and a complete transfer proof are outside this finite receipt.
No larger kappa is asserted.
