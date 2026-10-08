# Independent review of the guarded CRT repair

Reviewed 2026-10-08 14:13 UTC against the CPU inverse agent's
[guarded-crt-batching.md](../inverse/reports/guarded-crt-batching.md), its
[address checker](../inverse/code/crt_guard_controls.py), and the historical
`compact-arbitrary-source-routing.md` at
`6b32837aee0561af85e4efaca21af07b9f2749d2`.
This is mathematical and physical-accounting criticism by a different agent,
not external peer review or formal verification.

The new argument repairs the specific arithmetic CRT charge identified in
[crt-cost-review.md](crt-cost-review.md). It does not reinterpret that charge
as an already available named-bit permutation. The following review is
positive relative to the inherited original chunk-interchange and rotation
contracts, with the explicit boundary requirements below.

## Algebra and inverse

The old masked BIT identity only needs every source outside the simultaneous
ACTIVE target set. Distinct source positions are unnecessary: both completed
four-update identities fix every source, so the loaded packed source word is
unchanged. Repeating a source bit therefore implements fanout to distinct
target bits. Its ideal map is an involution and preserves the original good
predicate; the globally bijective primitive program and exact bad-address
repair apply. This is an extension of the written historical contract, not
an assumed arbitrary Boolean circuit.

For a guarded packed addition, a good dirty high digit absorbs at most one
carry. The completed low word reveals that carry by `1[Y'<f]`; subtracting
all these indicators from the separately packed high digits has no borrow
on good states and restores them. The reverse program recomputes those
indicators from its current completed low words. It is an inverse on bad
states too, because each individual rotation retains its controlling prefix.

For `J(y)=a+b-1-y mod 2^L`, the interval `[a,b)` and its complement are each
invariant. Dirty predicate loading toggles the parity control, the two
conditional involutions give `J^c`, and unloading restores the digit. The
load is an ordinary prefix-controlled rotation after placing every completed
target before the packed dirty controls. It is not a nonlinear BIT-router
source. The three interval reflections implement an arbitrary right rotation
of `[0,s)` and fix its padded complement.

All endpoint and offset controls must remain outside ALL active targets.
This invalidates directly batching the original triangular axis schedule:
one axis can change another axis's lower-coordinate controls. The new
balanced CRT tree fixes this issue. Independent nodes at one level have
disjoint scalar coordinates; their left children are fixed controls and
their right children are targets. Recursion on those two children gives
`P_i^-1*k mod s_i` by induction, exactly the original scaled CRT coordinates.
No endpoint controls of one active node occur in another active target.

The ideal completed map fixes every borrowed dirty bit. Its good set is
therefore invariant. A globally bijective actual map agreeing on that good
set maps the complementary bad set onto itself. Sparse repair must use the
reversed actual primitive program, rather than assuming the dirty-state
implementation itself is an involution. The supplied checker makes this
distinction explicitly. Its finite checks support the identities; the
general argument above supplies the reason they extend beyond those checks.

## Real bank and spectator allocation

Let `b` be the address-bit upper bound. The campaign's leaf capacities have
widths between `ell` and `2ell`, with `d=Theta(b/ell)` and
`ell=Theta(b^(1-epsilon))`. After a fixed bounded number of tree levels,
each independent node has `O(b/m)` bits, where `m` is the current node count.
Partition nodes by total width into two classes; the error from exact half
balance is at most the largest node. For all sufficiently large parameters,
after discarding a fixed number of top levels, each inactive class has at
least `b/3` bits. The discarded levels contain only a fixed number of nodes
and may use the original individual rotations at `O(V)` total cost.

The additional outer dirty digits use `2mG=O(d log b)=o(b)` bits. Select an
untouched suffix of width at least a fixed fraction of `ell`, disjoint from
these digits, every active target and every offset control. This is possible
inside the inactive class. With the historical `K=64G`, the masked BIT
reservoir has `H=ceil(n/K)*G<=n/32` after its stated threshold. Its three
fields use at most `3b/32` bits. The outer digits, this reservoir and the
spectator fit within the inactive class with a fixed positive margin.

Repeated-source fanout is not a matching, so its proof should not silently
invoke the historical matching's three-spectator partition. Here that
partition is unnecessary: one selected inactive suffix avoids every source
and target of the fanout, and one disjoint inactive reservoir supplies the
three temporary fields. Their placement uses paid original interchanges or
the inherited known-coordinate router. All remaining endpoint/source
positions are in the masked gadget's middle word.

The actual suffix makes enlarged records of size
`Q*2^Omega(ell)`, which dominates every fixed polynomial in `b` for fixed
`epsilon<1`. Every ordinary rotation acts uniformly in that untouched
suffix. Its prefix-offset arithmetic is therefore charged once per enlarged
prefix fiber, rather than once per coefficient or payload bit. Router and
fanout descriptors are polynomial-size constructions, not growing advice.
Their dependence is on address `b`, not on coefficient precision `Q`.

For each active class a constant number of interval reflections invokes
`O(log b)` masked residue calls and a constant number of known layouts.
There are `O(log d)` tree levels and two classes. Thus the charged bound is
`O(V*b^tau*polylog b)`, including every full-volume ordinary rotation.
The complete stream remains the same rectangular binary box throughout;
no clean address ancilla or increased tensor volume is needed.

## Padding, monotone scans and sparse repair

Splitting a valid scalar node index is a genuine payload operation. The map
`k=A+S_L*B -> A+T_L*B` is strictly increasing on
`0<=k<S_L*S_R`, because `T_L>=S_L` and crossing the end of an `A` run still
increases the target address. Products of these injections preserve the
Cartesian lexicographic order. A joint scan can therefore consume one
advancing source stream at occupied target positions, writing zeros at the
remaining binary positions. The inverse gather consumes the corresponding
occupied positions in the same order.

Deleting old invalid slots is justified only if their payloads are already
known zeros. At completed boundaries the ideal interval rotations preserve
all current node-validity intervals; set `f=0` for an invalid left control.
Exact repair then restores this property on ALL addresses. Temporary dirty
bank operations can change validity, so no split, deletion or zeroing is
allowed between the primitive operations and their completed outer repair.
The implementation must preserve this order explicitly.

For direct scans, the sum of squared node widths is at most `b^2`.
Schoolbook division and comparisons on all current nodes thus admit a
conservative `O(b^3)` metadata bound per coefficient. With
`Q=Theta(d^18)` and `epsilon>1/2`, this is absorbed by the actual `Q`-bit
traffic. One should use this concrete bound rather than claim that arbitrary
polynomial metadata is automatically absorbed. Prefix descriptors may
alternatively be generated incrementally.

Outer dirty-digit failures have density at most `2m/2^G`. With the proposed
`G=6 ceil(log2(b+2))+6`, this is `O(b^-5)`. Extraction, polynomial address
inverse evaluation, stable binary radix sorting of `O(b)`-bit keys and
reinsertion are charged. They can operate on the untouched enlarged records,
because the program and bad predicate are independent of their suffix; or
use the concrete low-degree metadata bounds with the long `Q` records.
Inner masked-shear repairs are paid separately and complete before the
next outer primitive.

## Scope

No new obstruction was found after the independent-node, zero-padding and
bank-allocation clarifications. The strengthened movement result is a new
conditional lemma under the original fixed-tape primitives. It removes the
particular `dV` CRT row audited earlier if the full multiplier uses these
completed schedules. A larger multiplication exponent additionally needs
the coordinator's full recurrence, precision, Fourier, resampling, setup
and absorption checks. The earlier scoped ceiling `a/(1+a)` remains correct
for schedules that retain the original individual rotations.
