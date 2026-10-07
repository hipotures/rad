# Frequency policy live comparison

Status: COMPLETE_NEGATIVE.

One fresh server per profile, equal fixed 64-output warmup, serial three preserved 4096-output workloads. Controls reused unchanged; not three independent fresh-server replicates.

Existing --adapt-decay 0.7 ->1.0; source base/toolchain/common inference settings and physical cache capacities fixed.

| Profile | Config | PP median | TG min/median/max | TTFT median s | Wall median s | MTP accept | CPU fallback median | Mapped/remote median |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 32k | control | 4739.5 | 153.3 / 155.9 / 157.8 | 6.129 | 32.775 | 86.12% | 27006 | 539 |
| 32k | frequency | 4740.5 | 134.6 / 144.9 / 150.6 | 6.125 | 34.364 | 81.36% | 25072 | 517 |
| 128k | control | 5985.2 | 124.2 / 133.2 / 153.1 | 21.688 | 54.640 | 77.86% | 42738 | 1335 |
| 128k | frequency | 6007.4 | 121.5 / 131.3 / 135.3 | 21.582 | 55.255 | 75.41% | 39574 | 1390 |

The startup capacity check passes at both profiles. Predictor GPU/host allocation added by the supported decay option is zero. Exact slot-class byte budgets are linked in analysis/control-budgets-v2.json and each raw resource-check.json. No K/cache/MTP/worker/PCIe tuning was performed.

Native real-model parity zero failures, Python 268 pass/7 skipped, CTest 62 pass/2 skipped/4 documented environmental failures. Ten saved same-input-ID cases complete, four identical visible outputs; all six textual differences preserved. Numeric/JSON checks pass; no universal bitwise parity claim.

The six differing short answers have coherent preserved differences (phrasing, formatting and worked example choice); mathematics remains correct and both strict JSON cases parse to the requested values. This is basic correctness evidence, not an automatic quality ranking or proof that all numerical divergence is harmless.

All run statistics, decode-only CPU/GPU/power/PCIe samples and per-payload comparisons are in summary.json. Decode telemetry spans first visible token through the response end at 1 Hz. CPU is reported on both one-core and 16-vCPU bases. PCIe bursts have no causal attribution from these samples. Unknown expert-file counters remain unavailable.

32k median deltas (%): `{'PP': 0.02109927207512019, 'TG': -7.055805003207183, 'TTFT_s': -0.06308085142257003, 'wall_s': 4.847631243833672}`. Saved-input comparisons: `[{'run': 1, 'same_input_ids': True, 'control_TG': 157.8, 'candidate_TG': 134.6, 'TG_delta_pct': -14.70215462610901, 'wall_delta_pct': 12.659211165542494, 'same_visible_output_hash': False}, {'run': 2, 'same_input_ids': True, 'control_TG': 153.3, 'candidate_TG': 150.6, 'TG_delta_pct': -1.7612524461839585, 'wall_delta_pct': 1.650097831041264, 'same_visible_output_hash': False}, {'run': 3, 'same_input_ids': True, 'control_TG': 155.9, 'candidate_TG': 144.9, 'TG_delta_pct': -7.055805003207183, 'wall_delta_pct': 6.084826104759511, 'same_visible_output_hash': False}]`.
128k median deltas (%): `{'PP': 0.3709149234779163, 'TG': -1.4264264264264082, 'TTFT_s': -0.4906027664558832, 'wall_s': 1.1248909449125266}`. Saved-input comparisons: `[{'run': 1, 'same_input_ids': True, 'control_TG': 133.2, 'candidate_TG': 131.3, 'TG_delta_pct': -1.4264264264264082, 'wall_delta_pct': 0.2273128076506925, 'same_visible_output_hash': False}, {'run': 2, 'same_input_ids': True, 'control_TG': 124.2, 'candidate_TG': 135.3, 'TG_delta_pct': 8.937198067632867, 'wall_delta_pct': -5.154349942008862, 'same_visible_output_hash': False}, {'run': 3, 'same_input_ids': True, 'control_TG': 153.1, 'candidate_TG': 121.5, 'TG_delta_pct': -20.640104506858258, 'wall_delta_pct': 14.379777159128505, 'same_visible_output_hash': False}]`.

Do not select this policy solely from the offline nonlocal reduction. The real goal is latency/TG with correct execution. Preserve the slower candidate and its executable launchers. Investigate its free-generation/MTP/cache history before claiming cache accounting implies a speed gain.

Next: bounded diagnostic frequency trace at both profiles if needed to explain the loss; actual boundary/router availability study, and compatible-slot placement replay. Do not repeat the unchanged headline points.

Reproduce: variants/frequency-v1-ready/reproduce.sh --experiment NEW_EXPERIMENT --attempt v1. Within the original campaign, the three-attempt limit remains binding; launcher paths/binary hashes/configs are frozen. Manual starts remain available without updating/rebuilding.
