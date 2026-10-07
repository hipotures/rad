# Phase C — matched live information ablations

**Victim information dominates the loss in the tested first-feasible scheduler.** Full future improves all nine main matched decode pairs; restricting victim lifetime loses the gain, while the incoming retention utility is structurally inactive in this policy. This does not establish a universal information requirement.

F/F median replay-equivalent rates are 120.19 / 97.04 / 89.83 tok/s at 32K / 128K / 256K, versus current 104.36 / 87.01 / 79.81. Median within-block TG ratios improve by 15.17% / 11.24% / 12.56%; these are medians of paired ratios, not ratios of medians. Request-wall ratios improve by 9.17% / 6.51% / 2.63% respectively. The frozen follow-up I=FULL/V=256 loses every larger-context decode pair: median TG changes -7.37% at128K and -10.23% at256K. Its tiny 256K wall improvement (0.42%) accompanies worse decode and varying prefill, so is not a practical scheduler win. On the previously observed independent archive task F/F improves all three pairs (median +16.37% TG); V256 retains 39.44% of full time saving at the median, with range -54.49% to63.35%. That task has different CPU/miss characteristics and sampled byte-check costs; it is not an untouched holdout or quality evaluation.

## Transactional mechanism

| Profile | Arm | Victim-absent entries | Victim reloads | Victims reloaded >=2 times | Actual target-admission hit entries | Admissions reused in >=2 invocations | End-censored admissions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 128k | F256 | 85,759 | 89,901 | 16,702 | 118,240 | 73,647 | 10,700 |
| 128k | FF | 19,736 | 52,635 | 13,583 | 73,004 | 48,773 | 9,201 |
| 128k | current | 185,345 | 24,222 | 6,725 | n/a | n/a | n/a |
| 256k | F256 | 83,093 | 88,454 | 15,950 | 115,474 | 70,435 | 10,448 |
| 256k | FF | 17,639 | 53,520 | 13,455 | 73,870 | 48,001 | 8,920 |
| 256k | current | 168,745 | 23,217 | 6,592 | n/a | n/a | n/a |
| 32k | 6464 | 87,241 | 87,381 | 15,743 | 112,621 | 67,933 | 10,504 |
| 32k | 64F | 15,886 | 51,711 | 13,349 | 70,678 | 46,117 | 9,251 |
| 32k | F64 | 86,179 | 87,823 | 15,784 | 113,420 | 68,272 | 10,519 |
| 32k | FF | 11,736 | 53,850 | 13,729 | 73,273 | 47,616 | 9,306 |
| 32k | current | 151,049 | 20,547 | 5,594 | n/a | n/a | n/a |

At32K the full policy has median 11,736 observed victim-absent entries, versus 86,179 with V64 and 151,049 under native current. Full copies 204.67GB, V64 313.00GB, current 87.42GB. Thus this feasible gain pays more transfer traffic than current; it is not a cheap static-cache result. V64 achieves a higher local share than current yet slower decode, with more churn and online planning/publication. At128K V256 causes median 85,759 victim-absent entries versus 19,736 for full. Its copies are roughly321GB versus202GB, and oracle-planner counters 9.65s versus6.81s. These overlapping costs support the mechanism but do not isolate a unique critical-path penalty. Incoming64 slow attempt3 is retained: staging median272.6us versus 139.3us for its paired full attempt, more late publication and victim absence, despite valid query limits/work/state. Copy-with-host-wait medians remain similar. Unique VM/scheduling causation is unresolved. Readiness, distinct persistent reuse, native/oracle reload recurrence, right-censored survivors and finite-end interior sensitivity are reported separately; routed-lane multiplicity is not durable reuse.

## Information sufficiency

Incoming: I=64 is the smallest tested budget reproducing deterministic F/F decisions at unchanged E64 in the offline model and source tests. Its live median retention is75.96%, range -25.67% to94.05%, so an 80–90% performance-sufficiency claim is unresolved. I4/I16 shorten eligibility as well as value information and therefore do not isolate incoming lifetime. Victim: neither V64 at32K nor V256 in the larger profiles is sufficient under the tested policy/fallback. FULL is the only tested passing reference; the smallest sufficient finite V remains unmeasured. This is not proof that a causal predictor needs exact whole-request next-use, nor that every short-history victim policy fails. Interaction has signs +1181/-3150/-2575ms across blocks, not a stable linear law.

## Admission accounting and scope

Every main and task-transfer request passes the exact tape/state/query/ownership checks. All48 main layers and3classes are covered. Initial five donor withdrawals and restoration are charged only to oracle, inside decode/request respectively. Native current keeps original capacity/adaptation. Completed payloads, publications, target-local use and later distinct reuse are different funnel stages. Native/oracle absent demand is rebuilt from chronological journals and checked against actual service slots for every routed batch. Scope-specific empty oracle journals in current do not mean zero native churn; only the comparable victim journal is used for that comparison. No timing outlier exclusion or fourth attempt.

The inherited native decode timer stops before final commit wait, drain, restoration and buffered trace flush. Whole request wall includes them. Tape/index setup and attestation remain separately reported. Short ordinary/replay overhead is uncertain (median+5.61% decode, +11.42% wall); fixed-work forced tokens do not establish ordinary quality or deployable TG. Main-thread affinity is not every-thread affinity; retained56-thread snapshot documents this. CPU steal differs across arms and secondary KV DMA service is incompletely observed.

## Next causal target

One next research target: calibrated **victim-return risk / eviction regret for a proposed same-layer, same-class, same-device exchange**, conditional on an already visible incoming E64 action. Estimate whether demand for the displaced resident will return before ready incoming reuse amortizes copy and planning cost. Use causal usage, heat, recency, age, reload history, class, queue and protection state; retain uncertainty when future use is censored. A later causal system must independently supply incoming predictions and replace privileged whole-current-window P with safe available dependency state. Do not train a generic expert-popularity model or assume exact distant next-use is required. First instrument/use an effective net exchange ranking or veto: the present computed reuse utility never compares two feasible actions.

No real-serving baseline change. No model/source upgrade, helper, pool/K/PCIe/MTP tuning or learned training.

VICTIM_INFORMATION_DOMINATES
