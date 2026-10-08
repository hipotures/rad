# Upstream draft publication

The user-requested [draft PR20](https://github.com/CrocSwap/integer-mult-bounds/pull/20) is public. Its final fork head is `4f8d6c8272b5ff307a0da51df545ec3cd96a8b6e`, based on retained main `6e564879f51ae16f23d392e9e196c605f36d90df`. It preserves the conditional source-framed h53 witness `5834475279233921242758637328164947/(5*10^39)` and makes no current-best, first-threshold or priority claim. Newer PR17/18 state larger savings. They were not independently validated in this publication step.

The original research campaign ran from 2026-10-07T22:25:21Z to the user-extended 2026-10-08T10:00:00Z deadline. Subsequent work packaged already frozen results, checked reproducibility and followed the user's attribution/presentation requests. No new scientific search or clock restart occurred.

## Credit

The PR credits the original OpenAI manuscript and Douglas Colkitt's network/routing/compact-control framework as foundations. It explicitly adopts eumemic's PR13 source-frame mechanism and credits the recorded Claude assistance. It acknowledges icekylinx's batching/tape/precision framework, Bortlesboat's alignment, dleen's retained totals/stage sharing, eumemic's earlier complex/resampling/center work, Zhihao Chen's ternary producers/nested basis, Rohan Arun's geometric/matching/composition work, Aurel Prosz's parameter analysis, and the Harvey–van der Hoeven analytic background. The package distinguishes adopted mechanisms from related work whose producers were not imported.

Our contribution is limited to the selected binary graph/allocation, actual-frame cloning, common metric-isometry and separately reviewed shared-complex/tape/resampling/precision composition. The inherited theorem and proof machinery are not claimed as ours. Existing Apache-2.0 notices are retained. The final sentence is exactly: “Analysis and pull request prepared with Codex and GPT-6.1-Sol Ultra.”

## Checked publication

The standalone standard-library-only verifier reproduces three native variants, the complex characteristic and all twelve complete exact assembly rows. Relocation and corrupted-input rejection pass. Its source and all sixteen original source/input copies remain pinned. The final remote PR body matches the supplied text; the final fork verifier, provenance and README match exact bytes acquired through `gh`. Both display formulas are separate; the full kappa comparison stays together, with no terminal periods as requested. The original baseline suite was not repeated during publication.

Targeted text review corrected the stock coefficient to `(50*974+41*272)*(2+1/25)=122098.08<123000`, made the `2d<m` profile premise explicit, and stated the complete enhanced complex charge `2*G*W^2+8*s+4*W+4+32*m<E`. The source, scientific certificates, `p^123000` stock and kappa were unchanged. Agent reviews remain distinct from external human peer review.

## Recovery and limitations

The provided reconstruction patch preserves the new research package and its small root README/Makefile additions against the obtainable pinned main commit. It is not an integrated replacement multiplication-manuscript patch. The draft is a research record for independent review and possible reuse. It retains constructive but unmaterialized basis/table/shared-prime setup and separately eventual machine/record/absorption constants.

```sh
gh repo clone hipotures/integer-mult-bounds /path/to/external/publication-clone
cd /path/to/external/publication-clone
git checkout 4f8d6c8272b5ff307a0da51df545ec3cd96a8b6e
python3 research/rad-source-framed/verify.py
```

Alternatively obtain CrocSwap main at the pinned base, run `git apply --check` on `code/upstream-source-framed-review.patch`, then apply it in that separate checkout. Existing full finite evidence and conditional proofs remain in the RaD record; the portable package does not repeat 86 million coefficients or instantiate the giant setup. Full evidence remains whole gzip files with original hashes and CRCs.

The publication protocol and exact remote checks are in [the publication run](../runs/20261008T1030Z-upstream-publication/protocol.json). Raw API/replay receipts and the late upstream metadata snapshot are archived separately; authored source, compact results and this report remain readable.

The retained patch was applied to a fresh detached pinned-base worktree.
`git apply --check`, application and the recovered twelve-row arithmetic
replay all passed. Original completed scientific sources were unchanged.

The nested unified-diff artifact necessarily contains leading context spaces
on blank lines and before original Makefile tabs. Those source-preserving
markers are retained. Ordinary whitespace checks pass for all other task
files; the patch passed application and recovered-source checks. Its archive
check disables only blank-at-eol/space-before-tab warnings for that single
patch, without changing repository configuration.
