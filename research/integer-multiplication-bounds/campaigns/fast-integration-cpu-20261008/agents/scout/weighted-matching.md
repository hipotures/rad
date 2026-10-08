# Actual fixed-matrix matching lane

## Scientific change

The previous exhaustive generic-rank continuation exclusion does not exclude better matchings in fixed I+J coordinates. Two different original-envelope maximum-cardinality matchings can have identical `R`, rank histogram mass and exterior controller denominator, while producing different ordered matrix pivot runs. This lane changes those physical transition occurrences and evaluates their complete fixed-basis child costs.

For an eligible donor `d`, preserved operand `v` and target `t`, continuation reuse removes `I-P_d`, `P_v` and `P_t-P_v`, and adds `P_t-P_d`. At fixed maximum cardinality, every matching has the same `R`, `W` and total rank. Close to exponent one,

`width^(1-a) = width - a*width*log(width) + O(a²)`.

Thus the local derivative surrogate favors larger

`S(P_t-P_d)-S(I-P_d)-S(P_v)-S(P_t-P_v)`,

where `S(A)` is the sum of `width*log(width)` over the ACTUAL fixed I+J pivot runs. It is not a scalar-role or generic-rank surrogate. The authored [fixed_matching_surrogate.hpp](code/fixed_matching_surrogate.hpp) uses the eligible pinned Gram formulas and profiles one admissible field only for this ranking. Floating logarithms, one-field corner mistakes and deliberately added deterministic noise can affect search order; none is used as a mathematical certificate.

[weighted_profiler_prepare.py](code/weighted_profiler_prepare.py) adapts eligible PR40 `full_profiles23.cpp` at `43f59ff533598762cbc43a5e14af2bbbc76fabbd`. It orders donor and adjacency ties by that surrogate, with a reproducible seed and noise amplitude in thousandths of log-moment units. The original rank/time/nesting eligibility test and Hopcroft–Karp augmentations are unchanged. Arbitrary traversal order preserves maximum cardinality. The selected original transitions are then profiled by the unchanged FULL five-prime rational northeast-rank reconstruction. Rank-two transitions retain the proved native singleton fallback.

No enlarged-positive label, generic rank moment, scalar-role-only denominator or optimistic data geometry enters the native scoring path.

## Recovery and source identities

[weighted-profiler-receipt.json](weighted-profiler-receipt.json) records the first compiled version and bounded controls. Its exact preparation script is retained as [weighted_profiler_prepare_v1.py](code/weighted_profiler_prepare_v1.py). The current version adds a matching-only exit and an exact-use stream for safe deduplication. [weighted-profiler-v2-receipt.json](weighted-profiler-v2-receipt.json) preserves its distinct source/generated/header/compiler/binary hashes. Generated third-party source retains the upstream Apache-2.0 notices; it and the binary live only in ignored work.

From the campaign directory:

```bash
python3 -B agents/scout/code/weighted_profiler_prepare.py \
  --source-root work/scout/snapshots/pr40-43f59ff53359 \
  --output work/scout/<fresh-build>
work/scout/<fresh-build>/fixed_ij_weighted_profiles \
  work/<copied-changed-input>.bin work/<fresh-matching>.links \
  17 100 --matching-only
```

The last argument skips full profiling. Omitting it performs the complete five-prime pass and writes `<input.bin>.fixed_ij_weighted_seed17_noise100.json`. Use fresh run/output paths; never overwrite another attempt's evidence.

The legacy link stream stores donor and target NODE, omitting the exact target occurrence. Donor traversal also changes file order. Therefore its raw byte hash is not a complete semantic matching identity. The new `<links>.uses.bin` stores donor and encoded exact use, including operand position or root occurrence. Sort those pairs canonically before hashing. This distinguishes semantically different occurrences and removes irrelevant donor serialization order.

## Completed bounded controls

[weighted-controls.json](weighted-controls.json) records two truly changed small graphs, each tested at seed0/noise0 and seed17/noise100. All four cases preserve original maximum `R`, loss and mass, pass every five-prime assertion, and produce distinct links and changed fixed profiles. A direct independent link checker verifies their original nested target-use assignments.

An independent exact logarithm enclosure also proves positive local `sum(width*log(width))` changes: over `8.3177` for both h6 variants, over `43.4983` for the h8 deterministic variant, and over `40.7257` for its noisy variant. These are derivative controls on local blocks, not complete non-native data geometry or multiplication exponents.

## Native worker

[weighted_native_worker.py](code/weighted_native_worker.py) is a single serial CPU worker. It copies the changed native h23/h25 DAGs and exact base profiles into task-owned immutable input files, verifies all exact source/output supports, runs matching-only trials, validates EVERY exact donor/use independently, and skips already seen canonical occurrence fingerprints before full profiling. Full-mode replay must produce precisely the same occurrence fingerprint as matching-only mode.

Each distinct selected profile is inserted into the full ordered `(23,25)` controller, retaining the other validated base axis, both exterior banks, both growth families, fixed data geometry and the endpoint charge. Its exact rational bit-saving search uses a 10^16 grid with 1,000-tick strict safety backoff. No weighted matching or global controller optimality is claimed.

