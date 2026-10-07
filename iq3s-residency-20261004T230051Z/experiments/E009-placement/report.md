# Compatible-slot placement replay

Status: COMPLETE_POSITIVE for the predeclared replay objective.

| Profile | Current nonlocals | Compatible nonlocals | Delta | Current promotion GB | Compatible promotion GB | Victim damage current/candidate |
|---|---:|---:|---:|---:|---:|---:|
| 32k | 36776 | 34838 | -5.27% | 10.697 | 10.008 | 14487 / 12521 |
| 128k | 45276 | 43284 | -4.40% | 14.373 | 13.808 | 21323 / 19331 |

The policy exchanges cold slots and hot incoming experts across layers only within one device. Incoming blobs must fit the actual physical slot. Both GPUs retain their exact own bytes, fixed K25 ownership and original asynchronous safe-publication queue. Per-layer capacity changes and wasted size slack are saved in summary.json. No assumption of a shared48GiB pool.

The decline in nonlocal entries and bytes is enough to justify one bounded actual native runtime experiment, E010. It is not a TG forecast. Copies and CPU/mapped/resident work compete in real inference; predictor/selector overhead and free-generation/MTP differences must be measured.

Source feasibility and constraints: v1/source-audit.md. Existing prompt loans restore the dynamic expert identity from host_res, but extra modes (resident CPU, mmap, elastic, helper, batch) are outside the bounded candidate and rejected. Wrong predictions always use original model-selected experts through safe fallback.

Exact C++/Python selector equivalence was checked across310/362adaptations in E010, with identical complete replay outcomes. Offline native selector median about0.786ms/call, including bridge temporary vectors. This materially exceeds the old selector cost and is charged as an uncertainty/risk, not hidden.

