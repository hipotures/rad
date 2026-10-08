# Independent layout review of guarded CRT reflections

Reviewed 2026-10-08 at 14:15 UTC. The candidate is the inverse agent's
[guarded CRT batching lemma](../inverse/reports/guarded-crt-batching.md).
This review supports its changed physical mechanism and identifies explicit
bank constants. It remains conditional on inherited fixed-tape bit primitives;
it is neither a numerical exponent certificate nor external peer review.

## Exact tree and joint monotone splitting

A balanced node has leaf products SL,SR and binary capacities TL,TR. Its
scalar coordinate k=A+SL*B is first mapped to

`(A, B+SL^-1*A mod SR)`.

The right node then holds `SL^-1*k mod SR`. Repeating this independently in
the children yields leaf coordinate `P_i^-1*k mod s_i`. Normalization factors
are essential; a tree computing only unnormalized residues would not match
the inherited tensor convolution convention.

The occupied-slot injection from the old node word to its two new fields is

`k=A+SL*B -> B*TL+A`.

It is strictly increasing because TL>=SL. Product injections over disjoint
nodes preserve the Cartesian source order. Thus a single full-capacity output
scan can consume the next valid source record at each occupied new address,
emitting zero at the remaining new addresses and skipping old zero padding.
The capacity is TL*TR at every node and exactly T globally; it is not rounded
separately at each level. Both the TL-SL gap and the last wider polynomial
leaf must be included in the occupancy counters.

After splitting, route LEFT words before RIGHT targets using a paid known-bit
coordinate permutation. Every node's offset depends on its own LEFT word and
constant endpoint descriptors, and on no other node's coordinates. The active
LEFT word is never a dirty bank. Node classes can therefore borrow actual
address bits from the inactive class without changing active offsets.

Each repaired completed node batch fixes all inactive coordinates and padded
node intervals. A later joint splitting/deletion scan must occur ONLY after
every primitive, outer repair, and borrowed-field restoration has completed.
Temporary validity during guarded additions or dirty predicate loads is not
the validity mask of a tensor consumed by a numerical operator.

## A conservative constructive bank allocation

Write N=log2(T)=d*ell+h with `0<=h<ell`. There are d-1 leaf widths ell and
one leaf width ell+h<2ell. All complete binary field words exist physically,
including zero-valued invalid prime addresses. This supplies full dirty ranges.

Use original ordinary rotations at the bounded first tree levels. Thereafter
the largest node width is at most `N/4+O(ell)`, while ell/N tends to zero.
Assign active nodes to two classes by greedily balancing their TOTAL binary
widths, rather than merely balancing their counts. Unsplit leaves are always
inactive donors. For sufficiently large inputs each active class has an
inactive complement of at least N/8 bits; this weak bound allows a generous
constant margin and also handles the last wider leaf.

For m active targets the primary U,T digits require2mG bits with
`G=6 ceil(log2(b+2))+6` and m<=d. Since `d log b=o(N)`, these occupy o(N).
Reserve an untouched suffix of width ell from the remaining inactive bits.
It contributes real enlarged records of size `Q*2^ell`, exceeding every fixed
polynomial in b. It is disjoint from U,T and every active endpoint/control.

The inherited masked-shear scratch spacing may use

`K_router=256 G_router`, `G_router=4 ceil(log2(b+2))+6`,

instead of its displayed64G. This larger fixed spacing improves its guard
estimate and leaves its `b^tau polylog b` cost unchanged. With
`H_router=ceil(N/K_router)G_router`, nine reservoir pieces occupy at most
`9N/256+O(log b)<N/16` eventually. They fit inside the conservative N/8 bank
after U,T and suffix ell are reserved. Using nine pieces at64G against the
N/8 bound would be an incorrect constant calculation.

For the repeated-source fanout one can alternatively supply three FIXED
inactive compact scratch fields directly: all sources are parity(U_i), all
targets are active RIGHT bits, and the chosen scratch avoids both. The
matching-specific three-cohort endpoint decomposition is unnecessary for
this standalone shear. Accepted original swaps place these fields and undo
their placement; every enlarged suffix record is scanned and restored.

Coordinate routers used for placement have their own complete restoration
and enlarged-spectator argument. They are applied to KNOWN named slots,
not to computed CRT residue keys. The controls and variable node lengths
have polynomial-size tape descriptors; they are not growing advice or
one persistent machine tape per node.

## Conditional reflection interface

`J(y)=a+b-1-y mod 2^L` is an involution that preserves `[a,b)` and its
complement exactly. Conditional complementation followed by guarded binary
addition implements J controlled by a dirty U parity. Its endpoint controls
are fixed outside all active targets. Predicate loads/unloads are whole-field
prefix-controlled rotations, with completed targets moved BEFORE U; no
nonlinear predicate is assumed to be an address-bit source.

The inherited XOR proof extends to repeated source positions because the
loaded digit list reads only bits outside the simultaneous target set. Each
completed shear fixes those sources and therefore the loaded word. This
explicit extension permits parity(U_i) to fan out to an entire target word.
It is a new justified extension, not an unchanged old contract.

Three partial reflections implement each valid-interval rotation. All guarded
programs are bijective even at dirty all-ones boundaries. Their actual reversed
primitive program gives an address inverse. The outer bad set is determined
by U,T all-ones digits; the ideal interval rotations fix those digits, so
the same bad holes can be extracted and filled after exact key sorting.
The inherited inner bit shear pays its own repair separately.

Both input operands must use the same CRT tree/layout and the opposite CRT
must reverse the repaired programs and monotone splitting. This is enough
to match the original algebraic map, provided the coordinator charges its
finite number of routes, scans, and setup terms at every tree level.

The supplied ordinary rotations, repeated-source shears, and known-bit routes
therefore support `O(V b^tau polylog b)` CRT movement with O(log d) levels,
conditional on the stated interfaces. The original O(dV) CRT row cannot be
removed using a bit permutation alone; this new reflection/dirty-bank program
is the substantive replacement.

## Evidence boundary

The inverse agent's finite checker validates the arithmetic program, actual
inverse, and bad-address repair. Our independent
[older-rotation and substitution control](code/check_crt_movement_obligations.py)
checks24,573 valid records in five prime shapes, charges525,376 payload-record
reads for the old forward/reverse schedules, and retains failures of a known
bit route, a monotone scalar-to-CRT embedding, and unrouted tensor convolution.
These scoped negatives explain why the new program is necessary; they are
not a universal fixed-tape lower bound.

Remaining full-multiplier obligations belong to the coordinator: accepted
native graph/moment bounds, global numerical error/recovery, precision and
prime setup, complete recursively shrinking multiplication charges, and a
joint strict parameter certificate. This review found no new bank or source-
dependency obstruction after the explicit spacing/count correction above.
