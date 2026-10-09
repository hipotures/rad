# A shared dirty helper does not rescue these canonical exchange words

## Finding and scope

The earlier four-incidence Clifford example costs five recursive mixing axes
where every symmetric graph frame costs at least six. That is a local finite
gain with specified physical ports. The complete canonical exchange tested
here does not inherit that gain. With two mutable data banks and one reused
arbitrary-dirty helper, a twelve-shear exchange at one actual common Clifford
frame costs at least `3h`, exactly the three banks' rank capacity. At `h=3`,
allowing a different common Clifford frame at each gate still gives exact
minimum nine for both retained odd labels and both three-shear orders.

These are negatives for named scalar chronologies. They do not exclude a
different shared-helper word, a simultaneous mixer, many-label central
compression, nonlinear matching frames, nonunit address operators, or an
entangled pre/post chronology. No new complete multiplier, native runtime,
characteristic saving, or exponent is certified.

## Exact physical contract

Let `A_U=C_U`, where `C_U` is the dyadic Gaussian convolution along a nonzero
odd-weight label `U`, and let `F=C_full`. The three input address operators are
`(A_U,I,I)` and the output operators are `(F,F*A_U^-1,F)`. The virtual signed
exchange is

```text
(x,y,z) -> (y,-x,z).
```

For arbitrary physical input payloads, the required actual output is therefore

```text
(F*y, -F*X_U*x, F*z),
```

because `A_U^2=X_U` and these convolutions commute. The helper's initial
payload is arbitrary; it finishes as the exact raw `F*z`, with all its fields
present. It is not assumed zero, discarded, or restored only after quotienting
by an address frame.

For a virtual shear `target += c*source`, the shared-helper implementation is

```text
target -= c*z
z      += source
target += c*z
z      -= source.
```

The two decompositions tested are `XYX` with coefficients `(1,-1,1)` and `YXY`
with coefficients `(-1,1,-1)`. Both realize the same signed exchange in twelve
shears. Exact scalar matrices include every prefix and arbitrary dirty helper
term. Deleting the final helper cleanup changes the scalar matrix.

## Common-frame obstruction

Write `L_R` for the inverse-Z Lagrangian of an actual Clifford address operator
`R`, and `d` for the dimension/intersection metric. A word performing all
scalar gates at one actual frame `M` pays each source-to-`M` and `M`-to-sink
interface. Pair the X input with the Y output, Y input with X output, and
helper input with helper output. Each paired endpoint distance is `h`:

```text
d(L_AU, L_(F AU^-1)) = h
d(L_I,  L_F)        = h
d(L_I,  L_F)        = h.
```

The first equality follows from the actual relative operator `F*X_U`, whose
mixing rank is `h`; monomial translation preserves that rank. The three
triangle inequalities give total at least `3h`. The identity common frame
attains it: the six edge ranks are `(1,0,0,h,h-1,h)`. This argument is all-size
and independent of the internal twelve-shear count, under the one-common-
frame assumption.

The complete `h=3` enumeration covers all 135 Lagrangians. For both `U=1` and
`U=7`, the minimum is nine. Forcing the retained four-incidence median gives
17 and 16 respectively. Its helper path alone costs `3+3=6`, exceeding the
helper's `h=3` capacity before the data ports are considered. Importing the
old local cost five into this different set of canonical endpoints would
omit real interfaces.

## Gate-specific exact optimization

[multiframe_helper_chronology.py](../../code/complex/multiframe_helper_chronology.py)
removes the one-common-frame restriction for the same scalar word. Its exact
dynamic program retains two current frame labels. Immediately after a gate,
the two participating banks share frame `P`; the other bank has `Q`. At the
next interaction of the helper with the other bank, choosing frame `R` costs
exactly `d(P,R)+d(Q,R)`; the untouched bank remains at `P`. The program
minimizes over every candidate `Q` and `R`, including all source and sink
interfaces. Consecutive gates on the same pair can share one frame without
changing the minimum, by the metric triangle inequality.

This state describes the entire named helper-star chronology. It does not
drop scalar incidences or auxiliary returns. All 135 full Lagrangians are
allowed, including chart-boundary and degenerate subspace frames. Rank-zero
monomial changes of actual representatives remain in the executable word;
they are not declared free native operations.

