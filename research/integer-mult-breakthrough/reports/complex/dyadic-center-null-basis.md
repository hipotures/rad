# A reversible dyadic center/null basis for the five-subset family

Status: **CONSTRUCTIVE SCALAR LEMMA, EXACT FINITE INVERSES AND REVERSIBLE
SCALAR WORDS**. The required native phase chronology is still open. No larger
characteristic root or kappa is asserted.

## Why change the scalar basis?

For five-subset labels, the central polynomial is

    K(S,T)=(|S intersect T|-1)(|S intersect T|-3)/8.

It has unit diagonal and vanishes at distinct odd intersections. The side
matrix I-K therefore has support only on orthogonal binary labels. Previous
retained-output zeta circuits compute every self term before subtracting its
center contribution; their monotone compilation pays a separate final release.
This motivates factoring the whole scalar map through a shared center quotient,
without asserting that the separate releases are a global lower bound.

Let v=binom(h,5), q=binom(h,2). The pair bank P has P_ij(S)=1 when ij is
contained in S. Replace exactly the two rows 01 and 02 by D_ij=1-P_ij to
obtain G. The total is recovered dyadically:

    T=(sum retained P-sum two D)/8.

The existing dyadic decoder R gives K=R G. If an invertible basis B has G as
its first q rows, then G B^-1=[I_q,0]. Thus K annihilates the last v-q
coordinates and I-K acts as the identity there. This is a scalar coordinate
statement. It does not implement the identity as a free physical transport.

## Exact Smith discriminator

The [integer reducer](../../code/complex/center_null_basis.py) performs and
replays only unimodular integer row/column operations, checks the divisibility
chain, reconstructs both transformation matrices, and verifies the resulting
complete square basis and its two-sided rational inverse. Every central-kernel
entry and every null column is checked, without approximate arithmetic.

| h | Original pair-bank Smith invariants | Two-D bank invariants | Mixed inverse dyadic? |
| --- | --- | --- | --- |
| 8 | 1^20,2,4^6,20 | 1^21,4^6,32 | Yes |
| 10 | 1^35,2,4^8,20 | 1^36,4^8,32 | Yes |

The original bank has an odd factor five, so rational full rank would not have
justified a Gaussian-dyadic inverse. The two-D change removes that obstruction
in these complete finite tests. The [four-worker run](../../runs/20261008T232753Z-complex-center-null/protocol.json)
finished in 3.65 seconds. No Smith formula for every h is inferred from this
table; the following separate construction proves the required existence.

## Explicit all-h pivot construction

Start at h=7 with all 21 five-subsets as columns and all 21 pair features as
rows. For the original bank, identify a column with the complementary pair.
Its matrix A has entry one for disjoint pairs. Its inverse has entries 3/5
on equal pairs, -3/20 on pairs sharing one point, and 1/10 on disjoint pairs.
These formulas can be checked by counting disjoint pair intersections. If C
is the pair/point incidence matrix, A=J+I-C*C^T and C^T*C=5I+J. Thus the
constant, point and remaining subspaces have eigenvalues 10,-4,1 with
multiplicities 1,6,14, so det(A)=10*4^6.

Replacing two rows by T-P multiplies the determinant in absolute value by
1-2/10=4/5. The mixed base therefore has determinant 8*4^6=2^15. Its
inverse is an integer matrix divided by 32, retained in the immutable
[base fixture](../../fixtures/complex/mixed-center-h7-inverse.json). Both exact
products equal the identity, and the verifier rejects a corrupted numerator.

For a new point j, retain these j pivot columns:

- `{j}` plus each of the five four-element subsets of `{0,1,2,3,4}`.
- `{j,i,0,1,2}` for 5<=i<j.

The new rows are pairs `{i,j}`. They vanish on all earlier columns. On the
new columns the matrix is

    border=[[J5-I5,U],[0,I]],

where U has its first three rows equal to one. The inverse of J5-I5 is
`-I5+J5/4`, and the border determinant is four. Thus the global pivot minor M
is block upper triangular and

    |det M| = 2^15 * 4^(h-7) = 2^(2h+1),  for every h>=7.

This gives an explicit power-of-two minor, rather than only a greatest-common-
divisor argument about several minors. In pivot/nonpivot source order, keep
all nonpivot source coordinates. Then

    B = [[M,G_nonpivot],[0,I]],
    B^-1 = [[M^-1,-M^-1 G_nonpivot],[0,I]].

Both matrices are Gaussian-dyadic. This proves the scalar completion for all
h>=7 by an exact base and elementary induction. It is not formalized in Lean.
The [constructor](../../code/complex/structured_center_basis.py) checks every
new lower-left zero block, border determinant and both inverse products.
Four workers verify h=7,10,20,28 in
[the structured run](../../runs/20261008T233228Z-complex-structured-centers/protocol.json).

