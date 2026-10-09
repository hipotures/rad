# Exact reflected execution of the converged physical placement

This review concerns only the frozen `live161-components-converged` placement
on upstream PR #161, source commit
`d14e29157bc905be1ced0776dd893d0714013f3a`. It changes physical operation
frames while retaining the scalar DAG, carrier word, gauges, alias pairs,
deadlines, original-source mixing, copied centers, and three-stage assembly.
The complete file identities are in [the pin manifest](configs/converged-pins.json).

The independently authored [executable](code/reflected_paid_replay.py) imports
no producer, frame, replay, or certificate code. It reconstructs an explicit
physical chronology from the frozen exported graph, frame witness, carrier
selection, alias pairs, and candidate frames. Its checks use integer masks,
exact Gaussian rationals for the phase anchor, and exact integer matrices for
the source blocks. Saved PASS fields are not evidence.

## Exact representatives and their reflected frames

Let `H = F_2^22`, with the standard dot product. In `H + H`, use
`L_0 = {(0,z)}` and the binary symplectic action
`F(x,z) = (x+z,z)`. For any binary subspace `U`, define

`L_U = {(u,u+v): u in U, v in U^perp}`.

The executable explicitly constructs every distinct `L_U` used by this
placement and its reflected execution. It verifies that each has dimension
22 and zero symplectic pairing, and that `F L_U = L_(U^perp)`. No Gram
nondegeneracy of `U` is assumed. In particular, radical directions in this
general Clifford construction are legitimate frame directions; the older
orthogonal-projector admission test does not apply.

For a generic subspace, deterministically extend its reduced basis to an
invertible binary matrix `G`. Let `P_G` be the exact address permutation
`|x> -> |Gx>`. For the symmetric binary matrix
`S = I + G^-T G^-1`, define the diagonal exact unit phase

`Q_S |x> = i^(sum_i S_ii x_i + 2 sum_(i<j) S_ij x_i x_j) |x>`.

The exact Clifford `K_G = Q_S P_G` has binary action

```text
[ G            0     ]
[ G + G^-T     G^-T  ].
```

Thus `T_U = K_G C_[0:dim U] K_G^-1` is an explicitly defined exact
Gaussian-dyadic circuit. The executable checks its binary action, its
preimage `L_U`, its Fourier rank `dim U`, and its binary square. Its exact
square is a Pauli, because the exact coordinate `C` square is a translation.
The check of the binary square is not asserted to prove an exact identity.
Use `T_0=I`, `T_H=F`. For a norm-one source line `q`, retain the exact
translation phase `T_q = ((1+i)/2) I + ((1-i)/2) X_q`, so `T_q^2=X_q`.
The executable verifies the one-coordinate identity `C^2=X` and the exact
inverse over `Q(i)`, not by binary XOR.

For the complete reverse define the actual representative

`D_U = T_U F^-1`.

Its inverse acts on the preimage as `F T_U^-1`, giving
`L(D_U)=F L_U=L_(U^perp)`. More decisively, the transition identity is exact:

`D_U D_V^-1 = T_U F^-1 F T_V^-1 = T_U T_V^-1`.

This is literal cancellation of adjacent exact operators. It requires no
commutativity of partial frames and does not replace an operator by its
binary matrix or frame coset. Consequently a forward transition
`T_V T_U^-1` reverses to its exact inverse with the same Fourier rank.
For nested `U subset V`, the executable independently computes that rank
as the Lagrangian union rank minus 22, and checks it equals
`dim V - dim U`. Every frame transition in the emitted chronology is
checked in both orientations by this calculation.

At common scalar gates every incident stream uses the same chosen exact
representative. Scalar additions and the four-port rational source blocks
therefore commute with that common address operator. At a norm-one target
endpoint the retained representative is `F T_q^-1`. Its preimage equals
that of the canonical `T_(q^perp)`, so the actual left adapter
`(F T_q^-1) T_(q^perp)^-1` has Fourier rank zero. The program emits and
checks all 1,320 such adapters and their literal inverses. They are finite
scalar/router operations; they are not removed from the implementation.
Likewise `D_0=F^-1` differs from `F` by the actual Pauli `F^2`. The inherited
endpoint normalization includes that rank-zero operation.

## Complete physical chronology

The replay initializes each physical auxiliary at frame zero, source data
at its norm-one source line, and target data at frame zero. All 2,970
selected gauge roles are paired, and every physical slot has a zero
entrance gauge. The executable verifies each donor's death precedes its
recipient's read, that the recipient is first used at the stated deadline,
that alias pairs have no chains or cycles, and that the donor's last frame
lies in the recipient's rank-18 gauge.

The emitted forward sequence is:

1. All undeferred expanded old-value corrections at the common zero frame.
2. Every source injection at the identical source-line frame.
3. The literal original-source `K` blocks, after all source injections.
4. Every phase-one signed carrier operation.
5. Every copied-center read, while data targets still have frame zero.
6. Every remaining carrier operation, with each compensated recipient read
   at its actual late deadline immediately before its first operation.
7. Every side-root read and every target's final source-line cap.
8. The original-source `K` outputs added at their actual target caps.
9. Original sources raised to the full active frame and inverse `K` blocks.
10. All auxiliaries raised to the full active frame, the exact signed inverse
    of every carrier operation, and every source-subtraction cleanup.
