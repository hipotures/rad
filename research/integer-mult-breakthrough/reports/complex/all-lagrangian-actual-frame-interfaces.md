# Actual Gaussian frames for arbitrary binary Lagrangians

Status: **CONDITIONAL ALL-SIZE ALGEBRAIC CONSTRUCTION**, with **EXACT FINITE
FRAME AND PORT CERTIFICATES**. Native wrappers have their separate conditional
complete-stream contract. No complete multiplier or improved kappa is claimed.

The earlier full-Lagrangian local median gain was a finite primitive. The
canonical [L_E interface compiler](scalable-actual-frame-interfaces.md) supplied
actual frames for every label subspace, including degenerate E, but its family
is smaller than all Lagrangians. This construction gives actual representatives
outside that family and prices their relative operators without identifying
different representatives for free.

## Frame synthesis

Coordinates are `(x,z)`, encoded with the low h bits for X and the high h bits
for Z. Let L be an h-dimensional isotropic subspace. Its X projection E has
dimension r; its pure-Z part is exactly E-perp by isotropy and dimension.
Choose a full binary basis P whose first r columns form a basis of E.

Applying the actual address route P-inverse sends those X directions to the
first r coordinate axes and sends Z by P-transpose. Pure-Z labels now span
all inactive coordinate axes. Row combinations of those labels remove the
inactive Z parts of the active generators, leaving generators `(e_j,A e_j)`
on the first r axes. Isotropy makes A symmetric. The canonical quadratic
chirp with polar matrix A clears that Z graph; Htilde on the r active axes
then turns the resulting pure-X directions into pure Z. This yields an actual
word F with `F^-1 Z F=L`. Every gate is Gaussian dyadic and its exact global
phase is retained.

When L has the form `L_E={(a+b,b): a in E-perp,b in E}` in `(z,x)` notation,
the factory uses the previously pinned canonical F_E word exactly. Thus its
identity, odd-line, full-C and odd-hyperplane anchors remain unchanged. The
new construction is used for all other Lagrangians. It chooses an actual
representative, including its Pauli characters; a label subspace alone does
not specify those characters or the global phase.

The [source](../../code/complex/lagrangian_frame_interfaces.py) uses only binary
elimination and O(h)-variable quadratic Gauss sums. It imports the immutable
scalable compiler `3da400b0...` and canonical frame library `ddb0255a...` as
read-only helpers. It extends actual path sums to quadratic chirps and affine
bit translations. Its current factory words exercise the quadratic extension;
arbitrary translated word families have not been exhaustively screened here.

## One-child relative operator

For actual frames A and B, put `M=B A^-1`. Conjugating both inverse-Z
Lagrangians by A identifies the source with pure Z. The dimension of the
pure-Z intersection with `M^-1 Z M` is the original intersection dimension.
Hence the rank of the X projection is

```text
r = h - dim(L_A intersect L_B).
```

The corresponding forward tableau has the same mixing rank. The exact
normal-form algebra from the pinned compiler applies to the whole actual
word: an affine support of dimension r, a nonsingular active bilinear pairing,
two quadratic unit chirps, invertible input/output binary routes, and one
C-rank child. The global coefficient is computed from the actual word,
rather than inferred from a projective tableau.

A normalized uniform Gaussian-dyadic coefficient divided by alpha-to-r has
unit norm in `Z[i,1/2]`. Parity descent in the two-square norm equation leaves
only the four Gaussian units, so an extra eighth-root or irrational physical
gate is not needed. The actual exact coefficient test retains that unit.
The [paid wrapper plan](native-frame-wrapper-plan.md) then applies for fixed
h>=3 under its complete-slot, long-record and guard assumptions. Growing h,
same-width calls, full stream stock and termination retain their existing
charges and obligations.

## Finite binding and retained physical ports

The [first bounded run](../../runs/20261009T032540Z-complex-all-lagrangian-bounded/)
constructs all 15 dimension-two Lagrangians and recompiles four interfaces at
the earlier local witness, comparing all 256 relative coefficients. Its
two-case check took 0.008 seconds. Dimension two is an algebraic control;
it does not silently inherit the three-slot native routing simplification.

The [full construction run](../../runs/20261009T032604Z-complex-all-lagrangian-full/)
constructs all 135 dimension-three frames, including 119 outside L_E, and
generates all 8,640 literal matrix coefficients. Seeded dimension-16 and
dimension-32 interfaces check all 32 and 64 Pauli images and an exact global
coefficient, respectively. Their mixing ranks are 11 and 22 and path-variable
counts are 16 and 34. Four workers completed the four cases in 1.986 seconds;
the large cases allocate no complete address arrays.

The separate [anchor verifier](../../code/complex/verify_general_clifford_anchors.py)
checks every one of the 8,640 dimension-three literal matrix entries against
the complete phased Pauli action and checks all 1,080 zero-column values
against the actual quadratic path sums. It rejects a non-isotropic frame.

An endpoint gauge must remain paid. For that reason, the anchor verifier binds
the local median directly to the original four symmetric K_A port operators:
`Htilde^-1 Q_A Htilde`, whose scalar Htilde phases cancel. The generic common
representative is new, but every original input and output operator is retained.
All 256 coefficients of the four actual relative words match their normal
forms, with selected ranks `[1,1,1,2]`. The resulting two-role shear matches
`inverse original input K -> y+=x -> original output K` on both complete
four-field banks, for one and two columns. There are 72 paired addresses,
144 physical records, and 576 scalar field values across those two cases.
No extra scalar bank is introduced. The compiled local rank total remains
five, versus the independently retained all-graph minimum six.

The [anchor run](../../runs/20261009T033226Z-complex-original-clifford-repair/)
checks those three cases in 0.099 seconds with four workers. Its initial
[syntax-only attempt](../../runs/20261009T033202Z-complex-original-clifford-ports/)
failed before execution on one mismatched bracket. No mathematical result
was accepted from it. Original source `e6345dbad855e2473166900ee976e3a004e127ff972f2c264169969f47b9297d`
is recovered exactly from corrected source
`2f2d1f20e17c324bcbdf0ec7866850ae0a82971d4f8d13a08ee123b5aa22303f`
by the tracked [recovery patch](../../fixtures/complex/general-clifford-syntax-recovery.patch).
Isolated patch application and byte equality were checked; original logs and
snapshots remain unchanged.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/lagrangian_frame_interfaces.py \
  --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/verify_general_clifford_anchors.py \
  --workers 1 --bounded
```

These entrypoints use only Python's standard library, pinned task sources and
the small immutable witness. They have no fixed output path; optional fresh
`--output` paths use exclusive creation. The anchor check's source closure
adds the paid wrapper/GL sources to the three-source construction closure.
Protocols and persistence receipts bind all source/input hashes and actual
UTC execution intervals. Reference-array timings are not native tape timings.

The 5-versus-6 gain is local. A helper entering and leaving the common frame,
canonical source/sink adaptation, a whole dirty word and its scalar stock can
consume that credit. The next discriminator is one genuinely shared f=1
dirty-helper chronology with all those endpoints paid. Independent review of
the general frame extension is pending. Developed with OpenAI Codex, with no
formal verification or external novelty claim.
