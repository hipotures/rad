# Experimental fixed-work tools

These tools execute clairvoyant replay, not ordinary model serving. They verify the experimental source and binary, the Q4 model provenance, and the tape checksum. Each operation uses a fresh owned server, the preserved input IDs, a 4096-input/64-output warmup, and one recorded 4096-output workload. The default operation timeout is 1200 seconds. Port 18146 and GPU conflict checks refuse concurrent work.

After the original campaign is COMPLETE, an explicit invocation creates a separate `q4-oracle-reproduce-<UTC>` directory. It cannot overwrite the original evidence or reset the original eight-hour deadline. `--check` verifies the command without starting GPU work. `--tape /absolute/path.bin` selects another compatible tape and its required `.initial-state.bin` sidecar.

Examples:

```bash
./capture-128k.sh
./validate-tape.sh --profile 128k --tape /absolute/path/to/new-tape.bin
./replay-current-128k.sh
./replay-full-128k.sh
./replay-short-128k.sh
```

Corresponding wrappers exist for 32K and 256K. The short wrapper uses the audited horizon of 64 future main-model routed-layer invocations, with both admission and victim knowledge bounded. Offline horizons 1, 4 and 16 are simulation diagnostics, not supported live headline modes.

Run from this launcher directory:

| Profile | Capture | Current replay | Full-future replay | H64 replay | Validate preserved tape |
|---|---|---|---|---|---|
| 32K | ./capture-32k.sh | ./replay-current-32k.sh | ./replay-full-32k.sh | ./replay-short-32k.sh | ./validate-tape.sh --profile 32k |
| 128K | ./capture-128k.sh | ./replay-current-128k.sh | ./replay-full-128k.sh | ./replay-short-128k.sh | ./validate-tape.sh --profile 128k |
| 256K | ./capture-256k.sh | ./replay-current-256k.sh | ./replay-full-256k.sh | ./replay-short-256k.sh | ./validate-tape.sh --profile 256k |

Each shell entrypoint passed syntax and identity/config/tape checks. Capture/current/full execution backends actually ran all three profiles. Live H64 evidence is limited to the 32K confirmation; 128K/256K wrappers are identity/config checked, without an additional live horizon matrix. The post-campaign new-directory parent was statically checked rather than adding a fourth unchanged primary inference attempt. This scope is explicit in tests/launcher-checks/summary.json.

The operation prints the resolved configuration and progress, retains failures, drains pending copies, restores charged spare capacity, and stops only its owned processes. Tape data are loaded into RAM before timing; model expert transfers occur inside timed decode. Forced output is not freshly generated, quality-validated text. Normal control launchers remain separate under `../control/`.
