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

For the current reviewed 23-axis word, use `code/future_horizon_variant.py`
with `--h 23 --policy last-compatible`. Expected role count is 30,667 and
word SHA256 is
`f833497c99613b1f98091bc54cedc31d3d48fbe42bd3c9c76389bdc6f35c978e`.
Its 25-axis counterpart gives 40,350, so the selected pair instead retains
`code/nested_reclamation_variant.py --h 25 --retired-order high-rank
--live-order slot`, with 40,324 roles and word SHA256
`af211d47c52f613f4bb61fdc936724f1e158ff95ea470b01bed31d272868b768`.
The [independent review](../scout/latest-reviewed-pair.md) binds the full native
profiles, moments and 47-inequality certificate for exactly this pair.

## Native profile input reconstruction

The gradient experiments additionally need the scout's two finite exact
frame tables and their binary frame-ID dictionary. They are deterministic
outputs of durable authored code, not unrecoverable downloaded inputs. In a
fresh task-owned build directory compile the standalone profiler:

```bash
c++ -O3 -std=c++17 \
  "$CAMPAIGN/joint-frame/agents/scout/code/integer_crt_profiles.cpp" \
  -o "$EXECUTION/integer-crt-profiler"
python3 -B "$CAMPAIGN/joint-frame/agents/scout/code/prepare_joint_edge_costs.py" \
  --source-root "$EXECUTION" --h 23 \
  --binary "$EXECUTION/integer-crt-profiler" --output "$EXECUTION/frame-costs"
```

The fresh copy must contain the pinned source layout described above.
`frame-costs/frame-cost-input.bin` binds IDs to semantic frames;
`frame-costs/exact-frame-costs.jsonl` gives the every-corner profiles.
The generic twelve-prime integer determinant certificate proves those
rational ranks. Do not substitute one sampled modular rank or map a changed
compiler's raw region IDs directly into these tables. The 23-axis expected
hashes are respectively
`0a88ca913c44e7d5df9d52fac6d6afd9905ad3f7869d8dc4951c6ca33f0e49aa`
and `62cd325bb3ce92e205f8dc3dea4232e10b0fac4b7238ad25e4b364fe38da7eda`.
The 25-axis hashes are
`770fceb784b52c87d37e39432e4b9c34f59a14daa2ab3508e3469ca5316af155`
and `e83843584c28d1c03badc85a231bb1e8da19e82bafb68d4a77eef7f29638bac9`.
The scout exercised their full regeneration; this branch exercised their
loading, semantic remapping, hash binding and complete compiler outputs.

Run `code/profile_gradient_variant.py` with `--profile-table` naming the JSONL
and `--frame-input` naming the binary dictionary, in addition to the common
arguments. Expected roles are 30,678/40,343. The
`code/deadline_profile_fusion_variant.py` adds the future deadline before its
profile tie; it gives 30,669/40,350. Its optional `--fusion-helper` points to a
frozen copy of the coordinator's `joint-frame/code/consumer_guarded_fusion.py`;
`--max-moved-regions 256 --max-rank-gap 2` retains those role counts with changed
actual frame profiles. Each attempt uses fresh compiler/output directories.

## Complete-basis clearing selection

Use `code/dependency_selection_variant.py --policy min-rank-growth` or
`--policy min-clearing-xors`, preserving the other common arguments. The
corrected 23-axis expected counts are 30,699 and 30,731. The minimum-rank
25-axis counterpart gives 40,365. These are finished finite negatives, not
the selected bound. `code/dependency_live_fusion_variant.py` additionally
inserts future-live carriers guarded by all outstanding uses and optionally
the frozen fusion helper. Its exact per-attempt configurations are recorded
under `configs/`; each new result remains pending until completed.

`code/dependency-interpolation-fix.patch` reversibly reconstructs the initial
failed generated-source wrapper from the corrected driver. Those attempts
exit before a scientific receipt and are explicitly marked implementation
failures. Preserve their original run directories when reproducing repairs.

The single-lane `code/run_serial_variants.py` consumes an explicit immutable
JSON plan. It records each child command, source hash, PID, timestamps, exit
code and full log. Its optional live-PID wait also checks a command marker;
it never kills or otherwise controls a process. Each queued heavy child is
one-threaded, and different families have separate output directories.

## Paid nullspace-circuit continuations

Run `code/nullspace_cycle_variant_v1.py` with the common source-copy, intake,
`--h`, and output arguments, plus `--policy deadline` (or `rank-growth` or
`short-word`) `--exact-limit 8 --pair-limit 256`. The six version-1 plans
under `configs/nullspace-cycle-*-20261008T193009Z*` bind the frozen original
wrapper and its commands. These search the recorded retired-dependency span.
The current `code/nullspace_cycle_variant.py` adds
`--include-anchor-relations` for the complete admitted-pool kernel. Its larger
components are still searched only through bounded overlapping pairs. Every
run needs fresh source and output paths.

The small structural discriminator can be reproduced separately:

```bash
python3 -B "$CAMPAIGN/joint-frame/agents/layout/code/check_nullspace_discriminators.py" \
  --driver "$CAMPAIGN/joint-frame/agents/layout/code/nullspace_cycle_variant.py" \
  --output "$EXECUTION/nullspace-discriminators.json"
```

It checks two exact cancellation opportunities and deliberate missing-guard
and missing-gate controls. It supplies no native exponent certificate.

The extended kernel plans under `configs/full-kernel-*-20261008T194321Z*`
freeze six actual 23/25-axis commands with `--include-anchor-relations`,
complete driver hashes, the small-discriminator receipt hash and one CPU lane
per serial pair. Their queue coordinators wait for the corresponding frozen
version-1 serial plan, checking its live PID and command marker. Historical
PID records are provenance only and never authorize process control.