11. The explicit norm-one endpoint adapters.

Each physical auxiliary advance follows its actual alias slot; a donor
does not receive an exterior tail before its recipient uses that slot.
At every carrier operation the frame contains the node's conservative
source span. At every broadcast the literal source and all reached targets
have the required common frame. Each target chain is replayed in actual
read order. Initial old-value read masks are conservative decoder supports:
zero coefficients can remain in these charged scalar read bounds. Exact
signed coefficients and cancellations are established by the separate
integer response checker described below.

For each cube parity class the program constructs its actual three-space
and all opposite-parity target caps. Every four-port `K` matrix has entries
`+1/2` or `-1/2`; exact integer matrix products prove that its transpose is
its inverse. The four original sources pay `[2,18,1]`. No extra auxiliary
bank or uncharged source restoration is used.

For a center at `T_U`, the program copies the complete stream, applies
`T_U^-1` to the copy, performs its scatter reads at frame zero, and erases
that temporary copy. The original stays at `T_U` until its direct advance
to `F`. The copy transform has rank `dim U=20`, and the original's final
advance has rank `22-20=2`. In the complement reverse the original advances
from `D_H=I` to `D_U`, the copy advances from `D_U` to `D_0=F^-1`, and all
early scatter reads are at `D_0`. The exact copy transition is
`D_0 D_U^-1 = F^-1 F T_U^-1 = T_U^-1`, of the same rank 20. This extends
the retained copy/read/discard interface to the present arbitrary-subspace
representatives without a commuting-projector assumption. Complete-stream
copying, pointwise reads, erasure, and parked streams remain paid finite
work under that retained interface.

The inverse sequence is generated from the entire sequence, including old
corrections, copied centers, source mixing, and cleanup. It reverses every
frame with complementation and renames both data banks. A scalar gate
`a <- ca*a + cb*b` is inverted as `a <- ca*a - ca*cb*b`; each such pair is
checked by multiplying its exact two-by-two matrices. Every read or
injection shear has its sign negated, and every source block uses its exact
matrix inverse. All reflected registers are independently replayed from
their complemented initial frames to their complemented final frames.

## Arbitrary dirty contents and the global conditional boundary

The independent baseline integer checker, run on the same frozen graph,
selection, pairs, and complex record, establishes all 1,742,400 original
source/output coefficients and all 17,214,120 dirty/output coefficients.
It also checks the exact inverse cleanup of all 33,746 mutations. This
geometry checker does not claim to redo that large response calculation.
It separately proves that the full reflected scalar word is the literal
signed inverse with the stated bank renaming, and that every scalar
incidence has a legal exact common representative in both orientations.
Together these establish arbitrary-dirty restoration and both signed
orientations for this finite candidate. A forward coefficient check alone
would not have supplied the geometric reflection gate.

Because all physical entrance gauges are zero, each completed auxiliary
core acts exactly as `F_A` on arbitrary raw dirty input, and its complemented
complete inverse acts exactly as `F_A^-1`. The three shared invocations use
orthogonal 22-blocks. Their relative actions tensor; correcting the
reversed block uses `F_A^2`, an actual rank-zero Pauli. There is no remaining
positive-width gauge child or old independent-bank exterior tail.

For every one of the 1,320 actual data ports, the checker constructs both
orthogonal exchange involutions in the ambient 66-space, verifies their
orthogonality and inverse squares, verifies their active-space images,
checks the port-independent third offset, and checks all bank-specific
interstage labels in the retained three-shear table. The two final data
extensions each have rank two. The exact scalar composition is
`(X,Y) -> (X,Y+X) -> (-Y,X+Y) -> (-Y,X)`; the inherited norm-one Pauli,
sign, and bank normalization then gives the exact ambient tensor transform.

The enormous ambient `O(66,2)` group is specified parametrically and is not
enumerated by this finite checker. Its full order, routing and row-stock
allowances are retained by the assembly certificate. The general Clifford
child implementation, ordinary leaves, complete-stream copy interface,
uniform stopped recursion, precision/grid invariant, analytic reduction,
recovery and eventual tape implementation remain the inherited written
contracts. This review supplies the finite reflected placement gate; it is
not an unconditional integer-multiplication theorem or a formal proof of
those all-size interfaces. No new general hypothesis is introduced by the
changed placement.

## Paid distribution and negative controls

The local positive-width histogram is reconstructed from every physical
slot advance and every copied-center transform. The complete inventory is
three copies of local, source-data and target-data histograms, plus 2,640
rank-two final data children. Exact zero-width adapters remain scalar work.
The result is `m=66`, `W=15,681`, 228,306 children, maximum child width 20,
rank mass 1,033,626, and deficit 1,320. Forward and reflected multisets
agree exactly. This is the complete distribution used by the independently
enclosed moment and 47-constraint/seven-margin assembly review.

The checker tests omitted complements, negative indices, wrong inverse
signs, a deleted cleanup, inserted algebraically cancelling unpaid gates,
source corruption, and a rank-mass-preserving histogram alteration.
Assertion-disabled Python is explicitly rejected before execution. These
controls reject actual altered event lists or exact source/profile
bindings; they do not rely on Python `assert` or a saved verdict.

This note and the checker were prepared with OpenAI Codex assistance.
Inherited mathematical mechanisms retain their source credits and licenses;
this independent review does not claim their invention.
