# Literal complex basis wrappers cannot pay for their own routing

Replacing each binary row addition in the unchanged complex residual compiler by two additional complex children already destroys its rank deficit on one actual family of retained data fronts. This is a proved family-specific lower bound. The eligible source has not instantiated a literal instruction list for its common generic basis, so no exact total row-add count is claimed.

The eligible PR40 reference is`43f59ff533598762cbc43a5e14af2bbbc76fabbd`, by Rohan Arun, retaining icekylinx's copied-center complex assembly and the two-stage topology credited to Aurel Prosz and Zhihao Chen. `notes/copied-centers-complex.tex` gives `m=784`, `W=537696432`, `s=421548223824`, and `mW-s=5778864`. It retains`4N` physical data fronts of rank27, where `N=3276^2=10732176`. `notes/copied-centers-lemma.tex` explicitly keeps every exterior, data-front and endpoint-correction call. The inherited stage-one boundary in `references/copied-centers/pr29/two-stage-16-note.tex` contains the front

`Y: 0 -> im(I-P_X) tensor im(Q_Y)`

once per actual source triple pair. The current complex payload is Gaussian dyadic, but these address labels and the normal-form basis permutations are binary, as `notes/structured-bulk-complex.tex` and `notes/endpoint-gauge-complex.tex` specify. Triple indicators have binary norm one, so this front's residual space is

`V_XY = t_X^perp tensor span(t_Y)`, of dimension27.

Fix ANY one global binary address basis of the784-dimensional tensor address space. For each of the3276 distinct triple indicators`Y`, put `K_Y = F_2^28 tensor span(t_Y)`. Distinct binary triple lines are distinct one-dimensional subspaces, and therefore `K_Y intersect K_Z = {0}` for `Y != Z`. A coordinate27-space`V_XY` in this fixed global basis requires27 basis vectors lying in`K_Y`. Each global basis vector can belong to at most one`K_Y`. Consequently at most`floor(784/27)=29` values of`Y` can have even ONE coordinate first front. At least

`(3276-29)*3276 = 10637172`

of the actual retained fronts are noncoordinate, for EVERY such common basis. This is an allocation count over the actual source family, rather than an assumed overhead per arbitrary matrix.

In the literal residual normal form, both its input and output binary basis wrappers must transport the residual between this space and a coordinate child space. A bit permutation preserves coordinate subspaces. Hence a noncoordinate front requires at least one binary row addition in each wrapper, including the inverse wrapper. Unit diagonal phases do not change the address subspace. Just this retained family forces at least`21274344` row additions. Under the proposed identity charging two extra rank-one native complex children per addition at the same original role volume, it adds at least`42548688` rank units.

The unchanged controller can tolerate at most`2889431` such row additions, since its strict mass test needs `2*A < 5778864`. The conservative forced lower bound makes its moment at exponent1 at least

`1 + 1403/16084936 > 1`.

At every exponent strictly between0 and1, normalized positive child powers are at least their rank fractions, so it cannot regain a strict moment. Other data fronts, exterior wrappers and internal calls need not be counted to obtain the exclusion.

The assumptions matter. This excludes the additive substitution in independently implemented per-residual input/output wrappers, with ONE common address basis, the original child list and its denominator. It does not exclude a new schedule that shares or cancels basis changes across calls, uses persistent varying role bases with a paid physical interface, fuses the new children with existing ones, or implements a different complex self-routing mechanism. Such changes require a new complete map and controller accounting.

[check_complex_front_wrapper.py](code/check_complex_front_wrapper.py) checks the retained-front source assertions, records exact source hashes, confirms all3276 actual binary triple lines are distinct and odd, and verifies the complete integer deficit/count arithmetic. [The receipt](complex-front-wrapper-exclusion.json) distinguishes this analytic lower bound from an unavailable literal synthesized gate count. Run from the campaign directory after recovering the pinned source:

```bash
python3 -B agents/scout/code/check_complex_front_wrapper.py \
  --source-root work/<fresh-pinned43f59-source> \
  --output work/<fresh-front-wrapper-review>.json
```
