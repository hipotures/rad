# Independent review of the shared complex side circuit

Campaign clock: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.
Pinned original: `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

The new cancellation-free D/E circuit, binary frames, full-bank sharing,
unchanged guard constant, and decaying recurrence transfer pass independent
review for even ground sizes at least eight. The h50 side mixer uses
629,617 roles instead of 320,577,600. The tight composed strict witness is
`kappa = 96380770761102682050463/10^40`. This remains conditional on the
already reviewed phase-cell inverse and unaffected interfaces of the pinned
complete multiplication proof. No formal verification or broad novelty
claim is made.

## Circuit and scalar identity

The disjoint-source sum `D_S` and the intersection-two sum `E_S` give the
correction `(D_S-E_S)/2`. At intersections of sizes zero, one, two, three,
their sum with the original central coefficient `(|S intersect T|-1)/2`
is respectively zero, zero, zero, one. The full coefficient matrix is
therefore the identity after the central correction.

The weighted deletion recursion is correct by a disjoint partition. Pair
vertices into blocks. For an omission set, each touched block has at most
one survivor. A surviving edge is assigned to exactly the set of those
survivors it contains. The contracted far answer covers the empty set;
the corresponding component recursion covers each nonempty set and excludes
all other touched blocks. No omitted edge appears. Degree decreases in
the component recursions, and the contracted vertex count decreases.
Constants and weighted edges remain inside this recursion. Prefix/suffix
leave-one-out sums supply the E helpers.

Interning D and E separately is necessary: equal scalar sums do not
automatically have a common compatible binary frame. Shared original
inputs retain their same triple lines. The independent reviewer reconstructs
and checks every retained DAG support from its exact leaf bitsets and
disjoint child unions, then compares each D/E output against independent
stripe masks. At h50 this covers all 320,577,600 nonzero coefficients and
all required zeros. It does not rely on the producer's `verify_frames`.

The reversible mixer and signed chronological schedule are valid over
Gaussian dyadics:

```text
L, -J, L^-1, -R0, V, G, R0, L, J, L^-1, -G, -V.
```

Its dirty side contribution is `-JLz+JL(z+Vx)=JLVx`; its central
contribution is `-R0c+R0(c+Gx)=R0Gx`. Inverse mixers and copies restore
all scratch. Our independent sparse rational matrix expansion checks all
1,019 h8 coordinates, including both data banks, every side register, and
all central registers, in forward and inverse orientations. This is a
larger boundary than the producer's 963 source/side/central probes, which
omit the trivially unchanged target basis. The producer also checks an
actual signed three-stage h8 exchange with 175,616 values in each data
bank and 5,688,704 arbitrary dirty auxiliary values, including the reversed
and inverted stage2 chronology.

## Binary frames and exact excluded cases

The frame families are nondegenerate: triple lines have norm one,
coordinate bases have Gram I, pair-helper generators `t_P+e_j` have Gram I,
and a target kernel is the orthogonal complement of a norm-one triple.
All D ancestors have coordinate union of size at most `h-3`. At size
`h-3`, the unique compatible target determines the kernel immediately;
this avoids the alternating residual from a full outside-coordinate frame.
Active pair helpers have at most `h-3` third vertices, leaving a unit
outside their support for the terminal complement.

The independent code derives all these frames from DAG arguments and
output targets, rather than accepting the producer's special-node map.
It checks containment and norm-one witnesses for every distinct directed
frame pair and every terminal complement. For a full pair helper entering
the kernel of `S=P union {c}`, the residual witness is
`e_a+e_c+sum_(j outside S)e_j`, where `a in P`. Its weight is `h-1`, odd
when h is even; its dot product with the target and each helper is zero.

Reverse complements give exactly the same residual space:
`U^perp intersect V` for `U subset V`. Newly activated and retired roles
enter from the broad base and grow to the broad final frame. The early
mixers use the base frame, only the middle mixer uses these new families,
and the late cleanup uses the final frame. Thus no unsupported direct
transition from a frame to its complement is inserted. The full physical
timeline verifies every input and output boundary in both orientations.

Two exact negative controls establish the construction's scope. At h6,
disjoint triples partition the ground set; the line-to-target-kernel
residual has dimension four, full Gram rank, and zero norm on every vector.
At odd h9, the full pair helper's final residual has dimension two and is
also nondegenerate alternating. Neither has an orthonormal basis. These
are concrete interface failures outside the declared even `h>=8` scope,
not objections to its valid h50 construction.

## Stage joins, phase count, and guard

Partner flip `pi(T)={i xor 1:i in T}` is a bijective involution. Its
intersection with T is zero or two, so the corresponding binary triple
lines are orthogonal. Match stage1 bank `(A,B)` with stage3 bank
`(B,pi(A))`, preserving each local role index, including centers.
Arbitrary scratch restoration makes scalar sharing valid.

The joining labels are

```text
E = F tensor <t_A> tensor <t_B>,
H = <t_B tensor t_pi(A)>^perp tensor F.
```

They are nondegenerate, with `E subset H`. A tensor coordinate unit whose
middle index lies outside `A union pi(A)` lies in `H intersect E^perp`.
Such an index exists at h>=8. The join residual is therefore nonalternating
and has dimension `m-2h`; replacing the separate terminal edges removes
exactly m of phase rank and one physical role. Every remaining tensor
residual retains a norm-one witness from its local family or the original
coordinate argument. The common-frame identity and binary phase
factorization therefore apply without changing endpoint weights, signed
bank correction, fixed tapes, or coefficient formats.

Central returns remain the only decreases. At h50 the independently
recomputed shared counts are

```text
W = 498845589760000,
L = 2938824000000,
s = W*m - 2N + 2L = 62355689538576000000,
D = W*m-s = 9181424000000,
eta = 239/1623170000.
```

A new gate-count argument replaces the old bounded-touches explanation.
Four mixer passes, source/target groups and central gates use `4R+4`
grouped gates per invocation, because `R=c+2v`. Across `3v^2` invocations
this is fewer than `6W`, even after sharing. Saved-input evaluation of a
gate costs at most `2W^2` elementary coefficient operations. Thus
`12W^3+4s+4W+4 < 64(W+m+1)^3`. The old additive guard constant remains
valid. This is an actual new counting proof; physical wires need not have
the original twelve-touch bound.

## Decaying recurrence and all-margin ceiling

The new complex saving b exceeds the bit saving a. Hence `sigma=1-b`
is below `tau=1-a`, and the growing-geometric estimate is inapplicable.
The retained global K now gives a decaying sum, so the internal power is
`tau(1+c)`. Leaves still cost `sigma+beta(1-sigma)`. With `x=1-beta`,
the saving cap is `q=min(ac,a-tau*c,bx)`.

At fixed c, the limiting leaf choice is `x=q/b`. Besides the guard cap,
the prefix and CRT margins bound epsilon by

```text
1/[1+4q/b], 1/[1+c+q], 1/[1+q/a].
```

For c<=a, `q=ac`, and the score
`ac/[1+c*max(4a/b,1+a)]` increases with c. For c>=a, q decreases,
while `c+q=a+ac` increases; each active guard, prefix or CRT branch
decreases. Thus the scoped optimum is at `c=a`, giving

```text
U(a,b) = a^2/[1+max(4a^2/b,a+a^2)].
```

The prefix cap replaces the guard cap once `b>=4a/(1+a)`. The remaining
Gaussian margins permit approach to this ceiling with fixed positive
precision exponents. Both branches increase with a, and the guard branch
increases with b while the prefix branch is constant in b. Exact upper
primitive enclosures are therefore valid ceilings in this declared family.
This is not a ceiling for all multiplication algorithms. A stronger complex
primitive leaves the quadratic dependence on the bit saving intact.

The independent parameter audit checks three shared/unshared rows, all
30 strict conditions per row, longer exact logarithm enclosures, count and
guard identities, strict grid absorption and all four parameter cutoffs.
It also executes 680 complete stopped decaying recurrences. A separate
negative control shows the wrongly imported growing estimate can
underestimate even mandatory top-node overhead by an unbounded factor.
The tight shared row improves the previous accepted packed kappa by more
than `47419193/12500000000000`, about 3.79 parts per million. These are
exponent estimates, not practical runtime measurements.

Its common parameter cutoff is `log2(b_input)>=6640328716877726785`.
Additional prime, strict recurrence/logarithm absorption, and complete
machine thresholds remain explicit obligations. The common value is not
a complete all-input cutoff for the multiplication theorem.

## Evidence and reproduction

The [completed review run](../runs/20261008T004215Z-review-complex-transfer/)
contains final results, exact source/input hashes, commands, Python 3.14.4,
and a preserved earlier successful reviewer version. Independent peak RSS
was not instrumented; the protocol states this rather than inferring it
from the producer's separate measurement.

| Independent evidence | Count |
|---|---:|
| h50 reconstructed logical frames | 610,017 |
| h50 distinct nonzero residual witnesses | 1,006,767 |
| h50 distinct terminal-complement witnesses | 426,690 |
| h50 forward/reverse physical transitions | 3,620,902 |
| Dense binary frame/edge cases at h8/10/12 | 17,633 |
| Complete h8 scalar basis, both directions | 1,019 |
| Complete decaying recurrence controls | 680 |

The full h50 independent replay took 19.18 seconds on one worker. Source:
[review_complex_frames.py](../code/review_complex_frames.py),
[review_complex_boundaries.py](../code/review_complex_boundaries.py), and
[review_complex_assembly.py](../code/review_complex_assembly.py).

```sh
python3 -B research/integer-multiplication-bounds/code/review_complex_frames.py \
  --h 8 10 12 --output "$FRESH_SMALL"
python3 -B research/integer-multiplication-bounds/code/review_complex_frames.py \
  --h 50 --output "$FRESH_FULL"
python3 -B research/integer-multiplication-bounds/code/review_complex_boundaries.py \
  --output "$FRESH_BOUNDARIES"
python3 -B research/integer-multiplication-bounds/code/review_complex_assembly.py \
  --certificate research/integer-multiplication-bounds/runs/20261008T003550Z-downstream-complex-assembly/results/certificate.json \
  --output "$FRESH_COMPOSITION"
```

All acceptance checks use exact rational or binary arithmetic. No GPU or
floating residual is used for any claim in this review.
