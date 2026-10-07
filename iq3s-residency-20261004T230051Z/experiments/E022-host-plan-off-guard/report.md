# E022-host-plan-off-guard: controlled confirmation

Status: COMPLETE_MIXED. Reference: E019-skip-local-host-plan.

| Profile | Role | PP median | TG min / median / max | TTFT s | Wall s | MTP accept |
|---|---|---:|---:|---:|---:|---:|
| 32k | reference | 4758.3 | 156.4 / 175.4 / 179.3 | 6.108 | 30.864 | 86.12% |
| 32k | candidate | 4776.7 | 152.6 / 163.6 / 180.3 | 6.092 | 31.114 | 86.12% |
| 128k | reference | 6014.4 | 138.7 / 158.7 / 159.3 | 21.530 | 47.234 | 77.86% |
| 128k | candidate | 6030.8 | 127.2 / 159.0 / 161.3 | 21.271 | 47.056 | 77.86% |

32k median delta (%): {'PP': 0.38669272639386687, 'TG': -6.727480045610045, 'TTFT_s': -0.2595441422404088, 'wall_s': 0.809292517857374}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 179.3, 'candidate_TG': 180.3, 'TG_delta_pct': 0.557724484104849, 'MTP_acceptance_delta_pp': 0.0}, {'run': 2, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 156.4, 'candidate_TG': 163.6, 'TG_delta_pct': 4.603580562659837, 'MTP_acceptance_delta_pp': 0.0}, {'run': 3, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 175.4, 'candidate_TG': 152.6, 'TG_delta_pct': -12.99885974914482, 'MTP_acceptance_delta_pp': 0.0}].

128k median delta (%): {'PP': 0.27267890396383, 'TG': 0.1890359168241984, 'TTFT_s': -1.2045387927525408, 'wall_s': -0.3766223834883009}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 138.7, 'candidate_TG': 127.2, 'TG_delta_pct': -8.291276135544335, 'MTP_acceptance_delta_pp': 0.0}, {'run': 2, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 159.3, 'candidate_TG': 159.0, 'TG_delta_pct': -0.18832391713747842, 'MTP_acceptance_delta_pp': 0.0}, {'run': 3, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 158.7, 'candidate_TG': 161.3, 'TG_delta_pct': 1.6383112791430454, 'MTP_acceptance_delta_pp': 0.0}].

Three serial requests per fresh server/profile, not independent fresh-server replicates.
Batches occurred at different wall times; CPU scheduling and numerical trajectories can affect TG.
Output hashes compare visible answer plus reasoning, not unavailable clean output token IDs.
No diagnostic timings are headline measurements. Unavailable expert-specific I/O is not zero.

All raw attempts remain intact. No additional unchanged repetitions or production switch.

## Attribution guard

The apparent128k+19% versus an earlier control is not an isolated host-plan effect: same-binaryOFF reaches159.0 versus158.7ON.32kON175.4 versusOFF163.6 has strongly overlapping per-run ranges and inconsistent paired effects. No portable gain or deployment recommendation.

Serial batches at different wall times; three valid runs each. Same output/MTP/accounting rules out those trajectory explanations for these paired differences, not scheduling/binary-layout/VM effects. No more repetitions.
