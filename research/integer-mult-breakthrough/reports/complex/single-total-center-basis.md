# A single-total dyadic center basis with target-level capacity

**EXACT SCALAR COMPONENT / CONDITIONAL CAPACITY.** Replacing one pair feature
by the literal total gives an all-size Gaussian-dyadic center/null basis with
unit source-gather coefficients. A declared complete child profile can exceed
the required complex saving even when its old center cost is replaced by a
closed `2qh` release. No native chronology or larger kappa is certified.

## Mechanism

For five-subset sources, let `P_ij` sum all sources containing pair `{i,j}`
and let `T` sum all sources. There are ten pairs in each source, hence

```text
sum(all pair features) = 10 T.
```

Keep `T` and all pairs except `P_01`, for a total of `q=binom(h,2)` features.
Then

```text
P_01 = 10 T - sum(other pair features).
```

This identity uses integer multiplication and subtraction. The division by
ten that would be needed to reconstruct the total from the complete pair
bank is absent. It is essential that the total is an actual retained input
feature, rather than an uncharged scalar alias.

A weighted complement `2T-P_01` was the first algebraic stepping stone:
its total reconstructs by division by eight. Retaining `T` directly is
cleaner. In particular, every new source gather has coefficient one, avoiding
a per-source coefficient-two expansion penalty.

## Exact all-h dyadic completion

At `h=7`, identify a five-subset with its complementary pair. The original
21-by-21 pair-feature matrix is the disjoint-pair adjacency matrix `A`, up to
column order. Its eigenvalues are `10,-4,1`, with multiplicities `1,6,14`.
Equivalently, its inverse entries, classified by the intersection of the two
pairs, are

```text
equal pair: 3/5;  one shared point: -3/20;  disjoint pairs: 1/10.
```

The total row is `sum(A rows)/10`. Replacing the row indexed by pair 01 with
this total multiplies the determinant by `1/10`, cancelling the odd factor.
The absolute determinant is `2^12`. The determinant in the precise retained
row/column order is `-4096`.

For the inverse, the new total column is ten times the old pair-01 column;
its entries are `6,-3/2,1`. Every other column is its old column minus the old
pair-01 column. The odd denominators cancel, giving a grid of `1/4`. Both
complete base inverses are checked exactly.

For each new point `j>=7`, append the earlier structured five-subset pivots:
the five sets made from point `j` and four of `0..4`, followed by
`{0,1,2,i,j}` for `5<=i<j`. Append the pair rows `{i,j}`. The lower-left block
is zero, and the new diagonal block is

```text
[[J_5-I_5, U], [0, I]],
```

where the first three rows of `U` are one and the other two are zero. Its
determinant is four and its explicit inverse is dyadic. The pivots are
distinct because their maximum points distinguish blocks. Thus the pivot
minor `M` has absolute determinant `2^(2h-2)` for every `h>=7`.

Order all sources with these `q` pivots first. The full scalar basis and its
inverse are

```text
B = [[M, G_nonpivot], [0, I]],
B^-1 = [[M^-1, -M^-1 G_nonpivot], [0, I]].
```

This is an all-h dyadic existence proof. Uniform denominator four for the
whole pivot inverse is observed at `h=8,10,20,30`; the base and border
argument alone does not promote that observation to a uniform all-h bound.
The observed maximum pivot-inverse entry is six. That amplification and all
literal multiplication temporaries must enter the scalar guard.

## Reversible word and exact central decoder

The finite 21-bank base and five-bank border words use exact shears, exchanges
and scales. Apply older diagonal blocks first, then their additions from
still-original future inputs. The zero lower-left blocks make this order
valid. Each nonpivot original source adds once to the total and once to each
contained pair except pair 01. Nonpivot coordinates remain unchanged.
All banks initially contain arbitrary data; no zero helper is introduced.
The inverse reverses every gate and inverts its coefficient.

The source exposes `complete_word(h)` with the full literal source/pair
orders, bank count and total-feature index. It has been replayed on every
scalar basis column at `h=8,10`, on four arbitrary dyadic fields per size,
and against the complete central matrix. Both pivot inverses also pass at
`h=20,30`. Complete scalar forward/inverse values checked at `h=8,10` total
133,280; central entries checked total 66,640.

Write, with all numbers below divided by 32,

```text
alpha_ij(S) = 8 [ij subset S] - 3 ([i in S]+[j in S]).
beta_ij(S) = alpha_ij(S)-alpha_01(S), for ij != 01,
beta_T(S)  = 12+10 alpha_01(S).
```

Since `alpha_01` is `0,-3,2`, the total coefficient is `3/8,-9/16,1`.
All scatter coefficients have denominator at most 32. Substituting the
feature definitions gives exactly

```text
sum(beta_feature(S)*feature(T_source))
  = (intersection(S,T_source)-1)*(intersection(S,T_source)-3)/8.
```

Thus the diagonal is one and distinct odd intersections have central
coefficient zero. Decoder simplicity does not make its physical scatters,
undo operations or common-frame synchronization free.

## Scalar count and capacity discriminator

The total feature nonzero count is

```text
11v-binom(h-2,3),  v=binom(h,5),
```

