# Canonical closure of three independently restored framed shears

Three complete framed identity shears can close a raw-input `C_h` operator
using literal signs, address-X permutations and a final bank exchange.
Their helpers traverse three complete paths, however. Under a fixed stock
this individually restored construction fails the necessary recursive
moment before native tape or precision costs are considered.

For one odd source label T write `A=C_T`, `F=C_h`. One complete body has
initial data frames `(A,I)` and final frames `(F,F*A^-1)`. Its helpers go
`I -> F` and restore their original virtual dirty values. Its raw physical
data map is

```text
F * [[A^-1, 0], [X_T, A^-1]],   where X_T=A^2.
```

The same body with RIGHT-composed frames `F_E*B` has exactly the same
relative operators, because `(F_2*B)*(F_1*B)^-1 = F_2*F_1^-1`.
This is an identity of actual Gaussian operators. It does not identify a
generic frame with another representative having the same Lagrangian.

The complete word uses three bodies, sharing the same dirty helper banks:

1. Apply a positive body with ordinary frames. Its source is at F, its
   sink at `F*A^-1`, and all helpers at F.
2. Apply native `X_T` to the old sink, so it is at `A*F`. Exchange the
   source/sink roles for a negative body, implemented by exact source
   signs before and after the ordinary body. Every middle frame is
   `F_E*F` on the right. Both data roles and helpers now have a common
   `F^2=X_all` background.
3. Apply `X_all` to every data **and helper** bank, then `X_T` to the new
   source. The third positive body uses ordinary frames. Its virtual
   data are `(-old_y,old_x)`. Final line-X and sign corrections followed
   by a literal raw bank exchange give F times each original raw labeled
   data bank. Dirty outputs are F times their original arbitrary values.

The line monomial `X_T` and full monomial `X_all` have separate roles.
Omitting a line alignment corrupts data outputs; omitting the all-helper
full-background repair corrupts dirty outputs. No role is assumed zero,
and no dirty physical output is mistaken for raw identity.

The pinned generic intermediate operators distinguish LEFT from RIGHT:
13 of the 31 exact relatives change under LEFT composition in the h4
word. Nevertheless conjugating the **complete** middle body by common F
leaves its end map unchanged: its end blocks are convolutions commuting
with F. Thus an end-operator mismatch is an invalid local orientation
control. The first attempt made that mistake; its failure and exact
source recovery patch are preserved. The repaired run separately checks
all RIGHT relatives and the positive LEFT complete-word covariance.

The [four-worker repaired run](../../runs/20261009T022125Z-synthesis-joint-signed-swap-repair/report.md)
checks both h4 edge orders. Each f1 case replays all 384 initial physical
columns. Each f2 case replays all 24 bank origins and three complete
Gaussian dyadic fields; no origin-only covariance promotion is made.
Every scalar gate compares the full actual operators, including the
RIGHT background. The 20-file standard-library source closure and
[failed-attempt recovery](../../runs/20261009T021906Z-synthesis-joint-signed-swap-attempt/recovery.json)
are retained.

| Paid quantity | h4 value |
| --- | ---: |
| Actual payload stock W | 24 |
| Capacity Wh | 96 |
| Width-1 child calls | 108 |
| Width-2 child calls | 24 |
| Width-3 child calls | 36 |
| Width-4 child calls | 24 |
| Recursive rank | 360 |
| Rank deficit | -264 |
| Native address-permutation bank events | 36 |
| Native constant-sign bank events | 12 |
| Native full-bank exchanges | 4 |

The listed native events are implemented literally in the finite replay.
Their time on the intended fixed-tape model is an additional obligation,
not a free-cost premise. The scalar operations of all three bodies are
retained as well.

More generally each independently restored body pays at least
`Wh-2v`: source and sink paths cost `2v(h-1)` and the `W-2v` helpers each
pay h. Three bodies therefore cost at least `3Wh-6v`. For `h>=2` and
`W>=3v`, this is strictly greater than Wh. Since every child width is at
most h, the normalized moment at exponent `1-b` for `b>=0` is at least
its first moment. This entire fixed-stock, three-complete-body ansatz
cannot contract. The obstruction does not cover a joint chronology that
leaves helpers unrestored between stages, changes the topology, or uses
additional structurally justified data capacity.

Reproduce the exact successful cases from the dedicated worktree:

```bash
python3 research/integer-mult-breakthrough/code/synthesis/joint_signed_swap_control.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/<fresh-actual-UTC>-joint-signed-swap/results
```

The implementation is
[joint_signed_swap_control.py](../../code/synthesis/joint_signed_swap_control.py).
The next useful discriminator is a joint helper/birth chronology. Three
independently completed positive components cannot be combined by reusing
the same capacity denominator and charging only one helper traversal.
