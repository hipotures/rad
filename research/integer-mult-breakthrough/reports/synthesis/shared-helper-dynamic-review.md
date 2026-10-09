# Independent analytical review of the shared-helper exchange chronology

Status: **INDEPENDENT SOURCE AND MATHEMATICAL REVIEW**, not a duplicate
physical replay, native implementation theorem or general circuit lower bound.

The synthesis track inspected the literal scalar word, physical endpoint
formulas and dynamic program in the complex track's
[shared-helper report](../complex/shared-helper-canonical-chronology.md).
The reviewed sources are pinned as follows:

| Source | SHA-256 |
| --- | --- |
| `code/complex/one_helper_clifford_chronology.py` | `d9c1935951bfe2664fb2bff8f0cc250cd18f239b5be6b91624af8ff15c015474` |
| `code/complex/multiframe_helper_chronology.py` | `fc7d491a0da537629e5399324d03249c1b8b7acf19c6fa45979d70495454f59f` |

## Physical and common-frame contract

For arbitrary dirty `z`, the four shears `t-=c*z; z+=s; t+=c*z;
z-=s` implement `t+=c*s` and restore `z`. Three such commutators
implement the two tested signed-exchange orders without a zero-ancilla
assumption. The fixed incoming address frames are `(A_U,I,I)` and the
outgoing frames `(F,F*A_U^-1,F)`, where `A_U^2=X_U`. Consequently the
complete physical map is `(F*y,-F*X_U*x,F*z)`. In particular, the dirty
endpoint is the actual `F*z`, not raw `z` modulo a frame label.

At one actual common frame, pairing each X input with the Y output, the Y
input with the X output, and the helper input with the helper output gives
three endpoint distances `h`. The first relative operator is `F*X_U`;
translation does not change its mixing rank. Summing the three triangle
inequalities yields the correct all-size lower bound `3h`, attained by
the identity common frame. This conclusion is restricted to the declared
one-common-frame ansatz. The four-incidence median from a different port
problem does not supply an omitted canonical interface credit here.

## Gate-specific state and complete charges

The dynamic state `(P,Q)` is sufficient immediately after each helper-star
interaction: two banks share `P`, and the unpaired bank has `Q`. When the
next gate uses the helper and the previously unpaired data bank, choosing
their common frame `R` pays `d(P,R)+d(Q,R)` and leaves the other bank at
`P`. Thus the transition

```text
new(R,P) = min_Q old(P,Q)+d(P,R)+d(Q,R)
```

prices exactly the moving banks. Source initialization retains the third
bank's source frame; terminal charges include all three fixed sinks.
Backtracking reverses `(R,P)` to `(P,Q)` using the recorded minimizing
`Q`. The source assertion checking the initial off-pair endpoint is a
meaningful control against dropping that bank.

Consecutive gates on the same pair can be grouped: replacing several
intermediate common frames by their first frame increases the final
interface by at most one copy of the traversed metric distance, while
removing two copies from the paired banks. Scalar operations at a common
actual representative remain identical in virtual coordinates. The
grouping therefore preserves the minimum for this named scalar word.

All 135 full `h=3` Lagrangians are included in every state and transition.
The producer's exact minima `9=3h` for both labels `U=1,7` and both
orders follow from that finite dynamic program. The synthesis review
accepted its indexing, initialization, transition, terminal fees,
grouping and backtracking. The reported physical coefficient/field replay
belongs to the producer; this review did not rerun it independently.

The result does not enumerate alternative scalar words, simultaneous
bank mixers, shared releases across many labels, non-Clifford frames or
nonunit address operators. It does not prove the gate-specific optimum
for arbitrary `h`, a contracting full moment, or a native tape bound.
Actual monomial gauges and all physical helper endpoints remain paid
obligations in the producer word.
