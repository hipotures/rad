# Decisions

- Freeze Q4 K24/.28, 100us, workers15, spec4/.5. No pool/helper retuning.
- Preserve all prior research. New source/builds isolated; no normal launcher changes.

## Q4 trace-driven design corrections, before Phase B fitting

- The first conservative shared staged-link replay overstates original copy joins: actual32K pending join totals3.269s. Q4 event samples show3.072MB copies in0.233ms (~13.2GB/s) on each device, with ~3us host enqueue. New independent per-device pinned-copy references retain the old staged sensitivity data and reconcile join costs to measured values; no fitted TG.
- True next4-window utility references have higher nonlocals than current EMA despite future information. A short target is not sufficient evidence for a deployable eviction policy. Required linear/MLP remain horizon4; the single bounded temporal extension forecasts next16-window counts, normalized to four-window units, with explicit right censoring. No holdout labels select training/normalization/calibration.
- H8 Q4 native-gate membership is ~29.8% on the32K trace, not the old IQ3 ~70%. Q4 prediction quality must be measured anew. Five of48 target layers only. Native gates cost about18.4us each and have3.73ms median host lead at this diagnostic sample; original end-verify admission is late for that target.
- Any earlier copy experiment needs independent bounded copier ownership and charged staging capacity. Publishing a ready incoming expert only before its target CPU plan, with all current routed IDs protecting victims, could avoid graph-wait deadlocks/read-after-evict. This is a feasibility hypothesis, not an implemented or validated scheduler. Phase B selection precedes any runtime implementation.
- Analysis-only inline import and whitespace SyntaxError preflights were repaired before any inference; failed logs remain. No measured run was renamed/retried for performance.

Early projection preflight failed before any output or inference: victim candidate list shadowed the victim-accounting dictionary. Fixed distinct names; original failure preserved in logs/early-projection.log. No runtime/protocol change.

H4 selected for bounded signal transfer before runtime integration: on dev code its charged-spare ready persistent publications213 exceed H1118; H8 has weaker membership and an additional size-class spare. No predictor/calibration refit after held-out results. Collect H4 at3 long profiles and3 existing independent holdouts, once each, diagnostic-only.

C history-v1 patch application failed before compilation: selector body occurs in serve and one-shot CLI. Preserve partial source/logs. history-v2 applies only the first, serve-specific body and asserts both matches exist. Algorithm/config unchanged; no model request was run.

C test harness preflight missed parents=True for analysis/live-tests directories; failed before test execution. Repaired only directory creation; retained logs/live-tests.log. Compiler flag comparison first treated a source-relative STRATA_PLE_FIXTURE_DIR path as a flag mismatch. Runtime/compiler/CUDA options match exactly; location-only fixture paths recorded separately. No rebuild or performance protocol change.

Early live memory/order freeze: reuse existing verifier logits/ids/weights before the real router; no new GPU scratch or Qwen gate copy. Predictor host buffers/worker CUDA resources are initialized BEFORE automatic cache sizing so driver allocations are included in its free-memory envelope. One existing3.072MB physical slot/device is reserved during decode (active resident capacity minus2), then returned once per request; useful promoted experts are not automatically restored after use. Transfer source is explicitly full ArenaExpertSource, not compact resident/file assembly.
