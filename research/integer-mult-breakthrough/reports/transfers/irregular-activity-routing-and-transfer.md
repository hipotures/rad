# Guarded activity routing without power-of-two padding

Status: **EXACT FINITE ADDRESS-WORD EVIDENCE AND CONDITIONAL TRANSFER
INTERFACE**. The authored route accommodates every integer f >= 4 using
exactly 3f+12 existing complete K-bit address chunks. It stably compacts
selected action bits according to two immutable control bands and restores
all control bits, all twelve guard chunks, and every unselected bit plane.
It does not add a next-power-of-two address cube. The faster recursive
zeta supplier, its complete native allocation, and a new kappa remain
unsupplied.

## Mechanism and attribution

The starting point is the synthesis track's
[power-of-two guarded network](../synthesis/benes-control-fiber-native-interface.md).
This experiment uses its literal eight-rotation plus exceptional-repair
component, not its complete compaction algorithm. The two unchanged imported
sources are `benes_guarded_control_word.py` (SHA256 b3f85a39a2c737dd91ba9888b6fe94c2b6da79a3e386c75ba8cddd9dfd169242)
and its transitive `benes_control_fiber_probe.py` (0090d94c72943abc24ac77bf01db254134f5c4d069fce47e53c7747fc470b02f).
The former's whole compaction version had a control-label ordering issue
subsequently repaired by that track. This experiment calls only its frozen
local packed component and implements both control-label reconstructions
itself.