The first native run is `work/scout/weighted-native-20261008T1633Z`, with its exact input/configuration manifest in [weighted-native-protocol.json](weighted-native-protocol.json). It completed 16 distinct exact-use matchings, eight per native axis. Every selected profile passed the unchanged full five-prime evaluation. [The completed rows](weighted-native-results.json) and [summary](weighted-native-summary.json) preserve the finite outcomes. The exact worker used by this run is retained as [weighted_native_worker_v1.py](code/weighted_native_worker_v1.py).

The best h23 profile used seed0/noise0; the best h25 profile used seed1/noise0. Combining these two independently valid matchings preserves `W=182180194`, total child rank `104751764650`, deficit `1846900`, and the inherited ordered23/25 data geometry. [The simultaneous controller](weighted-native-joint.json) has a strict checked bit saving

`a = 402783398207 / 10^16`.

[The independent complete-expression checker](weighted-native-joint-independent.json) gives a positive moment-gap lower bound `14896880242672473454368825 / 2^128`. It separately validates the changed h25 DAG's exact output family and original nested target-use assignment; the h23 DAG was already independently checked in [the changed-DAG receipt](changed-fixed-independent.json), and every new h23 exact occurrence is checked in the worker rows. [The independent native bridge](weighted-native-joint-bridge.json) preserves bit halving degree9, 28 wire bits, row coefficient852, row degree2000 and unchanged complex/compiler premises. Under the written all-size assembly hypotheses, it supports

`κ = 40277937037301793 / 10^21`.

This finite improvement comes from changed physical continuation occurrences in actual fixed I+J coordinates. It is neither an optimality certificate nor an independent certification of the inherited all-size machine premises.

[The complete compressed exact-use witness](evidence/20261008T1651Z-exact-uses/weighted-native-exact-uses.json.gz) preserves BOTH canonical donor/exact-use streams, their encoded-use schema, immutable producer inputs, selected grouping/association/threshold and full profiles with byte hashes. Its unchanged decompressed JSON contains141,362 bytes. The local original `weighted-native-exact-uses.json` remains unchanged and is ignored as row-level evidence. The two canonical occurrence SHA256 values are `e2884da0690d00a525d4f11542609dad599ce974179a85f21b6d10c5cc568272` (h23, seed0/noise0) and `c3be611253cfb958d1ef56eb408b30d7461a17ed2cc21cb3ebc69bf7503beef8` (h25, seed1/noise0). These identities include operand/root occurrences; the separate legacy node-pair stream is not substituted for them.

[recover_weighted_native.py](code/recover_weighted_native.py) reconstructs only those two selected DAGs and then executes the specified weighted matching and full five-prime matrix profiler. It accepts gzip directly and falls back to the published gzip when its original JSON argument is absent. [The completed recovery receipt](weighted-native-recovery.json) proves that BOTH regenerated DAG byte hashes, canonical exact-use streams, full profile byte hashes and profile dictionaries match the preserved witness. The exact first source for that executed receipt remains [recover_weighted_native_v1.py](code/recover_weighted_native_v1.py); the current version adds only evidence decompression/fallback and retains the decompressed witness hash. This bounded complete recovery ran in the assigned scout CPU slot while that slot's queue was briefly paused and then resumed. It did not change another agent's processes.

From the campaign directory, with `gh`, Python3 and a C++17 compiler:

```bash
gh api repos/rohanarun/integer-mult-bounds/tarball/43f59ff533598762cbc43a5e14af2bbbc76fabbd > work/<fresh-source>.tar.gz
mkdir work/<fresh-source>
tar -xzf work/<fresh-source>.tar.gz --strip-components=1 -C work/<fresh-source>
python3 -B agents/scout/code/weighted_profiler_prepare.py \
  --source-root work/<fresh-source> --output work/<fresh-build>
python3 -B agents/scout/code/recover_weighted_native.py \
  --source-root work/<fresh-source> \
  --profiler work/<fresh-build>/fixed_ij_weighted_profiles \
  --witness agents/scout/evidence/20261008T1651Z-exact-uses/weighted-native-exact-uses.json.gz \
  --output work/<fresh-recovery>
```

The preparation receipt retains the exact compiler flags and pinned source/header hashes. A machine-local generated-source or binary hash can differ after path/compiler changes; the recovered DAG, canonical occurrences and profile bytes must still equal the immutable witness. The selected DAG patterns are h23 `(2,2,2,2,2,2,2,2,2,1,1,2)`, left association, threshold2, and h25 `(2,2,2,2,2,2,2,2,1,1,1,1,1,2,1)`, right association, threshold2. Recursive non-top groups use the pinned pair/single policy, the total is retained explicitly, and shared points use the pinned `aligned_points` schedule.

[weighted_serial_queue.py](code/weighted_serial_queue.py) replenishes one CPU slot with fresh seed/noise families. It records a fresh immutable protocol and separate output directory for every family, checks historical input DAG hashes, and reuses full matrix profiles when a canonical exact-use matching repeats. The currently running queue is `work/scout/weighted-serial-20261008T1645Z`, actually launched at16:42:47 UTC; later outcomes must be judged from completed family receipts. All worker/child execution is sequential, uses one assigned CPU and one native thread, and keeps snapshots/binaries/logs ignored.

The unchanged native data/corner, exact binary compiler, complex semantic `C1=1`, row-stock and all-size machine premises remain the same explicit conditional hypotheses as [the changed-controller review](changed-fixed-review.md).
