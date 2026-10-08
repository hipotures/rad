# Sharper moment for reflected joined pivots

The existing reflected R500703 program supports the strict native bit
saving `8184217082553401/(5*10^23)`, approximately
`1.6368434165106802e-8`. This is a sharper estimate of already grouped
canonical joined pivots. It does not change the graph, roles, factor
table, fixed native prime, physical schedule or maximum child width.
The completed parameter composition is recorded separately in the
[assembly report](downstream-joined-block-semantic-bulk.md).

The [block derivation](downstream-joined-block-hypothesis.md) identifies
`h-2` isolated maximal diagonal runs of length `h^2-2` in every joined
profile. At h51 they account for 127,351 diagonal pivots in 49 runs.
The retained universal bound supplies at least 5096 further diagonal
pivots in at most 156 runs. Therefore the joined logarithmic moment is
at least

```text
(R+h)*v^2 * [127351*ln(2599) + 5096*ln(5096/156)].
```

The proof-only lower factors expose these runs without altering the
canonical profile. They are never added to the executed factor table.
The remainder estimate uses Jensen and monotonicity; the ratio
5096/156 is greater than one. The formerly used whole-profile Jensen
moment remains a fallback and is regenerated exactly.

The fresh [profile source](../code/downstream_joined_block_profile.py)
passed four h5/h7 exact canonical-profile controls in
[run060824](../runs/20261008T060824Z-downstream-joined-block-profile-repair/results/certificate.json).
Each constructs both original and concentrated matrices and compares
the full rightmost-pivot profiles, not just ranks. The tests also show
that shifting the spike into an interior block can destroy its local
profile and that a sparse, unreflected first coordinate changes the
rank-one complement profile. Peak RSS was 30,712 KiB and mathematical
runtime was 0.8773 seconds. The earlier
[admission-only failure](../runs/20261008T055741Z-downstream-joined-block-profile/report.md)
is preserved; it launched no mathematical child.

The independent checker in
[run0603](../runs/20261008T0603Z-review-joined-block-drain/results/certificate.json)
directly checks every entry of the lower tensor transformation and the
full profiles at two h5 cases and one h7 case. Its positive-exponential
characteristic independently certifies the larger saving
`16368437325414951/10^24`; the producer keeps its own smaller strict
witness. The all-size argument is required in addition to these finite
controls.

The [characteristic source](../code/downstream_joined_block_characteristic.py)
uses exact outward logarithm intervals on a common 256-bit dyadic grid.
For `a=1-alpha`, rank sum s, total address rank W*m and a certified lower
moment M, it proves

```text
D - a*(W*m*ln(m)_upper - M) - (a^2/2)*s*ln(m)_upper^2 > 0,
D=W*m-s.
```

This follows directly from the lower tangent bound for the right side
and the quadratic upper bound for each negative exponential on the
left side. It does not require a denominator in this formulation.
Ninety-six rational bisections followed by downward rounding to a
10^-24 grid produce the strict rational witness. No floating-point
threshold is used. Both the two-family comparison and full tensor-data
characteristics passed in
[run060904](../runs/20261008T060904Z-downstream-joined-block-characteristic/results/certificate.json).

The unchanged maximum child is 127449, ratio 49/51. The retained depth
is at most `26*ceil(log2 e)`, and the complete row divisor remains below
p^2600 after the separately stated fixed setup threshold. The scalar
complex h28 guard is untouched. The new moment therefore needs no new
row-padding, precision or finite-prime claim.

Reproduce the mathematical controls and characteristic with the exact
commands in their protocols. `PYTHONINTMAXSTRDIGITS=0` is recorded for
trusted rational certificates. Each job used one worker under the
live repaired scientific cohort's shared reservation and released its
own slot. The original campaign start and deadline are retained along
with the authorized extension to 2026-10-08 10:00 UTC.
