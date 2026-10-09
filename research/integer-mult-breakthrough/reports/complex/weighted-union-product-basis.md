# A weighted-union product basis and the paid conversion boundary

Status: **EXACT FINITE ALGEBRA AND COMPLETE POLYNOMIAL PRODUCT CONTROLS**,
with **CONDITIONAL NATIVE CAPACITY ASSESSMENT**. Changing the product basis
reduces direct form incidences from `4^s` to `3^s`. The canonical input
conversion remains a full tensor operator, and no faster native conversion
or subset-zeta supplier is supplied. No new kappa is asserted.

## The changed product

The partial product algebra has unit `u=(1,1)` and generator `t=(1,-1)`,
with `t^2=-u`. Put `y=t-i u`. Then `y^2=-2i y`. For `s` commuting
generators and `D=2^s`, coefficient vectors in the y-subset basis multiply as

    m_y(f,g)[S] = sum_(A union B=S) (-2i)^|A intersection B| f[A] g[B].

This is a weighted union product. It remains valid when each coefficient
is a complete Gaussian negacyclic polynomial record: the proof uses only
commutative ring identities. It is not the canonical q product on the
original input coefficient basis.

Let `Z[S,A]=1[A subset S]`, and write `c=-2i`. Evaluation at all choices
`y_j in {0,c}` is

    E = Z diag(c^|A|),
    m_y(f,g) = diag(c^-|S|) Z^-1 ((E f) * (E g)).

The product has rank `D`, attained by those `D` Gaussian coefficient
products. The inverse powers are dyadic, because `c^-1=i/2`. Over integer
Gaussian coefficient inputs, the decoder numerator is exactly divisible
by `2^|S|`: weighted-union multiplication has integer Gaussian structure
coefficients. The literal decoder temporary still carries that denominator.
Exact trailing-zero removal requires complete field handling; it is not a
free precision rule for a native implementation.

The algebra has the multivariate free presentation
`R[y1,...,ys]/(y_j^2+2i y_j)`, where `R=Z[i,1/2]`, with exactly D
coefficient coordinates. Each two-root factor has unit root difference
`-2i`; repeated Chinese remaindering gives `R^D` without odd denominators.
This is outside the
[single-univariate monic quotient degree floor](dyadic-quotient-channel-volume.md):
that theorem requires one polynomial variable. The multivariate
presentation preserves coordinate volume but does not supply a cheap
ordinary integer-product encoding of its multiplication. The paid zeta
evaluation is still necessary in the present product word.

## The direct incidence floor changes with the basis

Multiplication by the coordinate basis vector `e_A` maps input column `B`
to row `A union B`, weighted by `c^|A intersection B|`. Nonzero rows are
precisely the supersets of `A`, so its rank is at most `2^(s-|A|)`.
Columns indexed by subsets of the complement of `A` give an exact identity
minor of that order. Thus its rank is exactly `2^(s-|A|)`.

The output bilinear slice for `S` has zero rows and columns outside subsets
of `S`. On those subsets it is the tensor power of
`[[0,1],[1,c]]`, whose determinant is `-1` and whose inverse is
`[[-c,1],[1,0]]`. Its rank is therefore `2^|S|`.

Applying the same rank-one incidence argument as in the
[canonical product boundary](product-slice-wire-boundary.md) now gives

    nnz(U)>=sum_A 2^(s-|A|)=3^s,
    nnz(V)>=3^s,    nnz(W)>=sum_S 2^|S|=3^s.

The evaluation and decoding matrices attain all three floors. This is a
representation-specific escape from the canonical `D^2=4^s` floor,
not a contradiction. The canonical coordinate basis consists of units;
most new coordinate basis vectors are zero divisors. Its minimum-rank
forms need not be dense characters of the original coordinates.

These are direct formula incidences. Shared zeta evaluation uses `sD/2`
ordinary additions, so its literal arithmetic time differs from `3^s`.
Neither count proves faster fixed-tape execution.

## Original inputs still require a full conversion

Since `e0=(u+t)/2` and `e1=(u-t)/2`, the one-axis source conversion is

    B = [[alpha,beta],[1/2,-1/2]],
    B^-1 = [[1,1-i],[1,-1-i]],
    alpha=(1+i)/2, beta=(1-i)/2.

