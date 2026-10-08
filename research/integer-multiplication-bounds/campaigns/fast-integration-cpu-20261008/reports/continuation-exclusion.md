# Generic copied-center continuation frontier

## Result and scope

The unweighted pinned continuation is already optimal for the generic native
child moment among all maximum-cardinality matchings in the exported positive
label graphs at dimensions 23 and 25. This is an exact finite, scoped exclusion,
not a new multiplication saving. A separate implementation reproduced the
component decomposition, cardinalities and every nonidentical comparison.

The coordinator then extended the comparison to all matching cardinalities,
including the changed exterior bank and moment denominator. That stronger
extension has passed the coordinator's exact enumeration and is pending the
separate checker. The original maximum-cardinality conclusion is separately
reviewed. No claim covers changed producers, changed labels, fixed I+J native
profiles, other dimensions or other physical compilers.

## Inputs and experiment

The source is icekylinx's Apache-2.0 copied-center PR36, pinned at
`11817ccacb564bb7f98789c20dc11d3fece207e3`. Its retained scalar graph, positive
label construction and admissibility order are unchanged. The new mechanism
attempted is moment-aware continuation traversal; four traversal policies at
each dimension produced no improved witness. The two adverse controls did
change physical rank histograms, so the experiment was sensitive to choices.

The exported graph has 1,738 edges in 1,209 connected components at h=23 and
2,039 edges in 1,464 components at h=25. The largest component has four donors.
Exhaustion found 3,706 and 4,328 local matching states respectively. These are
sums over components, rather than claims to enumerate the Cartesian product
of all global matchings. Independent components make the objective additive.
The maximum cardinalities are 1,324 and 1,589. There are 46 and 25 nonidentical
native profiles among maximum-cardinality alternatives; every one is dominated
by the incumbent in the direction required by concavity.

## Exact comparison

For a rank-r factor edge at dimension h the inherited generic native profile is
`r` singletons if `2r<=h`, or `h-r` singletons plus one width `2r-h` otherwise.
A continuation with ranks `ru>=rv` and `rt>=ru` replaces physical histogram
entries `h-ru, rv, rt-rv` with `rt-ru`. Its rank change is exactly `-h`.
The checker reconstructs the native width difference, pads the shorter list
with zeros, and compares all descending partial sums exactly in integers.
The incumbent width list majorizes the alternative. Therefore its sum of
`width^tau` is no larger for every `0<tau<1` by concavity. Identical profiles
remain ties; the experiment does not claim a unique optimal matching.

For all-cardinality comparison let k be the number of matched continuations.
One bank role disappears per continuation, removing exterior children h and
`m-2h`, where `m=23*25=575`, and removing `m^tau` from `W*m^tau`.
Thus the additive numerator-minus-denominator change is the native internal
change minus `k*(h^tau+(m-2h)^tau)` plus `k*m^tau`. Its signed rank sum is zero.
The coordinator exhaustively checked 1,485 and 1,714 nonidentical comparisons
over all cardinalities with the same integer majorization method. None was
unresolved. Independent validation of these exterior and denominator charges
is the remaining acceptance step for the stronger exclusion.

## Recovery and attribution

Authored code is in [matching_discriminator.py](../code/matching_discriminator.py),
[moment_matching.cpp](../code/moment_matching.cpp), and
[continuation_frontier.py](../code/continuation_frontier.py). The scalar and
positive-label producer, original matching and copied-center physical schedule
belong to the pinned upstream contributors; source credits and Apache-2.0
license remain in the retained source and [license](../code/LICENSE.txt).
The independent review is [here](../agents/scout/continuation-review.md).
Input hashes are in [input-manifest.json](../input-manifest.json).

The useful implication is to change labels, actual producers or native
profiles rather than spend more search on traversal of this graph. PR38's new
fixed I+J profile is explicitly outside this exclusion.
