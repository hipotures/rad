# E014-policy-off-guard: controlled confirmation

Status: COMPLETE_MIXED. Reference: E010-compatible-runtime.

| Profile | Role | PP median | TG min / median / max | TTFT s | Wall s | MTP accept |
|---|---|---:|---:|---:|---:|---:|
| 32k | reference | 4745.3 | 136.7 / 150.2 / 167.8 | 6.115 | 33.362 | 84.85% |
| 32k | candidate | 4759.9 | 169.2 / 174.5 / 179.7 | 6.106 | 30.296 | 86.12% |
| 128k | reference | 5994.7 | 155.8 / 157.8 / 158.5 | 21.401 | 47.529 | 79.19% |
| 128k | candidate | 5974.8 | 122.0 / 139.2 / 141.9 | 21.700 | 51.106 | 77.86% |

32k median delta (%): {'PP': 0.30767285524622157, 'TG': 16.17842876165114, 'TTFT_s': -0.15953376163369004, 'wall_s': -9.188371967381325}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': False, 'first_diverging_visible_character': 178, 'reference_TG': 167.8, 'candidate_TG': 179.7, 'TG_delta_pct': 7.091775923718702, 'MTP_acceptance_delta_pp': 5.305549492970243}, {'run': 2, 'same_input_ids': True, 'same_output_hash': False, 'first_diverging_visible_character': 58, 'reference_TG': 136.7, 'candidate_TG': 169.2, 'TG_delta_pct': 23.77468910021947, 'MTP_acceptance_delta_pp': 1.7520365093020729}, {'run': 3, 'same_input_ids': True, 'same_output_hash': False, 'first_diverging_visible_character': 363, 'reference_TG': 150.2, 'candidate_TG': 174.5, 'TG_delta_pct': 16.17842876165114, 'MTP_acceptance_delta_pp': -0.41909200671770463}].

128k median delta (%): {'PP': -0.33195989790981706, 'TG': -11.787072243346019, 'TTFT_s': 1.3958059370387854, 'wall_s': 7.527781440107506}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': False, 'first_diverging_visible_character': 308, 'reference_TG': 158.5, 'candidate_TG': 122.0, 'TG_delta_pct': -23.02839116719243, 'MTP_acceptance_delta_pp': -2.411495047600951}, {'run': 2, 'same_input_ids': True, 'same_output_hash': False, 'first_diverging_visible_character': 506, 'reference_TG': 155.8, 'candidate_TG': 139.2, 'TG_delta_pct': -10.654685494223381, 'MTP_acceptance_delta_pp': 0.722064707376262}, {'run': 3, 'same_input_ids': True, 'same_output_hash': False, 'first_diverging_visible_character': 417, 'reference_TG': 157.8, 'candidate_TG': 141.9, 'TG_delta_pct': -10.076045627376429, 'MTP_acceptance_delta_pp': 0.14995483010693533}].

Three serial requests per fresh server/profile, not independent fresh-server replicates.
Batches occurred at different wall times; CPU scheduling and numerical trajectories can affect TG.
Output hashes compare visible answer plus reasoning, not unavailable clean output token IDs.
No diagnostic timings are headline measurements. Unavailable expert-specific I/O is not zero.

All raw attempts remain intact. No additional unchanged repetitions or production switch.
