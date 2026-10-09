# Independent source review of the irregular activity route

**ANALYTICAL AND SOURCE-ONLY ACCEPTANCE WITHIN STATED SCOPE.** This review
accepts the exact address-word composition of the transfer track's
[irregular activity route](../../code/transfers/irregular_activity_router.py)
and the explicitly conditional cost interface in
[its report](../transfers/irregular-activity-routing-and-transfer.md).
The reviewer did not import or execute the producer, rerun its sampled
measurements, or certify a native tape implementation, faster zeta child,
recursive allocation, precision theorem or multiplication exponent.

The reviewed producer is SHA-256
`fbc75032544670ec60c00e43753b2d3bc139a464d9ed91b9b0fd4b77c8f179c3`.
Its two imported local word components are pinned by the source itself:
`benes_guarded_control_word.py` at
`b3f85a39a2c737dd91ba9888b6fe94c2b6da79a3e386c75ba8cddd9dfd169242`
and `benes_control_fiber_probe.py` at
`0090d94c72943abc24ac77bf01db254134f5c4d069fce47e53c7747fc470b02f`.
The source-only protocol records exact hashes of these files and the read
report. The latter can acquire publication links later; this review's
algorithm pin is unchanged.

## Fixed network and odd widths

The alternating-color construction is consistent for every integer wire
count. The two pairings produce even alternating cycles or a path between
the unpaired input and the preimage of the unpaired output. In the odd case
those endpoints miss opposite matching types, so the path has even length
and both endpoints can receive color zero. If they coincide the component
is a singleton. Collapsing duplicate edges into a set preserves the coloring
constraint for doubled pairs. The resulting subnet assignments are complete
bijections of sizes ceiling and floor of half the wire count.

Recursively merging the two disjoint subnets gives the stated logarithmic
depth. Their switch locations depend on subnet sizes, hence on the original
wire count, while the requested permutation changes only switch settings.
Completing unused wires with zero-mask pairs adds no address bit and preserves
that fixed skeleton. The exact finite topology census in the producer is
additional evidence; this review does not relabel it as its own execution.

## Actual slots, label recovery and masks

For `f=4g+u`, the four quarter starts `0,g+1,2g+2,3g+3+u` put a complete
guard after every equal quarter. Residual chunks occur before the fourth
quarter, and the last whole-slot chunk is a guard. The selected-position
alignment permutes only actual active positions and fixes every guard
and unselected plane. It never pads the network to a larger power of two.

The initial twelve guard placements can spoil at most twenty-four active
labels in addition to the at-most twenty-four band-edge mismatches. The
remaining active role counts are balanced, so each role-repair exchange
can choose a still-wrong donor and fix at least its target. This justifies
the conservative bound of sixty complete-chunk exchanges. The full
within-band orders remain tracked rather than silently normalized.

The six-word full-band alignment has the exact endpoint action
`(x,y,z) -> (P x,P^-1 y,z)`. Before deriving switch settings, the source
decodes the current first control through `P` and both controls through
their recorded canonical label orders. It therefore classifies the original
same-column control pair. The action is routed through the corresponding
conjugated wire permutation. This addresses the earlier control-order
hazard in the synthesis track's old whole-compaction version.

During a quarter word the current donor quarter is distinct from the target
and borrowed companion. Switch settings use the two restored external
control bands. Those bands do not change during the quarter word, so the
setting is stable across the eight packed rotations. The donor and companion
restore at every complete word boundary, after which the next shear may use
the updated action donor. Native computation may recompute the setting from
these immutable controls; treating the simulator's saved list as free
persistent metadata is unnecessary and would be a different interface.

If a residual pair exists, its two action chunks and four existing action
guards are placed in six chunks, forming three equal complete two-chunk
slots. Three controlled shears use the donor action bit, an external fixed
switch setting and the two-guard companion. Placement and undo each use at
most six whole-chunk exchanges. Every displaced active chunk returns.
No guard from a controlling slot is borrowed or transiently changed by
this residual word. The final inverse alignment restores both external
controls, permitting reversed layer order to supply the actual inverse.

## Paid and conditional boundaries

The per-layer count includes six alignment words, six quarter words, at
most three residual words and six inverse-alignment words: at most
twenty-one packed words. The residual placements add at most twelve
whole-chunk exchanges. The separate stock placement/undo cost remains
paid. A rank-zero, zero-switch or spectator endpoint does not justify
dropping its literal routes.

This acceptance is conditional on the imported packed-word contract
transporting complete long records, fixing every donor/companion endpoint,
and correcting all exceptional records. A Python integer permutation or
mask value does not itself prove a fixed-tape runtime. The producer's report
correctly charges mask computation, canonical decoders, coloring, exceptional
repair and placement of control intervals before a target where required
by the original native ABI. Its movement bill retains the supplied exchange
exponent and the growing selected width.

The selected-only action permutation leaves all controlling chunks and
guard planes fixed at the complete endpoint. Thus complete active fibers
have the claimed mathematical cube shape; actual grouping, child tapes,
row allocation, exact endpoint arithmetic and rounding still require their
own interface. In particular, the conditional binomial moment for an
eleven-gate scalar word is not evidence that such a word exists. The
ordinary twelve-gate baseline remains noncontracting under the declared
ideal moment. This review supplies no new exponent.

The review was performed by the synthesis agent independently of the
transfer producer. Both are AI-assisted research artifacts. This is an
internal analytical review, not formal verification or external peer review.
