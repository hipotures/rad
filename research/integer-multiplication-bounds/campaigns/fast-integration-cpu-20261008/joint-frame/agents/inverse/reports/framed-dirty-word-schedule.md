# Complete framing of the four-mixer dirty word

This supplies an explicit conditional resolution of FRAMED-DIRTY-WORD in
the [PR58 transfer review](pr58-transfer-review.md). Independent layout
review accepted the actual gate assignments, owned-copy charges and
complemented reverse profiles on 2026-10-08. The scalar replay alone did
not supply this schedule. The retained residual and fixed-tape copy
implementations remain named hypotheses. Finite physical controls below
corroborate the new construction without proving those inherited machine
contracts.

Use the partial-swap address permutation from the pinned PR29 direct transfer:

```
S_U = [[I-p_U,p_U],[p_U,I-p_U]].
```

For orthogonal summands, `S_U S_V=S_(U+V)`; each is an involution. All of
these statements concern address permutations of bit arrays, not binary
linear maps on the rational address coordinates. A role-XOR gate acts
pointwise on its full array. Two touched roles in the same frame commute
with that common frame. Hence assigning common frames to every gate proves
the actual array map `D_out*S_scalar*D_in^-1`, on arbitrary inputs.

Suppress fixed tensor spectator lines. In one local invocation put
`D0=B tensor F_h`, `D1=D0 orthogonal-sum (P tensor F_h)`, with `P` a line.
Write `E_g` for the recorded local envelope of a mixer gate, and `t_T` for
a triple source line. A partial local frame means `D0 + P tensor E_g`.
All original auxiliary roles enter at `D0`; the data source has frame
`D0 + P tensor t_T`, and the target initially has frame `D0`.
These are prescribed endpoint representations; no physical preparation
is free. The inherited data-front/exterior schedule supplies its actual
entry and exit operations and is unchanged here.

## Gate-by-gate schedule

Let `M` be the entire literal scalar mixer, `J` its terminal scatter, and
`V` the source injection. The chronological scalar word is
`M,J,M^-1,V,M,J,M^-1,V`. It has the following legal physical implementation:

| Phase | Physical gate frames and paid changes |
|---|---|
| First `M` | All auxiliary gates at the common `D0` frame. |
| First `J` | Auxiliary sources and target data all at `D0`. |
| First `M^-1` | All auxiliary gates remain at `D0`. |
| First `V` | Raise each designated source carrier to its triple-line frame; its data source already has that common frame. |
| Middle `M` | Raise both endpoints to the recorded `D0+P tensor E_g` before each XOR. This is the only mixer that follows the local envelope paths. |
| Second `J`, centers | First read each retained center through a paid transformed copy at `D0`, while the target data are still at `D0`. |
| Second `J`, ordinary outputs | Raise target `T` to `D0+P tensor t_T^perp`; raise its distinct ordinary output carriers to this same frame and perform their scatters. |
| Cleanup | Raise every original auxiliary role to `D1`. |
| Last `M^-1` | All auxiliary gates at the common `D1` frame. |
| Last `V` | Raise each source data role from its triple-line frame to `D1`; inject at the common `D1` frame. |

The first three phases require no local envelope changes, whatever legal
reclamation order was used to synthesize `M`. The unused physical carriers
are arbitrary dirty inputs at `D0`, not newly clean roles. Each source
carrier is raised once before its injection. Every non-source carrier is
raised from `D0` at its first middle-mixer incidence; subsequent moves are
exactly its recorded monotone path. A retired role reused by a later gate
retains its actual current frame and must satisfy the same containment test.

All `J` gates commute as scalar operations: their targets are data roles,
their sources are distinct read-only terminal auxiliary roles, and no `J`
gate changes an auxiliary. Thus putting all center reads before ordinary
reads preserves the scalar word, without reordering any middle producer
consumer. The first `J` may use the same center-first order at no cost.
Distinct terminal carriers and the absence of later producer uses are
necessary. For guarded future-carrier borrowing, every outstanding terminal
use must be included in its containment guard.

