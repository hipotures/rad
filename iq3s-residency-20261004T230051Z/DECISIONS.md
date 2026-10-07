# Decisions

- D001: use exactly frozen CURRENT base; build clean control and candidates separately. Historical helper/v0.1.38 are explanatory references only.
- D002: honor total context limits and budget 4096 output plus runtime headroom; freeze tokenizer-rendered workloads before speed runs.
- D003: do not interpret 99% reported hit rate as local VRAM coverage. Audit disjoint dispatch categories first.
- D004: reuse hardware characterization rather than repeat its campaign.

## E008/E009/E010 checkpoint

Actual split activation-copy durations are around20us each, far below complete verify/window time; do not label all GPU wait as boundary transfer. FullCPU next-router scoring is commonly too late, and many predicted nonresidents are false positives. E009 compatible same-owner slot shares modestly improve finite-copy miss/byte accounting and justify E010 actual confirmation. Native selector costs about0.786ms/call; no guaranteed speed benefit. Correctness uses same frozen10inputs, basic numeric/JSON checks, preserved textual differences and original kernel parity. Complete both-profile3attempt batches; never retry a slow valid point.

## E010–E014 checkpoint

E010completed six valid4Krequests.32kcompatible median150.2vs155.9(control),128k157.8vs133.2. E011uses three selected-layer GPUevent brackets, preserves all4KIDs/router/MTP and firsthead, but its timing changes materially; never promote diagnosticTG to headline. E012unchanged compatible algorithm firstheadbit-identical then diverges after47/84outputtokens.128kMTP and resident-group work changes help explain end-to-end gain; CPUwait distributions are mixed. Falsify policy attribution with E014samebinaryOFF, not extra unchanged repetitions. E013min-heaps preserve all672causal decisions and fullfinitecopy outcomes while reducing offline native median selector cost from~0.786ms to~0.282ms. Meets preregistered25%cost reduction; complete correctness and bothprofile confirmation before choosing it. No production switch.

## E015 availability repair

Source audit shows doorbell_publish_res deliberately skips activation copies for all-localgroups. E008unconditional h_x capture mixed fresh/staleinputs. Realoutputs,routerIDs,boundaryevents and CPUfullGEMMcost remain valid; quality/readiness need separation. Preserve allraw/derivedoldattempts and label this limitation. Diagnosticfreshversion forces the existing selected-layer activation publication only, with no true-router/math/cachechange; additional traffic means noheadline or freeavailabilityclaim. Predeclare ranks32/128, sixindependentdev/cal/heldepisodes, no modeldownload/mutation.

## E016–E022 checkpoint

Safe stable IDs also require the independent PLE producer dependency. The unsafe variant is retained only as a diagnostic reproducer; repaired full traces preserve actual routing and outputs. Safe device planning alone did not improve confirmed TG.

The E019 apparent 128K gain does not survive E022 same-binary OFF: 159.0 OFF versus 158.7 ON, identical outputs/MTP/capacities. The 32K ranges overlap. No production switch or further unchanged repetitions.

E020 selected horizon8 from development/calibration before held-out labels. Queues, exact physical slots, victims and restoration materially reduce optimistic ready coverage. These temporary schemes do not justify a live cache-prediction build. Persistent placement and richer predictors are not claimed exhausted.

Use E021 same-binary timing to explain coordination; E023 changes only redundant output-row storage/copying, with captured row-ownership tests and full correctness before clean speed.

## Closing decision: preserved evidence and no deployment

The bounded research tree, runtime confirmations and attribution guards are complete. The existing100us pool option is the strongest scoped follow-up: unchanged control binary/input/output/MTP/capacity, TG178.5/154.0 and decode CPU28.0%/25.8%. CPU-positive wakeup waits increase to59–72us in the sampled layers, so independent miss-heavy workloads are the next validation. No universal15% gain, successful live selective-residency policy, or diagnosed VM/binary-layout explanation is claimed.

Recommendation: PROMISING_NEEDS_MORE_WORK. Keep the current normal launcher untouched. All failed/slower/unsafe attempts, source patches, builds, datasets/checkpoints and raw records remain available. Persistent admissions and cross-device scheduling are NOT_ATTEMPTED under the finite time budget, not negative conclusions. The original consolidation gate and09:00:51 hard deadline were never extended; the last admitted batch completed both profiles without another experiment starting.
