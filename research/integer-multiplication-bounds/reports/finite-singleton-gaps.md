# Aligned singleton placement scored by actual compiled roles

Campaign `20261007T222521Z`; immutable upstream
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`. This follow-up changes the finite
paired DAG while retaining positive support envelopes and the same exact
controller compiler. Results distinguish additions, precompile roles and
actual compiled roles.

## Family and objective

Within each common-point group, all other complete global pairs remain
intact. Only the position of the common point's unmatched mate changes.
Positions range from 0 through `h/2-1` among the complete pairs. The local
constructor is `finite_singleton_search.singleton_class`; it preserves
physical triple names even when the local point ordering changes.

The first search optimizes a pairwise sharing objective. A pair-star node can
occur only in the two groups corresponding to its fixed pair, so the exact
pre-pruning count is the sum of local additions minus the pairwise star-set
intersections, plus outputs. Seed 109 and 128 coordinate-descent starts at
h50 gave a candidate with 493,650 precompile roles, 600 fewer than the
494,250 aligned baseline. Its actual support-envelope compilation used
486,925 roles, **725 more** than the 486,200 baseline. This candidate is a
negative demonstration that fewer additions do not determine the objective.

The retained h50 sharing table is external, 34,897 bytes, SHA256
`db885f198d9f4539a7eab4314618ce0246cdbdbd071f144f851f293338bf747a`:

    derived/finite/singleton50-20261007T234745Z.npz

It is deterministically regenerable from the source, seed and run settings.
The full coordinate-descent trace and exact candidate positions are in
`runs/20261007T234745Z-finite-singleton50/results/certificate.json`; the h8
calibration is `20261007T235100Z-finite-singleton8`.

## Actual global-gap sweep

A globally aligned gap `t` assigns position `t` to common points with
`floor(common/2)<=t`, and position `t+1` to all others. Thus `t=-1` puts all
singletons first, while `t=h/2-1` is the prior all-last baseline. This is a
bounded deterministic family with 26 cases at h50.

Every global case in `finite_singleton_reuse_scan.py` checks the complete
finite map, disjoint additions, source common-point invariants, positive
support envelopes, every physical target pairing, exact scalar compilation
and both physical frame directions. Controller selection is the unchanged
root maximum-flow optimizer under the fixed rank schedule.

| h50 gap | Precompile roles | Retained links | Actual roles |
| ---: | ---: | ---: | ---: |
| -1 | 494,050 | 7,025 | 487,025 |
| 1 | 494,004 | 7,117 | 486,887 |
| 16 | 493,650 | 6,725 | 486,925 |
| 21 | 493,544 | 6,943 | 486,601 |
| 22 | 493,500 | 7,163 | 486,337 |
| **23** | **493,530** | **8,170** | **485,360** |
| 24 | 494,250 | 8,050 | 486,200 |

The full 26-case sweep took 442.40 seconds with three workers and one BLAS
thread per worker. Gap23 improves actual h50 roles by 840 (0.173%) despite
having 30 more precompile roles than gap22. Its exact recipe is position23
for common points 0–47 and position24 for common points 48–49.

Candidate identifiers:

- Additions 434,730; inputs 19,600; partial outputs 58,800; globally merged
  additions 56,160.
- Circuit SHA256
  `8d4d25074dea8e1fa8b42c15ad8ed8388c2a49c8149fb6281d02d1dfe8d28ac2`.
- Compiled SHA256
  `24f600725a229227434f6cfc35896fd20ed41fa2a33c8b33af51550fbb542aa2`.
- Exact target pairings checked: 2,763,600.
- Sweep source SHA256
  `b8e38c22e1b55f7f261eb27f53305fee6edbe8c9bb9e733a4cb7833fd0b3e91c`.

Results are in `20261007T235115Z-finite-singleton-global-roles`. The local n49
diagnostic checks all25 positions separately: position24 uses 10,875 compiled
roles; positions2–23 use10,877; positions0–1 use10,878. Therefore the global
gap23 gain comes from global sharing and controller scheduling, although its
two local recipes individually trail the all-last local recipe.

Reproduction, using a fresh output path:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  "$PYTHON" research/integer-multiplication-bounds/code/finite_singleton_reuse_scan.py \
  --reference "$REFERENCE" --h 50 --kind global --workers 3 \
  --output "$FRESH_OUTPUT"
```

For a bounded candidate replay, append `--parameters 23`. For local counts,
use `--kind local`. The accepted analytic headline uses unequal grounds
p52,q48; a smaller h50 role count alone does not establish a stronger
headline. The complete h48 and h52 screens tie the old counts:

| Ground | Valid gaps checked | Best gaps | Actual roles |
| ---: | ---: | --- | ---: |
| 48 | 25 | 22,23 | 426,624 |
| 50 | 26 | 23 | 485,360 |
| 52 | 27 | 24,25 | 549,120 |

The h48/h52 initial cohort command accidentally included invalid gap-2. The
unchanged range assertion caught it after 22/24 valid result rows had been
persisted. Original partial outputs and failure logs are preserved rather
than overwritten. Fresh repair runs retain only the missing valid evidence:
h48 gaps2,0,-1 and h52 gaps1,0,-1. The combined evidence covers every valid
gap exactly once in the retained result set. Original run IDs are
`20261008T000120Z-finite-singleton-{48,52}-global-roles`; repair IDs are
`20261008T000620Z-finite-singleton-48-global-repair` and
`20261008T000730Z-finite-singleton-52-global-repair`. Protocols distinguish
the failed cohort attempts from the successful repairs.

`finite_singleton_certificate.py` completed its separate promotion path in
`20261008T000730Z-finite-singleton-transfer`. It checked all logical and
physical envelope transitions with an independent constraint-based checker
at h48/50/52, all physical target pairings, every stage matching image,
source-copy lines and output frames. Small h6/h8 tests checked every dirty
basis orientation, complete equal-ground exchanges and asymmetric6/8 and8/6
exchanges at seeds1 and109. The independent elementary-operation reviewer
also checked arbitrary dirty restoration and both shears at h6. The near-end
h8 recipe itself uses684 roles, below the prior696.

The transfer acknowledgment retains the positive-envelope norm proof,
transparent dirty invocation, original central-return rank loss and
intersection-one middle-ground bank joins. It does not introduce additional
decreasing-rank costs. Reviewed Gaussian-LU scoring of the unchanged best
p52,q48 counts remains exactly

    kappa = 6412736146231 / 10^30.

Thus the h50 role gain is a verified conditional finite construction
improvement and the accepted analytic headline is unchanged. Full independent
dense scalar expansion of this newly ordered h50 graph is not claimed by
this certificate; the complete symbolic scalar map and independent full
frame timeline were checked. The upstream multiplication/lifting assumptions
and separately reviewed analytic interfaces remain conditional.

Fresh near-end screens at h42,46,54,58,62 will test the apparent recursion
parity dependence and whether a nearby asymmetric composition benefits.
