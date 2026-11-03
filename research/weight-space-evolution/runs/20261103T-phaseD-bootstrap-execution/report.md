# Phase D — Parent-to-Editor Bootstrap: completed bounded study

**Result: no parent-created candidate showed a confirmed improvement in neural-network editing ability.**
Four independent gpt-6.1-sol / medium sessions produced four distinct direct-weight variants of Qwen3.5-0.8B. None improved the frozen primary endpoint on the independent test split; every paired 95% confidence interval includes zero. The bootstrap gate did not pass. This is a negative result for this bounded study, not proof that all direct-weight bootstrapping is impossible.

## Primary result

The unchanged Phase D v2 primary endpoint uses 15 frozen family/tier cells on 200 independent test instances (3,104 paired instance × tier × sample outputs per candidate). Confidence intervals use the frozen 2,000-resample instance-cluster bootstrap; Holm correction includes all four parents. The frozen implementation averages paired differences within instances before averaging across instances. Gold primary recovery is -0.110919.

| Parent | Sealed patch | Test Δ vs Gold | 95% CI | Holm p |
|---|---|---:|---|---:|
| 01 | p-a1a9a0be281a | -0.000086 | [-0.004251, +0.004585] | 1.000 |
| 02 | p-9378a8c33b6a | +0.000518 | [-0.005185, +0.006807] | 1.000 |
| 03 | p-41d9a0038798 | -0.000834 | [-0.010403, +0.008612] | 1.000 |
| 04 | p-f6dc81f3da9a | +0.004645 | [-0.001639, +0.011901] | 0.748 |

No candidate was select-confirmed either. Select deltas were 01: +0.002382, 02: -0.001418, 03: -0.008679, 04: -0.009715; all Holm p-values exceed 0.05. Test evaluated the fixed sealed population, including select-negative candidates, under the execution plan recorded before parents started. No candidate was replaced or repaired after select, and no select/test/transfer output reached a parent.

## Useful repairs and regressions

Slightly less negative aggregate recovery is not evidence of a newly created repair capability. The table below uses all test T2/T2P cells, including the secondary F4/T2 cell excluded from the primary endpoint. An effective repair means frozen recovery ≥ 0.5; invalid edits are no-ops. Overall validity and regression rates include all four tiers, so T0 choice performance must not be mistaken for free-form editing ability.

| Editor | Effective T2/T2P repairs / 1,600 | Overall valid rate | Overall regression rate |
|---|---:|---:|---:|
| E0 | 11 | 0.7131 | 0.2941 |
| phaseD-parent-01 | 11 | 0.7103 | 0.2947 |
| phaseD-parent-02 | 9 | 0.7100 | 0.2903 |
| phaseD-parent-03 | 7 | 0.7272 | 0.2972 |
| phaseD-parent-04 | 8 | 0.7053 | 0.2978 |

The target-level no-op baseline has recovery 0. The frozen simple heuristic averages 0.313, the improved heuristic 0.766, and the oracle 1.000 on these test instances. These are references, not matched-compute claims: the improved heuristic uses multiple probe evaluations whereas T2P permits one per trial. Complete per-family/tier validity, effective/full-repair rates, regression rates, valid-only means and jointly valid paired contrasts are retained in results/final_analysis.json.

## Random controls and transfer

Each final candidate has one predetermined-seed random editor control that permutes its Gold-relative deltas onto live positions in the same tensors. Candidate positions are excluded where capacity permits. BF16 rounding can change the actual control count/norm slightly; exact mismatches are recorded in results/final_plan.json. No parent beats its own matched random editor on test: all four paired confidence intervals include zero. p50c and five fixed random editor controls were also evaluated. Target-level matched-random, no-op and heuristic baselines remain those of the frozen benchmark.

Transfer uses 92 secret-seed instances: 44 held-out F1–F4 subtype instances plus 48 instances of the unseen algorithmic-transformer family F5. F5 is secondary and is never added to the frozen primary cells.

| Parent | Transfer core Δ vs Gold | Core Holm p | F5 Δ vs Gold | F5 95% CI | F5 Holm p |
|---|---:|---:|---:|---|---:|
| 01 | +0.004539 | 1.000 | -0.003114 | [-0.007228, +0.000213] | 0.292 |
| 02 | -0.005032 | 1.000 | +0.006347 | [-0.004578, +0.019712] | 0.687 |
| 03 | +0.007759 | 0.816 | +0.012255 | [-0.007392, +0.032570] | 0.687 |
| 04 | +0.003458 | 1.000 | -0.001073 | [-0.010676, +0.010511] | 0.808 |

No parent has confirmed positive transfer against Gold. A secondary parent-03 versus its matched random control contrast on core transfer is positive before correction (p = 0.020), but does not survive correction across four parents (p = 0.080). It also does not establish improvement over Gold. No specialization, new general capability, or recursive improvement is demonstrated.

## What actually ran

The initial laboratory goal was complete. A new execution goal, configuration and session tools were committed and pushed before parent execution (commit ebe8ab98e). Subsequent user steering explicitly withdrew the earlier agent-proposed monetary/token approval wait and authorized existing Codex access. Parents used the existing ChatGPT login through Codex CLI 0.166.0, with no new service credential or separately configured billed service. No independent claim about account billing is made.

Each parent received a fresh conversation, separate scratch space, the common task brief with a different initial search approach, permitted Gold tensor views and dev-only per-cell feedback. Specializations were not assigned. Local maxima were 30 full dev passes, 200 numerical sandbox calls and four hours per parent. Parents chose different dev aggregations and stopped after diminishing returns; the final endpoint was common. Exact Gold/no-patch requests were refused by the initial broker, so parents used explicitly disclosed near-Gold controls; final operator evaluation always uses actual Gold.