The arbitrary-size switching construction is proved below rather than
imported from a paper. Waksman's *A permutation network*, JACM 15(1),
159-163 (1968), [DOI 10.1145/321439.321449](https://doi.org/10.1145/321439.321449),
and the [1968 erratum](https://doi.org/10.1145/321450.321465) are relevant
bibliographic leads. Their full contents were not obtained in this attempt;
no theorem, implementation, or novelty claim is attributed to an unread
paper. Recursive permutation networks and the earlier Benes composition
are established background. The present result concerns their explicit
guarded composition and the nondivisible-width interface.

## An irregular switching network on actual wires

Let pi be a permutation of n actual wires. Pair adjacent inputs and adjacent
outputs; when n is odd, each end has one unpaired wire. On the input-wire
vertices put the input-pair edges and the pullbacks of the output-pair edges.
Each component is an alternating even cycle, a doubled pair, or the path
between the two unpaired endpoints. The odd-size path has an even number of
edges: its first and last missing edges belong to opposite pairings.
Consequently its endpoints may both receive color zero. Alternate the two
colors on every component. Duplicate edges are harmless.

The first switch layer sends color-zero wires into the ceil(n/2) subnet and
color-one wires into the floor(n/2) subnet. Each subnet has exactly one wire
per input and output pair. The same coloring fixes the final switch layer.
Recurse within those two subnet sizes. Merge their layers on disjoint wires,
putting identity layers at the end of the shorter plan. This gives depth at
most 2 ceil(log2 n)-1. The locations of switches depend only on n; their
binary settings depend on pi. No fictitious wire is inserted.

Complete a partial layer matching by pairing its unused actual wires with
zero-mask switches. The completed matching has floor(f/2) pairs and, for odd
f, one bypass wire. This completion changes neither the permutation nor the
address volume. The verifier exhausts all 5,913 permutations for n=1 through
7 and checks both the fixed skeleton and logarithmic depth.

## Twelve complete guards and every remainder

Write f=4g+u, with 0 <= u < 4. In each of three roles the physical full slot
has f+4 complete chunks. Four equal active quarters of length g have a real
complete guard each. Their starts, in chunk units, are

    0, g+1, 2g+2, 3g+3+u.

The u residual active chunks occupy positions 3g+3 through 3g+3+u-1, before
the last quarter. Thus the last chunk of the whole slot is also its terminal
guard. The selected positions of the residual chunks are not appended beyond
that guard. Starting from three canonical f-chunk bands followed by twelve
guard chunks, at most twelve guard placements and forty-eight role repairs
produce this layout. This conservative total of sixty whole-K exchanges
permutes existing chunks and records the resulting within-band label orders.
Undo performs the inverse exchanges.

Align each completed matching to the four active quarters. The first 2g
pairs occupy the two pairs of equal quarters. If u >= 2, one real residual
pair remains; an odd bypass is left fixed. A fixed linear selected-bit
permutation P on the action slot, together with P inverse on one control
slot, is implemented by six complete packed XOR words. The second full
control slot is the restored companion. A further six words undo this
alignment after the layer.

After alignment the switch masks are recomputed from the actual two control
slots. The first control is decoded through P and both controls through their
recorded original label orders. Settings therefore depend on the original
immutable controls, never on the action target or borrowed companion. Six
quarter words implement the first 2g controlled swaps. Each word reads a
distinct donor quarter and two immutable controls, modifies a distinct
target quarter, and restores a third complete companion quarter.

For the residual pair, move its two active chunks and the same four action
guards into the arrangement

    action A, guard; action B, guard; guard, guard.

This requires at most six whole-K swaps each way. Three packed shears
A xor= s B, B xor= s A, A xor= s B exchange their selected bits when the
immutable setting s is one. The final complete two-guard slot is restored
after every word. Undo returns all four guards to their previous locations.
There is no new companion bit, row, or scalar helper bank.

One layer uses at most 21 packed words and twelve extra whole-K exchanges:
six alignment, six quarter, at most three residual, and six inverse-alignment
words. Each packed word performs the imported eight literal rotations and
its complete exceptional correction, giving at most 168 such rotations per
layer. A compaction and its inverse use O(log(f+1)) layers. At every completed
layer both control slots and all action spectators are restored. Reversing
the layer order therefore gives the actual inverse, not a separately fitted
map.

## Finite evidence and meaningful failures

The [authored route](../../code/transfers/irregular_activity_router.py) tests
the full address integer, including all guards and all unselected planes,
against a separate direct stable-compaction reference. Four-worker controls
with f=5,6,9,17 and K=1,2,6,6 passed 1,024 seeded samples, all four active
control patterns, and their true inverses. These are sampled full addresses,
not enumeration of the entire large cube or a complete Gaussian payload
array.

The [guard-branch verifier](../../code/transfers/verify_irregular_route_shapes.py)
additionally tests f=4,5,6,7 at K=10. All 1,024 seeded samples pass. It counts
63,373 nonzero literal words outside the finite repair predicate and 53,685
inside it. These counts come from extra exact oracle classification; they
are not fixed-tape runtime measurements. Corrected forced zero-guard inputs
also pass and discriminate omission of the complete exceptional repair.
Omitted canonical control decoding and omitted residual swaps have explicit
endpoint counterexamples.

Two earlier guard-branch attempts failed because the required omission
negative had insufficient coverage. The first sixteen random probes rarely
forced a carry failure with long guards. A first deterministic input exposed
individual primitive failure but could cancel at the full f=4 endpoint.
Changing only that negative input to canonical action zero, first-control
value three, and second-control value one distinguishes the full word.
The positive routing algorithm is identical in all three source versions.
The failed attempts, both original source hashes, exact recovery patches,
and later successful controls are preserved in
[the repair record](irregular-routing-negative-control-repairs.md).

Current bounded checks also pass: the route at f=6,K=1 retains all 5,913
topology controls plus 256 literal samples; the shape verifier at f=7,K=10
retains 256 samples and 16,988/16,765 nonzero uncorrected/repaired words.
These use one worker each. All effective source hashes match before and
after each completed attempt. All source code and proof notes are
AI-assisted research artifacts, not formal proofs or external peer review.

## Conditional native bill

The actual native interfaces are the previously pinned selected-bit rotation,
complete exceptional-record repair, and arbitrary-width whole-chunk exchange
suppliers. Their source revisions and exponent are reviewed in
[the routing-exponent note](activity-native-routing-exponent.md) and
[the paid balanced-transfer review](pr163-paid-balanced-transfer-independent-review.md).
The finite Python masks, list indexing, coloring, and label searches are not
implementations of these fixed-tape interfaces.

Let V=M R be complete payload volume, A the address header size, and tau the
supplied exchange exponent. The conservative movement bill for this route
and its inverse is

    O(V [(fK)^tau+1] log(f+1) + V K^tau log(f+1)).

The second term charges the residual and stock exchanges; it can be absorbed
in the first for f>=4. Whole chunks are not free merely because their selected
bits are later ignored. Metadata and complete exceptional-record repair add

    O(log(f+1) [M(A^3+C_G(A)) + delta M A(R+A)]),
    delta = O(f 2^-K).

C_G must include both label decoders, construction of the stable permutation,
alternating-color route generation, and the current word's selected mask.
A serial fixed-degree polynomial bound is a proposed header interface, not
certified by Python numeric operations. Masks read a fixed number of immutable
control intervals, all disjoint from target and companion. Where the original
rotation ABI requires controls before the target, separately charge the fixed
number of complete block exchanges needed for those intervals. Merely calling
an arbitrary-mask oracle does not prove this adapter. Uniform A=O(global p),
f<=d<=p, R exceeding every fixed polynomial in p, and K/log p tending to
infinity make the displayed metadata and exceptional terms small relative to
V; those conditions must hold throughout the actual recursive family.

The completed address map is a permutation independent of payload contents.
It therefore transports arbitrary complete coefficient fields if the inherited
native component already transports and restores those full fields. The finite
sample tests alone do not establish that native contract. This source neither
allocates nested fixed tapes nor supplies a child zeta transform.

## New all-width activity interface

For a hypothetical shorter three-axis scalar zeta word, choose

    f = floor((e-12)/3),   e = 3f+12+u,   0 <= u < 3.

The same twelve complete guard ranges are present. The intended full e-axis
zeta target must apply twelve paid elementary Z1 gates on their selected bits,
and u further Z1 gates on the residual selected axes, exactly once. The K-1
unselected bits in each such range stay spectators. These costs cannot be
deleted from the target or confused with applying Z_K to the whole guard
range. Since the completed route fixes those selected guards, their elementary
preprocessing commutes with the completed active route; internal carry excursions
do not change that endpoint statement.

In each scalar gate of the hypothetical three-axis word, exactly one of the
four two-bit control patterns is active. Under a complete address cube, the
active width W has distribution Bin(f,1/4). For fixed control addresses and
inactive action bits, the first W complete action chunks after compaction are
an entire W K-bit cube. Their K-1 planes remain independent spectators.
Every other coordinate is a retained row parameter. Thus disjoint complete
fibers, rather than a few selected samples, determine the child volume weights.
All active children have width at most f<e/3.

If g is the number of literal scalar gates, the ideal power moment including
the paid selected guard/residual passes is conservatively

    Phi_e(p) = g E[(W/e)^p] + (12+u) e^-p
             <= g 12^-p + 14 e^-p,       0 < p < 1.

Jensen gives the inequality. It proves that a hypothetical g=11 word has a
strict large-e moment for p sufficiently near one; the fixed small-width
cutoff and every base cost would still have to be charged. No such eleven-gate
word has been found. For the ordinary g=12 baseline, W/f concentrates at 1/4
and bounded convergence gives Phi_e(p) tending to 12^(1-p)>1. Hence that
baseline has no uniform strict sublinear moment in this ideal ledger. The
finite guard term cannot rescue it.

This route removes the previously proposed power-of-two rounding and its
large residual call. It leaves a residual of at most two selected axes, while
using no extra address cube. That is a useful layout interface, not evidence
that the shorter scalar word exists.

## Stopping, precision, and remaining leverage

The direct activity ledger still requires, for K=d^c and a cutoff e>=d^beta,

    tau(1+c/beta) < p < 1,

as well as a strict complete child moment, uniform local overhead, and lawful
rows. Its selected-width saving is (1-beta)(1-p), not kappa. The original
ordinary routing exponent tau=1-2^-50 permits only minute saving in this
particular interface. Under the distinct conditional ordinary supplier in
the independently reviewed public PR163, 1-tau is about 0.000594323213359227.
For example p=9997/10000, c=1/10000, beta=1/2 fits the strict local power
comparison there and would give selected-width saving 3/20000 if all other
activity contracts and the shorter word were supplied. That numerical choice
is a hypothesis about this direct interface, not an integer-multiplication
claim or a transplant of the public network's exponent theorem.

The [geometric endpoint guard](geometric-nonunit-endpoint-guards.md), under
its explicit product-of-local-factor contract, can consume exponentially
bounded Z_w endpoints when child widths decrease geometrically. Disjoint
width classes combine by a maximum endpoint norm. A variable number of
complete fibers must not be replaced by a fixed-branching count: at most
g(f+1) classes per level and O(log e) levels give a log-squared node-count
term. This does not by itself certify exact grid behavior, disk normalization,
an unsupplied word's prefixes, or outer integer recovery.

The next decisive obligations are a shorter literal scalar word, complete
native mask/control placement, recursive complete-fiber allocation and undo,
uniform local rounding or exact-prefix guards, and an outer consumption proof.
Any substantially larger saving also needs a stronger exchange supplier or a
different cost organization. None of these is hidden in the finite route.

## Reproduction and immutable evidence

From the canonical worktree root, standard-library Python is sufficient:

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/irregular_activity_router.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/verify_irregular_route_shapes.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/irregular_activity_router.py --workers 4
python3 -B research/integer-mult-breakthrough/code/transfers/verify_irregular_route_shapes.py --workers 4
```

Optional `--output` must name a fresh ignored directory; existing paths are
rejected. Sources and exact task seeds are pinned in
[the route CI contract](../../configs/transfers/irregular-router-ci-contract.json)
and [the shape CI contract](../../configs/transfers/irregular-route-shapes-ci-contract.json).
Durable run directories preserve unchanged protocols, compact certificates,
launch receipts and failed tracebacks. Full source recovery is recorded in the
repair note. The publication inventory identifies their raw locations and
hashes; the coordinator handles gzip evidence and CI registration. No external
checkout is executed or modified by this package.
