# Independent review of paired-five scalar and cap components

Status: **ANALYTICAL SOURCE REVIEW WITH IMPORT-FREE SMALL EXACT CONTROLS**.
The fixed-bank five-cube correction, pair-star decoder, dyadic cap completion,
and named terminal-reader exclusion are accepted within their stated scopes.
Neither scalar rank nor the local inverse supplies a smaller physical dirty
stock or complete native supplier.

This review binds the unchanged sources
`paired_five_cube_discriminator.py` (SHA256 720cf5d50d3afe4072a91ab013a5516e1cd28f3902b04edc608aefe5257c49c8),
`paired_cap_dirty_completion.py` (e4b02d24bc93dd3f41279f07c312c637f9126da7f31191189448d4f49eaa87cf),
and `paired_cap_fanout_flags.py` (5ebf72e309c42f9b654cff84f0c05585da3cbfdbfebc5d7b6156f6ce31ce41df).
The author's reports are
[the five-cube and complete baseline](../complex/paired-five-cube-scalar-and-side-baseline.md)
and [the cap completion and fanout boundary](../complex/cap-dirty-completion-and-fanout-boundary.md).
The present source reads their bytes for provenance but never imports or
executes their functions. It reconstructs only the small coefficient and
support statements used in the deductions below. This is model-assisted
independent review, not external peer review or formal verification.

## The five-cube correction is fixed-bank arithmetic

On a parity class of five selectors, write a four-bit parameter u and append
its parity bit. Opposite parity gives the target class. The direct side entry
is minus f5 of the actual overlap, where f5(t)=(t-1)(t-3)/8. Independent
character summation reproduces all 256 entries of

    Q = H4 diag(-1 on weights <=2, +1 otherwise) H4 /16.

H4 squared is 16I and the diagonal signs square to one. Therefore Q squared
is I and Q is orthogonal. Its absolute entries are 1/8 or 3/8 and its row-L1
norm is 7/2. This is a sixteen-bank scalar mixer, not one flat Clifford address
child. The author's two paid Walsh words, sign gates, divisions and inverse
are a correct finite implementation. The reported 219 gates and temporary
prefix charges are source-reviewed here, not independently replayed.

The same-parity source labels span dimension five and have radical dimension
four. Their scalar outputs may be assigned to opposite-parity target caps
because every original source label is orthogonal to those targets. This
allows a common actual F_U at the scalar gates. Equal dimension alone would
not suffice: the actual representative, affine labels and units must coincide.
Mixing across the two different parity representatives remains unpaid unless
a literal adapter is supplied. Unmixing at the common full frame in the
original physical slots is algebraically coherent and preserves arbitrary
source data; its full native chronology is still a separate contract.

For a nonpartner pair i,j, set w=e_i+e_j. Every pair-star label is w plus an
odd three-label selector outside those two coordinate pairs. With at least
four outside pairs, their span is exactly the graph of the outside parity
functional, with basis e_c+w. Differences within a selected pair generate its
pair sum; modulo these sums, three-subset incidence generates the outside
pair-coordinate space. Since w has norm zero and disjoint support from c,

    (e_c+w) dot (e_d+w) = [c=d].

The center is consequently nondegenerate of dimension h-4. This argument
supports the author's stated p>=7 range; it does not import the earlier
singleton-star geometry. The small control explicitly checks a complete p7
star and its proposed basis.

The decoder identity follows without a large matrix: if overlap is t, the
source's ten pairs have counts binom(t,2), t(5-t), and binom(5-t,2) in the
both/one/neither classes. Their weighted sum is

    [16 binom(t,2)-9t(5-t)+6 binom(5-t,2)]/160 = f5(t).

All six possible overlap values are checked independently. The fixed divisor
five is real. A dyadic-only grid or the retained divisor-three guard does not
cover this decoder automatically. A localization, common numerator grid and
complete restoration proof must explicitly add the new factor. This is an
integration obligation, not a contradiction of the finite identity.

## Rank-three cap rows retain four or eight dirty banks

For j shared pairs, fix the source parity opposite the target parity when j
is odd and equal when j is even. Independent exact construction of the j3
four-by-four and j4 eight-by-eight side matrices agrees with the stated maps.
The j3 block has constant kernel and rank three. The j4 block has precisely
the three weight-two character directions active and five kernel directions.
Their first three actual rows, followed by all killed Fourier rows, form an
invertible matrix M. Exact rational elimination independently gives
determinant -1/8 at j3 and -32 at j4, and an entirely dyadic inverse.

Every target row is an integer combination of those first three actual rows;
its coefficients on the other coordinates of M vanish. The readable map is
therefore rank three. Nevertheless an arbitrary incoming bank vector has
nonzero killed-character coordinates. Those coordinates must remain until
M inverse restores the complete input. Removing even one parked coordinate
makes the declared transform singular, as the independent corruption control
checks. Thus four/eight banks become three readable plus one/five parked
banks. They do not become three physical banks.

The author's elementary compiler uses integer Euclidean shears and power-two
unit scales, with four paid gates for a bank exchange. Its inverse reverses
and inverts every gate. Source inspection finds the grid, product-temporary,
full four-field and missing-parked-bank checks correctly scoped. The 51/186
gate counts and their literal prefix bounds are producer evidence; this
review does not duplicate those complete words or the full field replay.
All scalar gates must still share an identical actual address frame. Input
aggregation, injection and later restoration do not follow from M inverse.

