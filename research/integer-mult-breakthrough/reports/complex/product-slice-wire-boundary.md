# Direct product form incidences at arbitrary rank and small coefficient error

Status: **SCOPED ALL-SIZE ALGEBRAIC LEMMAS WITH EXACT FINITE CONTROLS**.
Increasing scalar product rank does not remove the quadratic direct form
incidence floor of the partial product algebra. The floor also survives
sufficiently small fixed coefficient errors. It does not bound the time of
shared or layered circuits, integer record products, or input-dependent
rounding. No native compiler, complete recurrence or larger kappa is supplied.

## Every coordinate slice is invertible

Let `D=2^s`, and let

    q_s(a,b) = C_s^-1 ((C_s a) * (C_s b)),

where the product is coordinatewise and `C_s` is the dyadic complex
butterfly tensor. The [retained algebra](partial-gaussian-product-fusion.md)
has structure coefficient

    q_s[z,x,y] = (-1)^(wt(x&y) + wt(z & complement_s(x xor y))) / D.

Fixing one input coordinate gives a tensor product of the local matrices

    [[1,1],[-1,1]]/2,    [[1,-1],[1,1]]/2.

Fixing one output coordinate gives tensor products of

    [[1,1],[1,-1]]/2,    [[-1,1],[1,1]]/2.

Each local raw matrix has Gram matrix `2I`. Thus every full slice is
`H/D` with `H H^T=D I`, and has rank `D` over both the rationals and
Gaussian rationals. This statement concerns all basis coordinates, not
only a generic slice. It follows by tensoring the displayed local identity.

## A floor on each of the three sides

Consider any finite separable Gaussian scalar product formula

    q_s(a,b) = sum_k U_k(a) V_k(b) w_k,

with linear input forms and output vectors. Coefficients and signs may
be arbitrary, and terms may cancel. Let `R` be the number of nonzero
rank-one terms. Fixing input coordinate `x` gives

    q_s(e_x,b) = sum_k U_k(e_x) V_k(b) w_k.

The left side has rank `D`. Each term on the right has matrix rank at
most one, so at least `D` values `U_k(e_x)` are nonzero. Summing this
count over the `D` coordinates proves `nnz(U)>=D^2`. The other input
side gives `nnz(V)>=D^2`. Fixing output coordinate `z` instead gives an
invertible bilinear form and proves `nnz(W)>=D^2` independently.

In particular, if every input form on one side has at most `L` nonzero
coefficients, then `R>=D^2/L`. A formula with `R<=D*g` has average form
support at least `D/g` on each side. This extends the
[minimum-rank character constraint](partial-gaussian-product-fusion.md)
to arbitrary product counts within the stated separable formula model.
It does not assume that the formula uses characters.

The named three-product tensor word attains all three floors. Its local
forms are `a0`, `a1`, and `a0+a1` on each input side. Its output numerator
weights are `[[0,-2,1],[-2,0,1]]`, divided by two. A tensor term with `j`
sum choices has support `2^j` on every side. Summing supports gives
`(1+1+2)^s=4^s=D^2`, with exactly `D` terms incident to each coordinate.
The word has `3^s` products and average support `(4/3)^s`. The minimum
rank character word also attains the incidence floor, with `D` dense
forms on each side.

The floor does not distinguish the execution time of these words.
Butterfly circuits can share intermediate sums while computing dense
forms. Charging every direct form incidence as an independent payload
pass would silently exclude that sharing. Likewise a complete polynomial
product is not a scalar rank-one Gaussian term. These are essential scope
boundaries for any transfer to the fixed-tape model.

## Small fixed coefficient errors preserve the floor

Use the complex norm `|z|_1=|Re z|+|Im z|`. Suppose a fixed approximate
bilinear tensor has error at most `epsilon` in this norm at every
structure coefficient. Its corresponding coordinate slice is `M+E`,
where `M=H/D` and `M^-1=H^T`. The induced row-sum norm gives

    ||M^-1 E||_infinity <= D^2 epsilon.

When `D^2 epsilon<1`, the matrix `I+M^-1 E` is invertible: if it killed a
nonzero vector, a coordinate of maximum complex norm would contradict
the strict norm bound. Hence every input and output slice of the
approximate tensor still has rank `D`. The same three incidence floors
apply to any exact separable formula for that fixed approximate tensor.

The finite controls choose `epsilon=1/(2D^2)`. Each coefficient receives
a Gaussian perturbation with real and imaginary parts independently
equal to `+/-1/(4D^2)`. They compute the full inverse-error row norms and
fraction-free Gaussian determinants exactly. At the larger error
`epsilon=1/D`, replacing every coefficient by zero produces a rank-zero
tensor, demonstrating why a precision premise is necessary. The sufficient
`D^-2` threshold is conservative; no sharp threshold is asserted.

This is a coefficient approximation statement about one fixed bilinear
map. A precision guarantee on a particular payload does not automatically
imply this entrywise bound. Input-dependent rounding, modular encodings,
nonlinear repairs and complete record products are outside the lemma.

## Evidence and reproduction

The [exact slice run](../../runs/20261009T054324Z-complex-product-wire-floor/report.md)
uses four workers at `s=1,2,4,6`. It checks all 532624 input/output Gram
entries; full matrices are generated rather than serialized. Exact input
symmetry binds the second input family. It also
enumerates every named tensor term's supports and rejects a one-entry
slice corruption. The arbitrary formula theorem is analytical, not a
finite search over formulas.

The [perturbed slice run](../../runs/20261009T055154Z-complex-approximate-product-slices/report.md)
uses four workers on twelve cases: the same four widths and three slice
families. It checks complete perturbed matrices of order up to 64 using
exact Gaussian Bareiss elimination, including exact divisibility at every
step. Both unperturbed full-rank and low-accuracy zero-rank controls pass.
There are no imports from the earlier algebra or slice producer.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/product_slice_wire_floor.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/approximate_product_slice_floor.py --workers 1 --bounded
```

The standard library suffices. Use four workers without `--bounded` to
regenerate the complete retained sets. Optional output paths must be fresh.
Configs pin source hashes, seed formulas, scope and expected outcomes.
Original run receipts are immutable; portable sources generate all finite
matrices and no irreplaceable external input is required.

## Consequence for the breakthrough question

Under the inherited full-size packet shape `s=Theta(E)`, a direct sparse
formula with support bounded by a polynomial in `s` still has exponential
product inflation `R/D>=D/L`. Polynomial chunk-width slack cannot absorb
that named direct implementation. This is an incidence/rank consequence,
not a lower bound on a shared encoder, layered evaluation or an outer
assembly that changes the product contract.

A credible next candidate should therefore supply useful shared input and
output circuits, a genuinely different record product representation, or
a complete architecture leaving only a small partial packet. Its actual
volume, signed precision, layout and child characteristic must be compared
with the [corrected packet envelope](partial-product-packet-prefix.md).
No target-crossing exponent is inferred from the present lemmas.

Attribution: the complex track derived the scoped lemmas and executed the
two exact finite control sets. This is AI-assisted internal research,
not formal verification or external peer review.
