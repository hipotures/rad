# Independent all-dimension two-axis phase review

The two broad source/sink transitions in the synthesis track's axis splice
are the same actual Gaussian operator and have relative rank `(h-1)^2`.
An independent derivation gives their canonical affine support and global
fourth-root unit, including odd labels of weight three modulo four.
The axis background operator has a separate rank `h*h-h`. These are phase
interfaces; they do not compose the virtual center and side maps into a
complete multiplier or inherit a previous master histogram.

## Actual operators and projection

Let s and t have odd norm, `m=h*h`,
`E_s=s tensor GF(2)^h`, `E_t=GF(2)^h tensor t`, `u=s tensor t`, and
`Phi_t=C_m*C_Et^-1`. The first-axis source ends at C_Es and the second-axis
source starts at `Phi_t*C_u`. The first-axis sink ends at `C_Es*C_u^-1` and
the second-axis sink starts at Phi_t. Their relative operators both equal

```text
M = Phi_t * C_u * C_Es^-1.
```

All factors are literal commuting translation convolutions. Their spectral
Z4 phase is

```text
q(z)=weight(z)-sum_j parity((s tensor e_j) dot z)
                  -sum_i parity((e_i tensor t) dot z)
                  +parity(u dot z) mod4.
```

Put `P_s=ss^T tensor I` and `P_t=I tensor tt^T`. Odd norm makes both
symmetric idempotents, and `P_s*P_t=P_u`. The polar map is

```text
A=I+P_s+P_t+P_u=(I+P_s)*(I+P_t).
V=image(A)=s-perp tensor t-perp, rank r=(h-1)^2.
R=kernel(A)=E_s+E_t, dimension 2h-1.
```

V and R are orthogonal nondegenerate complements, though V may be
alternating. On V, q is ordinary weight modulo four. Omitting C_u changes
the polar map to `A+P_u`, of rank `r+1`; it changes the actual operator.

## Canonical affine support

Let `ell_s=((weight(s)-1)/2) mod2`, similarly ell_t, and let one denote the
all-ones h-bit vector. The radical splits orthogonally into
`s tensor t-perp`, `s-perp tensor t`, and span(u). On these parts q is,
respectively, `2*ell_s*weight(b)`, `2*ell_t*weight(a)` and zero. Therefore
`q(z_R)=2*a_R dot z_R`, where

```text
a_R = ell_s*s tensor (one+t) + ell_t*(one+s) tensor t.
```

The Fourier kernel is supported exactly on `a_R+V`. This a_R lies in R
and is the unique support representative orthogonal to V. Another valid
support representative can differ from it by a vector of V, changing the
extracted row/global phases. Global factors must be compared at the same
offset, rather than comparing just their scalar labels.

## Closed Gauss unit and one child

For `S=s-perp`, dimension d=h-1, the elementary character sum is

```text
sum_{x in S} i^weight(x)
 = ((1+i)^h/2)*(1+(-i)^weight(s))
 = i^ell_s*(1+i)^d.
```

For a nondegenerate Z4 quadratic form, write its normalized Gauss phase as
`exp(pi*i*sigma/4)`, with sigma taken modulo eight. Here
`sigma_s=d+2*ell_s`, similarly sigma_t. The tensor form's sigma is their
product modulo eight. This fact can be checked without assuming an
orthonormal basis: split each form into odd one-dimensional lines and
alternating two-dimensional planes. The line signatures are +1 or -1;
plane signatures are 0 or4. An odd-line tensor multiplies those signatures.
The tensor of two alternating planes has zero diagonal quadratic values
on its four pure basis tensors and splits into two hyperbolic planes, of
signature zero. Orthogonal sums multiply Gauss factors, proving the rule.

Thus, with `alpha=(1+i)/2`, the kernel at `a_R+v`, v in V, is

```text
M(a_R+v) = g*alpha^r*i^(-weight(v)),
g = i^((h-1)*(ell_s+ell_t)+2*ell_s*ell_t).
```

Choose any basis B of V and its dot-dual D. Routing through `(B,R)` and
`(D,R)` retains all spectator coordinates. Apply output translation a_R
and row/column chirps
`i^(-(weight(B*a)-weight(a)))` and
`i^(-(weight(D*b)-weight(b)))`. The remaining block is exactly one C_r
child. Every input/output map, quadratic phase, affine translation and
per-column global unit is explicit. With f selected columns the native
selected rank is r, with f columns; the physical tensor has r*f C factors
and global unit g^f. No scalar bank coefficient is raised to f.

For weight-five s,t, both ell values are zero: canonical a_R=0 and g=1.
For weight-three s,t, the offset is generally nonzero and `g=(-1)^h`.
The actual dual chirps and routing remain necessary in both cases.

Separately, Phi_t has active subspace `GF(2)^h tensor t-perp`, rank m-h,
offset `ell_t*one tensor t`, and global unit `i^(h*ell_t)` per selected
column. The rank m-h applies to this particular pre/post background
operator. The broad M normal form instead has 2h-1 spectator coordinates.
Neither fact specifies their multiplicities in a whole algorithm.

## Exact independent checks and recovery

[The standalone verifier](../../code/complex/outer_axis_interface_review.py)
imports no producer code. It constructs the spectral phase directly,
uses integer FWHTs to compute complete small convolution kernels, and
independently splits larger quadratic forms by exact XOR elimination.
The [successful four-worker run](../../runs/20261009T013421Z-complex-outer-axis-repaired/report.md)
checks24 cases in0.444 seconds:

- Eight h3/h4 cases cover the two modulo-four label classes on both axes.
  Their528,384 complete kernel coefficients and1,049,600 active child
  matrix entries pass. Complete physical matrices follow by exact XOR
  covariance; giant address matrices were not individually serialized.
- Sixteen cases at h7,10,16,24 check projection/radical dimensions,
  affine characters and closed Gauss units by independent orthogonal
  quadratic elimination. They do not enumerate those large address cubes.
- Omitting the line correction increases rank by one. Nonzero offsets
  and global units are explicitly checked as discriminating controls.

The [first attempt](../../runs/20261009T013341Z-complex-outer-axis-review/report.md)
failed because its basis routine did not reduce older pivots after adding a
new pivot, so equal subspaces had unequal basis lists. Independent union-rank
and idempotence checks established the mathematical identity. The original
source SHA256 is
`013bfd6666bfd12a8106cd86077b5bb71d745d98e07c0477c63c19d81763e93f`;
the [exact recovery patch](../../fixtures/complex/outer-basis-canonical-recovery.patch)
produces the successful source SHA256
`b4db409f7ff3e1a2d0dc55fdd8a84a6447931a66d5f66a1111db70fe51f735b6`.
Original logs and input bytes remain unchanged. The repair changes canonical
linear algebra, not the proposed phase or rank formula.

The synthesis agent independently compared direct convolution at this
canonical offset for all four h3 pairs and h4 pairs(1,7),(7,7), accepting
the closed unit. Its different chosen h3 offset72 for(1,7) differs from
this review's504 by an active V direction; both support charts are valid.

```bash
python3 -B research/integer-mult-breakthrough/code/complex/outer_axis_interface_review.py --workers 4 --output research/integer-mult-breakthrough/work/complex/<fresh-run>/results
python3 -B research/integer-mult-breakthrough/code/complex/verify_phase_frame_primitives.py
```

The analytic phase/rank result and exact finite interfaces are accepted
within this scope. Fixed-tape implementation, full source/sink/dirty
chronology, actual role stock and a complete asymptotic recurrence remain
open. No larger kappa is asserted.
