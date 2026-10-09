# Connected binary frame exchanges and local-ring compatibility

The frozen candidate is `binary-component-pairs-p12`. Its source graph, literal
XOR operations, source injections, partner-pair source mixing, compensated dirty
reads, selected gauges, target chains, center closure and physical role count
are those of the pinned PR161/PR163 p12 word. This contribution changes common
operation frames on connected groups. It does not change the scalar producer
or remove an operation, copy, center, exterior gauge, finish or fallback.

The source bit word is PR161 commit
`d14e29157bc905be1ced0776dd893d0714013f3a`, as retained and framed in PR163
commit `15c702a929b7d640107a95e196186ad74e876c82`. The later live PR163 head
`e1813796ef5c3ca38c5dd7b9e8d81b3908ff5997` changed attribution and source
inventory only, according to the separate frontier scout's comparison. The
immutable mathematical source used here is the earlier `15c702a` snapshot.

## Exact legal interval

For a connected group of physical XOR operations, let L be the rational span
of every node value span and every external incoming register frame. Let U be
the intersection of every external outgoing register frame. A common new frame
F is legal when `L ⊆ F ⊆ U` and F is nondegenerate for `G = I - J/9`.

Every operation uses one identical frame on its two registers. Both incoming
registers' preceding frames lie in F; F lies in their subsequent frames. All
root, gauge, source and final endpoints remain fixed. Consequently the complete
ascending chains remain legal, including center-phase operations. The node
value-span condition retains every original source label in its operation
frame. The independent exact checker verifies these conditions for the final
exported plan, rather than trusting the group's discovery score.

For an unequal-frame component pair, internal transitions become rank zero
after collapse. The discovery score includes every incoming, outgoing and
internal edge, retaining duplicate edges when both registers incur the same
transition. The full local histogram is then recomputed from every physical
register chain. Each such child has three invocations. Source-data and
target-data transitions, width-three-times-gauge exterior children, copied
centers and `2v` width-two finishes are retained. The complete normalization is
`m = 72`, `W = 2v + R = 26,888`; no changed local profile is spliced into an old
normalization.

This candidate has 576 accepted connected exchanges. Its final explicit plan
has 1,848 operation frames different from the original PR161 node-frame plan,
and 1,128 operations different from the 1,296-descended PR163 control. Some
connected exchanges replace or reverse earlier descents, so these counts are
not additive. The scalar operation count and role stock are unchanged.

## Exact rational identity of each frame presentation

The explicit plan supplies independent primitive integer basis rows B for each
rational frame F. The checker uses exact integer elimination to compute an
annihilator A, checks `A B^t = 0`, and checks

`rank B + rank A = 24`.

Therefore `span_Q B = ker_Q A`: containment follows from the zero product,
and equal dimensions give equality. The new determinant witness explicitly
stores the defining rows and dimension. It uses B for a small frame and A for
a frame whose annihilator is smaller. There are 1,176 distinct supplied
bases. The choice of equivalent presentation does not change any rational
frame, dimension, transition, gauge or operation.

## Projector and allowed local rings

Fix an odd prime q above `2^80`, retaining the source's exclusions for unchanged
frames, and let R be `Z/q^w`. All new determinant witnesses below are nonzero
integers of at most 63 bits. Thus each is a unit in R for every w. The integers
9 and `9 - 24 = -15` are units as well. The ambient cleared determinant
`9^23(9 - 24)` has magnitude below `2^80`.

For a frame represented by B, the witnessed integer Gram matrix is

`D_B = 9 B B^t - (B 1)(B 1)^t = 9 B G B^t`.

Its unit determinant makes `B G B^t` invertible over R. The exact projector is

`P_F = B^t (B G B^t)^(-1) B G`.

The Gram inverse supplies a right inverse to the defining rows, so they retain
their intended rank over R and their image is a free direct summand.

For a large frame represented by `F = ker A`, the witnessed integer matrix is

`D_A = (9 - 24) A A^t + (A 1)(A 1)^t`

because `G^(-1) = I + J/(9 - 24)`. Its unit determinant makes
`A G^(-1) A^t = D_A/(9 - 24)` invertible over R. The exact projector is

