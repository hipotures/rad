# Integral ballot center/null completion and a unit-shear word

Subset-closed ballot features give an integral, in-place center/null basis
for every `h>=k+r`, `0<=r<=k`. For odd `k=2r+1`, their central decoder is
dyadic without an odd division. A constructive Bier recursion implements
the complete basis and its inverse with unit integer shears and signs.
This is a scalar mechanism on arbitrary dirty banks at one common actual
frame. Gaussian chronology, native routing, inverse magnitude bounds and a
complete multiplication transfer are separate obligations.

The first [Euclidean source](../../code/transfers/ballot_center_completion.py)
established small integral controls but produced large temporary
coefficients for k=7. The improved
[unit-word source](../../code/transfers/ballot_bier_words.py) removes that
implementation problem in the same four small cases. Both attempts and
their different row/column layouts remain immutable.

## Feature family and the all-size minor

Use zero-based increasing subsets `a=(a_0,...,a_(j-1))` with
`a_i>=2i+1`, called ballot features. Include every such feature of size
at most r, including the empty set. This family is closed under subsets.
There are `q=choose(h,r)` features when `r<=h/2`.

The feature bank is `G[a,S]=1[a subset S]`, with S running over all k-subsets.
Choose q source pivots recursively. If r=0, choose one k-subset. At
`h=k+r`, use every k-subset. For larger h, retain the old `(h-1,k,r)`
pivots and add the new point to every `(h-1,k-1,r-1)` pivot. These two
families are disjoint and have total size q. Order features by the same
old/new split. Their square minor has the form

```text
M(h,k,r) = [[M(h-1,k,r), U],
            [0, M(h-1,k-1,r-1)]],
```

where U is a zero/one incidence block. Each new feature contains the new
point, so its old-source entries vanish. The new diagonal block strips
that point from both feature and source.

