# Nonmonotone frame search on a complete cancellation word

**Status: complete exact scalar and chronological rank accounting; bounded heuristic frame search found no improvement. This is not an exhaustive exclusion, a literal Gaussian operator certificate, or a multiplication result.**

The monotone trimmed-zeta telescope retains each output's self label. This experiment removes that compiler restriction: every actual scalar shear can use its own common Lagrangian, unrelated to the logical support span. The cost includes all four mixer passes, both data injections, both scatters, every consecutive wire transition, and all source/sink/dirty endpoints. This tests whether cancellation can make the cheaper scalar architecture useful before spending effort on a native recurrence.

## Shared central-plus-side word

Use the coordinator's trimmed odd-subset side DAG. For each target T, append two SSA nodes forming `central_T=x_T-side_T`. Both outputs are read by the scatter J, so `J*M*x=x` over the rationals. The central and side outputs share the whole downward/upward side circuit rather than computing two independent feature banks. The essential identity term is retained.

Every SSA role is initially arbitrary dirty. Node calculations become additive invertible shears, and the complete word is

```text
M; -J; M^-1; inject x; M; +J; M^-1; subtract x.
```

The final scalar map is exactly `y+=x`, with each source and dirty role restored. All four finite cases were replayed for every initial column. Omitting the last source subtraction gives an explicit corruption witness in each case. Rational coefficients are used without numerical approximation; inverses of mixer shears negate their coefficient.

The endpoints use `L_E={(a+b,b): a in E^perp, b in E}`. For the odd-weight label t_T, source data starts at `L_span(t_T)` and ends at full `L_GF2^h`; destination data starts at zero `L_0` and ends at `L_(t_T^perp)`. All R dirty auxiliaries start at zero and end at full. The complete physical stock is `W=R+2v`.

Each shear is a graph vertex with one selected common Lagrangian. Each physical wire connects its consecutive shear vertices, with distances between their chosen frames; its first and last incidences also connect to its fixed endpoints. Unused wires contribute their direct endpoint distance. Parallel edges retain their multiplicity. Thus the graph energy is exactly the sum of all chronological frame transitions for this specified word, independently of whether the optimizer finds a good labeling.

The direct per-wire endpoint lower bound is `W*h-2v`. Assigning the same zero frame to every scalar gate attains `W*h`, as does assigning the full frame everywhere. A useful new labeling must recover some of the `2v` difference. Full-width calls are admitted and counted; the uniform baseline has fewer than W of them, so its failure comes from zero total deficit rather than a categorical same-width prohibition.

## Optimizer and independent controls

An alpha-expansion move lets any subset of gate vertices change to one chosen common frame. Because Lagrangian rank distance is a metric, this binary problem is submodular and is solved exactly by integer maximum flow. Thirty-two independent five-vertex controls exhaust all 32 binary choices and match the flow optimum. Every accepted move is checked to avoid increasing the original graph energy.

The many-label problem is not solved exhaustively. The initial attempt accepts only strict improvements from uniform zero/full starts and uses at most two sweeps. The full L_E domains contain all binary support subspaces, including radicals. Full-Lagrangian sampling includes nongraph frames, but does not cover the whole domain in the sampled cases. A failure to improve must remain a heuristic result.

The selected best word is independently replayed chronologically: every gate moves both actual participating roles to its common frame, its measured rank is added, and every wire's final completion is charged. The resulting histogram must equal graph energy and cannot lie below the endpoint bound. This is exact rank accounting, but no Gaussian frame lifts or selected-word/tape implementation are compiled by this source.

## First four-worker results

| h | k | v | R | W | Scalar shears | Frames searched / complete domain | Best rank / capacity |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 3 | 4 | 46 | 54 | 324 | 67 / 67 L_E | 216 / 216 |
| 4 | 3 | 4 | 46 | 54 | 324 | 128 / 2,295 all-Lagrangian | 216 / 216 |
| 5 | 3 | 10 | 103 | 123 | 740 | 128 / 374 L_E | 615 / 615 |
| 6 | 5 | 6 | 221 | 233 | 1,644 | 128 / 2,825 L_E | 1,398 / 1,398 |

All scalar-column and corruption controls pass. The maximum worker runtime was approximately 11.35 seconds. Every status is `NO DEFICIT FOUND BY HEURISTIC; NOT AN EXCLUSION`. Complete chosen frame bases and every gate's coefficient/frame are retained, together with chronological histograms, seeds, exact source hashes and optimizer limits.

