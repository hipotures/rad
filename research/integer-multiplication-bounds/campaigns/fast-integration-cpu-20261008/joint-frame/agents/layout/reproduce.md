# Reproduce component reclamation variants

Run from the repository root. Acquire CrocSwap PR58 tested revision
`bc2f7ed4c20dc18898305ab17165c0c995cbb804` from
<https://github.com/CrocSwap/integer-mult-bounds>. Its pinned PR48 and PR55
dependency trees and manifests must be present. The campaign coordinator's
public input manifest records acquisition. Do not run inside an immutable
input snapshot.

Create a fresh directory under the campaign's ignored
`work/joint-frame/layout/`. Copy `scripts/experiments/`,
`references/frame-compiler/pr48/`, and `references/frame-compiler/pr55/` from
the pinned input, retaining the relative paths and applicable source notices.
The scripts reject a changed base compiler hash. No installed numerical
package is needed for these exact Python compiler experiments.

With `$CAMPAIGN` set to
`research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008`
and `$EXECUTION` naming the fresh execution copy, run:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B \
  "$CAMPAIGN/joint-frame/agents/layout/code/reclamation_variant.py" \
  --execution-copy "$EXECUTION" \
  --intake "$CAMPAIGN/joint-frame/agents/layout/configs/reclamation-intake.json" \
  --h 23 --policy high-rank --output "$EXECUTION/results"
```

Expected role count is 30,688. The complete physical word SHA256 is
`c83396d1ea5427eed332c45931d59ed0c8ea5eae23d16e0ea909854d41796d1e`.
The separate 25-axis low-rank control gives 40,590 roles and word SHA256
`8970424798d82df5bc25a258b80e9d83527c9937b94688a12ad706bdf0979697`.
Every attempt needs its own fresh output directory.

For guarded future live carriers, replace the driver with
`code/extended_anchor_variant.py`, omit `--policy`, and keep `--h 23`.
Expected role count is 30,780 and word SHA256 is
`534f9840dc5d04e131f782c5d694bd637990bfd5501a1309a5636d1feaa4bc1b`.
For a combined priority variant use `code/nested_reclamation_variant.py`
with `--retired-order high-rank --live-order slot`.

The receipt includes the frame histogram, full dirty-basis result in both
orientations, scalar indexed oracle result, and source hashes. Independent
physical-word replay and actual fixed-I+J profile construction are separate
checks. The campaign coordinator assembles the two axes and verifies strict
moments and all absorption margins; a compiler PASS by itself is not the
conditional multiplication theorem.

`code/extended-anchor.patch` is an exact alternative reconstruction of the
guarded live-carrier generated compiler. Apply it to the pinned base
`scripts/experiments/binary_frame_compiler.py` in a fresh execution copy with
`patch -p1`. The authored driver is the preferred reproduction because it
checks the base hash and pins the result hashes.