At those four scales the actual pivot inverse has denominator at most 32 and
numerators of at most five bits. Its observed nonzero counts are `(4h-7)^2`.
Those uniform bounds are measured finite structure, not an extra all-h theorem.
Dyadic existence follows without them. A subsequent [independent closed-block proof](../transfers/center-basis-independent-review.md) establishes grid32, inverse maximum1 and `(4h-7)^2` nonzeros for all h>=7, with explicit scalar-prefix bounds.

## A complete reversible scalar word

The [scalar compiler](../../code/complex/center_basis_scalar_word.py) factors
the base and five-by-five border using the exact Smith operations. Every gate
is a shear, explicit bank swap, or scale by -1,4,32. The inverse reverses the
gate order and inverts each coefficient. No bank is assumed to start at zero.
This component requires the same actual address operator on participating
banks, rather than only equal Lagrangian labels with differing local gauges.

Process diagonal blocks from oldest to newest. After computing one block's
output, add its cross terms from future block inputs, which are still original.
The lower-left zero blocks ensure that an earlier output is never needed as
an original input. Then add the retained nonpivot source contributions to the
first q outputs. The nonpivot inputs remain unchanged throughout. This gives
the complete B map on existing v arbitrary-dirty scalar banks with zero extra
banks. It is not a dirty copied-center echo and does not restore B's output
coordinates until its explicit inverse is executed.

Each source column of G has at most 12 nonzero entries. The total is exactly
`12v-4binom(h-2,3)`. Local fixed-size factorizations and the sparse cross terms
give O(v+h^2) scalar gates. Swaps are retained; a pointwise implementation can
expand a swap into three signed shears and one sign correction at a common
frame. No address or phase cost is waived by counting a swap once here.

| h | v | Scalar additions | Swaps | Scales | Additions/v |
| --- | ---: | ---: | ---: | ---: | ---: |
| 8 | 56 | 626 | 20 | 16 | 11.1786 |
| 10 | 252 | 2823 | 26 | 20 | 11.2024 |
| 20 | 15504 | 182692 | 56 | 40 | 11.7835 |
| 28 | 98280 | 1168704 | 80 | 56 | 11.8916 |

The [four-worker scalar run](../../runs/20261008T234334Z-complex-center-scalar-word/protocol.json)
checks the complete h8/h10 operator and inverse, plus four arbitrary dyadic
fields. It checks 133280 forward/inverse basis values, and a reversed
chronology without inverse coefficients fails. For h20/h28 it retains exact
gate counts and pivot inverses; it does not claim full v-by-v payload replay.

These gate counts are not the R auxiliary-role parameter or a child ledger.
An invertible data-basis map can use existing roles while still requiring
expensive transitions to a common address frame. The original scalar source
labels and full initial/final anchors remain explicit in `complete_word(h)`.

## Physical obligations and next discriminator

The initial source banks have different one-line C frames. Moving all of them
to full before applying B can consume the useful source geodesic intervals.
Undoing B at target continuation frames is also not free. A favorable complete
chronology must retain the actual source/sink conjugations, every common-frame
transition, all scalar swaps, dirty role continuation, and all auxiliary banks.
The fixed-source-basis zero-excess transport lemma cannot be bypassed by naming
new coordinates without paying the operation that creates them.

The inherited decoder still has 9/256 entries and endpoint weight 25. New scalar
scales and all prefix temporaries must also enter the precision guard. No old
seven-bit allowance or frozen PR36 guard is imported. There is not yet a native
child profile or a recurrence for this basis.

The next useful test is a whole basis/central/side word with q shared releases,
not v independently materialized self cancellations. The synthesis track will
audit all scalar incidences and physical endpoints. A plausible target crossing
requires a favorable complete moment, not just the small quotient or sparse
scalar word.

## Reproduction

```sh
python3 -B research/integer-mult-breakthrough/code/complex/test_center_null_basis.py
python3 -B research/integer-mult-breakthrough/code/complex/structured_center_basis.py \
  --h 20 --output /tmp/fresh-structured-center.json
python3 -B research/integer-mult-breakthrough/code/complex/center_basis_scalar_word.py \
  --h 10 --literal --seed 20261008 --output /tmp/fresh-center-word.json
```

Only Python's standard library is required. Output paths must be fresh. Every
protocol pins source hashes, scopes, case modes and raw log locations. Exact
reduction-operation JSON uses the gzip evidence contract before publication;
source, base fixture and compact reports remain readable. Independent scalar reviews are complete; physical phase integration remains open.

Complete h10 Smith operation rows are published in [original-bank gzip](../../evidence/20261009T001615Z-checkpoint-six-00/results/h10-original.json.gz) and [mixed-bank gzip](../../evidence/20261009T001615Z-checkpoint-six-00/results/h10-mixed.json.gz), each addressed relative to the topic root in the compact summary publication fields.
