# Literal full-materialized side splice

A complete arbitrary-dirty center-plus-side word is exact, but its rank
charge is `Wh+2qh`. The side output returns spend all the endpoint saving.
This failed constructive chronology is more specific than a general
lower bound on multiplication or on arbitrary frame synthesis.

Use source banks `x_T` at frame `C_T`, sink banks `y_T` at frame `I`,
`v` arbitrary dirty center helpers `r_T` and `R_s` arbitrary dirty side
SSA roles `a_j`, initially at `I`. Let `B` be the in-place center/null
basis, `D` its decoder, `K=D*first_q_rows(B)`, and let the invertible
dirty SSA mixer `M` have output selection `P` satisfying
`P M injection = I-K`. The actual stock is `W=3v+R_s`, independently
of the scalar addition proxy used in other capacity screens.

The complete word is:

1. At the common actual zero frame, run `B r`, subtract `D r` from the
   sinks, and undo `B`. Run `M a`, subtract its output selection, and undo
   `M`. These are the two early dirty-image echoes.
2. Move each `r_T` and input role `a_T` from zero to `C_T`, inject `x_T`,
   then move both helpers to the identical full frame. Move the remaining
   side roles from zero to full. The sources stay at `C_T`.
3. At full run `B`. Move exactly the `q` center features full to zero,
   add their decoder to the still-zero sinks, return all features to full,
   and undo `B`. Both full-width feature directions are explicit.
4. Move every sink once from zero to its final `C_full C_T^-1` frame.
   Run `M` at the actual common full frame. Move each selected side output
   full to its corresponding sink frame, add it, and return it to full.
   Undo `M`. Each output excursion costs two rank-one calls.
5. Move each source once `C_T` to full and subtract it from both its
   center helper and side input helper.

The early and late images of arbitrary dirty values cancel independently.
The sink gains `Kx+(I-K)x=x`. Every virtual source and every virtual
center/side helper restores. The final **physical** dirty helper is
`C_full` times its initial virtual dirty value. A raw-identity expectation
would be wrong. Every scalar mixer gate sees the same actual Gaussian
operator, and each scatter sees the operator of its receiving sink.

The recursive width histogram, per selected column, is

| Width | Multiplicity | Actual paths |
| --- | ---: | --- |
| 1 | `4v` | Two helper input injections and two side output excursions |
| `h-1` | `4v` | Source, sink, center input helper and side input helper completion |
| h | `R_s-v+2q` | Remaining side helper initialization and closed center feature release |

Its rank is

```text
Wh-2v + 2qh + 2v = Wh+2qh.
```

Thus this complete full-materialization ansatz supplies no positive phase
deficit, even though the isolated center-only word has a useful deficit.
The equality is a cost derivation for this literal word. It is not an
exclusion of cancellation that occurs before a helper reaches full, of
nonmonotone shared center/side frames, of scalar channel compression with
different endpoints, or of address-dependent coefficients.

[closed_center_side_splice.py](../../code/synthesis/closed_center_side_splice.py)
executes all scalar initial columns for h7/h8 single-total centers,
explicitly reindexing the lexicographic trimmed side inputs and outputs
into the total-basis source order. It also checks a small orthogonal-color
control with a dirty `I-J` accumulator mixer. The h3/f1 control replays
every physical column; the h3/f2 control replays every bank's origin
column and uses common-XOR covariance for all addresses. Omitting a
selected side output's return gives an exact arbitrary-dirty physical
counterexample.

Four workers completed the
[actual-time run](../../runs/20261009T012901Z-synthesis-center-side-splice/report.md).
The h3 controls have deficit `-6`; h7 has `-294`, h8 has `-448`.
The h7/h8 cases are complete scalar-column and literal chronology-ledger
checks; their full physical Gaussian matrices were not numerically
replayed in this run. No native tape/precision theorem or exponent is
asserted. The protocol preserves the complete loaded source closure,
including the importlib-loaded side reference and the unused transitive
capacity dependencies. Originals remain unchanged in ignored storage.

Reproduce from the dedicated worktree root with a fresh output directory:

```bash
python3 research/integer-mult-breakthrough/code/synthesis/closed_center_side_splice.py \
  --workers 4 \
  --output research/integer-mult-breakthrough/work/synthesis/<fresh-actual-UTC>-center-side-splice/results
```

The next useful discriminator must change the joint cancellation
chronology or a channel's endpoint obligation. Repeating this completed
full-materialization word over larger h cannot cross the target.
