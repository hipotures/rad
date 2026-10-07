# E025-direct-parts-off-guard: controlled confirmation

Status: COMPLETE_MIXED. Reference: E023-direct-parts.

| Profile | Role | PP median | TG min / median / max | TTFT s | Wall s | MTP accept |
|---|---|---:|---:|---:|---:|---:|
| 32k | reference | 4751.5 | 155.9 / 158.1 / 166.0 | 6.105 | 32.362 | 86.12% |
| 32k | candidate | 4777.5 | 157.3 / 169.5 / 172.4 | 6.077 | 30.225 | 86.12% |
| 128k | reference | 5993.6 | 133.1 / 160.6 / 163.0 | 21.633 | 47.127 | 77.86% |
| 128k | candidate | 5951.5 | 131.4 / 144.4 / 153.2 | 21.782 | 52.951 | 77.86% |

32k median delta (%): {'PP': 0.547195622435015, 'TG': 7.210626185958269, 'TTFT_s': -0.4516617625577757, 'wall_s': -6.602940967819504}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 166.0, 'candidate_TG': 157.3, 'TG_delta_pct': -5.240963855421676, 'MTP_acceptance_delta_pp': 0.0}, {'run': 2, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 155.9, 'candidate_TG': 172.4, 'TG_delta_pct': 10.583707504810768, 'MTP_acceptance_delta_pp': 0.0}, {'run': 3, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 158.1, 'candidate_TG': 169.5, 'TG_delta_pct': 7.210626185958269, 'MTP_acceptance_delta_pp': 0.0}].

128k median delta (%): {'PP': -0.7024159103043326, 'TG': -10.087173100871727, 'TTFT_s': 0.6873332731661019, 'wall_s': 12.356839029073274}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 133.1, 'candidate_TG': 144.4, 'TG_delta_pct': 8.489857250187827, 'MTP_acceptance_delta_pp': 0.0}, {'run': 2, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 160.6, 'candidate_TG': 131.4, 'TG_delta_pct': -18.181818181818176, 'MTP_acceptance_delta_pp': 0.0}, {'run': 3, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 163.0, 'candidate_TG': 153.2, 'TG_delta_pct': -6.0122699386503164, 'MTP_acceptance_delta_pp': 0.0}].

Three serial requests per fresh server/profile, not independent fresh-server replicates.
Batches occurred at different wall times; CPU scheduling and numerical trajectories can affect TG.
Output hashes compare visible answer plus reasoning, not unavailable clean output token IDs.
No diagnostic timings are headline measurements. Unavailable expert-specific I/O is not zero.

All raw attempts remain intact. No additional unchanged repetitions or production switch.

## Interpretation

Direct rows regress32k versus same-binaryOFF and retain an apparent128k median advantage. Paired effects are mixed and ranges overlap. This is a workload/batch-dependent observation, not a portable20.57% win versus an earlier binary. No production switch or extra unchanged repetition.

Captured two-device row ownership,63nativepass/2skip/4knownenvironmentfail,Python268pass/7skip,realIQ0fail,10sameanswers,and repaired fullactual4096ID/router/path/MTP/cache/heat/head parity at both profiles.

Zero additional explicit GPU buffers; old hit_out retained for equal capacity. Driver graph allocations may differ and are not assumed free; normal telemetry retains peaks.
