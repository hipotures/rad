# Independent review: simultaneous rational kernel flags

A constructively defined fixed rational metric isometry gives the promoted
h51 R485680 bit primitive the explicit saving
`a=143492327855947419/10^24`, approximately `1.43492327855947419e-7`.
The proof groups one long canonical diagonal run in each of three
previously reviewed complementary-projector families. It preserves
all scalar maps, roles, frame ranks and endpoint operations.

This is an all-size construction theorem supported by exact small
instantiations. The giant h51 isometry, its full factor table and one
shared finite prime have not been instantiated. They are finite,
deterministically computable setup, with a separate eventual constant.
The deeper new bound is `p^66000`; the earlier `p^2600` bound is not
claimed for this construction. A new general-beta parameter assembly
is required before reporting a multiplication kappa.

The frozen [source](../code/review_generic_metric_basis.py) has SHA256
`4ad45dde7783479c822ef92329b2aba53c0cb62a069e78192ac594e9d1500489`.
The [protocol](../runs/20261008T0623Z-review-generic-metric-basis/protocol.json)
and [exact certificate](../runs/20261008T0623Z-review-generic-metric-basis/results/certificate.json)
record the accepted R485680 input, every reflection direction in the
small instances, exact profiles, strict characteristic and source hashes.
The certificate SHA256 is
`4946e2d26ff8553f8517f8895afac1fd2dd3600f0f5557a94da732ed92b09456`.
The Schur-profile question came from the campaign root; this independent
review gives the rational finite-family construction and its controls.

## Complementary-projector flag lemma

Let G be a nondegenerate rational symmetric metric on Q^m. Let Z be a
nondegenerate d-dimensional subspace, with `2d<m`, and choose a basis
matrix U. Define its orthogonal-projection dual

`V=(U^T G U)^-1 U^T G`.

Then `VU=I_d`, `P_Z=UV`, and `A=I_m-UV` has rank `m-d`.
Assume the first d rows of U and last d columns of V are invertible
square matrices. The first d rows of A have an invertible block in
the last d columns, namely `-U_front V_back`. Canonical rightmost-pivot
elimination therefore assigns those d rows distinct pivots in exactly
those last d columns. Their order is arbitrary; it is not assumed to
be an increasing source/target run.

For an interior row `d<=i<m-d`, eliminate that last block using the
first d rows. Its remaining row is exactly

`e_i-(U_i U_front^-1) E_front`,

where E_front comprises the first d coordinate rows. Thus it has pivot
`(i,i)`. Previous interior pivots affect only their own or earlier
columns. The first d pivots and the `m-2d` interior pivots already
account for the entire rank `m-d`; the last d rows are zero after
elimination. Right lower column operations do not change a future row
once the corresponding pivot column has been cleared.

Consequently the canonical lower/lower profile consists of d
off-diagonal pivots, followed by exactly one maximal diagonal run of
length `m-2d`, followed by d zero rows. The d off-diagonal pivots remain
individual children. No pivot gather, permutation adapter or runtime
basis conversion is required.

## One rational isometry for a finite family

The useful kernel collection is finite because h is fixed. Each member
is nondegenerate and proper. A single rational G-isometry can make
both flags invertible simultaneously for every member.

For an integer vector w with `q(w)=w^T G w!=0`, use the reflection

`R_w=I-2w(w^T G)/q(w)`.

It satisfies `R_w^2=I` and `R_w^T G R_w=G`. Under the reflection,

`U'=R_w U`, `V'=V R_w`.

A front flag changes by the rank-one update

`U_front'=U_front-2 w_front (w^T G U)/q(w)`.

A back flag changes by

`V_back'=V_back-2 (Vw) (w^T G)_back/q(w)`.

For a deficient square flag A of rank k<d, choose a nonzero left null
covector l and right null vector r. In the update `A-c u v^T`, exclude
the two linear equations `l^T u=0` and `v^T r=0`. Each is a proper
linear equation on w. For the front flag, this follows from the
surjectivity of the coordinate-front map and of `w -> w^T G U`.
For the back flag, it follows from the full row rank of V and the
invertibility of G. Outside the two equations, u is outside the
column span of A and v is outside its row span. A `(k+1)`-minor is
then nonzero, while the rank-one bound gives rank at most k+1.
The flag rank therefore increases by exactly one.

