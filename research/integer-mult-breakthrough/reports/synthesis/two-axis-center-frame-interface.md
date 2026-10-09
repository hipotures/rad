# Exact two-axis center frame interface

The new center-only component embeds isometrically in an odd-label tensor
subspace, and the broad interface between the two axes has rank
`(h-1)^2`. This is an actual Gaussian operator result. It does not complete
the scalar center/side composition or justify an inherited master profile.

Write the address space as `F2^h tensor F2^h`. For odd labels `s,t`, set

```text
E_s = s tensor F2^h,
E_t = F2^h tensor t,
u   = s tensor t,
Phi_t = C_full C_Et^-1.
```

Here `C_E` means the product of literal `C_direction = alpha I + beta X_direction`
over the specified orthonormal columns of `E`, where
`alpha=(1+i)/2` and `beta=(1-i)/2`. These operators retain the entire
address cube. The columns `s tensor e_j` and `e_i tensor t` are orthonormal
because the two labels have odd binary norm. Spectator coordinates and
payload fields are retained, rather than cropped to the active cube.

The first-axis center component starts with source frame `C_u` and sink
frame `I`, and ends with source frame `C_Es` and sink frame
`C_Es C_u^-1`. A second-axis component under the common spectator operator
`Phi_t` starts with source frame `Phi_t C_u` and sink frame `Phi_t`.
Consequently both broad transitions have exactly the same relative
Gaussian operator:

```text
M = Phi_t C_u C_Es^-1.
```

All the factors are commuting convolution operators. This equality
includes their phase gauges, rather than just their binary ranks.

For a spectral address `z`, the fourth-root exponent of `M` is

```text
q(z) = weight(z)
       - sum_j parity(s dot z_column_j)
       - sum_i parity(t dot z_row_i)
       + parity(s^T z t)                    mod 4.
```

Its polar matrix is `I+P+Q+R`, where
`P=(ss^T) tensor I`, `Q=I tensor (tt^T)` and `R=PQ`.
Since `P,Q` commute and are symmetric idempotents, this matrix equals
`(I+P)(I+Q)` and projects onto
`V=E_s^perp intersect E_t^perp`. Therefore `rank(M)=(h-1)^2` in the
quadratic-frame interface. The restricted dot form on `V` is nondegenerate;
it can be alternating. No orthonormal basis of that restricted form is
assumed.

A dot-dual input/output coordinate pair on `V`, combined with the
spectator coordinates `V^perp`, realizes `M` with one `C_(h-1)^2` child.
The native wrapper must pay both GF2 address routes, an affine output
XOR, and the per-selected-column row/column fourth-root chirps. The
affine offset is necessary when the spectral phase is nontrivial on its
radical. It is not safe to replace the relative operator by an unshifted
standard child on the basis of the polar rank alone. For multiple
selected columns every chirp is charged per column, including its global
unit factor.

The finite producer is
[outer_axis_frame_splice.py](../../code/synthesis/outer_axis_frame_splice.py).
Four workers test `h=3` with `(s,t)=(1,1),(1,7),(7,1),(7,7)`.
For each case all `512^2` physical matrix entries match the explicit
one-child reconstruction. The affine offsets are respectively `0,72,6,0`;
all four relative widths are4. The spectator pre/post operator `Phi_t`
has width6=`h^2-h` and a separately checked one-child/chirp interface.
The omitted-line-correction negative changes the exact convolution
kernel in every case. The completed receipt is
[the actual-time run](../../runs/20261009T012529Z-synthesis-outer-axis-splice/report.md).
The raw namespace mismatch is explicitly recorded in its persistence
receipt.

This interface explains how the old broad width can arise without
assuming the old cost ledger. It leaves every outer auxiliary stage,
second-axis dirty echo, scalar scale/exchange, tape route and precision
obligation open. Two independent `Kx` shear components produce an
addition of the two axis kernels. They do not by themselves produce their
tensor product or the identity. A product-kernel commutator is a separate
candidate and must count its repeated center calls and dirty carrier
stock. No value of kappa follows from this report.
