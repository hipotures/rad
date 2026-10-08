# Paid nullspace circuits for component reclamation

The pinned public controller exposes one dependency per dependent retired
carrier during Gaussian elimination. The complete-basis screens tested every
such returned expression but retained the elimination basis. This need not
find a short clearing circuit. The new search combines exact zero relations
before executing a clearing word. It preserves the public scalar graph and
uses the same explicit physical roles and causal frame constraints.

Let z_s denote the current exact source signal in physical role s. A binary
relation e is eligible for clearing a retired role s when s belongs to its
support, XOR_(a in support(e)) z_a = 0, and every participating role can be
raised to the current region G. Executing XOR(s,a) for every other support
role then clears its source signal. Every donor and target frame transition
and every XOR is recorded. A source signal becoming zero does not imply that
arbitrary dirty contents have become clean. The full wrapped reversible word
must still pass the complete dirty-basis checks in both orientations.

An external live donor is admitted only if G lies within every unconsumed
use of that donor, including terminal scatter. Raising a retired target has
no future continuation, while its donors remain unchanged as scalar
signals. All donors receive the actual paid frame raises.

## Search scope and independent review

Version 1 records dependencies emitted when compatible retired roles are
inserted after current and future-guarded live anchors. Each emitted
dependency has its own newly dependent retired coordinate; that coordinate
does not enter the elimination basis. The recorded relations are therefore
independent. Relations are connected when their supports intersect. Components
of at most eight recorded relations are enumerated over their entire binary
span. Larger components receive at most 256 overlapping pair combinations.
The selected exact relation is checked again on the current signal vectors
before executing any gate.

The independent scout review accepted the exact clearing and continuation
logic and identified a useful limitation: dependencies entirely among the
anchors were discarded by the original insertion routine. Thus version 1
does not represent the complete kernel of the admitted role pool. Its frozen
source is [nullspace_cycle_variant_v1.py](code/nullspace_cycle_variant_v1.py),
and the six queued version-1 configurations retain exactly those bytes.

The current driver [nullspace_cycle_variant.py](code/nullspace_cycle_variant.py)
adds `--include-anchor-relations`. It records dependencies from all distinct
admitted roles, including current and live anchors, and consequently
represents the complete kernel of that explicitly admitted pool. The search
over that kernel is exhaustive only within small support components; the
larger-component search remains bounded. It makes no global circuit
optimality claim. Overlapping pairs in the extended kernel must contain a
retired coordinate after cancellation, avoiding a budget spent solely on
anchor-only relations.

Three policies select among actual circuits: first preserving the earliest
future retirement deadline, minimizing immediate summed rank growth, or
minimizing clearing XOR count. They use deterministic ties and no
input-dependent advice. The enlarged circuit set can alter later reclamation
choices; a local improvement is not automatically a better native moment.

## Exact discriminating examples

The independently specified small cases in
[check_nullspace_discriminators.py](code/check_nullspace_discriminators.py)
exercise the actual generated acquisition routine. The
[retained receipt](results/nullspace-exact-discriminators-20261008T1937Z.json)
records the following exact conclusions.

- With signals a=1, b=2, c=4, s=7 and t=3, the fundamental relations
  s+a+b+c=0 and t+a+b=0 combine to s+t+c=0. The chosen earlier retired
  target s is cleared by two literal XORs.
- With current anchors a=1, b=2, c=3, d=4 and sole retired signal s=7,
  the retired-only kernel records s+a+b+d=0. Retaining the anchor relation
  a+b+c=0 permits s+c+d=0 and reduces this target's clearing word from
  three gates to two.
- A live donor whose future frame is narrower than G is rejected even when
  its scalar vector would permit clearing. Deliberately omitting the guard
  clears the local signal but violates the exact later frame inclusion.
- Omitting one actual clearing gate leaves source residual 4.

These examples establish a structural opportunity and falsify two unsafe
shortcuts. They are not native projector profiles or a multiplication
certificate. Full 23/25-axis runs use fresh task-owned source copies and
immutable configurations. Any candidate needs independent literal-word
replay, all physical transitions, rational fixed-basis profiles, complete
child moments, scalar charges, and the chosen all-size assembly before an
exponent claim is accepted.

The public dual-suffix producer and joint compiler are scientific inputs
from the authorized PR55/57/58 commits. Attribution and AI-assistance notices
remain in the campaign [credits](../../CREDITS.md); this contribution is the
paid nullspace-circuit search and its guarded finite discrimination.