For an already invertible flag, the determinant lemma reduces its
preservation to excluding the quadratic equation

`q(w)-2 v(w)^T A^-1 u(w)=0`.

This quadratic polynomial is not identically zero. Choose a rational
nonisotropic `w in Z^perp`. Such a vector exists because Z is proper
and nondegenerate, hence its orthogonal complement is a nonzero
nondegenerate rational symmetric space. The reflection then fixes U
and V, and the quadratic factor equals the nonzero value q(w).
This witness is used separately for each polynomial; the selected
global w need not belong to any of these orthogonal complements.

Multiply q(w), all deficient-flag linear factors, and all full-flag
quadratic factors. Every factor is a nonzero rational polynomial, so
their product is nonzero. If there are F kernel spaces, the total
degree is at most `D=2+4F`: each of the two flags contributes degree2.
Coordinate-degree interpolation guarantees a nonzero evaluation on
the explicit integer tensor grid `{0,...,D}^m`. Enumerating that grid
is therefore a finite deterministic search for the next reflection.

One selected reflection increases every deficient flag by one while
preserving every full flag. Each transformed kernel remains proper and
nondegenerate, so the polynomial properness argument applies again at
every round, including for indefinite G. At most the largest kernel dimension
reflections suffice. Their product is one rational G-isometry T for
the complete finite family. This proof uses no unquantified genericity,
orthogonal-group density assertion or transcendental oracle. The
implemented small search tries reproducible integer candidates first,
then has the proven finite tensor grid as a fallback.

## Apply it only to the useful three families

Use the promoted delayed-frame R485680 scalar construction and
`G=(I-J/9) tensor (I-J/9) tensor (I-J/9)` at h51. Nondegeneracy holds
because h is not9. The three kernels are:

| Residual family | Kernel dimension d | Copies | Grouped run m-2d |
| --- | --- | --- | --- |
| Middle-bank complement | `h^2=2601` | `(R+h)v^2` | 127449 |
| Joined auxiliary/central roles | `2h=102` | `(R+h)v^2` | 132447 |
| Two stage3 data families | `h^2+h-1=2651` | `2N` | 127349 |

The middle kernel is a tensor line times the full other factors and
is nondegenerate. The joined kernel is the orthogonal sum E+K from
the reviewed intersection-one matching; each tensor summand is
nondegenerate and they are orthogonal. The data kernel is the
orthogonal sum of a tensor line times the full remaining factor and
its complementary factor times the remaining tensor line. Its
dimension is `h^2+(h-1)`. Its complement has rank
`(h^2-1)(h-1)` as previously reviewed. All satisfy `2d<m=132651`.

There are at most `v+v^2+2v^3` distinct spaces before removing
duplicates, so the family is fixed and finite. The construction
need not make flags generic for any other edge. Every other pivot
can retain an individual recursive call.

Assign the isometric image T(U) to every source, gate, auxiliary and
output frame, including the actual first-consumer frames of the
delayed clones. Restricted Gram matrices, positivity/nondegeneracy,
source containment, target orthogonality, forward nesting and reverse
complement nesting are unchanged. Orthogonal projections conjugate
by T. The same common-frame telescoping therefore preserves all
source corrections and final endpoints; `T I T^-1=I`. The endpoint
role interchange on arbitrary dirty arrays is the old operation.
Image labels need not be coordinate support envelopes or tensor
products. Their definition as images of the accepted nondegenerate
frames suffices for the rational transfer.

The scalar DAG, actual plan, R, W, L, D and all rational edge ranks
are unchanged. The complete fixed triangular-factor table changes,
because every incidence matrix is conjugated before compilation.
There is no runtime T call and no additional same-size recursive
child. This is a new frame construction, rather than a reuse of the
old factor-table bytes.

## Exact characteristic and deeper rows