All coefficients are Gaussian-dyadic, and `det B=-1/2` is a unit in that
ring. The complete identity is `E B=C`, including the phases and grid.
Consequently canonical consumption is

    q_s(a,b) = B_s^-1 m_y(B_s a, B_s b),    B_s=B^tensor s.

The finite word pays both source conversions, the full weighted product
and the output inverse. It recovers the canonical q polynomial records.
Deleting the source conversions is rejected. A new integer-product
architecture could choose the y basis directly, but it must derive actual
integer input loading, polynomial encoding, consumption and recovery.
No such architecture is furnished here.

### Can B be cheaper than a fresh transform?

No faster native tensor B time bound is established. There is an explicit
upper reduction to two same-width zeta calls. Define lower and upper
shears `L_b=[[1,0],[b,1]]` and `U_b=[[1,b],[0,1]]`. Direct multiplication
gives

    B = L_beta diag(alpha,-beta) U_-i.

Each nonzero-parameter lower shear is
`diag(1,b) Z_1 diag(1,b^-1)`. Upper shears follow by exchanging the two
addresses. Tensoring gives two same-width Z calls, address exchanges and
Gaussian-dyadic diagonal powers. The inverse reverses these factors.
This is an algebraic reduction; the full address routes, polynomial
records, scalar buffers and intermediate fast-Z guards remain paid.

Some narrower shortcuts are excluded. One Z tensor with nonzero monomial
row and column wrappers still has zero entries, while B_s is dense. A
full-support Clifford kernel has a row chirp, a column chirp and an even
binary cross term, so every four-entry cross ratio is `+1` or `-1`.
Nonzero diagonal gauges cancel from these ratios, and address permutations
only relabel them. B has ratio

    B00 B11 / (B01 B10) = -i.

Holding all other tensor coordinates fixed preserves this ratio for B_s.
Thus a single full-support Clifford/C tensor, even with arbitrary nonzero
monomial row and column gauges, cannot implement B_s. A narrower C child
has structural zeros and cannot do so either. Helpers, block mixing and
multiple incidence chronologies are outside this shortcut test.

More generally, a serial same-bank product of charged C tensor factors
of widths `r_j`, with monomial wrappers between them, has column support
at most `2^(sum_j r_j)`. B_s has `D` nonzeros in every column, so
`sum_j r_j>=s`. For `0<sigma<=1`, that serial profile has
`sum_j (r_j/s)^sigma>=1`; it does not provide a contracting B recursion
by itself. This is a paid-profile obstruction in that named serial model,
not a running-time lower bound or exclusion of a new B/Z supplier.

## Complete coefficients, polynomial encoding and guards

The [full repaired run](../../runs/20261009T061742Z-complex-weighted-union-repair/report.md)
checks `s=1,2,4,6`. All 266312 basis-product coefficients agree with the
weighted-union formula. Every E B=C and B inverse matrix column is
reconstructed. Input identity minors and complete output tensor inverse
matrices bind the exact slice ranks without relying on numerical rank.

Four seeded dense polynomial packets use `(s,r,p)` equal to `(1,3,4)`,
`(2,5,8)`, `(4,3,16)`, `(6,3,32)`. Both the new-basis product and the
fully paid canonical product use the
[pinned signed-radix record implementation](../../code/complex/partial_polynomial_product_packets.py)
SHA-256 `b9fff086ff47cf80cdb0073bd9cc62f4d3b62f45236fbaf2794a5bdd529bc0f7`.
Each word pays `D` Gaussian record products, or `3D` signed integer
products; the respective counts are `6,12,48,192`. It decodes all `2r-1`
real coefficients before negacyclic folding, totaling 2676 decoded
coefficients over both words. All 1064 counted Gaussian real/imaginary
endpoint fields agree with direct products and the canonical literal C
reference. These are arithmetic reference controls, not native tape timing.

The new-basis record operands have maximum signed lengths `29,108,108,199`
bits in these cases; fully paid canonical operands have lengths
`30,112,107,199`. The actual complete record is multiplied, not only one
component field. The earlier
[packet precision review](partial-product-packet-prefix.md) explains this
record-size distinction and the use of the previous multiplier.

