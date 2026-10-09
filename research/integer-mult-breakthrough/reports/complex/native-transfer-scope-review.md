# Independent scope review of stopped recursion and short-record splitting

Status: **ANALYTICAL AND SOURCE-INSPECTION REVIEW** by the complex research
track. This review did not independently rerun the transfer track's full
experiments. It accepts the stated components conditionally and does not
verify a new native Gaussian circuit, complete CRT program or exponent.

## Routing-aware stopping

The [transfer report](../transfers/routing-aware-depth-transfer.md) explicitly
keeps the root chunk K in every local cost. For tau<=sigma<1 and a complete
moment Phi(sigma)<1, a stopped frontier has weighted sigma-potential at most
the root's d^sigma. Internal costs above H are bounded using
`e^tau<=e^sigma H^(tau-sigma)`, then summed geometrically. Early leaves cost
at most their sigma-potential times H^(1-sigma). Budget leaves occur at depth L
and are controlled by the first moment d*Phi(1)^L. These leaf classes are
disjoint and no paid same-width child is removed. A decreasing L terminates
such children without presuming a smaller same-width oracle.

Balancing at H=K^(tau/(1-tau)) gives the stated power
`sigma+c*tau*(1-sigma)/(1-tau)` when K=Theta(d^c). Complete W^L row stock,
all suffix fields, inactive stream parking and polynomial descriptor work are
explicit interface obligations. Their availability does not follow from the
potential argument. When borrowing complete chunks as a preceding prefix,
the eventual native layer must specify actual selected kernel positions and
how many kernels are applied per borrowed chunk; preprocessing cannot silently
omit K bit positions or collapse a required complete companion range. The
report marks native tape layout and Gaussian integration as still conditional.

Reviewed source SHA-256 for `routing_budget_transfer.py`:
`55a391b221f21aea1b1f0053dc150ed00e3cce929eb86ecd02e6d1bf3be91c8a`.

## Short-record monotone split

The [split component](../transfers/short-record-monotone-split.md) has a sound
equal-capacity contract: valid k=A+S_L B maps increasingly to B*T_L+A.
Independent adjacent splits preserve Cartesian lexicographic order. Sequential
old/new valid-record enumeration therefore pairs the correct complete payloads.
Invalid old payloads are discarded only after their zero contents are checked.

Source inspection confirms that binary comparison proceeds from least to most
significant bit with a three-state comparison, overwritten by each later
different bit. An explicit finite-symbol flag handles S=T. Counter/template
heads scan and return across all fields. Each old/new address is visited a
bounded number of times; carries and returns cost O(TB), and complete copy,
zero-template moves, payload rewinds and metadata erase cost O(TQ). The bound
O(T(Q+B)) is justified. Numeric coordinate arithmetic occurs in setup and
independent fixture generation, not in each consumer record decision.

For Q>=B, this component has linear full-volume work. Its finite trajectory
model still needs a complete integration with guarded rotations and exact
repair before the split, because invalid intermediate payloads may be nonzero.
The absence of repairs in this component is a scope limit.

The separate conditional delta=B^-5 arithmetic ledger is also consistent:
delta*M*B^4 polylog(B) is O(V B^-2 polylog(B)) when Q>=B, and full-payload
binary repair sorting costs delta*M*(Q+B)*B=O(delta*V*B). These deductions
require the real invariant exceptional set and exact key/inverse algorithm;
they do not constitute a tested short-record guarded CRT theorem.

Reviewed source SHA-256 for `monotone_split_tapes.py`:
`3d8339e0247f48535cf95226eee8e5e944bff99280ba9a5696592715ad2217e5`.

## Common-frame release boundary

The coordinator's [release lemma](../obstructions/coherent-release-minrank-bound.md)
is consistent with the scalar component contract. For fixed full diagonal
Lagrangian D, E(L)=L intersect D. E(A)+E(B)+(A intersect B) is isotropic;
its overlap with the common endpoint space equals E(A) intersect E(B).
The dimension inequality proves the stated lower bound on frame distance.

At any lost-direction event, adding one current scalar coefficient row to a
global released row space preserves the support-plus-released-space invariant.
At every scalar gate, the SAME ACTUAL address frame and fixed virtual scalar
basis are necessary. Equal Lagrangian labels with distinct residual gauges
alone do not justify that induction. Final identity rows decompose into an
orthogonal-supported part plus released rows, producing the central fitting
matrix and its rank bound. This does not sum an independent penalty per output.

Address-dependent operator mixtures, uncharged gauge changes and a tensor
lift of the bound are outside that proof. In particular one lost direction in
a bulk frame can invalidate a whole source block, so an extra f factor needs
additional separability. Shared low-rank releases remain mathematically open.
