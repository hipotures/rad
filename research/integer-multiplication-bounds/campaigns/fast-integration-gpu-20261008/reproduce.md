# Reproduction

From a clone of hipotures/rad on the GPU research branch, set `CAMPAIGN=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008`. Python3.11+ and C++17 suffice for the exact producer and assembly paths. Source snapshots are pinned in the scout/graph input manifests; retrieve their GitHub commits via `gh api repos/<owner>/<repo>/tarball/<sha>` into external task-owned storage. Preserve the Apache2 licenses and all inherited notices.

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B "$CAMPAIGN/code/exact_composition.py" --axes "$CAMPAIGN/fixtures/axes-left23-left25.json" --phase "$CAMPAIGN/fixtures/phase-pr36.json" --assembly "$CAMPAIGN/code/adopted_pr37_balanced_assembly.py" --output /tmp/rad-left-composition.json
```

Expected first candidate: a3941743329/10^14, κ3941587961/10^14,47strict constraints and rowdegree2000. This exact representative path was exercised during the campaign. Changed producer reconstruction and separate finite acceptance live in [graph reproduction](agents/graph/reproduce.md); [geometry report](agents/geometry/report.md) identifies geometry tests and negatives.

Optional GPU discovery needs Python3.14.7, CuPy14.2.0, NumPy2.5.3 and a CUDA-compatible NVIDIA driver. Use a task-owned `CUPY_CACHE_DIR`; run `code/gpu_corner_discovery.py --device 0 --seed 2026100800 --seconds 120 --output <fresh-external-dir>` and the corresponding distinct device1 seed2026100801. CPU/GPU integer eliminations agree on the baseline; discovered candidate001 fails an independent second-prime control. Finite-field samples are discovery, not universal rational rank certificates. The campaign stopped this family when information value diminished.

Reports preserve scope and eventual limitations. Completed text evidence is gzip-published before final commit; binary graphs, dependencies, environments and CUDA caches remain external and regenerable. No live service, host configuration or independent CPU campaign is needed.

The strongest accepted combination as of the ongoing extension uses the freshly optimized original-envelope I+J axis23 and the new negative-basis axis25. Its complete source-family receipt covers all4,073,300 source pairs. Recompute its exact assembly with:

```sh
python3 -B "$CAMPAIGN/code/explicit_profile_composition.py" --axes "$CAMPAIGN/fixtures/best-mixed-negative-axis-profiles.json" --phase "$CAMPAIGN/fixtures/phase-pr36.json" --assembly "$CAMPAIGN/code/adopted_pr37_balanced_assembly.py" --geometry "$CAMPAIGN/agents/geometry/results/fixed23-negative25-data-pairs.json" --output /tmp/rad-best-mixed-negative.json
```

Expected bit saving1031979409/25000000000000, kappa825549449/20000000000000, W177092019 and47strict assembly constraints. The corresponding both-negative family has192,596 exceptions in169 exact profiles; its full heterogeneous assembly is reproduced by adding `--data "$CAMPAIGN/fixtures/both-negative-data-profile.json"`, selecting `fixtures/best-negative-original-axis-profiles.json` and the geometry receipt `agents/geometry/results/both-negative-data-input-audit.json`. It gives the slightly smaller kappa2063858677/50000000000000. Both exact representative assembly paths were exercised. Full producer/matching/local-frame reconstruction is in the graph and geometry reproduction files; independent finite input/rank-product review is in the scout classification review.

Complete selected use maps are gzip-published under `evidence/checkpoint-1457-selected/`. To materialize a specifically named original, decompress its full `<campaign-relative-path>.gz` to a fresh task-owned destination and pass that path to the verifier, or recover its original campaign-relative path when reproducing the historical commands. The manifest records original and compressed hashes. Full completed discovery/control logs and root producer cohorts are retained under `evidence/checkpoint-1504/`; originals remain external. The capacity336-case full payload exceeded the single gzip10MiB limit and was retained externally without splitting; the compact summary and regeneration source remain in Git.

The campaign was extended indefinitely by the user. The original120-minute deadline is a historical scheduling field; ongoing monitors omit their optional `--deadline`. New attempts always use fresh external directories. `code/producer_order_queue.py` runs a bounded worker pool using a pinned PR36 source and compiled binaries regenerated as documented by graph reproduction; exact configurations are under `configs/`. GPU changed-basis discovery accepts explicit source triples and basis modes. Its xorshift zero-state correction prevents an otherwise infinite mutation rejection loop; the interrupted original attempts and repaired distinct source-pair attempts are preserved separately. A finite-field discovery remains separate from a complete conditional construction certificate.

## Accepted enlarged-positive-frame construction (16:05 UTC)

The exact accepted saving is4171385779/100000000000000 and κ=4171211781/100000000000000. Complete data geometry retains169 exact classes. Selected map fixtures and full wrappers are archived whole, with unchanged source-byte hashes.

From the repository root, after the pinned PR36 source and task environment described above are available:

```bash
C=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008
RAD_WORK_ROOT=/srv/ai/work/rad/integer-multiplication-bounds/fast-integration-gpu-20261008
mkdir -p "$RAD_WORK_ROOT/reproduce-accepted-1605"
for H in 23 25; do
  for KIND in base-parent whole-clones mapped-partitions; do
    gzip -dc "$C/evidence/checkpoint-1605-recovery/agents/graph/fixtures/best-positive-negative-$KIND-$H.json.gz" > "$RAD_WORK_ROOT/reproduce-accepted-1605/best-positive-negative-$KIND-$H.json"
  done
  python3 "$C/agents/graph/code/rebuild_alternative_selected.py" \
    --source "$RAD_WORK_ROOT/repos/scout/croc-pr36-11817ccacb56" \
    --work "$RAD_WORK_ROOT/reproduce-accepted-1605/h$H" \
    --base-parent "$RAD_WORK_ROOT/reproduce-accepted-1605/best-positive-negative-base-parent-$H.json" \
    --whole-selected "$RAD_WORK_ROOT/reproduce-accepted-1605/best-positive-negative-whole-clones-$H.json" \
    --selected "$RAD_WORK_ROOT/reproduce-accepted-1605/best-positive-negative-mapped-partitions-$H.json"
