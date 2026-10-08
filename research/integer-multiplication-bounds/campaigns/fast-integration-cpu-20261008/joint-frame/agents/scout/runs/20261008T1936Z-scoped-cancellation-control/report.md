# Separately stored cancellation sides cannot contract this native moment

The total-plus-input scalar identity is valid over the binary signal field.
This report eliminates one implementation family, rather than that identity
or every implementation using it. The family stores all three ordinary side
outputs for every source triple in distinct physical carriers, first at the
common-point frame of rank `h-1`, then returns each of those same carriers to
its prescribed ordinary output frame of rank `h-3`. It retains the current
data/boundary decoder, exterior bank rows, and reversible residual cost law.
Shared ports, redistribution across globally remixed carriers, and a changed
boundary decoder are outside this conclusion.

For a triple `T` and common point `c in T`, let `H` be the full common-point
envelope and `F` the envelope excluding the other two points of `T`. The
fixed-I+J projectors satisfy `P_H P_F=P_F P_H=P_F`; their ranks are `h-1`
and `h-3`. Thus `P_H-P_F` is an idempotent projector of rank two. Reusing the
high frame at the output would change a nonzero payload component: it is not
a free implementation of the low frame.

For a reversible physical role whose path begins at the zero frame and ends
at the full frame, write `U` and `D` for its total upward and downward rank
variation. Telescoping gives `U-D=h`, so its paid residual rank mass is
`U+D=h+2D`. A same-carrier visit from `H` to `F` contributes at least two to
`D`. There are `3*v` distinct side carriers, with `v=binomial(h,3)`, hence
`D>=6*v` and their extra mass is at least `12*v` on one axis. Paying copies,
clears, or additional upward movements can only increase this bound within
the stipulated implementation family.

In the paired 23-by-25 controller, the axes are copied `v25` and `v23` times.
Consequently the extra rank mass is at least

```
2*(v25*(6*v23) + v23*(6*v25)) = 24*N,
N = v23*v25 = 4,073,300.
```

The unchanged controller ledger has mass `575*W-N+L`, where
`L=v25*23*22+v23*25*24=2,226,400`. Its original deficit is therefore only
`N-L=1,846,900`. Adding the required side-carrier variation gives mass at
least `575*W+95,912,300`. At saving zero the complete native child moment
is already greater than one, independently of the number of allocated roles
and thus of `W`. For every positive saving, each nonzero proper child term
`(t/575)^(1-a)` increases. No positive saving satisfies the strict native
moment inequality in this family.

The executable [control](../../code/cancellation_rank_drop_control.py) checks
the projector identities, ranks, and explicit omitted-drop payload witnesses
over exact rationals for all 207 triple/common-point instances in dimensions
4 through 7, plus 12 selected native instances in dimensions 23 and 25. Each
omitted-drop negative has a nonzero basis-column witness. The dimension-uniform
argument above uses the nested projector ranks and telescoping law; the finite
controls are independent checks of the formulas, rather than a replacement
for that argument. The [receipt](results/control.json) binds the executed
source and the retained projector-formula source by SHA256 and records the
exact paired-controller arithmetic.

Reproduce from the campaign root:

```sh
python3 -B joint-frame/agents/scout/code/cancellation_rank_drop_control.py \
  --projector-source joint-frame/agents/scout/code/integer_crt_profiles_v1.cpp \
  --output work/joint-frame/scout/fresh-cancellation-control.json
```

The fixed-basis projectors and inherited boundary geometry are credited to
the pinned PR58/PR48 predecessor chain in [CREDITS](../../../../CREDITS.md).
The scoped rank-variation proof and independent rational control are CPU
campaign work prepared with OpenAI Codex. This is an accepted negative result,
with no claim of global frame/circuit optimality.
