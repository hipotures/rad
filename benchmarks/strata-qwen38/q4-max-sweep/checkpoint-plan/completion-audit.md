# Completion audit — INCOMPLETE

Objective is the entire22-section attached specification; scripts/plots existing alone do not prove execution. This file is a proof checklist, not a completion claim.

| Requirement | Current proof / required completion evidence |
|---|---|
| Frozen environment and reproducibility | raw/environment.json, archived help/docs/configs, observed HEAD9259cad; final HEAD/status/executable identity check still required |
| Native GGUF architecture, no experts.bin | architecture-notes.md and actual T2 runtime71.73GiB arena; final source references and paths verify |
| T0 control | raw/T0-control-done.json: one actual63399 run, PP1534.7,TG43.7 |
| T1 arena | raw/T1-arena-done.json: warmup and3 actual63400 runs; medianTG66.1 |
| T2 auto | raw/T2-auto-done.json: smoke8K,warmup,3 actual63400 runs; medianTG104.3 |
| T3 K sweep/top3 | Completed9validK screens after PSS exclusion and TOP3×3; raw/layer-sweep-selection.json. Best confirmedK22TG112.5, K26PP3135.9. |
| T4 helper placements/capacities/top2 | Completed both placements50/75/90/max for conservative and exact-native capacity, plus targeted static-helper check. raw/remote-native-capacity-selection.json; max7387slots with2GiBreserve. AdditionalTOP2 reused already confirmedlayer5806 and measuredstripe3693×3TG66.2; earlierbesthelper67.8. |
| T5 full RAM native multi GPU | Verified same ArenaExpertSource as T2/T3; no duplicate test claimed |
| static/adaptive | CompletedK22 static/adaptive:3runs each actual~63400/output256/reuse0; medianTG86.0 vs111.4 (+29.5%adaptive). raw/adaptive-selection.json. Final adaptive long4K evidence still pending. |
| calibrator/local CPU/PCIe/minp | Completed upstream calibrator and local workers/PCIe/min-p screens plus3run confirmation; raw/calibration.json and raw/cpu-pcie-selection.json. Local256 winner regressed; matched1024 default control completed (91.0 vs tuned111.5 TG), tuned retained. |
| MTP2/3/4/5 | Original MTP grid archived/excluded after spec3 natural stop91/1024. Complete uniform offline task rerun: spec2/3/4/5 warmup+2actual1024 verified; TOP2×3 and localmin-p comparison completed, all measured output1024; spec3/calibratedmin-p0.7 median111.5 TG. Warmup actual length now asserted. Post-MTP default1024control completed: default91.0 vs tuned111.5; raw/post-tuning-control-selection.json. |
| MTP OFF | Current native/serve guards require spec>=2 andMTP; explicit source evidence of UNSUPPORTED, no fabricated nonMTP rate |
| KV128/256 | Complete4variants: actual127000/259500 warmup+2 each,16measured+8warmups,output256,reuse0,max262144,2GPU K22; raw/kv-progress-verification.json independently verifies. BestTG256K: KV-k8v4. Final resource/byte telemetry audit still required. |
| prefill auto8192/6144/4096/2048 | All5actual127K screens and TOP2auto/8192 confirmations complete: each3measured actual127K plus1actual259500, with warmups; outputs256,reuse0,file blobs0. Both policies resolve8192. Evidence raw/prefill-auto-confirm-verification.json, raw/prefill-auto-256K-verification.json, raw/prefill-8192-confirm-verification.json and raw/prefill-8192-256K-verification.json. Selected explicit8192 medianPP3015.8 vsauto3014.6, same effective chunk. Separate upstream phase-timing diagnostic remains prepared, not executed, after all4timed stages, excluded from medians; final renderer and audit now require its real evidence. |
| cold/warm | vmtouch absent, virtiofs host cache not controllable; warm-only allowed by specification, no cold claim/drop_caches |
| FINAL-A/B | FINAL-A complete12measured: each3actual31400/63400/127000/259500,output256,reuse0,max262144,warmups excluded,filefetch0,minavailable79.57GiB. raw/FINAL-A-matrix-verification.json. FINAL-B now complete12measured. Full24requests verified in raw/final-matrix-verification.json: tokenizer/API actualcounts agree, alloutput256/reuse0/greedy, all24messagesSHA unique, warmups excluded, max262144, expertfilefetch0. Totalactualprompttokens2887798, minavailable76.996GiB. contextsphase terminalexit0. Extended/quality and final artifacts still pending. |
| long decode | Require64K4K,128K4K/8K sampled(temp1/top_p.95/top_k20),one greedy, actual lengths and full streams/1Hz telem. Before execution, existing upstreamSTRATA_TRACE verified in code/help/docs: positions/widths permit cumulative normal MTP+suffix acceptance, reconciled against end counters. External parser synthetic tests passed; actual four traces still required. Per-GPU/time-resolved hit-rate/cache evolution remains unavailable and must be reported explicitly. |
| agentic | Require11 uninterrupted turns each initial64K and128K, initialoutput1024,tool additions500–2000, subsequent caps256–1024,reuse counters/new prompt clocks |
| compaction | Require actual127K/~250K recorded coding-agent history,≤4096summary tokens, measuredPP/TTFT/TG/wall and provenance |
| quality | Require exact savedIQ3 messages/sampling/caps forFINAL-A INT8/alternative KV,full responses,existingIQ3 copies,difference flag without judgment |
| needle | Require upstream methodology atactual32K/128K/256K,depths10/50/90, normal recall result evidence; code-alone is insufficient |
| IQ3 control | HEAD/config same => reuse existing campaign; verify originals/provenance, no unnecessary sweep |
| telemetry/abort |~1HzGPU/RAM/RSS/CPU/I/O/dmon;PSS outside timer. Final absent/available counters documented, errors/abort states reviewed |
| summary fields | summary.csv includes all mandated columns; null means unavailable, notzero. Final rows and medians must matchraw |
| plots | All15 requested plots+long acceptance artifact must regenerate from final data; placeholders are not completed figures |
| report20questions/commands | Must write evidence-backed answers, IQ3 comparison, best-observed recommendations, readyQ4 andIQ3 configs/commands |
| constraints | No patch/download/weights/newquant/commit/push; final git/source/model state verification required |

No goal completion call until current-state evidence proves each requirement or permitted unsupported/availability outcome.

Recovery note: external harness/session vanished during FINAL-A128K run1, engine logged request cancellation and remained idle. Only own orphan server/engine was stopped after identity/idle verification. Interrupted request excluded; archive `raw/interrupted-driver-20261001/`. Retain verified32K/64K three-run cells, repeat128K warmup and all remaining matrix requests with identical config; new detached driver PID153641. This is not a Strata crash or OOM. Full requested scope remains pending.

Long-decode completion proof: raw/long-progress-verification.json verifies all4actual requests (64K4K sampled,128K4K/8K sampled,64K4K greedy), total20480generated tokens, zeroexpertfilefetch, normalupstreamwindowacceptancecurves reconstructed and aggregate-matched. Per-GPU/time-resolved cache counters remain unavailable. Extended stage continues agentic/compaction; this does not complete campaign.

Agentic recovery: first64Ksession naturally stopped after217tokens atturn5, below required256minimum. Fullattempt archived/excluded under raw/agentic-short-eos-excluded; driverterminalexit1 andownengineexitverified before restart. Newcomplete11turnsessions use ten distinct real files/reviewtopics and detailedsix-sectionanswer tasks, same FINAL-Aengine/config. Main24 andlong4completedresults retained. No EOS suppression, enginepatch, newweights or qualityprompt changes. Actualnewsessioncompletion still pending.
