# Rank-two fallback refinement

## Mechanism and proof status

The eligible PR40 fixed I+J profiler pays every rank-two transition as two singleton children. This is conservative, rather than a structural theorem about their ordered pivot profiles. The independently authored [rank_two_profiler_prepare.py](code/rank_two_profiler_prepare.py) makes a distinct variant which profiles those transitions under the same five primes. It retains the original rank-one and full-identity fallbacks, matching, frame formulas and rational northeast-rank reconstruction. Its output suffix is `.fixed_ij_rank2_profiles.json`, so it preserves all original evidence.

The fixed-basis legality follows from existing general contracts at pinned commit `43f59ff533598762cbc43a5e14af2bbbc76fabbd`:

1. `notes/structured-bulk-bit.tex` gives the rational lower-triangular conjugation of an idempotent partial swap to its cross-bank pivot swaps. It then charges one width-`t` interchange for every contiguous diagonal run of `t` pivots. There is no lower restriction excluding `t=2`.
2. `notes/batched-algorithms.tex` defines `BLOCK_SHEAR` for any `t` contiguous fields, with exactly one recursive interchange and ordered-affine wrappers. Its `EDGE_SHEAR` uses the stored block start and length. Thus two pivots with row indices `i,i+1` and column indices `j,j+1` legitimately form one width-two child. Nonconsecutive or decreasing columns still require singletons.
3. A nested original-envelope rank-two difference is an idempotent projector of rank two. It is within the already proved diagonal-mask-plus-rank-at-most-four minor class. The same denominator gates and five-prime numerator product recover its exact rational pivot profile, including zeros.
4. The fixed-both `(23,25)` selected tensor corner is `diag(v) A diag(nu)`, with all scales nonzero. It has the full rank of the local projector. Therefore its ordered rational minors and pivots are exactly the local ones, and no additional physical pivot lies outside that corner. This proves the same width-two transfer in the actual fixed bases. Its affine coefficient wrappers and endpoint/bank charges remain paid.

Replacing two singleton children by one width-two child would strictly decrease the characteristic moment at every `0<tau<1`, because `2^tau<2`. It leaves `R`, `W`, loss, total rank, source/output geometry, native halving degree and the unchanged complex `C1=1` constants unchanged. The proof establishes legality if such a run occurs; it does not establish that the supplied graphs contain any.

## Bounded changed-graph controls

The variant was compiled in one explicitly allocated coordination slot, then tested on the already authored changed graphs `h6-g212-t2-balanced` and `h8-g2212-t2-balanced`. The original and refined profilers independently recomputed matching and all rational profiles. Both controls passed the original `h/v/R/loss/rank_sum` identities and every CRT/mass assertion.

| Changed graph | Additional rank-two matrices | Width-two merges | Profile runtime pair |
| --- | ---: | ---: | ---: |
| h6, grouping 212 | 78 | 0 | 0.0042 s |
| h8, grouping 2212 | 357 | 0 | 0.0208 s |

[rank2-controls.json](rank2-controls.json) binds both input DAGs, original/refined full profiles, binary hashes and block deltas. [rank2-profiler-receipt.json](rank2-profiler-receipt.json) records the public source/generated source/compiler/binary hashes, supported dimensions and exact CRT enclosures. This is a useful negative for the two changed small graphs, not an exclusion of all native h23/h25 transitions. No improved bit saving is claimed from it.

The compiled execution binary is

`work/scout/rank2-profiler-20261008T1606Z/fixed_ij_rank2_profiles`.

From the campaign directory, recover it with a fresh output directory:

```bash
python3 -B agents/scout/code/rank_two_profiler_prepare.py \
  --source-root work/scout/snapshots/pr40-43f59ff53359 \
  --output work/scout/<fresh-rank2-build>
work/scout/<fresh-rank2-build>/fixed_ij_rank2_profiles \
  work/<changed-finalist>.bin work/<changed-finalist>.bin.rank2.links
```

Profile a changed finalist in an assigned worker slot, compare only its ORIGINAL-envelope base blocks, and score the complete controller before reporting any saving. An unchanged large-graph baseline replay is unnecessary.

## Native family exclusion and limits

The coordinator subsequently profiled both changed native finalists. The refined h23 profiler visited 88,862 matrices instead of 71,412; the refined h25 profiler visited 118,361 instead of 95,139. Both five-prime runs had zero modular disagreement and exactly unchanged complete block arrays. Those observations alone would exclude only these two graphs.

[rank_two_native_family.py](code/rank_two_native_family.py) supplies a stronger exact scoped exclusion. Nested ORIGINAL rank-two transitions exhaust source-line growth, same-core-one/two growth by two coordinates, core-two to core-one growth with one new coordinate, and complements of rank-(h-2) frames. Zero-to-envelope rank-two projectors are included in same-core growth from an empty outside set. For h23 and h25 this gives 136 canonical representatives.

The independent rational formulas use the H-orthonormal core-one basis `e_j+e_core/2`, the core-two triple Gram matrix `I+J` with inverse `I-J/(n+1)`, and the normalized source triple line. Conjugate their primal and dual coordinates by `I+J` and its inverse. Both forms commute with coordinate permutations. Joint membership classes under the two frames reduce density checking to 6,716 exact representative entries, including diagonal and off-diagonal entries within any repeated class. Every entry is nonzero; every increment has trace two. [rank2-native-family.json](rank2-native-family.json) preserves the complete family/category check.

Consequently any coordinate permutation still gives an entrywise nonzero rank-two matrix. Its first rightmost pivot is in column h-1. Its second pivot must use another column and cannot be the next increasing column, so a width-two run is impossible. This excludes rank-two fallback savings for every ORIGINAL h23/h25 frame graph, rather than just the current producer. It does not exclude improved higher-rank profiles or matching choices.

The dimension/basis restriction is substantive. [rank_two_other_dimensions.py](code/rank_two_other_dimensions.py) constructs exact core-two-to-core-one increments at h11/n7 and h19/n11, with explicit coordinate permutations whose two pivots are respectively `(0,9),(1,10)` and `(0,17),(1,18)`. Both form a legal width-two run. [rank2-other-dimensions.json](rank2-other-dimensions.json) retains their full small rational matrices and permutations. These are non-native frame examples without a complete producer or data geometry; they prevent an overbroad exclusion, not a new multiplication bound.
