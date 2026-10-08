# Profile ties, future accessibility, and clearing relations

The best independently reviewed pair remains the future-horizon 23-axis
compiler and the guarded high-rank 25-axis compiler. Their complete native
profiles support conditional arithmetic saving 4.766283731e-5; see the
[independent review](../scout/latest-reviewed-pair.md). The experiments here
screen additional finite words. A smaller role count or a valid scalar word
does not replace native profiling and complete assembly.

## Native profile gradient

Let a recorded frame increment have native block counts n_t and rank
r=sum(t*n_t). Its internal characteristic contribution at saving a is

    C(a) = sum_t n_t*t*(575/t)^a.
    C'(0) = r*log(575) - log(product_t t^(t*n_t)).

Among equal-rank increments, maximizing the exact integer product orders this
derivative without numerical logarithms. This is a derivative criterion at
zero, not an exact finite-a cost. The compiler sorts compatible retired
carriers by rank growth, then decreasing product, then their original role ID.
The deadline version puts the last compatible future region first.

The scout supplies certified native profiles for 50,446 and 68,893 transitions
in the original finite 23/25-axis graphs. We map frame IDs to their semantic
(core mask, cover mask, rank) triples before lookup. That is necessary after
guarded fusion changes region ownership. The tables mostly cover carry and
clone transitions; they do not cover most possible retired-carrier moves.
An absent profile uses product 1, the all-singleton derivative. Unknowns are
counted explicitly, and no inferred native block is added to a final profile.

The gradient-only queries have 1,615 known versus 284,082 unknown pairs at
23 axes, and 2,465 versus 468,517 at 25 axes. Thus the rule is mainly a finite
heuristic for the current table, with a correct but loose fallback. It is not
a complete profile optimizer. All coefficients of the eventual candidate
must instead be extracted from its complete physical word.

## Finished screening results

All rows below preserve the pinned PR55 scalar graph, execute the complete
arbitrary input/output/dirty basis in both scalar orientations, and pass
every physical frame-inclusion assertion. The changes are isolated policy
or consumer-guarded fusion changes. Results are in [results/](results/).

| Policy | Roles, 23 axes | Roles, 25 axes | Interpretation |
|---|---:|---:|---|
| Public PR58 | 30,790 | 40,446 | Pinned baseline |
| High-rank retirement | 30,688 | 40,338 | Improved finite words |
| Last compatible future region | 30,667 | 40,350 | Best current 23-axis count |
| Fewest remaining compatible regions | 30,690 | 40,346 | Inferior to selected pair |
| Guarded live carriers plus high-rank retirement | 30,711 | 40,324 | Best current 25-axis count |
| Rank then native derivative | 30,678 | 40,343 | Neither beats selected pair |
| Deadline then native derivative | 30,669 | 40,350 | Profile tie changes h23, costs two roles |
| Deadline, derivative, guarded fusion | 30,669 | 40,350 | Same counts, changed actual frame profiles |
| Future horizon plus guarded fusion | 30,667 | 40,350 | Preserves counts, changed profiles pending review |
| Complete compatible basis, minimum clearing rank growth | 30,699 | 40,365 | Local objective worsens role counts |
| Complete compatible basis, minimum clearing XORs | 30,731 | pending | Larger 23-axis count despite fewer clears |

The separate high-rank ordering of eligible live sources produces byte-identical
physical words to the already measured guarded-live controls in both dimensions.
Those are retained neutral controls, not additional improvements. Reversed
unit-vector completion and low-rank retirement negatives are retained in the
[causal review](reclamation-review.md).

The future-horizon fused h23 word has SHA256
`43ff8f9775880899941f306d5336c504c632c4a742225131706ebfd20d3790fa`.
Its role count is unchanged, but neither its word nor its frame histogram is
the same as the accepted unfused h23. Actual native profile and full moment
comparison is therefore necessary. Fusion uses the coordinator's
[guarded helper](../../code/consumer_guarded_fusion.py), whose containment and
causal argument is independently reviewed in [consumer-fusion-review.md](consumer-fusion-review.md).