done
python3 "$C/code/explicit_profile_composition.py" \
  --axes "$C/fixtures/mapped-positive-negative-axis-profiles.json" \
  --phase "$C/fixtures/phase-pr36.json" \
  --assembly "$C/code/adopted_pr37_balanced_assembly.py" \
  --geometry "$C/agents/geometry/results/both-negative-data-input-audit.json" \
  --data "$C/fixtures/both-negative-data-profile.json" \
  --output "$RAD_WORK_ROOT/reproduce-accepted-1605/exact-certificate.json"
```

Both source-only scalar/frame/link recoveries were exercised, not only the recurrence calculation. For native physical basis profiles, replay each retained provenance.native_command after replacing its DAG and selected-use inputs with the recovered copies; build the profiler from retained positive_frame_profiles.cpp using the documented command. Compare all child multiplicities and rank mass with the retained fixture. The exact local profiles use per-transition rank upper bounds and sufficient proven-prime products, rather than a sampled generic rank assumption. Completed GPU parameter catalogues are discovery evidence only and are not dependencies of this accepted certificate.

## Weighted and conjugate-basis continuation (16:26 UTC)

Weighted matching source-only replay passed on both recovered mapped parents, with mode4 and seed2026100801. The complete commands, source hashes, map hashes and CRT/physical compiler checks are retained in geometry/results/weighted-source-recovery-20261008T160331-{23,25}.json. Use geometry/code/reproduce_positive_weighted.py with those recovered scalar DAGs and labels. Full weighted and conjugate wrappers are whole gzip copies in evidence/checkpoint-1604/agents/geometry/results/.

The conjugate basis beta=-1/3 preserves every source and copied-center coordinate product. Its local matrices are transposes of the original basis projectors and must use the newly computed physical child distributions, not the old counts. The independent transfer gate is graph/results/dual-basis-transfer-gate.json and the exact rational saving is4171808793/100000000000000, withκ104290869/2500000000000. Substitute fixtures/weighted-positive-dual-negative-axis-profiles.json in the exact-composition command above and choose a fresh output filename. All47 strict constraints pass.

Completed root640/768/2304 producer tables and the256 new physical-profile experiments are archived whole under evidence/checkpoint-1622/. The new ready paid-clone192 batch follows code/continue_seeded_clones.py, after producer completion; code/continue_seeded_partitions.py searches three source-partition policies on those new clone descendants. Both preserve their full raw per-case evidence outside Git. Profile and role counts are discovery evidence until a complete exact composition and interface gates pass.

## Global matching, uniform source data and public skip-prefix integration

The stronger global-dual certificate givesκ521461257/12500000000000 after all four fresh selected mode6 source-only replay/profile/compiler checks: geometry/results/global-recovery-20261008T1628.json. Complete global wrappers are archived whole in evidence/checkpoint-1622/agents/geometry/results/. Exact composition uses fixtures/global-positive-dual-negative-axis-profiles.json and the heterogeneous negative data fixture.

The uniform hybrid source proof uses a different25 basis, beta=1/57. Its complete exact certificate is scout/gpu-parameter-results/hybrid-half-uniform-data-certificate.json; the independent audit is complete-data-input-audit-20261008T1655.json. Every47×47 integer99M matrix has entries bounded by7542. The 24 proven primes exceed the strict740bitminor bound, and directNE tables are bounded above at every pair/prime. Expected lower ranks are attained using the prior complete65521/1000003 arrays with disjoint exceptions. See retained scout/code/gpu_basis_family_crt_wide.py and its CUDA checker source hashes. GPU environment and regenerated input tables must match the audit; per-prime table hashes are deterministic reconstructions, not GPU readbacks. The exact hybrid composition remains a candidate until its new basis/interface/map reconstruction gates pass.

The public PR53 skip-prefix identity is independently implemented in code/independent_skip_search.py on the pinned PR36 generator, with retained authorship credit. No PR53/54 derivative implementation is needed. After rebuilding the already documented moment_match_positive and match_exported_dag binaries into a task-owned external directory, run the script with --source <pinnedPR36> --code "$C/agents/graph/code" --work <fresh-external-run> --workers 3 --cached-builds <own-rebuilt-binary-dir>. The default147 joint configurations include smallh10 controls and23/25 producers. Threshold3/4 continuation uses --dimensions 23 25 --thresholds 3 4 --seed 1500000041 and6workers after reserving the global CPU allocation. Scalar/output verification, support disjointness and positive native ranks are discovery gates; fresh matrix profiles, full compiler and exact composition remain mandatory.


## Pinned skip-prefix baseline and independent arithmetic

Download read-only public snapshots outside the checkout, with `gh`, Git, and Python3.12+ available:

```sh
C=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008
python3 "$C/code/fetch_public_baselines.py" --work /tmp/skip-prefix-public-sources-fresh
P54=/tmp/skip-prefix-public-sources-fresh/pr54-84eb0b067741dc2690da837743fda06d133da865
env PYTHONDONTWRITEBYTECODE=1 python3 "$P54/research/skip-clones/witness.py" --output /tmp/skip-prefix-public-arithmetic.json
python3 "$C/code/explicit_profile_composition.py" \
  --axes "$C/fixtures/pr54-original-axis-profiles.json" \
  --phase "$C/fixtures/phase-pr36.json" \
  --assembly "$C/code/adopted_pr37_balanced_assembly.py" \
  --geometry "$C/agents/scout/gpu-parameter-results/pr54-IJ-conjugate-data-compatibility-20261008T1714.json" \
  --data "$C/fixtures/uniform-21-17-data-profile.json" \
  --output /tmp/skip-prefix-independent-baseline.json
