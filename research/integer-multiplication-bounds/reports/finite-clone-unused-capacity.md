# Explicit clones using unused controller capacities

The new construction reduces the h51 mixer from 502,134 to **500,703 physical
roles** by adding 1,431 explicit duplicate sums and 2,862 retained-controller
links. The complete changed graph passes the existing exact logical,
coefficient, forward-frame, reverse-complement-frame and designated-target
checks. The parent independently promoted this finite witness in run
20261008T051931Z-review-explicit-clone-repair, including all 70,471,800
partial coefficients, the complete physical/frame witness and fresh improved
h12 dirty bases. It does not by itself certify a new final integer
multiplication exponent.

## Sufficient construction and proof

Let P be a binary addition of values A and B, with at least two controller
chains of outgoing uses. Suppose the original selected flow does not use P's
capacity to retain either input. Let an earlier gate Q use the same formal
value B, have an unused controller capacity, and have frame contained in P's
frame. The old B recipient at P is already occupied; otherwise the original
flow was not maximal. The A use at P has no outgoing controller link.

Insert an explicit identical addition P' immediately after P in the rank,
then node-ID schedule. Move one entire outgoing P chain to P'. Retain every
old selected link, now on its corresponding mapped uses. Add two links:
the A use at P to the A use at P', and the B use at Q to the B use at P'.
Both are chronological, join the same formal scalar value, and have nested
frames. P and Q were unused capacities. Each new recipient is fresh. The
original pivot at P can consume B while retaining A; P' consumes a terminal
input. Thus the existing reversible compiler applies.

Moving a complete outgoing chain ensures every old selected link still has
equal formal sources at both ends. A batch selects disjoint capacities
{P,Q} and conservatively excludes any selected clone parent that is a formal
input of another selected job. The changed witness is independently audited
for source equality, chronology, one retained input per gate, one predecessor
per recipient, and exact frame inclusion. Maximum-flow optimality of the new
plan is unnecessary and is not claimed.

For C compatible clones, the logical additions increase by C, incoming users
increase by 2C, selected links increase by 2C, and physical roles decrease by
C. Explicit duplicate IDs are never re-interned by scalar support.

## Frames, dirty scratch and stage transfer

Every mapped original node retains its old envelope E(C,V), and each clone
has its parent's envelope. Rewired inputs have identical formal values,
cores and supports. Since canonical envelope labels depend only on these
cores and supports, mapped labels agree with freshly constructed labels in
all Space fields. This equality was checked for every node at h12, h20 and
the complete changed h51 graph.

The frame family is unchanged: coordinates in the nonempty common core are
equal to z, total sum is 3z, and coordinates outside the support vanish.
Its restricted rational form is positive. Consequently nested forward
frames and reversed orthogonal complements retain the old rank argument.
Every designated target still meets the entire source support at its common
point in the core; the unchanged physical-target orthogonality check passes.
Initial source-copy frames remain the original triple lines.

The L/J/L-inverse/V schedule is unchanged. Complete arbitrary dirty-scratch
and center bases for the improved h12 witness pass in both orientations.
The original odd-ground h51 matching and first/third bank alignment are
inherited: cloning changes the side mixer and its physical role count,
while its inputs, target partial maps and data/center endpoints remain the
same. Full odd-stage matching was independently checked for the earlier h51
family; the changed mixer has now passed the parent's independent promotion.

## Exact measured witnesses

| Ground | Original roles | Explicit clones | New roles | Verification |
|---:|---:|---:|---:|---|
| 8 | 665 | 0 | 665 | No sufficient opportunity |
| 12 | 3,804 | 17 | 3,787 | All mapped fields, unchanged full checks, complete dirty bases |
| 20 | 23,839 | 101 | 23,738 | All mapped fields and unchanged full checks |
| 51 | 502,134 | 1,431 | 500,703 | All mapped fields and unchanged full changed-graph checks |

