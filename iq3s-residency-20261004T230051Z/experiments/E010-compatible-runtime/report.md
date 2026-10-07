# Compatible-slot live comparison

Status: COMPLETE_MIXED.

One fresh server per profile, equal fixed 64-output warmup, serial three preserved 4096-output workloads. Controls reused unchanged; not three independent fresh-server replicates.

Causal same-owner compatible-slot EMA matching vs original same-layer EMA; frozen source base, toolchain, heat thresholds/cadence and total per-GPU slot-class bytes. No additional GPU allocation.

| Profile | Config | PP median | TG min/median/max | TTFT median s | Wall median s | MTP accept | CPU fallback median | Mapped/remote median |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 32k | control | 4739.5 | 153.3 / 155.9 / 157.8 | 6.129 | 32.775 | 86.12% | 27006 | 539 |
| 32k | compatible | 4745.3 | 136.7 / 150.2 / 167.8 | 6.115 | 33.362 | 84.85% | 23869 | 540 |
| 128k | control | 5985.2 | 124.2 / 133.2 / 153.1 | 21.688 | 54.640 | 77.86% | 42738 | 1335 |
| 128k | compatible | 5994.7 | 155.8 / 157.8 / 158.5 | 21.401 | 47.529 | 79.19% | 37720 | 1078 |

The startup capacity check passes at both profiles. Additional GPU allocation is zero; host immutable slot metadata is about150kB and selector scratch/cost must be charged. Native bridge median selector cost0.786ms/call is preserved in selector-tests. Exact slot-class byte budgets are linked in analysis/control-budgets-v2.json and each raw resource-check.json. No K/cache/MTP/worker/PCIe tuning was performed.

Native real-model parity zero failures, Python 268 pass/7 skipped, CTest 62 pass/2 skipped/4 documented environmental failures. Ten saved same-input-ID cases complete, five identical visible outputs; all five textual differences preserved. Numeric/JSON checks pass; no universal bitwise parity claim.

The five differing short answers have coherent preserved differences (phrasing, formatting and worked example choice); mathematics remains correct and both strict JSON cases parse to the requested values. This is basic correctness evidence, not an automatic quality ranking or proof that all numerical divergence is harmless.

All run statistics, decode-only CPU/GPU/power/PCIe samples and per-payload comparisons are in summary.json. Decode telemetry spans first visible token through the response end at 1 Hz. CPU is reported on both one-core and 16-vCPU bases. PCIe bursts have no causal attribution from these samples. Unknown expert-file counters remain unavailable.

32k median deltas (%): `{'PP': 0.12237577803566602, 'TG': -3.656189865298276, 'TTFT_s': -0.21819783881311672, 'wall_s': 1.7892295398339142}`. Saved-input comparisons: `[{'run': 1, 'same_input_ids': True, 'control_TG': 157.8, 'candidate_TG': 167.8, 'TG_delta_pct': 6.33713561470215, 'wall_delta_pct': -4.4888228025726225, 'same_visible_output_hash': False}, {'run': 2, 'same_input_ids': True, 'control_TG': 153.3, 'candidate_TG': 136.7, 'TG_delta_pct': -10.828440965427276, 'wall_delta_pct': 10.105581201749336, 'same_visible_output_hash': False}, {'run': 3, 'same_input_ids': True, 'control_TG': 155.9, 'candidate_TG': 150.2, 'TG_delta_pct': -3.656189865298276, 'wall_delta_pct': 2.9903354703190166, 'same_visible_output_hash': False}]`.
128k median deltas (%): `{'PP': 0.15872485464145658, 'TG': 18.46846846846848, 'TTFT_s': -1.3227934385701245, 'wall_s': -13.015210244498132}`. Saved-input comparisons: `[{'run': 1, 'same_input_ids': True, 'control_TG': 133.2, 'candidate_TG': 158.5, 'TG_delta_pct': 18.993993993993996, 'wall_delta_pct': -11.69521440632958, 'same_visible_output_hash': False}, {'run': 2, 'same_input_ids': True, 'control_TG': 124.2, 'candidate_TG': 155.8, 'TG_delta_pct': 25.442834138486315, 'wall_delta_pct': -13.015210244498132, 'same_visible_output_hash': False}, {'run': 3, 'same_input_ids': True, 'control_TG': 153.1, 'candidate_TG': 157.8, 'TG_delta_pct': 3.0698889614630964, 'wall_delta_pct': -2.005729352895813, 'same_visible_output_hash': False}]`.

Do not select this policy solely from the offline nonlocal reduction. The real goal is latency/TG with correct execution. Preserve the candidate and its executable launchers, including any slower profile. Investigate its free-generation/MTP/cache history before claiming cache accounting implies a speed gain.

Next: scoped GPU wait diagnostics and same-input first-head comparison; a policy-versus-trajectory explanation is required before selecting the apparent128k gain. Native selector overhead remains a separate repair opportunity. Do not repeat the unchanged headline points.

Reproduce: variants/compatible-v1/reproduce.sh --experiment NEW_EXPERIMENT --attempt v1. Within the original campaign, the three-attempt limit remains binding; launcher paths/binary hashes/configs are frozen. Manual starts remain available without updating/rebuilding.
