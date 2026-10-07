# Decisions

Phase 0 only. Existing campaigns remain unchanged.

- D001: Earlier Phase 0 timing-only directory discovered; its earlier 18:49:49.997758 UTC start and 19:49:49.997758 UTC deadline govern this campaign. Earlier directory preserved unchanged.

- D002: First two capture configs inherits legacy descriptive headline_instrumentation=OFF/Strata_HEAD=base fields. Actual capture executable/source hashes and record environment are correct and verified. Episode results explicitly label instrumented=true. Future configs correct these descriptive metadata fields only; no engine argument, environment, resource or sampling change. Original attempt/log retained.

- D003 HARNESS REPAIR1: Legacy tape validator wrongly assumed all2051 QSA capacity cells were active. Episode6 short179-token prompt has179 active indices then unused zero tail. Source qsa_selection_width=min(n_kv,2051) proves this. Validation now checks active width per lane,including strict uniqueness and bounds; original failure and original validator preserved. Same original trace passes; no model rerun, no attempt exclusion, no engine/binary change. Sampling resumes at episode7.

- D004: Original driver uses a conservative445s prelaunch planning allowance. A future/resumed driver may use actual measured component maxima plus20s allowance for pending tasks, capped445s, to assess fit before the unchanged T+50 cutoff. Startup180/request240 and owned cleanup limits remain unchanged. No deadline reset, ordering change or repeated task. Estimates are not CI/p95. Running driver is unchanged; its executable script version is preserved.

- D005 HARNESS REPAIR2: Natural EOS can terminate emission inside the final accepted verifier window. The native engine commits the whole accepted prefix but emits only through EOS. The validator now bounds reconstructed emitted IDs by the immutable header output_count and verifies the truncation belongs only to the last window; actual IDs and the observed EOS termination are checked separately. Original failure/tape and previous validator are preserved. No model rerun, counter alteration or engine change. Evidence: provenance/EOS-emission-contract.txt.
