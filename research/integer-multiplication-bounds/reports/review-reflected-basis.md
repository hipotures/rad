# Independent review: the all-ones rational reflection

One explicit fixed rational basis change gives the accepted h51 R500703
bit graph the stronger primitive saving
`a=2609524868705289/(2*10^23)`, approximately `1.30476243435264e-8`.
It preserves the complete scalar circuit, role count, rational Gram
forms and frame transfer. The change is made before compiling the fixed
address table; there is no runtime basis-conversion call. A fresh final
composition, including its finite setup qualification, is required
before reporting a multiplication kappa.

The source [review_reflected_basis.py](../code/review_reflected_basis.py)
and repaired [run0541](../runs/20261008T0541Z-review-reflected-basis-repair/protocol.json)
are independent of the producer characteristic. The terminal
[certificate](../runs/20261008T0541Z-review-reflected-basis-repair/results/certificate.json)
contains complete exact small profiles, all h51 triple coefficient
controls, metric checks, full arbitrary-dirty modular payload checks,
and explicit strict characteristic inequalities.

## A fixed metric isometry

The ground metric is `H=I-J/9`. Define

`Q=I-2J/h`.

Since `J²=hJ`, `Q²=I`. Both H and Q are polynomials in J and commute;
Q is symmetric, so `Q^T H Q=H`. The ambient metric is nondegenerate for
h not equal to9. At the promoted h51, Q has rational denominators only
dividing51.

For an original triple indicator t, with `sum(t)=3` and `t^T H t=2`,

`u=Qt=t-(6/h)1`,

`v^T=(t^T/2-1^T/6)Q=t^T/2+(h-18)1^T/(6h)`.

Consequently `v^T u=1` and `Q P_t Q=u v^T`. At h51, the two possible
source coefficients are `15/17` and `-2/17`; the two dual coefficients
are `31/51` and `11/102`. Every coordinate of both vectors is nonzero,
for every triple. The independent audit checks all 20,825 h51 triples,
not a random selection, and reproduces the projector conjugation on
representative triples at eight ground sizes.

The uniform coefficient argument applies for every h>18. The exclusions
are real: at h6 a supported source coefficient is zero; at h18 an
unsupported dual coefficient is zero. Exact negative profiles distinguish
both cases. The first run's h6 negative comparison was written incorrectly
and is retained as a failed run with its executed source bytes; the repair
compares the actual diagonal pivot (0,0) with the claimed generic (0,5).

Apply `Q tensor Q tensor Q` to every ground factor in the already accepted
axis cycle `(3,1,2)`, simultaneously to all sources, gate incidences and
sinks. This tensor map preserves `H tensor H tensor H`. Each image frame
has exactly the old restricted Gram form: positivity and nondegeneracy
are preserved. Every old source containment, target orthogonality,
forward inclusion and reverse-complement inclusion is preserved.
Orthogonal projections conjugate as `P_(Q U)=Q P_U Q` in each factor.

The image of a coordinate envelope need not have the original coordinate
core/support representation. It is assigned as the isometric image of
that envelope; equality to the original support formula is not a premise.
The cancellation-free scalar graph and its formal coefficient map are
unchanged. The full independent R500703 finite promotion therefore
supplies those scalar facts, while the isometry supplies the new labels.

## The complete common-frame identity survives

Replace every old frame matrix M by `T M T^-1`, where
`T=Q tensor Q tensor Q` followed by the fixed cycle. All residual matrices
are conjugated by the same T; their rational ranks are unchanged. At
source/gate/sink interfaces, the common-frame differences still telescope.
An incidence whose two role labels were equal still has equal transformed
labels. Source corrections are transformed too; they are not removed.
The final endpoint difference remains I, so the completed external address
shear and role interchange are exactly the original operations.

Two complete finite-field dirty-payload controls exercise this argument
with a non-permutation rational reflection on three address fields,
modulo5. All 125,000 output entries, across two spectator prefixes and
arbitrary dirty arrays, agree with the required original endpoint shear
and role exchange. Omitting one incidence conjugation fails both controls.
These are exact complete arrays, not floating-point or zero-scratch tests.

## Uniform canonical profiles

For any rank-one projector `u v^T` with `v^T u=1`, `u_0!=0` and
`v_(h-1)!=0`, the rightmost-pivot lower/lower profile of its complement is

`(0,h-1), (1,1), ..., (h-2,h-2)`.