```

Both paths must return bit saving1132311451/25000000000000, κ141532521/3125000000000 and W159592676. The independently authored path reconstructs complete child counts, moments and all47 strict assembly inequalities; its frozen local matrices alone are not a source or compiler verifier. Fresh native/physical replay is recorded in `agents/graph/results/public-pr54-rebuild-1710.json` and `agents/geometry/results/pr54-unmodified-profile-comparison-20261008T1717.json`. All606 paid edits, source/target/dirty basis bits in both orientations, and the two full matrix profiles were independently reconstructed. Full-data compatibility includes exact recovery of all ten bad-primary-prime pairs and the unchanged complete coverage proof.

Selected independent PR36 skip-prefix configurations can now be rerun with `code/independent_skip_search.py --config-file <frozen-configurations.json>` and its ordinary source/code/work/build arguments. The native matching binaries must be rebuilt from the retained matching sources before publication-level recovery. Each replay requires a fresh external output directory.


## Accepted enlarged-frame skip-prefix construction

The complete unchanged selected constructor/profile inputs are retained as six unsplit gzip files under `evidence/skip-selected-1740/`; `configs/skip-selected-publication-manifest-1740.json` records their original SHA256 values. Recovery does not require the old absolute execution paths embedded as provenance. Use a fresh external directory:

```sh
C=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008
R=/tmp/enlarged-skip-recovery-fresh
mkdir "$R"
python3 "$C/code/fetch_public_baselines.py" --work "$R/public"
mkdir "$R/pr36"
git --git-dir "$R/public/objects.git" archive 11817ccacb564bb7f98789c20dc11d3fece207e3 | tar -x -C "$R/pr36"
for h in 23 25; do
  gzip -cd "$C/evidence/skip-selected-1740/agents/graph/fixtures/skip-selected-parent-$h.json.gz" > "$R/parent-$h.json"
  if [ "$h" = 23 ]; then selected=skip-cloned-axis-23; else selected=skip-fixed-selected-axis-25; fi
  gzip -cd "$C/evidence/skip-selected-1740/agents/graph/results/$selected.json.gz" > "$R/selected-$h.json"
  gzip -cd "$C/evidence/skip-selected-1740/agents/geometry/results/best-skip-enlarged-fixed-axis-$h.json.gz" > "$R/profile-$h.json"
  env PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 "$C/agents/graph/code/rebuild_skip_selected.py" \
    --source "$R/pr36" --work "$R/graph-$h" --parent "$R/parent-$h.json" \
    --selected "$R/selected-$h.json" --skip-driver "$C/code/independent_skip_search.py" --dirty
  python3 "$C/agents/geometry/code/reproduce_positive_profile.py" \
    --dag "$R/graph-$h/clones/round-2/dag.bin" \
    --selected "$R/graph-$h/clones/round-2/selected-links.json" \
    --expected "$R/profile-$h.json" --source-receipt "$R/graph-$h/rebuild-result.json" \
    --work "$R/matrices-$h" --output "$R/profile-receipt-$h.json"
done
python3 "$C/code/explicit_profile_composition.py" \
  --axes "$C/fixtures/skip-enlarged-fixed-axis-profiles.json" \
  --phase "$C/fixtures/phase-pr36.json" \
  --assembly "$C/code/adopted_pr37_balanced_assembly.py" \
  --geometry "$C/agents/scout/gpu-parameter-results/pr54-IJ-conjugate-data-compatibility-20261008T1714.json" \
  --data "$C/fixtures/uniform-21-17-data-profile.json" \
  --output "$R/exact-certificate.json"
```

Expected: R32669/42974, W159392254, bit saving4551960559/10^14, κ1137938341/25000000000000, all47 strict constraints and seven positive margins. The exact source-only path, native matrix rebuild and independent compiler were exercised on both selected axes; acceptance hashes are in `reports/skip-enlarged-fixed-acceptance-1740.json`. Do not substitute the different h25 DAG with equalR. A fresh automatic public acquisition helper replay also passed for all three pinned sources; live PR54 head has since advanced, while the requested construction pin remains84eb0b067741dc2690da837743fda06d133da865.
