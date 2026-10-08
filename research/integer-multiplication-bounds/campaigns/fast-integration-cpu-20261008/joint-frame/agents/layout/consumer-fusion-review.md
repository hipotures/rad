# Independent review of consumer-guarded fusion

The coordinator's `joint-frame/code/consumer_guarded_fusion.py` has a valid
sufficient finite geometry and causal guard. It retains the original scalar
graph and every source and terminal frame, and moves a complete nonterminal
region F only to an existing direct consumer G satisfying

    F is contained in G, and G is contained in every direct consumer H of F.

An original incoming edge A to F remains legal because A is contained in F
and therefore in G. Every outgoing edge remains legal by the second guard.
If a consumer itself moves to a containing frame H', then G is still contained
in H'. The helper additionally forbids a selected destination from moving and
forbids a moved source from becoming another selected destination. This gives
a simpler acyclic, one-level replacement map. Several regions may merge into
the same fixed destination without violating either implication.

The actual helper checks every final modified edge, not just the candidate
that caused the merge. It also checks each source and each designated output
against its original frame. This last check matters when a region contains
both terminal and nonterminal scalar nodes: the whole original region is
excluded from movement, rather than only its terminal node.

The underlying regional compiler still iterates scalar node IDs in their
original topological order. Thus dependencies inside a merged region have
already been computed when their consumer rows are formed. External inputs
are explicitly collected and the completed binary matrix is invertible on
all incoming physical roles. Changes to retained continuations are recomputed
after grouping. The helper does not reuse a matching from the original graph.

All requested output frames remain original, so the scalar graph's terminal
contract and inherited data endpoints are available unchanged. Actual frame
incidences, dirty scratch restoration, copied centers, and native fixed-I+J
profiles still need their respective full checks. In particular, legal region
coalescence by itself does not prove that a lower role count has a lower
moment, or that the complete repeated dirty wrapper has been assigned a legal
all-size schedule.

## Important negative cases

Checking only F contained in one consumer G is insufficient. If another
consumer H does not contain G, the moved outgoing edge is illegal even though
the source signal still has the correct scalar value. A terminal output in
the original F region also prevents movement: it must retain its required
partial frame. A chain F to G to H must either be resolved simultaneously
with all affected consumers rechecked or be forbidden, as the current helper
does. The current implementation chooses the latter.

The selector should receive a strictly positive `max_moved_regions`. Its
current append-then-limit loop would select one region for a zero limit.
The running declared configurations use positive limits; this is a bounded
configuration edge case, not a failure of those experiments.

## Scope

This is an independent source-level causal and rational-geometry review of
the authored helper, not a formal proof of the inherited multitape transfer.
The new mechanism is credited to the campaign coordinator. Public PR55/57/58
supply the scalar graph, original envelopes, regional synthesis, and dirty
wrapper. Changes to source or terminal labels, new frame families, and nested
replacement chains require a new review.
