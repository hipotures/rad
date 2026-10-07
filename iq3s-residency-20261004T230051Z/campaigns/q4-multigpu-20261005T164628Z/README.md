# Q4 multi-GPU measurement campaign

This campaign compares three execution modes of the same frozen Strata 0.1.39 executable: layer split, original expert helper, and upstream optimized expert helper. It reuses the existing Unsloth UD-Q4_K_XL weights and pack; it does not change the runtime or model.

The final matrix is nine cells, each with a fresh server, the same 4096-input / 64-output warmup, and three serial 4096-output measured requests. Total context limits are 32768, 131072 and 262144. The actual input IDs and their hashes are preserved in `inputs/`. `protocol.json` defines settings and the bounded preliminary layer check.

`STATUS.md` and `STATUS.json` show the current state. `report.md`, `summary.csv` and `summary.json` contain the completed results after all 27 valid requests. Raw requests, engine timers, generated text/token IDs, actual input capture, full commands and metrics remain under `raw/<method>/<profile>/`. No result is reconstructed from a screenshot or a remembered number.

After completion, `launchers/` contains the selected method and three safe foreground launchers. Each prints the complete resolved configuration, verifies the executable hash and source, refuses conflicts, streams logs and preserves Monitor metrics. Existing IQ3_S and old Q4 launchers remain untouched.

To regenerate analysis from the preserved data without inference:

```bash
./scripts/reproduce-analysis.sh
```

The analysis is gated on exactly 27 valid fixed-length requests. The audit verifies source/binary/model provenance, common settings, input identities, protected old launchers, all new launcher configurations, and final GPU cleanup. It performs no new inference. Run it with no active Strata server, since cleanup is part of the audit.

Limitations are recorded in the report: architecture can change floating-point order and greedy trajectories; the displayed cache-hit denominator excludes nonlocal GPU work; sampled PCIe bandwidth is aggregate traffic; post-adaptation cache-ID overlap and exact worker sleep/wake counts are unavailable on the frozen executable. Missing counters remain unavailable.
