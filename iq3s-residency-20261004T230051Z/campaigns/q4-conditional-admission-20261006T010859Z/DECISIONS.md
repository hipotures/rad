# Decisions

- Frozen Q4 control unchanged. Gate required before live candidate.
- No unrelated architecture/pool/tuning work.
- Old v2 campaign immutable.

## Before fitting/holdout

- Twelve task-level splits frozen before any Q4 data generation; entire structured/prose family held out. Four development, two calibration, six holdout. No primary long-document fit.
- Logistic L2=1, one scalar Platt calibration on the two calibration tasks; victim log-count auxiliary L2=5. No hyperparameter search.
- Rule share thresholds0.015/0.03/0.06; logistic probability thresholds0.05/0.12/0.25. Three coarse points each, no dense sweep. Prior resolved failures and victim protection/history included.
- Select largest unpublished-byte reduction that retains>=80% both next4 benefit and observed later use, modeled nonlocals/victim<=+2%. If none, freeze closest constrained tradeoff before untouched holdout and preserve failure.
- Final4windows censored for future-use fit/threshold evaluation; current+next3 demand labels. No terminal lifetime-as-negative labeling.
- Fixed-native-schedule paired attribution ends on a transaction touching either expert. It respects same-layer byte/capacity but does not predict alternate native adaptation/MTP trajectories or simulated TG. Conservative lost-use bound also reported.
- H4/history ablation uses identical numeric features excluding H4 columns, not a broad model bake-off. Auxiliary victim risk is measured separately.

- Before holdout: pooled gate cannot hide family collapse. Each held-out code/math/structured family must retain>=70% both benefit/use, reduce unpublished bytes>=50%, modeled nonlocals<=+2%; the pooled useful retention remains>=80%. No live fallback to a different held-out operating point.

##01:28:51UTC — freeze before holdout

Logistic balanced p>=0.12 chosen only from2calibrationtasks: unpublished-77.9%,next4benefit86.6%,observedlateruse94.8%,attributednonlocal+1.35%,victimabsence-12.2%. Checkpoint40f43308e62168d1f0c814dd5d4bbae9c13efaa21193ce69ce70a37e007c508c. No nonlinear fit justified because primarylinear already passescal gate. Untouched holdout not yet evaluated; no guarantee of generalization.

## Documented live gate judgment after sealed holdout, no retuning

Pooled user aids pass: waste-73.76%,next4benefit85.38%,observeduses90.16%,nonlocal+1.342%,victimabsence-15.15%. Our additional family guard failed onlycode at+2.20% versus+2.00%. Original strictFalse verdict remains immutable. User explicitly makes numerical aids approximate and allows judgment. Permit experimental live validation of the SAME p>=0.12/checkpoint, with family warning retained. No re-fit/rethreshold/alternative selection. Only measured practical improvement may change deployment baseline; modeled attribution is not proof of a speedup. Seephase-b/live-gate.json.

## Main protocol arm-order repair before third replicate

The original context-rotation/parity formula placed control first in all three256K pairs. This was detected after11valid requests, before anythirdreplicate. The first12plannedpoints/results stay untouched. Thirdreplicate uses256Kconditional-first,32Kcontrol-first,128Kcontrol-first, yielding both armorders at everycontext. No binary, model, settings, input, warmup or repetitionlimit changed. Both orderversions remain saved.

The already-running control32Krep2 is allowed tofinish. An ownedzero-request sentinel invokes the originaldriver's refuse-overwrite guard at the NEXTpoint, before serverstartup. This is a safe checkpoint, not an interrupted/invalid measured request. Sentinel evidence is archived before resuming the remaining sixpoints with the repairedorder. Absolute deadline is unchanged. Seephase-c/order-repair.json.

## One candidate-OFF timing guard

After the complete 18-request matrix, add one fresh 32K/4096 request with the already-built candidate and both early/conditional flags OFF. The 32K gain coincides with lower CPU completion timers, while CPU translation-unit sources and flags match. This is a narrow source/code-generation/environment guard, not another production-control repetition or tuning branch. Full-length input/output/MTP/routing/capacity parity will be checked. A single later-time timing ratio is diagnostic only. Original ablation plan remains preserved; no model or threshold changes.

## OFF guard: do not attribute the 32K headline gain to admission

The one later-time candidate-OFF 32K/4096 run produced 106.7 TG versus preserved control replicate 1 at93.9, with exact full-length output/MTP/routing/capacity parity. This exposes source/build or environmental timing confounding. A single later run cannot separate these causes. It cannot be credited to conditional admission, which was disabled. Keep all 18 matrix measurements; do not replace or repeat unfavorable controls. Deployment requires an independently demonstrated gate benefit, not this apparent gain.

## Final scientific classification versus production baseline

PROMISING_CONDITIONAL_ADMISSION is the scientific classification required by the stated selection rule: admission efficiency clearly improves, while end-to-end evidence remains insufficient/confounded. Production remains KEEP_Q4_100US_BASELINE with deployment_switch=false. The earlier deployment-focused draft is preserved. This is report terminology, not threshold/model retuning or a new inference experiment.

## Final attribution and preservation audit

The stricter post-hoc contiguous holdout audit retains 49,647/55,067 local entries (90.16%) with the SAME frozen threshold/checkpoint. Attribution ends at the first native/other early touch; it does not prove exclusive counterfactual savings. Next-four benefit is demand potential. The original calibration and strict holdout decisions remain preserved.

All 18 primary requests and 12 application requests are complete, with no favorable retries. Six actual launcher smoke checks pass. Prior v2 hashes (4776 files) and full model/MTP/profile hashes match. Owned process records and both GPU compute lists are empty. No substantial experiment is left running or pending. The bounded campaign finishes early; no extra tuning or same-binary follow-up is started.
