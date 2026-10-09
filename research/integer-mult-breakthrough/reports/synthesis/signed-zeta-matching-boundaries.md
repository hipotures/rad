# Signed-zeta directional and nonlinear matching boundaries

Status: **EXACT FINITE POSITIVE COMPLEMENT WORDS; RESTRICTED CAPACITY
OBSTRUCTION**. No faster native zeta supplier or multiplication exponent
is asserted.

## Changed source primitive

Write `F=T_h=[[1,0],[1,-1]]^tensor h`. A directed signed-zeta line
`T_(u,ell)` pairs address a with `a xor u`, where `ell(u)=1`, and applies
`(x_low,x_high) -> (x_low,x_low-x_high)` with low defined by ell=0.
It is an integer involution. Its source entrance can be represented by
one width-one T child under a paid linear address route.

For noncoordinate u, the origin column of `F*T_(u,ell)` has all `2^h`
nonzeros when wt(u) is even and `2^h-2^(h-wt(u))` when it is odd. For
coordinate `u=e_i` but noncoordinate ell, row `all xor e_i` has
`3*2^(h-2)` nonzeros. Either forces summed child width at least h for
any product of Z/T children with invertible monomial or diagonal wrappers.
Each width-r child has at most `2^r` nonzeros per row and column, and
these branching bounds multiply under composition. Arbitrary nonunit
diagonal coefficients and cancellations cannot increase this limit.
The ordinary coordinate orientation alone retains its h-1 complement
in this linear-direction model. All 28 and 120 oriented lines at h3/h4
verify the formulas exactly. This is a restricted adapter bound, not a
lower bound for arbitrary native algorithms.

## Nonlinear cover matching escape

Let M be any perfect matching of Boolean cover edges. Orient every pair
from lower weight to higher weight and apply the same triangular
involution. The resulting `T_M` is a nonlinear-address conjugate of a
single T1 child. A literal router maps child-bit-zero/one positions to
the low/high endpoint of each pair. The full address permutation,
control computation and workspace restoration must be paid; a table
of addresses is not a native routing proof.

Unlike a general linear direction, every cover matching has
`F*T_M` maximum row and column branching exactly `2^(h-1)`. For a row
a other than all, its contributing pairs number at most the vertices
of the subcube below a, hence at most `2^(h-1)`; the all row has one
contribution from every matching pair. The empty lower endpoint gives
a column of size `2^(h-1)`. This proves only the necessary branching
bound. It does not prove a one-child factorization.

An explicit scalable example chooses axis0 when an untouched control
bit2 is zero and axis1 when it is one. The complementary matching M'
chooses the other axis. They act within each fixed control sector, so
`T_M'*T_M=T_{0,1}`. Consequently

```text
F*T_M = T_remaining * T_M',
```

with child widths h-2 and 1. The source router is a controlled exchange
of axis0/axis1 (three controlled XOR operations); all controls, complete
address slots and required guards remain native obligations. The identity
uses no densely conjugated C supplier. A more general Boolean control
on spectator axes has the same algebra, with its own paid computation.

The complete finite factor search tests signed cover-matching T1
children, with no free gauge identification:

| h | Cover perfect matchings | Complements factored into h-1 cover children | Other complements unresolved in this factor model |
| --- | ---: | ---: | ---: |
| 3 | 9 | 9 | 0 |
| 4 | 272 | 232 | 40 |

The h4 search enumerates all 73,984 ordered two-child candidates,
retaining 39,603 distinct exact products. It exhaustively tests every
rightmost third child. A negative here excludes only products of three
cover-matching T1 children. It does not exclude bulk children,
non-cover matchings, nonunit gauges or other native implementations.

Only the h coordinate matchings have two disconnected equal-size
components in their complementary nonzero graph. The other matches
have a connected graph, which prevents representing the complement
as one `T_(h-1)` with only invertible monomial/diagonal wrappers. The
multiple-child positive words are thus structurally different from a
simple coordinate relabeling.

## Dirty return and complete canonical control

The reflected return is the actual `F*T_M*F`, since F is an involution.
It cannot be replaced by T_M without proving commutation. Exact
branching lower bounds are:

| h | Lower summed child width of reflected return | Number of matching primitives |
| --- | --- | ---: |
| 3 | 1, 2 | 3, 6 |
| 4 | 1, 2, 3, 4 | 4, 24, 156, 88 |

These are necessary support bounds, not complete minimal child costs.
A complementary source boundary alone therefore does not provide
the old geodesic dirty-helper return.