The first row's last entry is nonzero. Clear it in later rows. Rows
1 through h-2 reduce to `e_i-(u_i/u_0)e_0`, and pivot in their own columns.
The last row reduces to zero because `v^T u=1`. The same proof applies to
the tensor line `u_1 tensor u_2`, whose first and last dual coordinates
are products of nonzero coordinates. This is a canonical lower/lower
profile, not an arbitrary chosen basis of the image.

For middle-bank residuals `(I-P_t) tensor I_(h²)`, all triples now have
exactly two increasing source/target runs:

`h²(h-2)` and `h²`.

The latter includes the off-diagonal base pivot. Thus with
`J_mid=(R+h)v²`, the middle first moment is

`J_mid [h²(h-2)ln(h²(h-2))+h² ln(h²)]`.

For the two stage3 data families, the rotated residual is
`(I-P_3) tensor (I_(h²)-P_1 tensor P_2)`. Tensoring the two lower/lower
factorizations gives the canonical partial permutation. Each of the
h-1 base pivots has one increasing suffix run `h²-2` and one single
off-diagonal pivot. The exact data moment is

`2N(h-1)(h²-2)ln(h²-2)`.

These increasing off-diagonal blocks use exactly the earlier segmented
update and one recursive interchange. There is no gather or pivot-order
adapter. Two full middle and two full data tensor matrices reproduce
these profiles, including the off-diagonal blocks and total ranks.

For joined roles, the low-rank bound remains `t=m-4h` diagonal pivots
in at most `g=4h+1` runs. Their conservative moment is still
`(R+h)v² t ln(t/g)`. In the rotated basis the kernel contains
`F tensor u_B tensor u_piA`. Its first inner coefficient is nonzero,
so columns `0,h²,...,(h-1)h²` depend on strictly later columns in their
own block. None can be a canonical rightmost pivot, including after
earlier used columns are eliminated. Every increasing run therefore
has length at most `h²-1`. Two complete reflected joined matrices at h5
independently check the dense kernel relations, canonical rank, omitted
columns, all increasing run lengths and the low-rank diagonal bound.

## Rank characteristic and fixed tapes

The middle and data families are disjoint from joined roles and from
the retained individual rank-one calls. Their total ranks still sum to
`s=Wm-D`; no rank saving is inferred from a change of basis alone.
The stronger saving comes from actually grouping longer canonical runs.
The independent audit reconstructs these first moments with safe
64-term rational logarithm intervals, verifies the normalized strict
characteristic from [the uncapped review](review-uncapped-middle.md), and
accepts:

| Variant | Explicit primitive saving a |
| --- | --- |
| Reflected middle and joined | `11792927768720789/10^24` |
| Reflected middle, joined and exact data | `2609524868705289/(2*10^23)` |

Both are strictly above the matching uncapped unreflected witnesses.
The maximum child is still `h²(h-2)=127449<m=132651`; the full integer
main/tail construction, volume V/W, fixed tape stack and scratch/bitmap
restoration are unchanged. The deeper uncapped row bound remains
`W^D<p^2600`, with sufficient reservoir condition
`b^(1-epsilon)>10400(log2(b)+8)`. No old h-fold shrink is assumed.

## New finite table and precise limitations

The fixed rational factor table changes. In addition to the metric/frame
conditions, exclude primes dividing a denominator or a nonzero diagonal
entry of any canonical triangular factor, including the new h denominators.
There are finitely many fixed matrices and exclusions. One fixed odd q
outside this union makes every table entry and triangular inverse valid
modulo every q^b. This q is shared by the entire bit primitive, rather
than selected per recursive call. It has a fixed bit-encoding overhead;
the retained fixed-alphabet binary/radix transfer therefore retains its
asymptotic cost, with a possibly different setup/width constant.

The giant h51 table and an explicit common prime have not been materialized.
They remain finite, deterministically constructible setup with separate
eventual thresholds. A numerical cutoff must not be described as covering
an unknown table constant. The separate h28 complex scalar factors,
literal operation guard and precision argument are unchanged. No runtime
transform or additional same-width recursive child is present.

The repaired independent run used Python3.14.7, one worker, one thread per
numerical library, a 16GiB address-space limit and a 120s timeout. It
finished in 24.88s, 52668KiB peak RSS, zero swaps, and released its owned
reservation. Exact commands, seed659, hashes and full source paths are
in the protocol. The initial 22.13s assertion failure is preserved as
run0538 and `review_reflected_basis_v1.py`. The final multiplication
claim remains conditional on retained upstream dependencies and must
consume the newly reviewed characteristic in a fresh assembly.