instead of the previous two-complement `12v-4binom(h-2,3)`. The literal base
has 227 additions, eight exchanges and 13 scales. Its integer shear
coefficients expand to 277 unit additions. Each five-bank border has
18 additions, three exchanges and two scales; it expands to 22 unit
additions. The complete plain-addition count is

```text
11v-binom(h-2,3)+6+sum_{j=7}^{h-1}(3-j).
```

The capacity proxy expands every integer shear into `abs(coefficient)` unit
additions, charges four operations per exchange, and pays two scalar charges
for multiplication by four. It gives

```text
R_proxy = 11v-binom(h-2,3)+22h-47-(h-7)(h+6)/2.
```

This is conservative accounting for the specified scalar word only. It is
**not** an upper bound on all auxiliaries in an unbuilt native algorithm.
The remaining central decoder, side cancellation, source/sink transitions,
dirty echoes and phase adapters may require additional roles or children.
The envelope explicitly assumes the complete algorithm's actual `R` stays
within this declared proxy.

For each declared loss `L0`, use the full inherited shape

```text
m=h^2, N=v^2, W=2N+2vR,
children: 2vR at m-h, 2N at (h-1)^2,
          4N at h-1, N at 1,
          2v(hR+L0) further rank-one children.
total rank = Wm-N+2vL0.
```

All local residual rank is placed at width one. Exact outward log/exp bounds
evaluate `sum n*(t/m)^(1-b)/W`. The target is `b=20/189981`, the necessary
complex saving under the previously studied outer tradeoff.

| h | R proxy / v | Root bracket if old center cost is replaced by `2qh` |
| --- | ---: | --- |
| 28 | 10.975702 | `(0.000109875261, 0.000109875262)` |
| 30 | 10.978408 | `(0.000112120106, 0.000112120107)` |
| 32 | 10.980742 | `(0.000111706655, 0.000111706656)` |
| 34 | 10.982753 | `(0.000109746506, 0.000109746507)` |

All four target moments are strictly below one. The best of these, at `h=30`,
has only about 6.5% root margin over the target. The closed `2qh` loss must
**replace** the older center cost. Adding it to the single-total copied-frame
analogy instead gives roots from about `7.13e-5` through `9.02e-5`, all below
the target. An actual compiler must show which earlier calls disappear.

The copied-frame analogy `q(h-2)+2`, one traversal `qh`, closed release
`2qh`, and additive release are each retained as separate hypotheses.
None is inferred from the scalar determinant or a geometric minrank bound.
Bulk scaling by `f` belongs to the declared native profile; the coordinator's
single-label minrank lower bound cannot be multiplied by `f` automatically.

## Scientific boundary

The total source feature spans the entire binary label space. Differences of
five-subset labels span its even-weight hyperplane, and any one five-subset
supplies an odd vector. The total therefore requires its actual full frame.
It cannot inherit a pair-star's dimension `h-2` merely by occupying the old
pair-01 bank slot.

Scalar gates need identical **actual address operators**, including gauges,
while they mix. Equal virtual labels are insufficient. The exact dirty word
here restores the scalar coordinates at a common operator; it does not pay
the unequal source anchors or final sink continuation. Identical basis words
on source and sink copies with paired middle ports also retain the synthesis
track's crossed-endpoint obstruction. The new scalar basis does not remove
that obstruction by renaming its quotient coordinates.

The useful next discriminator is a changed auxiliary center echo or shared
quotient chronology that pays the full total frame and removes the previous
center calls. This is assigned for independent physical exploration. The
current result justifies that work; it does not establish kappa.

## Failures, provenance and reproduction

Two initial bounded attempts produced no accepted results. Capacity counts
were exact fractions with denominator one; the existing Decimal root helper
rejected their type. Converting the verified integral counts to integers
repairs that interface. The first basis assertion expected positive `4096`,
whereas its retained column order gives `-4096`; the absolute determinant
claim is unchanged. Both original sources and full logs remain immutable,
with exact zero-context recovery patches and separate attempt records.

The [local-word fixture](../../fixtures/complex/total-center-local-words.json)
retains complete base/border gates, both base matrices, source orders and
decoder semantics. The [independent scalar review](../transfers/total-center-independent-review.md)
accepts the complete basis and decoder, proves a uniform all-h inverse grid
of 1/4 with maximum pivot coefficient six, and gives a conditional scalar
prefix guard including multiplication temporaries. Physical synthesis is
reviewed separately; this is not a verified complete native algorithm.

Run the bounded closure from the correct worktree:

```bash
python3 research/integer-mult-breakthrough/code/complex/test_total_centers.py
python3 research/integer-mult-breakthrough/code/complex/total_center_basis.py \
  --h 10 --literal --output /tmp/fresh-single-total-basis.json
python3 research/integer-mult-breakthrough/code/complex/total_center_capacity.py \
  --h 30 --output /tmp/fresh-single-total-capacity.json
```

The basis run records complete scalar checks at `h=8,10` and pivot checks at
`h=20,30`; the capacity run records the four finite distributions separately.
Their protocols pin every authored dependency and all unchanged original
hashes. Python's standard library suffices. All arithmetic is exact.