For explicit analytical guards, use complex L1 norm and let input
coefficient norm be at most `A=2^p`. B_s has row norm at most `2^s`, its
integer numerator implementation has row norm at most `4^s`, and B_s^-1
has row norm at most `3^s`. E has row norm at most `3^s`, and Z^-1 at
most `2^s`. Intermediate partial zeta passes respect the corresponding
coarse bounds. The three-real-product Gaussian multiplication and its
recombination are bounded by `5r` times the square of the operand bound.
Thus the literal new-basis product's component prefixes are at most
`5r 18^s A^2`, and the fully paid canonical numerator word is at most
`5r 864^s A^2`. Coarse additional numerator guards of
`5s+ceil(log2 r)+3` and `10s+ceil(log2 r)+3`, respectively, are sufficient
for those named linear and component arithmetic stages. Full signed integer
product temporaries instead have up to twice their whole operand length.

A new-basis input on fractional grid P has product endpoint grid `2P`;
the literal decoder temporarily reaches `2P+s`. In the paid canonical
word, each B adds s fractional bits, multiplication doubles that input
grid, and decoding temporarily reaches `2P+3s`. Known zeros give the
canonical endpoint grid `2P+s`. Fixed-format padding can create further
literal multiplication temporaries and must be charged separately, as in
the earlier packet audit. These bounds cover the displayed literal
evaluation word; a future faster native Z/B supplier must prove bounds on
its own actual prefixes. Endpoint norm bounds alone do not cover it.

## Optimistic target capacity and the next decisive condition

The synthesis track is independently exploring a native subset-zeta
supplier. Its [existing exact C transfer](../synthesis/subset-zeta-primitive-screen.md)
uses two Z calls and paid dyadic chirps/diagonals. An independently proved
faster Z exponent could transfer to C with a constant number of calls,
without treating them as recursive same-size C oracles. Weighted-union
consumption supplies a different product interface using three Z calls.
All loading and consumption constants belong to a changed assembly.

An optimistic gate-level capacity model illustrates the potential scale.
Suppose an in-place Z_h circuit uses g elementary row additions. Each gate
acts on two of D address symbols. In f tensor columns, if complete paid
activity partition and compaction supply exactly the corresponding child
blocks, their volume-weighted active count has law

    w ~ Binomial(f,2/D),    parent selected width h f,
    Phi_sigma = g E[(w/(h f))^sigma].

For `0<sigma<1`, Jensen gives
`Phi_sigma<=g(2/(hD))^sigma`, even for finite f. At h=3, a **hypothetical**
g=11 word has bound `11/12^sigma`. Taking `sigma=4999/5000` gives a raw
saving `b=1/5000=2e-4`, comfortably beyond the frozen balanced assembly's
necessary threshold `20/189981`. The exact inequality
`11^5000<12^4999` proves contraction of this optimistic profile. The old
two inequalities would leave room for `a=3/20000`, and their resulting
`a/(1+a)=3/20003` exceeds `1e-4`.

There is currently **no g=11 word or complete activity compiler** in this
campaign. The capacity calculation is a conditional discriminator, not
a discovered recurrence. The g=12 baseline has first moment one and
cannot yield a positive saving under the same normalized profile.
Whole inactive alphabets, arbitrary payload fields, restored address
companions, selected guard chunks, same-width endpoint work, child row
counts, precision and fixed-tape compaction are outstanding. A full
profile could also add multiplicities absent from the optimistic model.
The native allowance is `V(EK)^tau`; raw moment slack must pay its actual
overhead and stopping conditions before any exponent is accepted.

Continue this family only if an exact better Z circuit or another
scale-changing supplier is found, or if a new assembly makes the changed
source basis natural while paying all conversion and recovery. Do not
launch a larger weighted-union scalar parameter sweep: its all-size
algebra is already determined.

## Reproduction, failure recovery and attribution

```sh
python3 -B research/integer-mult-breakthrough/code/complex/weighted_union_product_basis.py --workers 1 --bounded
```

Use four workers without `--bounded` for the retained full cases. The
closure is this source plus the pinned owned record implementation; both
use only the standard library. The initial
[failed run](../../runs/20261009T061653Z-complex-weighted-union-basis/report.md)
stopped because a local matrix list shadowed an evaluator function. Its
traceback and original source are unchanged. A current-to-original patch
and hashes preserve exact reconstruction; no scientific output was
accepted from that attempt.

Attribution: the complex track derived and checked the changed product
basis, rank minors, conversion boundary and complete polynomial word.
The synthesis track's exact zeta/C identity and live activity model are
read-only references; it has not supplied the hypothetical eleven-gate
word. All work is AI-assisted internal research, not formal verification
or external peer review.