For an ordinary output indexed by a target triple `T` and common point `c`,
the recorded envelope has core `{c}` and cover `F_h minus (T minus {c})`.
For any vector `x` in it, `x_c=z`, `sum(x)=3z`, and the other two target
coordinates vanish. With metric `I-J/9`,

```
<x,t_T> = sum_(i in T) x_i - sum(x)/3 = z-z = 0.
```

It lies in `t_T^perp`. Raising its rank-`h-3` envelope to that rank-`h-1`
target frame costs exactly two ranks; cleanup to `D1` costs one more.
The published ordinary side-growth split and endpoint line pay these calls.
The middle compiler never reads those terminals after its completion.

## Center ports and complete payload traffic

A center ends at its nondegenerate envelope `E_c`, rank `h-1`. Keep that
original at its recorded frame. Copy its **complete** physical role stream
to one owned work stream, transform the copy from `D0+P tensor E_c` to
`D0`, perform all its center reads, then erase/overwrite that work stream.
The original next grows directly to `D1`, costing one rank.

The temporary is an owned disposable work-tape port. Copying or zero-writing
initializes it in `O(V/W)` time; it is not an arbitrary initial routed
role or a borrowed dirty address bank. No promise is made to restore its
previous disposable contents. If one borrowed an original dirty role
instead, this argument would require another restoration protocol and
explicit charges. The arbitrary inputs of the `R` original roles are all
preserved by the scalar wrapper, with their specified final address map.

Copy, all pointwise reads, rewind, erase, and eventual formatter work are
paid. The `J` reads are already counted in the complete XOR word. A
conservative additional four linear stream operations per center cover
initialization/copy, parking/return and erasure. The two axes add at most
`4*(2300*23+1771*25)=388700` fixed local stream groups, independently of
input length. The inherited fixed-tape copied-stream scheduler parks the
original while its copy is active, has one additional fixed work stream,
and never scans parked ancestors. A copy has volume exactly `V/W`, with
the same complete control and spectator ranges and child row stock.
It is not an additional independently varying row coordinate.

Every original auxiliary's monotone path from local rank zero, through all
middle incidences, to its final full local frame telescopes to `h`.
Thus the original paths and cleanup pay `h*R`. Each of the `h` center
copies pays rank `h-1`, giving exactly

```
local residual rank mass = h*R + h*(h-1).
```

This count includes each copied transform **once**. The disposable copy
is not transformed back before erasure. Restoring its original would add
an unnecessary second recursive transform and change the recurrence.
Data source and target grow by rank `h-1` each; they are outside this
local auxiliary total and remain in the full network's data profiles.
All four mixer words are still executed pointwise, and their complete
XOR/stream costs are fixed overhead. They do not induce four recursive
address traversals. Cleanup must precede the last inverse mixer; an
unframed inverse mixer would invalidate this argument.

## Opposite orientation

There is a direct opposite shear with source and target data roles
exchanged. The same forward schedule supplies it, with the same local
path and cost. For the literal reverse-transposed word used by the public
compiler, the following compilation gives the stronger corresponding
statement rather than assuming an uncharged full interchange.

Reverse the event order, transpose each role-XOR, and complement each
local frame within `P tensor F_h`, holding the orthogonal `D0` background
fixed. Let `F_local=S_(P tensor F_h)`. The complemented frame is
`F_local*S_frame`. Since `F_local` commutes with every such frame, a
reverse complemented change has quotient

```
(F_local*S_old)*(F_local*S_new)^-1 = S_old*S_new^-1.
```

This is the inverse of the already charged forward change, with the same
partial-swap residual and fixed-basis contiguous profile. No physical
conjugation by a full-width `F_local` call is performed. The source/sink
frames are complemented in the representation proof, not implemented
as extra outer operations. Every reverse XOR has a common complemented
frame, so the same common-frame invariant applies.

