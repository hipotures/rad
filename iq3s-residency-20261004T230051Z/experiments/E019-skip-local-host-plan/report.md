# E019-skip-local-host-plan: controlled confirmation

Status: COMPLETE_MIXED. Reference: E002-controls.

| Profile | Role | PP median | TG min / median / max | TTFT s | Wall s | MTP accept |
|---|---|---:|---:|---:|---:|---:|
| 32k | reference | 4739.5 | 153.3 / 155.9 / 157.8 | 6.129 | 32.775 | 86.12% |
| 32k | candidate | 4758.3 | 156.4 / 175.4 / 179.3 | 6.108 | 30.864 | 86.12% |
| 128k | reference | 5985.2 | 124.2 / 133.2 / 153.1 | 21.688 | 54.640 | 77.86% |
| 128k | candidate | 6014.4 | 138.7 / 158.7 / 159.3 | 21.530 | 47.234 | 77.86% |

32k median delta (%): {'PP': 0.39666631501213967, 'TG': 12.50801796023091, 'TTFT_s': -0.34450835083327247, 'wall_s': -5.832058912342375}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 157.8, 'candidate_TG': 179.3, 'TG_delta_pct': 13.624841571609636, 'MTP_acceptance_delta_pp': 0.0}, {'run': 2, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 153.3, 'candidate_TG': 156.4, 'TG_delta_pct': 2.022178734507496, 'MTP_acceptance_delta_pp': 0.0}, {'run': 3, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 155.9, 'candidate_TG': 175.4, 'TG_delta_pct': 12.50801796023091, 'MTP_acceptance_delta_pp': 0.0}].

128k median delta (%): {'PP': 0.48787007952950656, 'TG': 19.144144144144136, 'TTFT_s': -0.7294332746608068, 'wall_s': -13.553506109294633}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 133.2, 'candidate_TG': 138.7, 'TG_delta_pct': 4.129129129129128, 'MTP_acceptance_delta_pp': 0.0}, {'run': 2, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 124.2, 'candidate_TG': 159.3, 'TG_delta_pct': 28.260869565217405, 'MTP_acceptance_delta_pp': 0.0}, {'run': 3, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 153.1, 'candidate_TG': 158.7, 'TG_delta_pct': 3.6577400391900605, 'MTP_acceptance_delta_pp': 0.0}].

Three serial requests per fresh server/profile, not independent fresh-server replicates.
Batches occurred at different wall times; CPU scheduling and numerical trajectories can affect TG.
Output hashes compare visible answer plus reasoning, not unavailable clean output token IDs.
No diagnostic timings are headline measurements. Unavailable expert-specific I/O is not zero.

All raw attempts remain intact. No additional unchanged repetitions or production switch.

## Mechanism, correctness and interpretation

This opt-in suppresses only unused host plan/group/pointer construction and mapped CPU-row zeroing when every actual routed entry is local and the corrected GPU plan already owns those rows. Actual usage/heat, local-entry counts, layers and expert totals still update. Mixed CPU/mapped groups retain their original dispatch. The independent PLE fence and stable per-layer IDs are mandatory; helper/peer/batched paths remain out of scope. No expert capacity, cache policy, GPU arithmetic or routing changes.

The full diagnostic matches every actual output ID, speculative input/acceptance, router entry, execution path, initial/final heat/residency and first-head bit at both profiles. All footer categories reconcile. The 10-prompt clean battery has ten identical answers; default-off tests retain only the four previously documented environment/fixture failures.

Clean medians are 175.4/158.7 TG versus 155.9/133.2 in the original control. All six visible outputs and MTP/counts are unchanged, so the improvement is not explained by a new free-generation trajectory. Nevertheless, prior same-output guards also changed TG substantially, and one OFF guard reached 174.5 at32K. Serial batches/binary identity remain confounds. A same-binary original-path guard is therefore predeclared as E022, with no additional unchanged ON repetitions. The difference is provisional until that falsification and the phase diagnosis are complete.

No additional GPU bytes are allocated beyond safe E016. Exact per-profile slots/classes are retained inside each24GiB envelope. Source039ea29916d3155514688fb6d5a5de6129d69675; cleanbinary58aab77cd65222e9396d68b428591b44118172c1353a6e8e01f67b94ccfb649c. No deployment or normal launcher switch.
