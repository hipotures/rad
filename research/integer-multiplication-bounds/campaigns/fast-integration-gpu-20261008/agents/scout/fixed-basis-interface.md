# Exact interface for a new graph and the PR38 fixed basis

Source: Dominik Scholz, [CrocSwap PR38](https://github.com/CrocSwap/integer-mult-bounds/pull/38),
commit `cc794077f6c103e24ec0939be765cd1521239aab`, read 2026-10-08 around
13:03 UTC. Immediate dependencies are icekylinx PR36 (`11817cc...`),
icekylinx PR32 (`0ef3aeb...`) and Dominik Scholz PR35 (`9c345a2...`), with
the source notices and assistance disclosures retained. The external snapshot
is recorded in [input-manifest.json](input-manifest.json).

## Fields and label choice

Bit payload arithmetic is over F2. Address geometry is rational and is later
reduced modulo an eligible odd address prime; these are separate fields.
The address metric is `G_h=I-J/9`. For an addition with core C and union M,
use the **original** envelope

`E(C,M)={x: support(x) subset M, x_i=t for i in C, sum_i x_i=3t}`.

Here `c=|C|` is 1 or 2 and rank is `|M|-c`. Sources are the triple lines
`<t_T>` with G-norm two, rank one; the c=3 source case is separate.
For each core point i, the envelope lies in
`U_i={x: sum_j x_j=3x_i}`, where `x^T G x=sum_{j != i} x_j^2`, so every
original envelope and its nested residual is nondegenerate.

These labels are not the enlarged backward-positive labels. PR38 computes
original rank from core and cover and rebuilds the **original** oriented
matching in `rankone_profiles.cpp`. Its matching and matrix formulas cannot
be attached to a different positive-label matching by changing only the
role-count input. A new graph must establish its original-envelope inclusion
and matching again, or derive a different fixed-basis profiler for the
positive labels.

## Source projector and fixed conjugation

Both local bases are `L_h=I+J`, with inverse `I-J/(h+1)`. For a triple t,

`P_t=t*(t^T G_h)/2`,
`L_h t=t+3*1`,
`(t^T G_h/2)*L_h^{-1}=t^T/2-5*1/(3(h+1))`.

All primal and dual coordinates are nonzero at h=23 and h=25. The general
original-envelope projector after conjugation is a 0/1 diagonal mask on
`O=M\C` plus a rank-at-most-two correction. With

`c=|C|, n=|O|, s0=3-c, d0=s0^2+(c-1)n`,
`pO=1_O, w0=1_C+3*1, z0=3(h+1)*1_C-10*1`,

the exact numerator identity is

`3(h+1)d0*(P'-Delta_O)`
`=s0*pO*z0^T +3(h+1)s0*w0*pO^T +n*w0*z0^T -3(h+1)(c-1)*pO*pO^T`.

This is the formula the C++ producer evaluates modulo certified primes.
Do not substitute the different positive-label projector while retaining
this correction-rank proof or its numerator bounds.

## Exact graph and chronology obligations

For every operand inclusion and every retained carrier continuation,
`C_target subset C_source` and `M_source subset M_target` establish actual
envelope nesting. Every addition remains disjoint in its scalar supports.
Every side output excludes exactly two points and is orthogonal to its
target triple; every retained total is `U_i`, rank h-1. Check the new graph's
source/support/output identities independently of frame rank.

An addition z contributes `(degree(z)-1)` copies of its projector, one
complement `I-P_z`, and each operand growth `P_z-P_y`. A source contributes
one source projector per actual use. For a matched donor u keeping operand
v into consumer t, remove the **physical occurrences**

`I-P_u`, `P_v`, `P_t-P_v`,

and insert `P_t-P_u`. The source matcher's event order is rank followed by
node order; output uses are separate late events. One donor and one use
can be matched only once. The actual recipient may be an operand or a
terminal output use; designated terminals stay separate, with no later
middle-producer consumer added.

The compiled local rank sum before copied centers is `h*R_h+2*ell_h`,
`ell_h=h(h-1)`. Copy scheduling replaces exactly h retained total cleanup
children of width h by width one; their rank-(h-1) copy transforms remain.
The new local rank mass is `h*R_h+ell_h`. Distinct designated carriers can
hold different arbitrary dirty values even when their scalar supports agree,
so support equality alone does not license a shared copied stream.

## Fixed basis and endpoint transfer

At factors (a,b)=(25,23), the common ambient basis has form
`K=T2*(I_a tensor L_b)`, with
`T2(x tensor e_beta)=M_beta*L_a*x tensor e_beta` and the exact controlled
permutation completions inherited from PR29. The first-a/last-a and
first-b/last-b local corners are nonzero diagonal scalings of the actual
conjugated local projectors. Auxiliary exterior corners are diagonal and
give `[25,525]` and `[23,529]`; physical corank-one growth gives `[1,23]`
and `[1,21]`. These statements use the same physical order for every edge.

The two 47-edge bipartite incidence trees prove both full data-nullspace
restrictions are nonsingular for **every** nonzero primal/dual coordinate
choice. Thus fixed I+J satisfies the full data-corner contract. A written
row-elimination argument preserves the first 21-block. PR38 conservatively
uses data `26*[1]+[21,481]`; it does **not** inherit the generic 15-block.
A reversed (23,25) fixed candidate must prove its actual permutation/tree
and rank-cut conditions again before using the PR37 second 17-block.

The copied-center frames, original source/sink endpoints, both invocation
orientations, all spectators and the separate N paid rank-one corrections
remain. A new graph changes W and the local distributions; its complete
physical list must be reconstructed, with `s=Wm-N+L` checked independently.

## Exact profile and assembly obligations

Every new physical local transition must be profiled. PR38 handles rank zero
by removing it, rank one/two conservatively as singletons, identity as one
h-block, and other matrices by their actual increasing contiguous northeast
pivot runs. Envelope/complement/same-core growth has correction rank at most
two; source growth at most three; core-two to core-one at most four.
Changing graph labels or allowing other transitions requires revisiting
these bounds.

At h=23,25, the source's dimension-specific numerator bounds certify every
minor, not only a sampled full rank. One prime suffices for correction rank
two; the product of Lucas-Lehmer-certified `2^61-1`, `2^31-1`, `2^19-1`
exceeds the rank-three/four minor bound. CRT zeros therefore lift exactly.
The new graph's complete transition multiset and every actual matrix must
be covered by these formulas before claiming an exact histogram.

Rebuild the full child multiset, strict rational moment, literal scalar gate
charge, coefficient/precision bound, semantic bridge, row stock and final
assembly. PR38 has C1=1, product stock p^2000 and unchanged complex saving
717/10^7, but those constants must remain valid for the new graph. A PASS of
an old certificate does not accept the changed local matrix or chronology.

## Source-overlap finding for sequential totals

In the inspected PR36, PR37 and PR38 sources `ExclusionCircuit.total()` is
balanced, splitting at `len(values)//2`. Swapnil round-five `sidegen.Excl.total()`
also uses that balanced split. The underlying exclusion producers already
use sequential prefix/suffix sums for leave-one-out arrays. The campaign's
specific switch of total trees to alter retained matching is absent from
these pinned sources; sequential addition in general is not new. Public
repository/code searches do not establish worldwide priority.