`P_F = I - G^(-1) A^t (A G^(-1) A^t)^(-1) A`.

This gives a split kernel of dimension `24 - rank A` and a nondegenerate
restriction of G. It avoids interpreting a particular enlarged integer basis
as a saturated lattice modulo q. Thirteen of the supplied large, scaled B
presentations have a primal cleared determinant above `2^80`; their smaller A
presentations define the same rational frames and have unit dual determinants
below the retained threshold. The proof and implementation use the A
projector for these frames, rather than ignoring a denominator.

The displayed projectors are G-self-adjoint idempotents. Their rational
denominators involve only the displayed Gram determinants, 9, and `9 - 24`.
All of these are units for every allowed q. Every exact rational value
containment and chain inclusion can be written as a projector identity, such
as `P_F chi_S = chi_S` or `P_U P_F = P_F`. Those identities reduce over R
because their denominators are units. Hence the containments and ascending
chains survive at every local-ring depth. For nested nondegenerate frames,
`P_U - P_F` is a G-self-adjoint projector onto a free direct summand of rank
`dim U - dim F`. The retained proper-projector compiler therefore receives the
same ranks as the exact rational ledger.

The new frame presentations add no excluded prime above the retained lower
bound, no larger rare-class envelope, and no uncharged conversion. The inherited
common-frame address permutations and projector adapters remain paid by the
same weighted local-ring compiler. These explicit finite projector witnesses
check compatibility with that all-size contract; they do not prove its
uniformity or construct a new analytic multiplication theorem.

## Complete finite word and native moment

Fresh formal replay checks all 26,888 independent source, target and arbitrary
dirty variables over F2. It also checks the unchanged defining integer decoder;
that integer decoder reduces to the identity only modulo two. All source and
dirty variables are restored. Dropping a compensated dirty read, dropping a
partner delivery, using a zero operation frame, or using an out-of-range plan
index is rejected. Source fingerprints are checked before importing the
retained program, and optimized Python is refused.

The complete profile has rank mass 1,934,000 and deficit 1,936, equal to
`2v - 3h(h-2)`. Every ideal child is positive and below m; the maximum child is
60. The complete edge count decreases from 319,644 in the PR163 control to
317,916. Each positive edge retains the full `32m^2` fallback on fraction
`10^-16`; `2m^3/2^80 < 10^-16` remains satisfied.

Exact rational log/exp enclosures accept the coarse grid point

`a0 = 37187295064613 / 62500000000000000`

and exclude the adjacent `10^-18` point for this fixed worst-case fallback
envelope. This is a native binary supplier saving. The first frozen composition
uses the conservative point `594996721/10^12` and retains atom stopping
`theta = 1/1000`, giving ordinary supplier

`A_B = 594440184179 / 10^15`.

The exact adapter inequalities `A_B < theta < 1 - A_B` remain strict. The
separately recorded finer atom choice is not substituted into the first frozen
composition. The binary saving becomes a final kappa only through the separate
complex supplier, precision, row-stock, routing, recovery and complete assembly
checks. An independent reviewer is responsible for fresh reflection and
conditional acceptance.

## Scope and attribution

The unchanged partner-pair K chronology and dirty-restoration argument are
eumemic's PR161 lineage. Paired cubes, modules and the paid ledger descend from
icekylinx PR144/130; Swapnil Jain/Zhihao Chen PR97, an664 PR128, ikeboy PR62 and
the h21 Fibonacci-strip word remain inherited contributors. Chafik Boukhalfa's
PR163 supplies the retained formal bit checker, 1,296 operation-frame descents,
moment enclosures and prime-witness approach. The paid stopping lineage credits
gupt1156 PR148 and Abhinav Ramachandran/geckods PR158. Exact original notices
and Apache-2.0 licensing must accompany reused source.

This connected-component search and frame presentation proof are prepared for
RaD/hipotures with OpenAI assistance. No unconditional theorem, global
optimality, new producer search, exhaustive physical-reuse impossibility, or
independent verification of all inherited analytic contracts is claimed.