Equal-cost assignments can change later frontiers without improving the first move. A separately authored [plateau_word_frame_search.py](../../code/synthesis/plateau_word_frame_search.py) therefore accepts unseen equal-cost words and adds a nonuniform four-block start. Its outcomes are separate attempts, not repairs replacing these receipts. Additional chronology families and residual per-address monomial gauges are independent questions; the present scalar word uses a coherent constant-coefficient frame gauge.

The second four-worker attempt completed four sweeps from each of three starts. It searched all 67 L_E frames at h=4, 256 of 2,295 full Lagrangians at h=4, all 374 L_E frames at h=5, and 256 of 2,825 L_E frames at h=6. Every best score again equals capacity. The h=5 zero and full starts visited respectively 161 and 174 distinct equal-cost words; its nonuniform start fell from 1,721 to 615 and visited 139 words. Thus the second attempt really explores distinct plateaus rather than repeating the first strict-only labeling. Its largest worker runtime was approximately 56.82 seconds. These are still heuristic no-discovery outcomes, not exclusions.

The [second compact receipts](../../runs/20261008T225452Z-synthesis-plateau-word-frames/results/summary.json) preserve all per-start traces, distinct-word counts, exact scalar controls and chronological histograms. Original JSON remains unchanged under ignored `work/synthesis/20261008T225842Z-plateau-word-frame/results/`.

## Reproduction and provenance

Run from the repository root, with fresh output directories:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/global_word_frame_search.py \
  --workers 4 --rounds 2 --full-limit 128 --large-limit 128 \
  --output research/integer-mult-breakthrough/work/synthesis/NEW-GLOBAL-WORD/results
python3 -B research/integer-mult-breakthrough/code/synthesis/plateau_word_frame_search.py \
  --workers 4 --rounds 4 --limit 256 \
  --output research/integer-mult-breakthrough/work/synthesis/NEW-PLATEAU-WORD/results
```

Only Python's standard library is needed. [global_word_frame_search.py](../../code/synthesis/global_word_frame_search.py) imports the earlier independent binary linear algebra and dirty trimmed-side compiler; all effective dependencies are hashed in the [first protocol](../../runs/20261008T225257Z-synthesis-global-word-frames/results/protocol.json). The [compact first receipts](../../runs/20261008T225257Z-synthesis-global-word-frames/results/summary.json) identify the unchanged original receipts in ignored `work/synthesis/20261008T225230Z-global-word-frame/results/`. The durable run ID follows the actual recorded launch UTC; the earlier directory label is merely a local output name.

The next step is to inspect complete nonmonotone frontiers or a genuinely different central/side cancellation word if these heuristics remain at capacity. Any positive score requires independent exact Gaussian lifting, full arbitrary-payload operator replay, every residual adapter, native tape/precision costs, and a favorable complete recursive moment before claiming an exponent. This source and analysis were developed with OpenAI Codex; no external novelty or formal verification is claimed.

A bounded reusable [verify_word_frames.py](../../code/synthesis/verify_word_frames.py) runs complete h=4 scalar columns, all matched scalar/dirty-endpoint/missing-transition corruptions, ten graph-versus-chronological frame assignments and the 32 independent binary mincut controls. It does not run a many-label discovery sweep. The [recorded bounded receipt](../../runs/20261008T225937Z-synthesis-word-ci/results/check.json) passed in approximately 0.06 seconds. CI may register the command `{python} -B research/integer-mult-breakthrough/code/synthesis/verify_word_frames.py` with all five effective files listed in that receipt; green checks have precisely its stated scalar/accounting scope.

## Complete text evidence recovery

The readable summaries omit only the full chosen frame bases and scalar gate words.
Recover every original field and byte from the [strict-search gzip](../../evidence/20261008T230948Z-checkpoint-four-20261008T225257Z-synthesis-global-word-frames/results/certificate.json.gz)
and [plateau-search gzip](../../evidence/20261008T230948Z-checkpoint-four-20261008T225452Z-synthesis-plateau-word-frames/results/certificate.json.gz).
Each summary records the original size, SHA-256 and omitted row counts. Original
local files are unchanged and ignored; the complete gzip copies are present in Git.
