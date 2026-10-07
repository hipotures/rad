# E016-device-plan-ids: controlled confirmation

Status: COMPLETE_MIXED. Reference: E002-controls.

| Profile | Role | PP median | TG min / median / max | TTFT s | Wall s | MTP accept |
|---|---|---:|---:|---:|---:|---:|
| 32k | reference | 4739.5 | 153.3 / 155.9 / 157.8 | 6.129 | 32.775 | 86.12% |
| 32k | candidate | 4735.7 | 151.5 / 152.3 / 157.1 | 6.130 | 32.999 | 86.12% |
| 128k | reference | 5985.2 | 124.2 / 133.2 / 153.1 | 21.688 | 54.640 | 77.86% |
| 128k | candidate | 5989.8 | 123.3 / 133.3 / 136.4 | 21.677 | 54.894 | 77.86% |

32k median delta (%): {'PP': -0.08017723388543674, 'TG': -2.309172546504168, 'TTFT_s': 0.019460234199386583, 'wall_s': 0.6827995616334626}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 157.8, 'candidate_TG': 151.5, 'TG_delta_pct': -3.992395437262364, 'MTP_acceptance_delta_pp': 0.0}, {'run': 2, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 153.3, 'candidate_TG': 157.1, 'TG_delta_pct': 2.4787997390737004, 'MTP_acceptance_delta_pp': 0.0}, {'run': 3, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 155.9, 'candidate_TG': 152.3, 'TG_delta_pct': -2.309172546504168, 'MTP_acceptance_delta_pp': 0.0}].

128k median delta (%): {'PP': 0.07685624540534342, 'TG': 0.07507507507509281, 'TTFT_s': -0.05288027733382217, 'wall_s': 0.46451340870568014}.
Per-saved-payload comparisons: [{'run': 1, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 133.2, 'candidate_TG': 136.4, 'TG_delta_pct': 2.402402402402415, 'MTP_acceptance_delta_pp': 0.0}, {'run': 2, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 124.2, 'candidate_TG': 123.3, 'TG_delta_pct': -0.7246376811594235, 'MTP_acceptance_delta_pp': 0.0}, {'run': 3, 'same_input_ids': True, 'same_output_hash': True, 'first_diverging_visible_character': None, 'reference_TG': 153.1, 'candidate_TG': 133.3, 'TG_delta_pct': -12.932723709993454, 'MTP_acceptance_delta_pp': 0.0}].

Three serial requests per fresh server/profile, not independent fresh-server replicates.
Batches occurred at different wall times; CPU scheduling and numerical trajectories can affect TG.
Output hashes compare visible answer plus reasoning, not unavailable clean output token IDs.
No diagnostic timings are headline measurements. Unavailable expert-specific I/O is not zero.

All raw attempts remain intact. No additional unchanged repetitions or production switch.

## Correctness finding and repair

The first local version was unsafe. Stable per-layer ID snapshots fixed host demand accounting, but the GPU all-local path bypassed the layer-0 CPU completion flag. Layer 1 could then read PLE values before their CPU producer finished. A delayed-producer native fixture reproduced the stale read on both GPUs. This is an execution dependency failure, not harmless floating-point reordering. No unsafe headline runs were collected.

The repaired version waits for the independent PLE producer before layer 1. The strict same-binary snapshot experiment reproduced the original numerical error at window 3/layer 1 (relative L2 activation difference 0.24145), and the fenced version matched every captured activation, expert output and head row bit for bit. The first snapshot attempt had a directory-creation bug; its vacuous parity claim is withdrawn and both attempts are retained.

Both full-profile repaired diagnostics matched all 4096 output IDs, speculative window inputs, routing IDs, execution paths, initial/final heat and resident sets. The first captured head was bit-identical with KL 0. The clean 10-prompt battery also matched control. The native suite retains the same four documented VM/fixture failures, not four new waived correctness errors.

The six clean measurements have identical visible output hashes, MTP acceptance and input IDs to control. Median TG is 152.3 versus 155.9 at 32K and 133.3 versus 133.2 at 128K. This does not justify selecting the candidate. The first measured request includes lazy graph-capture work under the identical 64-output warmup policy. No extra unchanged repetitions were run.

Auxiliary GPU bytes are 81,984/67,880 at 32K and 81,528/67,560 at 128K, plus mapped CPU ID snapshots of 4,000/3,680 bytes. Exact expert capacities are unchanged. This experiment motivates separately testing removal of now-redundant host plan construction; it does not change the cache admission algorithm.
