# Independent review of the short-record split interface

Status: **ANALYTICAL COMPONENT REVIEW** plus a bounded replay of the authored
trajectory model. This does not establish the entire guarded CRT program or
a formally compiled fixed-tape machine.

The reviewed [source](../../code/transfers/monotone_split_tapes.py) separates
fixture generation from the consumer. Integer coordinate division occurs in
input construction and its expected-output oracle, while the consumer chooses
records using two bit-counter/template scanners. Its source was inspected at
SHA-256 `3d8339e0247f48535cf95226eee8e5e944bff99280ba9a5696592715ad2217e5`.
The coordinator replayed its source-only bounded check: all 1,152 complete
records and the padding/boundary controls passed. This is a replay of that
program, not an independently implemented consumer.

The monotonicity argument is correct on the positive valid interval: writing
`k=A+S_L*B`, the destination `B*T_L+A` increases within a block and increases
by `T_L-S_L+1>0` at its boundary. Cartesian ordered composition preserves
that order and the complete padded capacity. Thus the next valid source
record belongs at the next valid destination record. Invalid source slots
can be discarded only after their complete payload is known zero.

The LSB-first comparison needs only less/equal/greater states. A later unequal
bit overrides the earlier state. A full-capacity interval uses the explicit
delimiter flag; truncating its endpoint to the field width would be wrong.
Each scan crosses and returns through the complete counter/template words,
so it costs O(B) for B address bits. Field delimiters do not change this bound:
every field has at least one bit. Even the loose O(B) ripple/return bound for
every counter increment suffices for the claimed total.

The payload consumer reads every input record once, writes each destination
record completely, returns the zero template after padding, consumes the
source tail, rewinds both payload heads and erases all metadata/zero workspace.
These are actual monitored single-cell trajectories in the source. Seven tapes
and a fixed alphabet suffice for its operational control. The Python counters
used only for statistics do not select records. Preallocated blank monitor
storage does not replace a nonblank payload initialization: every output
payload and its final delimiter is explicitly written.

Writing known metadata/template words and returning their heads is counted;
constructing those known words and interval products remains separately paid
polynomial descriptor setup. The resulting component bound is
`O(T*(Q+B)+poly(B))`, hence O(V+poly(B)) when Q>=B and V=TQ. It makes no O(1)
per-record arithmetic assertion.

The sparse exceptional-key accounting in the [producer report](../transfers/short-record-monotone-split.md)
also has the stated conditional scale: density O(B^-5) times O(B^4 polylog B)
key arithmetic is O(V B^-2 polylog B) at Q=Omega(B), and radix repair moves
every complete payload on every key pass. Neither calculation proves the
exceptional predicate, its invariant density, exact inverse keys, bank layout
or preceding guarded rotations. Those remain separate obligations.

The concrete component has no exceptions and reports zero repair work. An
earlier nonlinear guarded transform must finish any real padding repair
before this scan; a nonzero invalid input is explicitly rejected. The review
therefore accepts the narrowed metadata improvement and its conditional
arithmetic deduction, while retaining the complete native integration boundary.

This review was developed by the coordinating OpenAI Codex agent. The complex
agent independently accepted the finite-state scan and conditional repair
accounting. Neither review is external peer review or formal verification.