A complete control uses three data banks x,y,z with arbitrary dirty z.
Initial actual frames are `(T_M,I,I)`; the first virtual source is
`T_M*x_raw`. Move y and z to the actual T_M frame, then implement a
virtual signed swap using three four-shear dirty-helper commutators.
All twelve signed bank additions occur at exactly the same actual
operator. Finish x and z through `F*T_M`, finish y through F, negate
x and exchange the two labeled data banks. The actual raw outputs
are exactly `(F*x_raw,F*y_raw,F*z_raw)`.

The paid recursive width ledger is at least

```text
two width1 entrances + two h-1 complements + one widthh call = 3h.
```

There are W=3 complete payload roles. Every retained h-1 complement
word attains capacity equality. Unresolved complements have not been
assigned the optimistic h-1 implementation. For the displayed all-T1
complements, histogram `{1:2h,h:1}` has normalized moment
`1/3+(2/3)*h^b > 1` for every b>0. The same conclusion holds for any
complete capacity-equality profile with a proper child, independently
of its partition into child widths. The full-width call's mass is
1/3; it is not intrinsically forbidden by same-width recursion, but
the complete moment fails to contract.

All arithmetic in this literal word is integral, with no endpoint
fractional-grid loss. When the retained h-1 complement words are used,
the elementary implementation has the coarse prefix magnitude bound
`2^(h+13)*B` for input bound B:
the two entrance involutions have row L1 at most 2, twelve scalar
shears multiply a coarse bound by at most `2^12`, and a final full
tensor pass multiplies by at most `2^h`. For an unresolved complement,
the generic word `F*T_M` can use one extra matching pass, giving the
unconditional coarser bound `2^(h+14)*B`. Neither bound certifies
internal prefixes of an unsupplied faster T child. Final signs,
complete bank exchanges, nonlinear routes and every record buffer
remain part of a future native time/precision bill.

The finite control checks all 216 h3 and 13,056 h4 physical bank
columns across every matching, plus two complete Gaussian fields on
grids 0 and 3. A selected nonlinear h3 matching additionally checks
all 192 two-column physical bank columns and the two full fields.
The layout is explicitly column-major h-bit fields; this supplies no
free native transpose. Missing dirty return and replacing a required
full target transition by a matching both reject.

## An all-size origin-color release obstruction

Color every cover matching M by the coordinate i in its origin pair
`(0,e_i)`. If M and N have the same color, `T_N*T_M*e_0=e_0` even
when their other pairs differ. Thus `(F*T_N*T_M)*e_0=F*e_0` has all
`2^h` nonzeros. It cannot implement a whole-payload side path with
summed width h-2.

The conclusion also tolerates weighted triangular involutions
`[[1,0],[c,-1]]`. Same-color composition yields
`e_0+(c_N-c_M)*e_i`; after F, the entire i-zero half still has
coefficient one. Its support is at least `2^(h-1)`, again larger
than `2^(h-2)`. All weights are native scalar/precision obligations.

Under this declared short-side geometry, a central fitting matrix K
has diagonal one and zero off-diagonal entries within every origin
color. Every color is an identity principal minor. For v labels,
`q=rank K >= max color size >= v/h`. Therefore closed full-width
central release costs at least `2hq >= 2v`, exhausting the endpoint
saving from v width-one source anchors. Nonlinear matching labels
lift the old global coordinate restriction but not this closed-release
capacity barrier. Constant whole-payload complex K coefficients are
allowed; address-dependent matrix intertwiners and dynamic/reused
central lifecycles remain outside the argument.

All h3/h4 matching labels have equal origin-color sizes 3 and 68.
The auxiliary origin probe verifies every same-color ordered pair and
weighted dyadic controls exactly. It is not a proof that all possible
frames fall into these classes.

## Persistence and continuation

The [matching run](../../runs/20261009T052335Z-synthesis-signed-zeta-matching-boundaries/)
retains immutable source/protocol identities, compact readable results
and an explicit fixture. Its original full 674,363-byte certificate
contains every matching record; compact publication omits those rows,
names the original path/hash and leaves them unchanged for gzip
archiving. The matching producer is standalone standard-library code.
The [origin probe](../../runs/20261009T052905Z-synthesis-matching-origin-release-bound/)
imports only that pinned source.

From the topic root, reproduce in fresh paths:

```sh
python3 -B code/synthesis/signed_zeta_matching_boundaries.py --workers 4 \
  --output work/reproduce/<fresh>-matching/results
python3 -B code/synthesis/matching_origin_release_bound.py --workers 4 \
  --output work/reproduce/<fresh>-origin/results
```

The next positive direction must avoid a closed full-width central
return, use a different whole-word chronology, or supply an actual
address-dependent intertwiner. Continuing a matching portfolio sweep
within the excluded closed-release geometry has no exponent leverage.