The h51 certificate is
[runs/20261008T050900Z-finite-clone-recovered51/results/certificate.json](../runs/20261008T050900Z-finite-clone-recovered51/results/certificate.json),
SHA256 `30337821be8c403c229a1f4588a53516f164e2e5cadc2fd2212bad803cf7fc65`.
Its compiled SHA256 is
`1c0f74cda784fe0366a1f4346f1acf1477faa2a234a9601f8f0678d60bfa30d8`.
The unchanged baseline candidate ID is
`52ce3ca9416394668daacec55e648096fd419747f393391c9bfb7fdcd039f878`.
Its base is 2 and normalized positions are eight zeros, twenty-six 23s,
then seventeen zeros. The exact baseline compiled hash is reconstructed
and compared with its immutable case; the old large physical replay is
not repeated.

The completed h51 run takes 77.997 seconds and peaks at 4,658,536 KiB RSS.
Its exact physical shared-network counts are:

```text
m = 132651
W = 452397413413750
s = 60010967023368169375
D = 2263379181875
N = 9031399015625
L = 3384009916875
```

The complete rank histogram sums exactly to s=Wm-D. Its current uniform
shrink saving enclosure has lower endpoint approximately
`3.19750461055e-9`; the exact rational is retained in the certificate.
This score is separate from the parent's newer batched recurrence.

Added scalar gates require a fresh guard. A mixer has c logical additions
and R-v scalar copies, where v is the number of inputs. Four mixers,
two J passes, two V passes and the central gathers/scatters cost exactly
`4(c+R-v)+20v` elementary scalar operations per invocation. The h51
literal scalar operation count is G=5,508,835,077,952,500. The unchanged
guard E=64(W+m+1)^3 exceeds `2GW^2+4s+4W+4` by
`3670794861655268745434778017984148373367443208`.
No old scalar gate bound is silently carried over to the changed DAG.

## Recovery and scope

[finite_clone_recovered_witness.py](../code/finite_clone_recovered_witness.py)
is SHA256 `bf4dba0b3f49534f2ff09c4153ae0d84473ec8c732dcb57bff5b4b31b56aca7d`.
It imports the frozen builder, explicit BatchCloneView and unused-capacity
candidate generator. The certificate records their exact dependency hashes.
All 1,431 clone edits, moved chain subsets, predecessor gate and use IDs,
formal child IDs and input positions are present in `rows[0].chosen`.
[finite_clone_plan_export.py](../code/finite_clone_plan_export.py) reconstructs
the exact selected-link artifact and a distinct candidate identity from
these edits, the frozen baseline and the unchanged rank schedule.

Use the math environment recorded by the campaign and the immutable original
upstream reference at commit bcd4ebde8692383539f8a48734e5fbf3a18a32c2:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -B code/finite_clone_recovered_witness.py \
  --reference "$REFERENCE" --candidate "$BASELINE_CASE" \
  --compare-frames --output "$FRESH_OUTPUT"
python -B code/finite_clone_recovered_witness.py \
  --reference "$REFERENCE" --h 8 12 20 --compare-frames \
  --dirty-ground 12 --output "$FRESH_SMALL_OUTPUT"
```

The baseline case lives externally under the campaign work root at
`derived/finite/20261008T041100Z-finite-odd-pair-refinement/cases/<baseline-ID>.json`.
The campaign publication archives preserve its complete bytes. Output paths
must be fresh. The two representative reproductions above were exercised.

The earlier two-earlier-predecessor and retained-input bridge searches found
no compatible opportunities on the best large graphs. This construction
uses the unused P capacity itself as one predecessor, so those scoped
negatives do not rule it out. The separate bounded multi-chain/repeated-round
test at h8, h12 and h20 found no additional second-round opportunity.
The completed 210-case fixed-frame clone cohort preserves every distinct
witness; its best roles by ground are h49 441,352, h51 500,651 and h53
565,176. These screen winners are distinct from the independently promoted
500,703 witness. A separate delayed-descendant-frame family now supplies
the stronger direction; see finite-clone-descendant-frames.md.
