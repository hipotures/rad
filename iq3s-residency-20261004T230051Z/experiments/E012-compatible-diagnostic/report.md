# Compatible-slot runtime mechanism diagnosis

Status: COMPLETE_POSITIVE_DIAGNOSTIC. No new placement algorithm.

The E010native selector header is byte-identical. These separate diagnostic builds add the same selected-layer GPU spans as E011 and an explicit schema2outgoing-layer field. The synthetic schema tests, actual captured-event fixtures,13native tests and realIQparity pass. Bothprofile4Krequests complete with zero reuse/exact inputs/capacities.

| Profile | Config | Diagnostic TG | MTP % | CPU entries | Mapped entries | Promotion GB | Useful/unused GB | Victim demand | Resident groups/output |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 32k | original | 188.0 | 90.16 | 35552 | 1224 | 10.697 | 9.967/0.730 | 14487 | 379.24 |
| 32k | compatible | 154.7 | 84.85 | 34493 | 1162 | 10.505 | 9.695/0.809 | 13684 | 387.87 |
| 128k | original | 122.6 | 76.78 | 43557 | 1719 | 14.373 | 13.030/1.344 | 21323 | 406.49 |
| 128k | compatible | 139.0 | 79.19 | 41085 | 1637 | 13.440 | 12.490/0.951 | 18793 | 398.16 |

Same effective input IDs and exact GPU resources. First-head logits bit-identical, then output diverges47/84tokens. Compatible128k has higherMTPacceptance and fewer resident unique expert groups/output; those trajectory changes can contribute to observed headline gain. DirectCPUwait changes vary bylayer; no general all-wait or all-miss saving is demonstrated.

First-head KL0/maxdifference0 and top1agreement hold at bothprofiles. Actual generated-token prefixes are47tokens32k/84tokens128k, then expert demand and MTPbranch trajectories diverge. The number of identical verified input windows is saved separately in summary.json. No automatic quality ranking.

Compatible128k promotion bytes and unused bytes decline in this actual trajectory;32k unused bytes increase. Many swaps cross layers inside the same ownerGPU. Every recorded copy fits its physical slot, true victims are withdrawn and publication appears after issue. Full accounting including rejected drafts passes. Per-layer CPUwait distributions remain mixed, not a uniform reduction.

Useful bytes mean at least one observed local entry in the promotion lifetime before its next withdrawal. Victim demand counts observed nonlocal entries during absence. Neither means milliseconds saved, and the logical native group byte proxy is not a hardware traffic counter.

This diagnosis supports a conservative interpretation of the real128k gain and motivates the same-binary OFF guard. It does not turn the18.47%headline delta into a cache-policy-only causal effect. All diagnostic rates remain excluded from headline ranking.