Transpose the center port as a linear map on the original roles. A
forward copy/transform/scatter is `y += J_c*T*a`, leaving `a` unchanged.
Its adjoint is `a += T^T*J_c^T*y`, leaving `y` unchanged. Implement it
with a paid zeroed work stream, gather the fixed target rows into it,
apply `T^T=T^-1` once, add to the original carrier, and erase. An address
permutation's transpose is its inverse; this statement does not assume
that its rational coordinate matrix is Euclidean symmetric. The same
complete role volume and row stock suffice. The transformed gather is
one rank-`h-1` call, and all gathers/additions/initialization/erasure are
fixed linear-volume costs. It restores every original arbitrary input
specified by the reverse-transposed scalar word.

## All-size consequence and remaining scope

For every allowed chunk width, the fixed rational frames induce the same
partial-swap permutations on complete radix-address boxes. The common-frame
induction is algebraic and uniform in payload strings, spectators and row
count. The inherited eligible-prime/radix and residual-block implementation
supplies each recorded rank/profile at volume `V/W`; this proof introduces
no computed nonlinear address routing, same-width child or extra row stock.
Copies and the four scalar mixers add explicit fixed overhead. The native
moment and integer-width recursion therefore use the recorded one-pass
profile, provided the original and copied residual implementation satisfies
its stated physical and tape contracts.

This schedule addresses the additional fourfold-versus-one-pass obligation.
It does not independently prove the inherited ordered-affine residual
compiler, machine construction, analytic reduction, or final recovery.
Finite physical-array positives and deliberate missing-transform/cleanup
negatives support the schedule and must retain their exact scope.

## Independent physical controls

The independently authored [array fixture](../code/framed_dirty_cube.py)
uses actual partial-swap permutations derived from
`p_U=B*(B^T*G*B)^-1*B^T*G`, with `G=I-J/9`, three distinct retained
centers and a deliberately non-self-inverse mixer. It executes all eight
scalar phases with the stated physical moves. At prime 5, bitset rows
represent every one of 78,125 source, target and arbitrary dirty basis
columns at once; both direct endpoint orientations pass at every address.
The [complete basis receipt](../runs/20261008T183440Z-framed-dirty-q5-basis/results/result.json)
retains actual missing-center-transform, missing-cleanup and wrong-inverse
counterexamples. Prime 7 and 11 controls check distinct frozen words at
every physical address; the latter checks 1,771,561 addresses per role.
They are complete address scans for their frozen words, not full basis
checks or public 23/25-axis executions.

The distinct [literal adjoint implementation](../code/framed_dirty_adjoint.py)
reverses all 39 physical events, transposes every role-XOR and inverts
every address move. Each center read becomes an actual owned zero-gather,
one inverse copy transform, original-carrier addition and erasure.
Its [prime-5 complete basis receipt](../runs/20261008T183856Z-physical-adjoint-q5/results/result.json)
and [prime-11 address receipt](../runs/20261008T183900Z-physical-adjoint-q11/results/result.json)
both pass. Omitting the inverse copy transform or reverse cleanup fails;
prime 5 gives 61,000 and 55,000 mismatched physical rows respectively.
This stronger control is kept separate from merely exchanging data roles.

The scout independently constructs a larger five-axis producer and exact
group-ring address operators. Its version 2 reverses and transposes the
literal physical events, rather than only renaming endpoints. It accepts
the schedule over three fields and supplies single-address omission
witnesses. That computation is independent evidence, not this author's
execution. It still treats the copied residual's native recursive stock
and tape cost as the inherited contract described above.

Primary sources are the immutable PR58 snapshot's
`upstream/build/sections/03-motifs.tex` (common-frame identity),
`references/copied-centers/pr29/paureel-direct-transfer.tex` (direct
partial swaps, copied streams and fixed tapes), and
`notes/copied-centers-lemma.tex` (retained-center endpoints and paid copy).
The explicit all-phase assignment and its application to the changed
joint-mixer/reclamation words are the present campaign's transfer argument.