The base minor is unimodular. Complement each base k-subset S to an
r-subset R. The inclusion matrix P_r with unrestricted r-subset rows and
ballot-feature columns is unimodular, as stated in Theorem1.3 of
[Ducey et al., Integer diagonal forms for subset intersection relations](https://alco.centre-mersenne.org/item/10.5802/alco.406.pdf),
Algebraic Combinatorics8(1),2025,pp.29-57, DOI10.5802/alco.406.
Here `r<=h/2` is explicit. Subset-closed complement Möbius inversion gives

```text
1[a subset S] = sum_(b subset a) (-1)^|b| * 1[b subset R].
```

The square transform on ballot features is triangular by inclusion and
has diagonal signs. Therefore `M=C*P_r^transpose` is unimodular. The
block recursion proves the claim for every larger h. This analytical
deduction initially used the cited theorem; the constructive recursion
below independently supplies its required elementary incidence word.

The primary PDF was acquired at2026-10-09T01:22:37.605045+00:00,
1,034,271 bytes, SHA256
`61208446e3d5c1eb41f5381399a67cc82f676002e1fe93e7e4d182c288e4c7c0`.
Its official URL, ignored local path and recovery command are in the
[config](../../configs/transfers/ballot-center-completion.json). The
experiment does not load the PDF.

## Complete dirty basis and central decoder

Put the pivots first in the source order, followed by every nonpivot.
The actual full scalar basis is

```text
B = [[M, G_nonpivot],
     [0, I]].
```

Thus its first q rows are precisely G and its remaining coordinates
retain their original arbitrary dirty data. It is integral and has an
integral inverse; replacing the null identity by a zero bank would make
it singular. This is a center/null completion, not a spectral decomposition
of I-K or a free physical bank permutation.

For `k=2r+1`, let `f_k(t)=choose((t-1)/2,r)` and
`K[T,S]=f_k(|T intersect S|)`. This polynomial has degree r, is one on
the diagonal and zero at every distinct odd intersection. Its row space
is contained in the rational row space of ordinary degree-r incidences:
each lower-degree feature b is a rational sum of r-features containing b,
using the nonzero factor `choose(k-|b|,r-|b|)`. Since the q ballot rows
have an invertible minor, they span this same q-dimensional space.

Consequently the complete decoder is determined by its pivot values,

```text
D[T,:] = K[T,pivots] * M^-1, K=D*G.
```

No division is used in this expression other than f's dyadic values. For
integer t these values are dyadic: odd t gives an ordinary integer
binomial, while even t follows from Vandermonde with
`choose(-1/2,j)=(-1)^j*choose(2j,j)/4^j`. The finite check independently
compares every complete D*G source/target entry against f. It does not
infer an exponent from the scalar factorization.

## Constructive unit-word recursion

The improved source constructs P(h,r) on unrestricted r-subset rows and
ballot-feature columns, rather than using arbitrary Euclidean elimination.
For `h>2r`, partition both by the last point:

```text
P(h,r) = [[P(h-1,r), 0],
          [P(h-1,r-1)*E, P(h-1,r-1)]].
```

E selects the shared lower-degree feature coordinates. Add those old
original coordinates to the matching new coordinates before either
diagonal word, then apply the two smaller P words. If `h=2r`, the old
block is a complementary `(r-1)`-slice. It is a smaller P word preceded
by the subset-closed upper zeta transform and feature signs. Both branches
then use the smaller P word. The base r=0 is identity.

Every zeta edge is a single unit shear between features differing in one
bit. Transposing the elementary P word requires reversing its order and
reversing each addition's ports. Append the lower complement transform
to obtain M. For larger h, execute the old M word, add U from still-original
new pivots, then execute the new M word. Finally add every nonpivot feature
incidence. Exact reversal implements B inverse. All fields remain in-place;
the program uses no zero scratch bank, no nonunit scale and no unrecorded
integer quotient.

For fixed k,r, the recursive cross work is O(h^(2r)) by induction on r.
The full nonpivot gather has at most
`v*sum_(j<=r) choose(k,j)` unit shears, where `v=choose(h,k)`.
For odd `k=2r+1`, the complete scalar word is O(v). This is an operation
count under one common actual frame; it does not price fixed-tape bank
movement or claim those operations require no native scratch.

## Exact finite evidence and prefix scope

The Euclidean
[run20261009T012717Z](../../runs/20261009T012717Z-transfer-ballot-center-completion/report.md)
and constructive
[run20261009T013244Z](../../runs/20261009T013244Z-transfer-ballot-bier-words/report.md)
each used four workers on precisely the following four cases. They
completed in1.568 and1.314 seconds respectively. Each checks all526
full basis columns and exact inverse columns, and all126,836 central
source/target entries. Initial-null coordinates are included. Integral
operator equality extends those controls to every Gaussian dyadic field.

| h,k | v,q | Euclidean word gates | Unit word gates | Unit word inverse row-L1 prefix |
| --- | --- | ---: | ---: | ---: |
| 6,3 | 20,6 | 73 | 64 | 23 |
| 8,5 | 56,28 | 878 | 517 | 60 |
| 10,7 | 120,120 | 15,812 | 734 | 650 |
| 11,7 | 330,165 | 26,219 | 10,540 | 819 |

The two implementations document different feature and pivot orders.
Their pivot sets are identical by the block induction. At most
`2(q-1)` whole-bank exchanges align both orders, with every nonpivot
already in the same order. Even charging that upper bound gives at most
972 and10,868 scalar gates for the last two improved cases. Those
exchanges require paid native movement if the external layout is fixed.
The table compares complete representations rather than asserting that
different orderings are the same physical layout.

The Euclidean k7 base used a coefficient23,485,175 and inverse row-L1
prefix696,549,103; its h11 inverse prefix was6,187,660,842. Those figures
remain preserved as an implementation limitation. Every improved gate
has magnitude coefficient one. Its forward prefixes are20,56,120,330,
and its inverse prefixes are23,60,650,819, including every coefficient
times source temporary. The k7 pivot inverse maximum is64 and the decoder
common denominator16 with numerator maximum110 in both implementations.
The decoder coefficients refer to the documented feature order.

The improved forward bound extends analytically to every h for fixed k,r.
Each leaf base word reads original pivot fields; cross edges read new
original pivots before their own basis word. Completed rows are positive
incidence sums. Hence forward row-L1 is at most
`max(v,C_base)`, where C_base is the maximum literal prefix of the fixed
bases `(k-j,r-j)`. The checked k7 constants are120,28,6,1.
This controls the literal data components and multiplication temporaries
on a common frame. It does not include native bank-exchange buffers.

All forward and inverse gates are integer, so a common dyadic grid P is
retained without any added denominator bits. A **uniform all-h inverse
magnitude bound has not been proved**. The observed small prefix values
are not promoted to an all-size theorem. The inverse acts after a
nonpivot subtraction and may read fields already enlarged by another
block; that amplification needs its own bound or exact closed classes.

Negative controls in the unit-word run remove an actual scalar edge and
omit the required Bier transpose; both change the complete matrix. The
Euclidean run's large prefixes are a meaningful paid-control baseline,
not a failed algebraic certificate.

## Mathematical leverage and next obligation

This mechanism permits an integral k7 central basis even when a highest-
degree-only incidence basis has forbidden odd denominators. The odd-label
affine relative interface supplies a candidate rank-(h-1) address adapter
for its seven-element source labels, with a paid quotient flip and i per
selected column. Its closed central feature stock remains q and its
central-only loss remains2qh; neither is silently reduced by scalar
unimodularity.

The gather bound is64v for k7, so the integer basis alone does not certify
target leverage. A separately materialized closed I-K side is excluded
by the [conditional side obstruction](../obstructions/materialized-side-release-bound.md)
under its premises. A useful full circuit must instead intertwine the side
with legal source/sink geodesics or remove another named premise. Dirty
helper stock, affine routing, complete prefix guards and row/depth transfer
remain unpaid. No wider h sweep or new kappa is justified by these results.

Reproduce with Python's standard library from the repository root:

```bash
python3 -B research/integer-mult-breakthrough/code/transfers/ballot_center_completion.py --workers 4 --output research/integer-mult-breakthrough/work/transfers/<fresh-UTC>-ballot-euclidean/results
python3 -B research/integer-mult-breakthrough/code/transfers/ballot_bier_words.py --workers 4 --output research/integer-mult-breakthrough/work/transfers/<fresh-UTC>-ballot-unit/results
python3 -B research/integer-mult-breakthrough/code/transfers/ballot_bier_words.py --workers 1 --small
```

The bounded command exercises both k3 and k5 full matrices, inverse
columns, decoder and negative controls. Each full run pins its effective
source/config closure. The second source imports only the first source's
scalar arithmetic and incidence functions, not its config or any producer
module. No downloaded PDF is needed to execute the checks.