After aggregation, source bucket spans have dimensions 3 and 2 respectively,
and their common cap has dimension 5. A component that closes back to its
original input frames around the word/read/inverse pays

    2 * 4 * (5-3) = 16,    2 * 8 * (5-2) = 48

per parity block. Weighted over ten j3 and five j4 subsets and two parities,
these sum to 800. This is a named closed-wrapper bill. A delayed inverse at
full or a changed global dirty echo can use a different frame history; it
must retain the parked coordinates and show its actual endpoints rather
than subtracting this bill without replacement.

## Decoder fanout changes the geometric obligation

Each retained j3 row serves its own target pattern and the missing dependent
row's pattern. Each retained j4 row serves four patterns, including the
antipodal copies. For one fixed source/target cube pair, a single raw target
pattern spans 3 or 2 label directions, while an actual-row channel spans 4.
The whole Fourier-channel target class spans 5. All these local ranks are
independently reconstructed. No inference from the scalar rank is needed.

Let m=p-5 be the number of outside pairs and include every target cube with
the given proper intersection. At j3 each retained row has
8 binom(m,2) distinct recipients. For m>=3 the outside two-subset labels span
the even outside-coordinate space of dimension 2m-1. The two common patterns
add one independent difference, giving total target-label span 2m+1. The m=2
boundary remains the local span 4. At j4 each row has 8m recipients. The
outside one-label set has an affine difference span of dimension 2m-1; its
four common patterns add two independent differences. The total span is
2m+2. These formulas and recipient counts are independently checked at
p7/8/9/12, both parities. In particular p9 gives ranks 9 and 10, not the raw
single-pattern or scalar rank-three dimensions.

The pair-coordinate permutations and a shared-coordinate bit flip preserve
literal overlaps, parity blocks, rank and the premise that the selected source
cube is last. They therefore justify using the representative first J and
one parity in the author's expensive previous-support witness generation.
The first-three-row basis for the other blocks must be the transported basis,
with its actual role labels recorded. Symmetry is a counting argument, not a
free physical bank permutation.

## Accepted terminal-reader exclusion and its boundary

Assume the named monotone whole-source-cube ordering: every earlier cube's
literal nonzero side source remains in each target's accumulated frame. The
author constructs h-1 independent eligible previous source labels for every
recipient of the final cube's selected channels, excluding both its own cube
and the final cube. Hence that target's frame is already T perpendicular.
This review inspected the witness generator and its exclusions but did not
independently rerun all those witnesses. That is the finite premise supplied
by the author's exact source and results.

Distinct target lines give distinct codimension-one caps. Their Grassmann
distance is two. Under the retained one-column actual-frame child interface,
a single scalar carrier starting in the dimension-five cap and ending at full
while visiting n such common-frame reads must pay

    (h-6) + 2(n-1) + 1 = h-5+2(n-1).

The triangle inequality also permits arbitrary intermediate Lagrangians;
it does not permit dropping a fixed recipient frame. The excess over the
cap-to-full geodesic is 2(n-1). Ordinary phase or affine gauges cannot make
two distinct fixed caps identical. This conclusion prices the retained
columnwise frame interface, not an unproved entangled-column supplier or a
general nonunit multi-bank boundary.

Using the exact recipient counts, both parities and all J give the closed
last-cube excess per core

    120 [8 binom(m,2)-1] + 60 [8m-1]
        = 960 binom(m,2) +480m -180.

It equals 1740, 4140, 7500 and 23340 at p7/8/9/12. Three retained cores add
three times this amount. At p9 and p12 it turns the inherited positive
deficits 2016 and 34848 into -20484 and -35172. These independent counts
match the author's table without enumerating a huge physical network.
Aggregation, earlier reads, kernel retirement and native work are omitted
optimistically, so their addition cannot repair this named architecture.

This excludes that last-cube monotone ordering with separate common-frame
scalar readers. It does not exclude interleaved readouts, copied readers,
target-bank mixing, changed endpoints, frame support changed by a complete
paid cancellation word, shared parking, or dirty birth reuse. These are
meaningful possible escapes, not implemented components in this review.
The complete independent-edge baseline's separate moment failure remains
a scoped result; it is not a lower bound on all paired-five architectures.

## Evidence and next discriminator

The [import-free control](../../code/transfers/paired_cube_cap_review.py)
passed all four j/parity cases with four workers in the actual
`20261009T095844Z-transfer-paired-cap-review` attempt. It binds unchanged
reviewed source bytes before and after; it executes no producer. Its
certificate includes the complete small side matrices, integer decoders,
support ranks and closed terminal count. No random seeds or external package
are required. A bounded one-worker run retains both j values at parity zero.

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/paired_cube_cap_review.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/paired_cube_cap_review.py --workers 4
```

The positive continuation criterion is a literal interleaved or jointly mixed
readout using every parked coordinate and complete dirty endpoint, with its
source and target adapters paid. A scalar rank table or an unsupported
replacement R/v does not justify a broad sweep or a claimed exponent.
