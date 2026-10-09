# Independent review of scaled Gaussian product recovery

Status: **ANALYTICAL AND SOURCE REVIEW**, independently accepted under the
stated complete error and exact product contracts. No producer module was
imported or executed for this review. This is not a native multiplier,
whole-integer assembly proof, or claim of a larger exponent.

The reviewed [source](../../code/obstructions/rounded_product_recovery.py)
has SHA-256
`ea33343b73ce046e6bf39ff0032bf7de31d1da4526a30135f43f74b60c685788`.
The reviewed [report](../obstructions/rounded-product-coefficient-recovery.md)
has SHA-256
`c22845a842b9004059c002b355731d20e9a6f16369f97b471720d3f590cda149`.
These source identities bind this receipt; future changes require a new
review. The transfer track derived the algebra and constants independently
before inspecting the implementation.

## Integrality and normalization

Put alpha=(1+i)/2, beta=(1-i)/2 and
`C_1=[[alpha,beta],[beta,alpha]]`. It is exactly unitary. Direct expansion
of `C_1^-1 ((C_1 a)*(C_1 b))` gives

```text
q0=(a0*b0+a0*b1+a1*b0-a1*b1)/2,
q1=(-a0*b0+a0*b1+a1*b0+a1*b1)/2.
```

Each structure coefficient is +1/2 or -1/2. Taking the s-fold tensor
product gives coefficients +2^-s or -2^-s. The derivation is bilinear
over any commutative Gaussian coefficient ring, including
`Z[i][X]/(X^r+1)`. Thus `2^s Q_s(A,B)` has integral real and imaginary
coefficients for every complete Gaussian-integer input. Ordinary or
negacyclic polynomial multiplication preserves that integrality. The
recovery scale is an actual part of the target; recovering Q itself as
an integer or omitting the scale is invalid.

This says nothing about a smaller convolution, a sparse field ordering,
or a free evaluation/conversion map. The exact matrix and signed product
must be the ones in this contract.

## Complete error fields

For one length-r negacyclic record, coefficient signs at wrap can be
dropped in an upper bound. Young's inequality gives
`||P*Q||_2<=||P||_1||Q||_2<=sqrt(r)||P||_2||Q||_2`.
For an array of records, summing the squared record bounds and using
`sum a_j^2 b_j^2 <= (sum a_j^2)(sum b_j^2)` gives exactly

```text
||P*Q||_F <= sqrt(r)||P||_F||Q||_F.
```

The argument covers every coefficient of every record. Error directions
need not be independent, random, input-aligned or zero on padding.
Unitarity of C_s on that complete array means its exact forward and
inverse do not amplify these norms. If the actual forward results are
`C_s A+E_A` and `C_s B+E_B`, expand their exact product. Its difference
from the ideal product has norm at most

```text
sqrt(r)(||A||_F epsB+||B||_F epsA+epsA epsB).
```

The approximate inverse must meet its complete absolute tolerance epsI
on the ACTUAL perturbed product array. A guarantee on only ideal products
or basis/test inputs would leave a gap. Its error is added after the
exact inverse; then the exact scale 2^s multiplies the entire error.

Any rounded products, discarded fields, payload-dependent control,
normalization or inexact scale introduce additional errors. The current
contract explicitly uses exact full products and exact scale application;
they are not supplied for free by a numerical transform lemma.

## Sufficient reserve and exact recovery

The integer real/imaginary L1 bounds A1 and B1 dominate the input Frobenius
norms. Let `L=r*(A1+B1+1)>=1` and set

```text
t=s+ceil(log2 L)+4,
epsA,epsB<=2^-t,    epsI<=2^(-s-4).
```

Since `sqrt(r)<=r` and the forward tolerance is at most one, the product
part of the scaled error is at most `2^s L 2^-t<=1/16`. The inverse part
is at most `2^s epsI<=1/16`. Their sum is at most 1/8, strictly below
1/4. Every real and imaginary output coordinate has error no larger than
that complete norm. The ideal scaled coordinates are integers, so
nearest-integer rounding recovers each uniquely.

The source uses slightly finer per-coordinate perturbation grids to
meet these full-array tolerances, checks exact squared norms, and applies
its inverse perturbation after multiplying the actual perturbed inputs.
Its missing-scale, coarse-grid and skipped-inverse controls match genuine
premises of the proof. The author's nine-case PASS and 616 recovered
coefficients are retained producer observations; this review did not
independently rerun them.

The [unitary rounding contract](unitary-rounding-depth-contract.md) can
provide the numerical endpoint tolerances if the actual program satisfies
its complete state, local norm, injection-count and guard hypotheses.
It does not furnish a cheap program, previous integer multiplication,
record packing, native row layout, or outer carry recovery. Those remain
separate. In particular, this product-format lemma is different from the
original source-transform and whole-integer assembly.

Attribution: independent AI-assisted internal proof and source review;
no formal proof assistant or external peer review was used.
