# early-v1

Experimental H4 native-router + CPU-only frozen linear ranking, dedicated persistent staging worker and guarded target publication. Charges one existing3.072MB physical spare/device; possible output/MTP divergence. Not a universal improvement.

Default bind127.0.0.1, port8080. Settings frozen: Q4, K24, PCIe0.28, workers15, pool100us, spec4/minp0.5, INT8, kv-resident32768 where runtime permits, prefillauto, lookup/reuse0.

```bash
./start-32k.sh
./start-128k.sh --host 0.0.0.0 --port 8080
./start-256k.sh
./stop.sh
./reproduce.sh --profile 128k --port 18140
```

Start runs in foreground and streams engine/frontend logs; Ctrl-C stops owned processes. `--check` verifies frozen identities/config without inference; `--smoke` actually starts and generates the fixed64-output saved warmup, then stops. Reproduction is refused during the active research campaign. No auto build/update/download. Colliding GPU/port/Strata processes cause a visible failure. Monitor snapshots are preserved under manual/<variant>/<profile>-<timestamp>/telemetry/ui-monitor/.

Source/binary identities and exact command are in each profile JSON. Large weights retain previous verified hashes with current size/mtime checks; small pack/profile/tokenizer files are rehashed. Existing main model weights/normal user launchers are untouched. See ../../report.md for correctness and negative performance limitations.

Post-campaign `reproduce.sh` uses three fresh server starts, each with the same fixed 4096-input/64-output warmup and one measured run, matching the primary protocol. It does not run three measured requests on a shared warmed server. All reproduction files have a new timestamped directory.
