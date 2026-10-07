# E023-direct-parts: controlled confirmation

Status: COMPLETE_MIXED. Reference: E002-controls.

| Profile | Role | PP median | TG min / median / max | TTFT s | Wall s | MTP accept |
|---|---|---:|---:|---:|---:|---:|
| 32k | reference | 4739.5 | 153.3 / 155.9 / 157.8 | 6.129 | 32.775 | 86.12% |
| 32k | candidate | 4751.5 | 155.9 / 158.1 / 166.0 | 6.105 | 32.362 | 86.12% |
| 128k | reference | 5985.2 | 124.2 / 133.2 / 153.1 | 21.688 | 54.640 | 77.86% |
| 128k | candidate | 5993.6 | 133.1 / 160.6 / 163.0 | 21.633 | 47.127 | 77.86% |

32k median delta (%): {'PP': 0.25319126490135346, 'TG': 1.4111610006414255, 'TTFT_s': -0.39116521810903526, 'wall_s': -1.2610347518361764}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 157.8, 'candidate_TG': 166.0, 'TG_delta_pct': 5.196451204055763, 'MTP_acceptance_delta_pp': 0.0}, {'run': 2, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 153.3, 'candidate_TG': 155.9, 'TG_delta_pct': 1.6960208741030547, 'MTP_acceptance_delta_pp': 0.0}, {'run': 3, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 155.9, 'candidate_TG': 158.1, 'TG_delta_pct': 1.4111610006414255, 'MTP_acceptance_delta_pp': 0.0}].

128k median delta (%): {'PP': 0.1403461872619305, 'TG': 20.570570570570567, 'TTFT_s': -0.2543869510984842, 'wall_s': -13.749712593778462}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 133.2, 'candidate_TG': 133.1, 'TG_delta_pct': -0.07507507507507061, 'MTP_acceptance_delta_pp': 0.0}, {'run': 2, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 124.2, 'candidate_TG': 160.6, 'TG_delta_pct': 29.307568438003216, 'MTP_acceptance_delta_pp': 0.0}, {'run': 3, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 153.1, 'candidate_TG': 163.0, 'TG_delta_pct': 6.466361854996738, 'MTP_acceptance_delta_pp': 0.0}].

Three serial requests per fresh server/profile, not independent fresh-server replicates.
Batches occurred at different wall times; CPU scheduling and numerical trajectories can affect TG.
Output hashes compare visible answer plus reasoning, not unavailable clean output token IDs.
No diagnostic timings are headline measurements. Unavailable expert-specific I/O is not zero.

All raw attempts remain intact. No additional unchanged repetitions or production switch.

## Same-binary guard

Direct rows regress32k versus same-binaryOFF and retain an apparent128k median advantage. Paired effects are mixed and ranges overlap. This is a workload/batch-dependent observation, not a portable20.57% win versus an earlier binary. No production switch or extra unchanged repetition.

See ../E025-direct-parts-off-guard/attribution.json for ON-versus-OFF deltas and raw references.
