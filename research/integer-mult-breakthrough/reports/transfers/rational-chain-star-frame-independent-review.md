# A rational chain enlargement with a dyadic Gram inverse

Status: **INDEPENDENT EXACT FIXED-PORT GEOMETRY AND IDEAL MOMENT**. The
single frame replacement at operation 23272 is valid within its retained
rational previous/following ports and conservative source span. It reduces
the ideal child power sum for every p in [999/1000,1), while preserving
rank mass and scalar stock. Its actual Gram determinant is four and its
inverse is dyadic. No literal physical word, all-size compiler, global
characteristic root or multiplication exponent is certified here.

The proposal comes from the synthesis track's connected-frame experiment,
not from this review. The [complete candidate fixture](../../fixtures/synthesis/rational-frame-block-23272.json),
SHA256 `5758611bb6bfb2478f6df6b7bc244a4a17e3bf1e03e3c9e8276f011e9f88830a`,
retains every actual port basis, the original/current/proposed bases, all
source labels and the full three-block histogram delta. The reference
head is `15c702a929b7d640107a95e196186ad74e876c82`; upstream source/data
identities are retained in that fixture. This review reads it as data and
imports neither its producer nor upstream code.

## Actual chronology and scalar support

The ambient rational form is G=I-J/9 in dimension 24. Both actual previous
frames, of dimensions five and seven, lie in the proposed ten-dimensional
frame. Both actual following frames, of dimensions ten and 24, contain it.
The current nine-dimensional frame is contained in the proposal, and the
proposal remains inside the retained original twelve-dimensional frame.
Every involved frame is nondegenerate for G. All sixteen conservative
triple source directions are present; scalar cancellation is not used to
shrink this requirement.

The complete chronological width lists are therefore

    old: 4,1,2,15
    new: 5,3,14.

The zero-width new edge is omitted. Both lists sum to 22; with the actual
three-block multiplier, rank mass remains 66. The positive child count
decreases from twelve to nine. The histogram delta is minus three at
widths 1,2,4,15 and plus three at widths 3,5,14. These are distinct
properties: neither unchanged rank nor fewer calls alone proves the
power-sum improvement.

## Low-height star frames

Let z be a coordinate distinct from 0, let J be q further distinct
coordinates, and define w=e0+2ez, d_j=e_j-ez. For G=I-J_all/9 their
integer basis has exact Gram matrix

    [[4, -2*1^T], [-2*1, I_q+J_q]].

Its determinant is four. Its inverse is

    [[(q+1)/4, (1/2)*1^T], [(1/2)*1, I_q]].

Multiplying the two displayed matrices proves both formulas directly,
including q=0. This construction is independent of the ambient dimension
provided the distinct coordinates exist. It gives a rational frame with
a Gram inverse of denominator at most four and coefficients bounded
linearly in q. Among triple indicator vectors, its span contains exactly
those containing coordinate 0 and supported on {0,z} union J: all span
vectors satisfy total coordinate sum = 3 times coordinate 0.

For the actual proposal, z=23 and
J={2,3,4,5,6,7,8,9,22}, so q=9 and the inverse denominator is two. The
reported cleared integer determinant 13,947,137,604 equals 4*9^10.
It is not the actual rational determinant. The full coordinate projector
still has denominator six because G contributes its ambient factor of
three. Thus this Gram change introduces no new odd prime, while the
existing ambient and basis/interface exclusions remain required.

The family observation was developed jointly with the synthesis track:
this review independently derived the q=9 inverse from the fixture;
that track supplied the general-q extension, whose displayed product is
checked here. It is not a new local-ring or Clifford compiler.

## A strict comparison across the relevant powers

Set

    D(p)=4^p+1+2^p+15^p-5^p-3^p-14^p.

At p=1, D(1)=0. The derivative there is the logarithm of the exact rational

    (4^4*2^2*15^15)/(5^5*3^3*14^14)
      = 5189853515625/10851569165584 < 1/2.

Since log 2>1/2, D'(1)<-1/2. Also log 15<3: already the first five terms
of the exponential series at three sum to more than 15. For 0<p<=1,
every x^p is at most x, giving

    |D''(p)| < 9*(4+2+15+5+3+14)=387.

The width-one term has zero curvature. Consequently on [999/1000,1],
D'(p)<-1/2+387/1000=-113/1000, and therefore

    D(p) > (113/1000)*(1-p) > 0

for every p<1 in that interval. The complete three-block improvement is
3D(p). This interval includes the supplied external bit exponent and
p=1-10^-3. This is an exact analytic ideal-profile comparison; it does
not certify a new bit supplier after changing frames.

At p=999/1000, the independently reconstructed 48-bit integer-power
enclosure gives exactly the producer's lower gain
624778854771/281474976710656. No floating point or modular rank sampling
is used.

## Independent evidence and interface limits

The [independent checker](../../code/transfers/rational_chain_candidate_review.py)
imports only this track's frozen rational/modular matrix source, SHA256
`6297988b996bb76dc4e307abbf0dbef252e088b4c257866e381f2170a6c404fd`.
The first run began at `2026-10-09T09:02:54.291988+00:00` and passed in
0.4257 seconds using one process. It binds the complete fixture and all
ports, verifies the literal inverse, reconstructs the histogram and exact
power bounds, and checks the star family at q=0,1,2,9,22. Four negatives
reject a cropped actual future port, an extra source direction, omitted
three-block multiplicity and confusion between cleared and actual Gram.

Reproduce the one bounded candidate from the repository root:

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/rational_chain_candidate_review.py
```

The effective closure is this source, the frozen independent matrix
source and the candidate fixture; all imports are standard library beyond
that owned helper. Optional `--output` requires a new directory. Original
evidence remains in ignored
`work/transfers/20261009T090254Z-transfer-rational-chain-first/`; compact
unchanged exports and pins are retained in the matching durable run.

The unchanged scalar program and conservative support give a legitimate
fixed-port geometric candidate. Actual local-ring normal forms, arbitrary
dirty physical endpoints, shared generic bases, exceptional classes,
primitive routing, precision, setup and the full recurrence must still be
bound. Reusing the old numerical child profile without updating those
interfaces would be invalid. Enlargements at multiple neighboring gates
also need a joint chronology; this one-candidate certificate is not a
global frame optimizer or an invitation to an unmotivated parameter sweep.

Authored with OpenAI Codex assistance; proposed frame and upstream
provenance are credited through the retained synthesis fixture.
