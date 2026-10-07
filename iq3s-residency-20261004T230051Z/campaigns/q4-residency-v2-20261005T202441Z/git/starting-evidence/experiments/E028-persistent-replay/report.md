# E028 persistent same-device admission replay

Completed before live headline execution. This is fixed-trajectory simulation, not measured TG. P1 full4K traces have exact baseline output/MTP/routing parity. Horizon8 was selected in E020. Alpha1.0 selected from first64windows of three development episodes before fulltrace ranking.

| Context | Link model GB/s | Current nonlocals | Persistent nonlocals | Current GB copied | Persistent GB | Current wait s | Persistent wait s | Useful / total | Repeated | Victim entries |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 32k | 1.8 | 36776 | 172013 | 10.697 | 0.704 | 5.125 | 0.139 | 365/367 | 362 | 2579 |
| 32k | 12.6 | 36776 | 172013 | 10.697 | 0.704 | 0.268 | 0.000 | 365/367 | 362 | 2579 |
| 128k | 1.8 | 45276 | 162958 | 14.373 | 0.855 | 7.033 | 0.210 | 435/436 | 430 | 3692 |
| 128k | 12.6 | 45276 | 162958 | 14.373 | 0.855 | 0.421 | 0.001 | 435/436 | 430 | 3692 |

The lifetime mechanism works in replay: almost all admissions get repeated subsequent uses, physical ownership/capacity invariants hold, no restoration. The conservative 16window/80us utility suppresses many useful lowheat admissions and raises nonlocals 3.6–4.7x. Large modeled copy savings cannot establish speed because CPU/mapped execution costs stay fixed in replay. Live screening will measure this tradeoff; this candidate is NOT promoted to production.

The transfer sensitivity changes queue charges only; admission uses the same conservative1.8GB/s cost. Fixed trajectory does not model altered FP path/MTP/output. Prediction arrival is observed before endverify, but copies issue only at the safe boundary after current target demands: currentwindow late opportunities are not counted as early hits. Copycompletion and nextwindow publication are separate. Initial age/history is unknown except warmup heat; no invented history. Selector offline CPU is measured but not charged to synthetic TG; no TG predicted.

Artifacts: `policy-v1.json`, `selected-policy.json`, `development-v1/`, `full-v1/`, `selector-tests/`, `signal-v1/` (fullparity checks). The development view is deliberately limited to64windows because original signals stop there. The replay keeps immutable RAM canonical and original variable-byte physical slots separately on each GPU.

## One predeclared lifetime repair (v2)

Change only policy horizon16→64windows and batchbudget16→64MiB/device, preserving h8/alpha1/miss80us/owner/recency/age/bytefits. This repairs demonstrablyunderadmittingv1; no dense tuning. It reduces32/128nonlocals to73,593/79,077 (stillaboveCURRENT36,776/45,276), while copying3.885/4.715GB. Useful1,905/1,935 and2,322/2,361; victimdamage9,563/13,422entries. Queuewait1.8GB/s1.498/1.893s vs12.6GB/s0.023/0.052s. StillnoTGprediction. Fullrawv2-replay preserved.

Measured P1diagnostic CURRENT pending-boundarywait is0.139/0.212s, with10.697/14.373GBpromoted. Conservative1.8model5.125/7.033s significantly overcharges exposedwait; evenisolated12.6model0.268/0.421s isnotexact. Copyoverlap/scheduling mean bytes dividedbycriticalwait isnot physicalbandwidth. Therefore no admissionclaimrests on simulated savedseconds. The utilityapproximationneeds livevalidation.

H8signal currentwindow anybranchmembership35.2/42.4%, subsequent16window60.1/61.8%; distinct normalizedfiniteconfidence checksPASS. These are differentmetrics/horizons from prior next-layer69–71%, not a claim that the next-layer predictor regressed. Only5of48targetlayers predicted. Safe-boundaryissuescannotcatchcurrentwindowtargetdemands; ready-first-subsequentuse isexplicitly separate.

## Warmup protocol correction

`warm-chain-v1/` corrects the earlier simulation's P1afterwarm initialstate: appliespersistentv2 to theactual64-output warmup, retains predictionheat/recency/birth/state, drains pending betweenrequests and adds the measured prefillheatdelta. Newsimulationpoint; earlierrawnotchanged. Nonlocals73,926/79,719, copied3.941/4.809GB;1.8modelwait1.537/1.948s,12.6sensitivity0.027/0.053s. Differences small, qualitativeunderadmissionpersists. Independentreservation/slotcapacityauditPASS fororiginalv2fullreplay.

Observed pending-boundarywait does not include pageable/stagedcopy submission time or adapt-thread join. Do NOT interpret0.139/0.212seconds as the whole exposedcopycost; diagnosticmeasurement must alsocharge thosehostphases. Aggregate measureddecode is the actualspeed metric.
