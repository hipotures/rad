# Generic metric flags: exact native characteristic

The promoted h51 R485680 bit construction has the strict native saving
`a=143492085004836477/1000000000000000000000000`. This is a changed fixed construction: one rational
ambient metric isometry places every useful kernel in the same two full
coordinate flags, creating one long canonical diagonal run per selected
residual. It is not a new rounding of the old uniform rank bound.

The all-size simultaneous-isometry theorem and complete small controls are
in [the independent proof](review-generic-metric-basis.md). The complete
h51 isometry, rational factor table, admissible prime and alphabet have
not been instantiated. Their finite deterministic computation is a
separate eventual setup constant, not covered by the numerical cutoffs.
No runtime basis adapter is charged or omitted: every actual frame and
its finite factor table are defined in the new common basis from the start.

## Counts and characteristic

The actual delayed-clone input is candidate
`5ca948ed6bd951f011d325627ca1730e4268aa63695cabcdbb59840b36dbb513` with compiled SHA256
`eb34b7ccee4439e5758643b25cc81260442a8723e5987b3d7f97b0b74ef1422f`. Its complete changed
frame/rank audit and arbitrary-dirty controls remain the accepted input.
The exact counts are `m=132651`, `W=439367045355000`,
`D=2263379181875`, and `s=58282475670006923125`.
Let `J=(R+h)v^2`. Three disjoint residual families give:

| Family | Kernel dimension | Multiplicity | One diagonal run |
| --- | ---: | ---: | ---: |
| Final middle-bank complement | 2601 | J | 127449 |
| Joined auxiliary/central complement | 102 | J | 132447 |
| Stage3 data complements | 2651 | 2N | 127349 |

The actual complete histogram validates each family rank and retains
every other edge as an individual native child. There is no identity
padding. The first `d` off-diagonal canonical pivots for a kernel of
dimension `d` also remain individual calls. Write
`M=sum_f n_f r_f log(r_f)`. With rigorous lower `M_L` and upper `log(m)_U`,
the executable certificate proves

`D-a*(W*m*log(m)_U-M_L)-a^2*s*log(m)_U^2/2 > 0`.

This follows directly from `exp(-x)<=1-x+x^2/2` for `x>=0` and
`m^(1-a)>=m*(1-a log(m))`. It certifies
`sum n_r r^(1-a)<W*m^(1-a)`, not a uniform `log(s/W)` surrogate.
All logarithms use outward exact rational intervals on a common dyadic
`2^256` grid. The strict gap is an exact positive rational; its downward
six-place decimal is `0.000001`.
The independent theorem certificate uses a slightly stronger positive
normalization witness, `143492327855947419/10^24`, and covers this value.
The root's later [actual data-family and longer-log review](generic-basis-independent-review.md)
independently reconstructs the counts, moments and relevant tensor data
matrix rather than relying only on abstract kernel pilots.

## Deeper rows and setup

The maximum selected run is `132447=m-4h`. Exact integer arithmetic proves
`m^651>2*132447^651`, so depth is at most `651 ceil(log2 e)`.
After `e<=C*p`, `p>=C`, `log2 p>=25`, and `W<2^49`,
`49*651*(2+1/25)<66000` gives the complete row stock `p^66000`.
The sufficient numerical reservoir condition is
`b^(1-epsilon)>264000(log2 b+8)` for the retained `p=6b` convention.
The former `p^2600` claim is explicitly rejected for this new basis.
The alphabet/table/layout constant `C` remains separately eventual.

## Executed evidence and reproduction

The [source](../code/downstream_generic_metric_characteristic.py),
[protocol](../runs/20261008T063741Z-downstream-generic-metric-characteristic/protocol.json),
and [certificate](../runs/20261008T063741Z-downstream-generic-metric-characteristic/results/certificate.json)
are frozen. Certificate SHA256: `54b21ef62e78b5e2b376d7249b64a6d4d632e417ee835703b89f2ca4e6f0639f`.
The one-worker exact child completed within the recorded 0.066-second
wrapper interval and released its reservation. No large baseline or
accepted graph was replayed.

From this topic directory, with one numerical thread and
`PYTHONINTMAXSTRDIGITS=0`, use a fresh output path:

```bash
python3 code/downstream_generic_metric_characteristic.py \
  --descendant-characteristic runs/20261008T062036Z-downstream-descendant-joined-repair/results/certificate.json \
  --generic-review runs/20261008T0623Z-review-generic-metric-basis/results/certificate.json \
  --output /path/to/fresh-certificate.json
```

The [general-beta complete assembly](downstream-generic-general-beta.md)
checks the new native row stock and stops explicitly above `2m`.
This primitive is conditional on the retained native movement and
multiplication-machine interfaces. The original campaign start remains
2026-10-07 22:25:21 UTC; the user-authorized deadline is 2026-10-08 10:00 UTC.