| Finite case | Complete stock | Exact minimum rank | Capacity |
| --- | ---: | ---: | ---: |
| `h=2,U=1,XYX` bounded control | 3 | 6 | 6 |
| `h=3,U=1,XYX` | 3 | 9 | 9 |
| `h=3,U=1,YXY` | 3 | 9 | 9 |
| `h=3,U=7,XYX` | 3 | 9 | 9 |
| `h=3,U=7,YXY` | 3 | 9 | 9 |

This finite optimization does not prove its minimum for every `h`. It gives
no incentive for a larger parameter sweep of this particular scalar word.
The complete chosen frame sequences and actual interface normal forms are
retained in the certificates; the full cost matrices are deterministically
regenerable and their hashes are recorded.

## Physical verification and the failed first attempt

For each chosen word, every coefficient of every actual interface is checked
against the compiled Gaussian normal form. The native wrapper reference then
moves complete payload permutations, applies all chirps and global units,
and executes the selected C factors. Each case includes every physical
origin column in all three banks and one dense deterministic input, with
four signed integer fields per address. Forward canonical outputs and the
complete inverse restoration are exact on a common Gaussian-dyadic grid.
Grid alignment uses zero extension, never truncation. The full common-frame
run checks 19,200 field values, and the full gate-specific run independently
checks another 19,200. These are literal small operator checks, not a native
fixed-tape timing experiment.

The first bounded common-frame attempt failed because its direct reference
used the low GF(2) coordinate as the low packed address bit. The native
wrapper stores slot zero in the most significant selected address bit. For
`h=3,U=1`, the required physical flip is address mask four, not one. A
discriminator confirmed that the wrapper output agrees with mask four and
disagrees with mask one. Only the direct reference indexing and translation
destination were repaired; the scalar word and compiled interfaces were
unchanged.

The exact failed source SHA is
`6d829ef5f026c63d020aa55d654ff85515377fbe5fade784e2d7a2f13f895222`.
The corrected source SHA is
`d9c1935951bfe2664fb2bff8f0cc250cd18f239b5be6b91624af8ff15c015474`.
[The recovery patch](../../fixtures/complex/one-helper-address-orientation-recovery.patch)
applies to the corrected source with `git apply --unidiff-zero` in an
isolated directory to recover the exact failed bytes. This recovery was
tested against the failed SHA. No original run or receipt was overwritten.

## Evidence, provenance, and reproduction

All sources are repository-authored exact controls; no external package or
new literature input is used. The read-only dependencies are the pinned
general actual-frame compiler, scalable compiler, canonical frame factory,
native wrapper, and native GL reference. Protocols and certificates record
each effective SHA and confirm it did not change during execution. Python
3.14.4 was used; source and bounded checks use only the standard library.

- [First failed attempt](../../runs/20261009T034744Z-complex-one-helper-first/)
- [Four-worker common-frame repair](../../runs/20261009T035246Z-complex-one-helper-reference-repair/)
- [Common-frame bounded check](../../runs/20261009T035246Z-complex-one-helper-bounded/)
- [Gate-specific bounded check](../../runs/20261009T035638Z-complex-multiframe-helper-bounded/)
- [Four-worker gate-specific run](../../runs/20261009T035638Z-complex-multiframe-helper-full/)
- [Common-frame config](../../configs/complex/one-helper-clifford-chronology.json)
- [Gate-specific config](../../configs/complex/multiframe-helper-chronology.json)

From the correct research worktree:

```bash
python3 research/integer-mult-breakthrough/code/complex/one_helper_clifford_chronology.py --workers 1 --bounded
python3 research/integer-mult-breakthrough/code/complex/multiframe_helper_chronology.py --workers 1 --bounded
python3 research/integer-mult-breakthrough/code/complex/multiframe_helper_chronology.py --workers 4
```

An optional `--output` path is created exclusively; omit it for repeatable CI
checks. Raw execution logs and source snapshots are retained in the
task-owned ignored `work/complex/<run-id>/`. Compact certificates and failure
logs are durable under each linked run. Their local persistence receipts
distinguish ignored originals from Git material. Complete text archive
publication is the coordinator's separate milestone action.

Independent synthesis-track inspection accepted the scalar echoes, actual
canonical outputs, `F*z` restoration, and the common-frame triangle scope.
Independent synthesis-track source inspection also accepted the gate-specific
state recurrence, initialization, terminal charges, grouping and backtracking;
it did not duplicate the physical run. The next useful mechanism must change
the scalar chronology or share releases across
several labels; the original median by itself supplies no complete-stock
credit for these words.