| Parent | Dev passes | Sandbox calls | Final changed entries | Direct intervention |
|---|---:|---:|---:|---|
| 01 | 12 | 19 | 36,864 | Attenuate 36 selected layer-11 MLP output columns by 0.9 |
| 02 | 15 | 17 | 1 | Multiply layer-11 query-norm coordinate 52 by 1.5 |
| 03 | 14 | 26 | 44 | Subtract 1.0 from selected decay biases in six layers |
| 04 | 12 | 23 | 64 | Subtract 0.125 from selected decay biases in six other layers |

The parent search completed 53 full dev passes and 85 sandbox calls in 1122.37 s wall time. It produced 46 distinct accepted patches. All four parent processes and both dev workers exited zero. Final independent evaluation completed 49 jobs in 935.42 s: 16 fixed evaluator entries on select, test and transfer, plus one select-only Gold technical repeat. There were four distinct final candidate tensor states, not duplicate submissions.

All candidate updates are direct numerical edits of the pinned immutable Gold checkpoint. Final recipes and parent interpretations are in parent_reports/; exact tool code, calls, responses and failures are archived. No candidate training, LoRA, SFT, autograd or optimizer updates were used. The targets are separate frozen networks; ordinary language-model answers were not used as a substitute for editing quality.

Parent thread IDs and raw CLI token usage, editor generation/probe/scoring/transition times, token-normalized and GPU-second-normalized recovery, and peak allocated/reserved memory are in results/final_analysis.json. CLI input counts include repeatedly cached conversation context and must not be interpreted as unique input data or a monetary estimate. Resource ratios for negative recovery are descriptive, not evidence of useful efficiency.

## Integrity and the observed repeat anomaly

All 595 original benchmark payload pairs and all five manifest commitments were checked, as were Gold and the original secret-salt commitment. The frozen benchmark/evaluator source lock still matches after execution. No instances, accepted cells, decoding settings, samples, metric definitions or primary statistical functions were modified. The original held-out files and salt remain private and owner-restricted.

Parent tools ran through a session-bound local broker with transactionally enforced evaluation counters, candidate ownership and irreversible sealing. Numerical Python ran in the existing no-network numpy sandbox; Gold was read-only. An outer filesystem namespace hid the topic from remaining Codex builtin tools; the privileged broker communicated over one session-specific socket. Dev workers refuse held-out splits. Final evaluation is an operator-only adapter around the unchanged persistent evaluator and registry.

Two cross-GPU dev repeats differed: 58/1,664 output texts for one near-Gold state and 7/1,664 for another state, with mean-recovery differences −0.002453 and −0.001085. Other observed repeats agreed. Transition fingerprints passed; the cause is unresolved, so global bit reproducibility across concurrent workers is not claimed. The diagnostic is preserved in results/dev_repeat_audit.json.

Before held-out scoring, Gold, all four parents and their matched controls were assigned to one discovered GPU. The second GPU ran the legacy controls and its own Gold reference. Both persistent engines stayed alive across splits; all select work completed before test, and all test work before transfer. A same-GPU Gold select repeat matched all 1,664 responses and scores exactly before test was opened. It contributes no extra primary samples. All four dev/final worker Gold audits passed. Both GPUs were idle with 1 MiB used after shutdown.

The synthetic five-job two-GPU smoke and 22 infrastructure/frozen-benchmark tests passed. A separate BF16 two-generation archive test passed, including corruption rejection. A fresh registry reconstructed all 46 archived parent patches with matching content IDs and tensor hashes, without changing production Gold. A representative p50c export also reconstructed its original ID.

## Persistence, limitations and next step

- [Compact complete analysis](results/final_analysis.json), [fixed final plan](results/final_plan.json), [sealed candidates](results/sealed_candidates.json), [recovery check](results/recovery_check.json).
- [Parent provenance and all 46 lossless patch exports](../../evidence/20261103T-phaseD-bootstrap-parent-provenance/), [full dev rows](../../evidence/20261103T-phaseD-bootstrap-dev/), [full final rows and control patches](../../evidence/20261103T-phaseD-bootstrap-final/).
- [Goal](../../GOAL.md), [configuration](../../configs/phaseD_bootstrap/), [ordered reproduction and recovery](../../reproduce.md#12-authorized-existing-codex-four-parent-execution), [artifact manifest](../../artifact-manifest.json).

Confidence is high that none of these four candidates passed the frozen primary criterion. It is limited to one configured frontier model/effort, this small Gold model, these task families and 53 dev passes. The intervals do not prove exact equivalence or exclude every small gain. No ordinary-task regression campaign or broader tentative gate threshold was validated; no broader gate success is claimed.

The provider exposes a model ID, not an immutable parent-model build revision. Exact parent re-execution is therefore not promised; accepted weight edits themselves are recoverable byte-for-byte from the archives and public pinned Gold. The private persistent backup location for the original held-out salt remains unknown. Its loss would break regeneration of these secret split identities; this pre-existing recovery gap is disclosed rather than described as solved. Private CLI login homes/account databases are excluded from evidence.

Recommended next step: diagnose the cross-GPU dev repeat differences, then preregister a qualitatively different bounded parent interface or mechanism (for example controlled activation inspection) before increasing search or population size. The present evidence does not justify recursive or population-scale improvement claims.

Configuration guidance consulted and exercised locally: [official Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), accessed 2026-11-03. The first transport probes failed closed on code-mode-host and tool-approval settings; the corrected probe succeeded. Their complete diagnostic logs are archived separately.