Let `J=(R+h)v^2` and use the three run lengths from the table. Their
credited first moment is

`M=J r_mid ln(r_mid)+J r_join ln(r_join)+2N r_data ln(r_data)`.

Each such complementary profile has d additional single pivots.
All other edge ranks also remain single pivots. Thus the total
rank sum is exactly the old `s=Wm-D`. The checker reconstructs
all counts independently from h and R and agrees with every field
of the complete R485680 finite audit. It uses safe 64-term rational
logarithm intervals and downward `2^-256` rounding, and verifies

`D-a(s ln(m)-M)-a^2 s ln(m)^2/[2(1-a ln(m))]>0`.

This implies the actual strict recursion characteristic
`sum n_r r^(1-a)<W m^(1-a)`. The explicit a at the start of this
report is rounded downward from the certified interval; it has
positive exact slack. It is a primitive saving, not a final kappa.

The largest grouped child is now `r_max=m-4h=132447`. For every
integer invocation width `e>=2`, the main/tail construction gives
child width `r floor(e/m)<=r e/m<e`. The fixed tail has length below m
and uses the already reviewed constant-width crossing schedule.
The exact integer inequality `m^651>2 r_max^651` gives depth at most
`651 ceil(log2(e))`. The old shorter-depth claims are not used.

For eventual `e<=Cp`, `p>=C`, `p>=2^25`, and `W<2^49`,

`49*651*(2+1/25)<66000`

gives enough row stock in `p^66000`. The fixed C includes the new
alphabet and table constants. With the retained suffix reservoir
`ell>=p^(1-epsilon)/2`, the conservative explicit sufficient condition

`b^(1-epsilon)>264000(log2(b)+8)`

provides enough rows. Padding remains below twice the used volume,
and completed activation bitmaps/scratch are restored as before.
All child volumes, segmented modular arithmetic and fixed-tape
stack operations inherit the reviewed V/W construction. A final
assembly must explicitly verify this new condition and the eventual
`p>=C` qualification. The separate complex primitive's scalar table,
literal operation guard and precision argument are unchanged.

## What was executed, and what remains finite setup

Four complete simultaneous families at dimensions 5,7,9 and 12 cover
positive and indefinite rational metrics. They begin with deficient
flags, use 2,3,4 and 4 reflections, respectively, and verify every
rank increase, final dual Gram identity, full metric identity and
conjugation. All 12 resulting complete canonical profiles match the
flag lemma. A negative control without the flags leaves a fragmented
diagonal profile; another without `VU=I` has full rank.

A complete actual h5 tensor-metric instance includes two distinct
joined kernels of dimension10 and one middle kernel of dimension25
in ambient dimension125. Seven shared reflections raise each joined
front/back flag from rank3 to rank10 while preserving both full
middle flags. The resulting complete canonical profiles have runs
105,105 and75, with the correct ranks and top/off-diagonal pivots.
All exact integer directions and norms are retained in the certificate.

A complete finite-field common-frame control checks 62,500 output
entries on arbitrary dirty arrays with spectator prefixes. It includes
the transformed negative source correction, all gate incidences and
complementary sinks. Omitting one incidence conjugation fails.

The Python3.14.7 run used one worker, one numerical thread, a 16GiB
address-space cap and a 120s timeout. It finished in 8.71s, with 55868KiB
peak RSS and zero swaps, then released its owned reservation. The
exact command, seed683, source/input hashes and latest finite-queue
admission are in the protocol.

The full h51 family search, resulting T and giant compiled factor
table are not present. Their deterministic construction may be
astronomically expensive, but is a fixed finite computation.
Exclude primes dividing any relevant metric determinant, T entry
denominator, or nonzero canonical triangular diagonal/denominator.
One fixed odd prime outside the finite union works for the whole
primitive and every `q^b`; it is selected once, not per recursive
call. Binary/radix encoding has a fixed, possibly much larger width
constant. That setup and its constant remain separately eventual;
a numerical parameter cutoff does not cover an uncomputed constant.
The result remains conditional on the retained upstream transfer
dependencies and must be composed under general-beta constraints.
