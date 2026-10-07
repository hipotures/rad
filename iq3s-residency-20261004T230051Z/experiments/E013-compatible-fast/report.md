# E013-compatible-fast: controlled confirmation

Status: COMPLETE_MIXED. Reference: E010-compatible-runtime.

| Profile | Role | PP median | TG min / median / max | TTFT s | Wall s | MTP accept |
|---|---|---:|---:|---:|---:|---:|
| 32k | reference | 4745.3 | 136.7 / 150.2 / 167.8 | 6.115 | 33.362 | 84.85% |
| 32k | candidate | 4755.8 | 143.3 / 163.5 / 164.9 | 6.121 | 31.149 | 84.85% |
| 128k | reference | 5994.7 | 155.8 / 157.8 / 158.5 | 21.401 | 47.529 | 79.19% |
| 128k | candidate | 5959.7 | 132.5 / 134.3 / 135.9 | 21.776 | 52.179 | 79.19% |

32k median delta (%): {'PP': 0.22127157397846542, 'TG': 8.854860186418122, 'TTFT_s': 0.09365393988789439, 'wall_s': -6.633424970517932}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 167.8, 'candidate_TG': 143.3, 'TG_delta_pct': -14.600715137067933, 'MTP_acceptance_delta_pp': 0.0}, {'run': 2, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 136.7, 'candidate_TG': 163.5, 'TG_delta_pct': 19.60497439648867, 'MTP_acceptance_delta_pp': 0.0}, {'run': 3, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 150.2, 'candidate_TG': 164.9, 'TG_delta_pct': 9.78695073235687, 'MTP_acceptance_delta_pp': 0.0}].

128k median delta (%): {'PP': -0.583849066675568, 'TG': -14.89226869455006, 'TTFT_s': 1.7503827119821125, 'wall_s': 9.784753490563759}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 158.5, 'candidate_TG': 132.5, 'TG_delta_pct': -16.403785488958988, 'MTP_acceptance_delta_pp': 0.0}, {'run': 2, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 155.8, 'candidate_TG': 134.3, 'TG_delta_pct': -13.799743260590503, 'MTP_acceptance_delta_pp': 0.0}, {'run': 3, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 157.8, 'candidate_TG': 135.9, 'TG_delta_pct': -13.878326996197721, 'MTP_acceptance_delta_pp': 0.0}].

Three serial requests per fresh server/profile, not independent fresh-server replicates.
Batches occurred at different wall times; CPU scheduling and numerical trajectories can affect TG.
Output hashes compare visible answer plus reasoning, not unavailable clean output token IDs.
No diagnostic timings are headline measurements. Unavailable expert-specific I/O is not zero.

All raw attempts remain intact. No additional unchanged repetitions or production switch.
