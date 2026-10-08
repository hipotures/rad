# Complete moment exclusions for the new fixed geometries

The complete actual `(24,26)` and `(26,28)` fixed I+J geometries are valid, but the completed frozen producer pools do not improve the reviewed `(23,25)` weighted witness. An independently assembled exact controller proves that EVERY pair in either pool fails at its saving `a=40278503243/10^15`. This is a scoped finite exclusion; it does not exclude future producers or matchings at either geometry.

| Geometry | Distinct axis profiles | Frozen pairs | Selected safe saving | Halving degree | Wire bits |
|---|---:|---:|---|---:|---:|
| `(24,26)` | `373 × 244` | 91,012 | `40082537907/10^15` | 9 | 28 |
| `(26,28)` | `258 × 200` | 51,600 | `392917298121/10^16` | 10 | 29 |

The selected controllers have respectively `W=237417488`, mass `148146000912`, and `W=390065312`, mass `283963124536`. All copied internal blocks, both exterior directions, growth fronts, actual fixed-basis data profiles and the paid endpoint are included. The second geometry requires degree10: degree9 does not halve its largest child676 inside parent width728. The exact test uses `2*676^degree < 728^degree`; the first uses `2*576^degree < 624^degree`.

[check_geometry_moment_pools.py](code/check_geometry_moment_pools.py) imports no producer, matcher, matrix profiler or root controller optimizer. Its rational arithmetic is the independently authored32-term logarithm/Taylor8 enclosure from [check_changed_fixed_dag.py](code/check_changed_fixed_dag.py). Every supplied profile byte count/hash, exact rank sum, original-envelope loss and zero-CRT-disagreement flag is checked against the completed frozen protocol. Both actual-geometry certificates are verified separately. The changed matrix profiles and tape compiler are inputs to this review rather than new proofs from their flags.

For `N=binom(a,3)*binom(b,3)` and a local profile at `h`, copying removes the `h` retained total blocks of width`h` and replaces them by `h` blocks of width1. With `c=N/binom(h,3)` and `B=cR`, its axis contribution to

`F(a)=sum count*(width/m)^(1-a) - W`

is `c*sum copied_blocks[t]*(t/m)^(1-a) + B*((h/m)^(1-a)+((m-2h)/m)^(1-a)-1)`. Growth, data, endpoint and the base`2N` of`W` form a constant independent of both profiles. Consequently the minimum of a rigorous LOWER enclosure for `F` over every frozen pair equals the constant lower enclosure plus the two independent minimum lower axis contributions. The bank subtractions are integer-exact. This preserves the changing denominator`W`; a rank/loss shortcut is not used.

At the reviewed reference saving, the all-pool lower bounds are respectively greater than19 and152. Thus EVERY frozen pair strictly fails, without enumerating the Cartesian product or relying on a floating point winner selection. The selected lower safe moments separately pass a strict exact upper enclosure. [The independent receipt](geometry-pool-moment-independent.json) retains exact fractions, controller mass checks, pool cardinalities and the axis-minimizing input identities.

The complete evidence needed to replay this moment exclusion is [the input bundle](evidence/20261008T1730Z-geometry-pools/complete-frozen-geometry-pools.json.gz): all838 original UTF-8 profile, protocol, result and actual-geometry files, preserved byte-for-byte with their hashes. Its1,104,576 original bytes compress to178,510 bytes. Original execution files remain unchanged and ignored. This bundle contains the finite moment inputs, not producer binaries or an implied replay of all source matrix calculations.

From the campaign directory:

```bash
python3 -B agents/scout/code/check_geometry_moment_pools.py \
  --bundle agents/scout/evidence/20261008T1730Z-geometry-pools/complete-frozen-geometry-pools.json.gz \
  --output work/<fresh-geometry-pool-review>.json
```

[The completed recovery receipt](geometry-pool-moment-recovery.json) confirms this precise gzip-only path succeeds while evaluating the captured files in memory. It does not depend on the original ignored input paths. The first checker is preserved as`check_geometry_moment_pools_v1.py`; the current version adds this archive recovery path without changing the complete-controller arithmetic.