## Complete-basis dependency selection

The public greedy controller stops at the first retired role dependent on
the local anchors and earlier compatible retired roles. The new controller
first inserts every compatible retired role, collecting the dependence
expression returned at each elimination step. It then chooses one of those
actual relations before mutating any role.

For target s and distinct clearing donors A, the immediate rank growth is

    (rank(G)-rank(frame(s))) + sum_(a in A) (rank(G)-rank(frame(a))).

The target is raised only once; each donor appears once in its binary
expression. This is the actual summed rank of the clearing moves. The two
selection rules minimize this sum or the number of clearing XORs, with
future deadline, rank, and role ID as deterministic ties. They inspect all
relations exposed by one deterministic elimination order, not all circuits
of the binary matroid. Every selected XOR is still executed literally,
and every frame move is recorded.

The first corrected h23 minimum-rank run clears 1,842 roles with 4,021 XORs,
versus 1,874 and 4,389 in the last-compatible future rule. It retains 30,699
roles. The minimum-XOR version performs 3,709 clearing XORs but retains 30,731
roles. This discriminates a plausible but unsuccessful local objective:
paying less now need not preserve the future dependencies that free roles.

For any monotone role path from rank zero to the completed local rank h,
the sum of residual ranks telescopes to h. Including cleanup, the original
role rank mass is hR, irrespective of the clearing policy. Paid center copies
add h(h-1). Reducing immediate clearing growth alone therefore shifts rank
to other gates or cleanup; it does not automatically reduce total rank mass.
The choice of R and the actual contiguous block decomposition still matter.

The first two implementation attempts failed before scientific receipts:
generated-source ranking expressions were accidentally retained as strings.
The failure receipt and exact reverse-recovery patch are retained. Corrected
attempts use fresh run IDs and output directories. No mathematical negative
is inferred from this implementation error.

## Physical and all-size scope

These selection policies are fixed computations on a finite public graph.
They do not compute input-dependent address keys or provide growing advice.
Their literal scalar words and frame paths feed the inherited ordered native
residual compiler. Guarded live borrowing requires every remaining use,
including terminal scatter, to contain the raised frame.

The [explicit all-phase dirty schedule](../inverse/reports/framed-dirty-word-schedule.md)
assigns each gate, copied center, and reverse-transposed port. Four scalar
mixers are paid, but only the middle mixer follows the recursive frame paths.
Owned center ports require complete copy/gather, parking, reads, rewind, and
erase. This schedule is accepted conditionally under the named inherited
residual, copied-stream, row-stock, and tape contracts. It does not prove
those inherited contracts or an unconditional multiplication bound.

All inputs are the authorized public tested PR58 revision
`bc2f7ed4c20dc18898305ab17165c0c995cbb804`, including its pinned PR55/57 sources.
Public scalar/frame construction and notices are retained. The contributions
here are the finite policy changes, combined guarded controller, source
recovery, and scoped discriminating results. See [reproduce.md](reproduce.md)
for commands and the manifests for hashes and execution-artifact recovery.

## Guarded-live dependency search and execution recovery

The guarded-live extension of complete compatible-basis selection completed
all 23-axis scalar and dirty checks. Minimum clearing rank growth retains
30,703 roles; adding 256 consumer-guarded frame fusions with rank gap at most
two preserves that count but changes the literal word. Minimum clearing XORs
retains 30,714 roles and performs 3,824 clearing XORs. These words are valid
finite screens, with no new native moment or exponent claim. The corresponding
25-axis attempts were interrupted before complete receipts. Their original
outputs are retained unchanged, and only those pending configurations were
continued in fresh execution copies on 2026-10-08 at 19:26:28 UTC. The
[recovery receipt](results/structural-interruption-recovery-20261008T192628Z.json)
binds the completed cases and interrupted attempts.
