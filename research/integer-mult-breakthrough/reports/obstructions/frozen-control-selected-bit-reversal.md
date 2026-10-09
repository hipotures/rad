# Frozen-control masks supply a conditional selected-bit reversal

Status: **CONDITIONAL NATIVE ROUTING EXTENSION**, with **EXACT FINITE
QUOTIENT AND COMPLETE-PAYLOAD CONTROLS**. This supplies an address component,
not a whole Gaussian network, favorable characteristic root or new exponent.

## Changed control mechanism

The pinned original packed-addition lemma uses three complete equal-width
address chunks x,y,z. Its eight rotations perform selected XORs into y,
restore arbitrary z, and preserve x, after exact exceptional correction.
The [independent literal helper](../../code/transfers/native_gl_review.py)
retains that chronological word. The
[packed Toffoli extension](../transfers/packed-nonlinear-routing.md) already
uses a nonlinear mask from two unchanged control chunks.

More generally, let each selected mask bit G_j depend only on chunks that
remain fixed throughout one complete eight-rotation word. For L=(g+1)K,
select rho+jK for 0<=j<g and reserve the terminal full K-bit range. Every
offset may inspect G_j and the OTHER current target/companion parity. It
must not inspect its own target. The existing displacement, safe-guard and
exception-set arguments therefore apply to the same immutable mask, regardless
of how it was computed. Reverse correction recomputes that same mask.

If computing G from an address descriptor of width A costs C_G(A), the
conditional inherited bill is

    O(V(L^tau+1) + M*(A^3+C_G(A))
      + delta*M*A*(R+A)),
    V=M*R, A=ceil(log2(2V)), delta=min(1,80*g*2^-K).

The fixed eight calls do not hide a growing number of bit gates. The mask is
computed as scalar row metadata; it is not obtained by first permuting the
complete payload array. All copies, head returns, descriptor work, temporary
record motion and exceptional repair use the original complete-stream
contracts. R must satisfy their long-record condition before discarding the
metadata term. This is an analytic extension, not a measured tape runtime.

## Three completed words

Let R_g reverse the g active selected bits of one complete subslot. It is
linear over GF(2), involutive, and ignores all unselected bits and the
terminal selected guard position. On two such subslots x,y, perform

    x <- x xor R_g(y),
    y <- y xor R_g(x),
    x <- x xor R_g(y).

The masks are fixed during each individual completed word, although their
control chunks change between words. Since R_g^2=I, the active result is
(R_g(y_old),R_g(x_old)): exactly reversal of the concatenated 2g selected
bits. Every spectator remains unchanged. Each word uses an existing distinct
equal-width third subslot z and restores its entire arbitrary address value.
Thus only three packed primitives, or 24 literal rotations plus corrections,
are required. Computing the reflected mask costs O(A^2) by ordinary descriptor
arithmetic, subsumed in the retained A^3 term.

This three-word identity does not hold for an arbitrary nonlinear involution.
The finite negative control uses a Toffoli involution and retains a concrete
failure. The general mask supplier is wider than the special linear exchange
identity; those claims must not be conflated.

Reading control guard bits is allowed by the standalone immutable-mask
permutation argument. To commute precomputed selected-bit Gaussian guard
gates past the completed router, however, G must be guard-independent or
have a separate commutation proof. R_g is guard-independent. The completed
permutation acts identically on both terminal guard axes and therefore
commutes with their C factors. Intermediate rotations need not commute.

## Existing-volume guard shape

For fixed h>=2 and e>=4h, write

    g=floor(e/(2h))-1, u=e-2h(g+1), 0<=u<2h.

Each old logical slot has two complete subslots of (g+1)K bits. There are
2h such ranges already inside the eK-bit address cube. The reversal of one
old slot uses its two halves and borrows any third distinct existing subslot.
No extra complete coordinate range, zero scratch or scalar bank is introduced.
Pay one elementary selected-bit C on each of the 2h terminal guard ranges
and one on each leftover selected axis: fewer than 4h local kernels. These
are two-address maps on bit rho, not whole C_K blocks.

A rank-r active child contains both g-wide bands of each of r logical slots,
so its selected width is 2gr. In the first 2gr complete K-ranges, every hole
is an already processed terminal guard, and there are at most 2r holes.
Exchange them with the same number of active donor ranges, call the ONE full
active child on the compacted prefix, and undo all exchanges. The geometry
does not force two independent Gaussian subcalls. The unchanged width bound is

    2gr/e <= r/h.

For r=h the actual width is e-2h-u<e. Thus neither address volume nor the
positive-power child majorant worsens merely because two guards are reserved.
The [independent label-set source](../../code/obstructions/double_guard_reversal_layout.py)
checks 4160 cases for h2/3/4/6, g1 through32, every remainder and every r.
It reverses every whole-range exchange and checks exact rational inequalities.

This is conditional on an actual whole active Gaussian child with that
interface. It does not supply such a network or its contracting profile.
Splitting it into two separate g-wide calls can increase the power moment by
2^(1-p) and must be charged if that is the only implementation available.
Using the original fixed-h network across both bands requires masks that omit
the internal processed guard position and its own full phase/field semantics.
The geometric certificate alone cannot certify that integration.

## Finite word and scope

The [literal source](../../code/obstructions/general_control_bit_reversal.py)
retains all four two-bit control masks, 65536 complete low target/companion
pairs, 1024 seeded full K6 addresses and forced carry-free guard samples.
It detects omitted repair and checks current-record correction. A separate
full toy array has prefix2, three eight-address complete subslots and suffix2:
2048 complete records with four independent payload fields. All 24 rotations
and three repair permutations are executed, followed by the true inverse.
Another 512 full K6/g3 address triples check the selected reversal and all
spectators. The nonlinear three-shear counterexample is retained.

These are finite permutation certificates, not measurements of native tape
time. The native extension inherits the pinned `original-layers` and
`original-streams` contracts. Complete numerical prefix bounds, Gaussian
network chronology, role stock and all multiplication transfer obligations
remain separate. This order supplier does not rescue the synthesis track's
already excluded additive two-order scan family. It opens a lawful routing
component for wider architectures; it does not establish a new kappa.
