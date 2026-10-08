# Independent odd-ground h51 bit witness

The new h51 bit candidate passes independent finite promotion. Its complete
conditional multiplication composition is a separate arithmetic and interface
claim. This milestone continues campaign `20261007T222521Z`; its user-extended
deadline remains 2026-10-08 10:00 UTC (12:00 Polish CEST).

## Identity and exact construction

The immutable producer candidate is
`19945bccf2127679a684a457425017aade6746e66e51d0955fa7d1ff67cadf0d`.
Its [retained input](../runs/20261008T041200Z-review-odd51/results/candidate.json)
has SHA-256
`a5b91dce64ddb3b1660767fcea13a615df47146d25c88767124ed319c4041c2d`.
The weighted pair recursion uses cutoff 2 and positions
`[0] * 6 + [24] * 25 + [0] * 20`. The final position is unused and normalized
to zero.

Partition the first 50 points into consecutive pairs and distinguish point
50. For a common point below 50, remove its original pair and insert the pair
consisting of its orphaned partner and point 50 at the designated position.
For common point 50, retain all original pairs. Every local root therefore
has 50 points. Reuse the pinned weighted recursion; merge equal cross-group
sums and compile exact retained-controller chains.

The [independent reviewer](../code/review_odd_pair_witness.py) reconstructs
these orders from pairs rather than importing the producer's odd constructor.
It then expands all coefficients from graph arguments, checks physical
register values, and checks rational frame transitions from their defining
equations. The construction compiler is shared; validity is checked separately
and does not depend on its claimed optimality.

| Quantity | Exact value |
|---|---:|
| Binary additions c | 473,241 |
| Designated partial outputs q | 62,475 |
| Compatible retained links l | 33,451 |
| Physical side roles R = c + q - l | 502,265 |
| Input triples v | 20,825 |
| Ambient dimension m = 51 cubed | 132,651 |
| Data bank size N = v cubed | 9,031,399,015,625 |
| W = 2N + 2v squared (R + 51) | 453,752,231,686,250 |
| Decreasing dimension L = 3v squared 51 squared | 3,384,009,916,875 |
| D = N - 2L | 2,263,379,181,875 |
| s = Wm - D | 60,190,685,022,033,566,875 |

The compiled SHA-256 is
`5183963ce3e380f2017eeb51a9f83b7ee406ec8537b9053897464e63bd5e18e9`.
There are 51 bit centers. The complex construction's `h(h+1)` expression
must not be substituted for the bit construction's `h squared` loss.

## Odd matching and transfer premises

The independent matching partitions triples into three disjoint classes.
Triples avoiding point 50 use the explicit even-ground matching. A triple
containing point 50 and points in two distinct pairs flips both paired
points. A triple containing point 50 and a full pair cycles that pair through
the 25 pairs. The inverse flips again in the second class and reverses the
cycle in the third. The even-ground inverse also reverses its cycle.

The reviewer checks both inverse identities, every intersection size, and
all 20,825 images. Its image SHA-256
`78d26086f73dd84ba4a75e8bd7f8535b9b37976a0d8cc545cf9cafb2c9810c60`
matches the producer exactly. These checks establish the first/third-stage
auxiliary-bank joins for this new ground.

Odd parity does not change the rational frame argument. The form `I-J/9`
is nondegenerate at h51. Every common-point envelope satisfies the same
positive quadratic identity, and its complement is nondegenerate. The new
orders change graph topology but not scalar input/output names. All source
frames, target orthogonality and both physical directions are checked.
Consequently the existing generic bit interface applies with the explicit
51-center count above: only the three central returns decrease, the source
correction contributes N, and every auxiliary route has endpoints zero and
identity. The scalar forward/inverse/forward invocations exchange the data
banks and restore arbitrary auxiliary values.

## Evidence and scope

The [exact certificate](../runs/20261008T041200Z-review-odd51/results/certificate.json)
has SHA-256
`a1ee766e8705772432874250ce9e0398ce928fcb092569513f833f3e647518fa`.
It independently checks 70,471,800 nonzero partial coefficients and all
required zeros, 473,241 disjoint physical additions, 481,440 fresh copies,
494,066 logical frames and 2,897,494 physical frame transitions.

New nonuniform h7 and h11 controls check every input basis vector, including
all centers and dirty scratch, in both orientations: 436 and 3,065 coordinates
respectively. Two complete h7 shared exchanges, with seeds 1 and 109, each
execute 3,675 invocations and restore both arbitrary auxiliary banks. The
independent side reviewer additionally checks 429 and 3,054 dirty coordinates.
These are bounded controls; the full h51 dirty-input transfer follows from
the checked scalar program and generic restoration argument, not an
exhaustive tensor-sized simulation.

The reviewer took 103.688 seconds and peaked at 3,358,156 KiB. The recorded
wrapper took 106.764 seconds. Source and producer bytes remained unchanged.
One worker used the existing locked aggregate admission counter; the running
odd refinement queue continued throughout.

## Reproduction

Use the pinned math environment and original reference checkout at
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python code/review_odd_pair_witness.py --reference "$REF" \
  --candidate runs/20261008T041200Z-review-odd51/results/candidate.json \
  --output "$FRESH_RESULTS/odd51-certificate.json"
```

The [protocol](../runs/20261008T041200Z-review-odd51/protocol.json) records
exact source hashes, inputs, commands, timing and external logs. This is a
finite construction and conditional interface review, not an unconditional
integer multiplication theorem, formal machine proof or established novelty.
