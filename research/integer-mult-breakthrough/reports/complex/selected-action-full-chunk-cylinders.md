# Complete cylinders from selected-action compaction

Status: **EXACT FINITE GAUSSIAN OPERATOR CONTROLS** and an **ALL-SIZE
ADDRESS-SHAPE LEMMA**. This changed codec leaves complete controls and
every unselected guard coordinate fixed. Its finite implementation uses
Python address indexing, so no native routing fee is inferred. The
[independently reviewed Benes candidate](benes-canonical-control-independent-review.md)
is a separate conditional implementation at supported power-of-two widths.

## The changed permutation

Use h complete fK-bit slots, with slot zero the action band. The other
h-1 bands contain immutable controls. At selected position K-1 in
column j, a row addition is active when all its controls are zero.
Let the active column list have length w. Stably move only the selected
action bits of active columns into positions 0 through w-1, then the
selected action bits of inactive columns into the remaining positions.
Leave every control bit and every K-1 unselected action guard bit at
its original address coordinate. The inverse uses the unchanged controls
to reconstruct exactly the same column permutation.

This is a bijection of the full hfK-bit address cube for every h>=2,
f>=1 and K>=1. It adds no address coordinate, clean carrier or initialized
guard. Slot ordering and orientation of a different source/target pair
would require their separate paid wrappers. The source deliberately uses
f=3 in one check; the mathematical shape does not require a power of two,
although the currently reviewed native Benes implementation does.

## Why unmoved guards give full child chunks

Fix all complete control bands. They determine w independently of action
bits. In compacted coordinates, also fix the high f-w complete action
chunks. The remaining low w complete K-bit chunks are free: their
selected values are the original active values under a bijection, and
their K-1 guard coordinates are independent unmoved spectators. A guard
need not travel with its original selected value for these free
coordinates to be the complete cube `{0,1}^{wK}`.

These cylinders are disjoint. Control prefixes with different w already
differ in their immutable control bits; for the same controls, distinct
high inactive action chunks give distinct prefixes. All cylinders
partition the full stream. In address order every cylinder is one
aligned contiguous interval of length 2^(wK). Low selected positions
are regular K-spaced axes, so a literal Z_w child preserves every
unselected guard coordinate inside that full interval.

The number of records with width w is

    binomial(f,w) 2^(f[h(K-1)+1]) (2^(h-1)-1)^(f-w).

Dividing by 2^(hfK) gives the exact binomial law with active probability
2/2^h. This includes all guard planes, inactive letters and complete
action chunks. Its total volume and normalized width law agree with
the earlier complete-chunk prefix codec, but the actual permutation is
different. A native proof of one permutation is not automatically a
native proof of the other.

## Actual Gaussian operator

For the pinned coefficient c=(1-i)/2, use the actual row addition
`G(c)=[[1,0],[c,1]]`. It acts on each original active action position and
as identity on inactive letters. The selected-only permutation moves
the active positions to the first w action axes. Its conjugate on the
complete tail cube is therefore exactly

    G(c)^tensor w = diag(c^weight) Z_w diag(c^-weight),

with c^-1=1+i and weight counted only in selected tail bits. Undoing
the address permutation returns the true physical row gate. Its inverse
uses Z_w^-1 in the same actual gauges, equivalently G(-c)^tensor w.
Controls, high inactive action chunks and all unselected guard planes
are spectators in both directions. Omitting the weight gauges changes
observable coefficients.

The endpoint is a direct sum over complete cylinders and all Gaussian
fields. Its endpoint norm is a maximum over cylinders. Sequential base
gates still compose their endpoint costs, and a recursive supplier needs
all parking regions and helper fields in this same block interpretation.
There is no precision theorem for an entire supplier in this checker.

## Evidence and distinction from the native word

The [standalone checker](../../code/complex/selected_activity_cylinders.py)
imports no Benes producer or prior prefix source. The
[full four-worker run](../../runs/20261009T073755Z-complex-selected-activity-cylinders/report.md)
uses `(h,f,K)` equal to `(3,2,1)`, `(3,3,1)`, `(3,2,2)` and `(4,1,2)`.
It checks every one of 4928 full addresses, every immutable guard and
control coordinate, and every aligned cylinder. It compares all 9856
complete sparse physical forward/inverse basis columns, including
implicit zero entries, against an independent direct row-gate loop.
All 19712 arbitrary Gaussian-dyadic fields and their actual inverse pass.
The omitted-gauge and cropped-unmoved-guard negatives reject.

Source time is 0.424360 seconds. These are exact arithmetic checks,
not measured native transform speed. The actual selected-only permutation
still uses an address-array oracle. Unlike the synthesis Gaussian binding,
these small cases enumerate all guard planes; unlike that binding, they
do not execute its modular rotations, stock placement or correction word.
Neither result substitutes for the other's scope.

The [bounded reproduction](../../runs/20261009T074655Z-complex-selected-activity-ci/report.md)
passes 576 full addresses, 1152 physical columns and 2304 Gaussian fields:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/selected_activity_cylinders.py --workers 1 --bounded
```

Omit `--bounded` and use four workers to regenerate all full cases.
The source is standard-library Python and stays unchanged across both
runs. Originals remain immutable; compact certificates retain every case
outcome, counts and seed rule. Generated field arrays deterministically
regenerate. No failed attempt occurred.

## Remaining leverage and obligations

The selected-only shape is compatible with a control-preserving switch
network and can avoid the harder variable-length full-chunk prefix route.
Batching widths, if needed, can use the separately paid seven-tape
grouping construction; direct dispatch still needs its complete fixed-tape
stack and row-count contract. Native guard placement, canonical label
pairing, all exceptions, both route directions and coefficient passes
must remain paid.

Ordinary twelve-gate Z3 remains neutral. A shorter complete word is
still missing, and even its favorable moment would need routing exponent
tau compatible with the chosen recursion exponent. Extra guard axes and
general-width remainders must appear in the full characteristic.
Consequently this shape and finite operator result certify no multiplier
or kappa.

Attribution: the transfer track proposed the selected-action-only
alternative, the synthesis track develops its guarded Benes implementation,
and the complex track derived and independently checked this complete
cylinder/operator model. This is AI-assisted internal research, not formal
verification or external human peer review.
