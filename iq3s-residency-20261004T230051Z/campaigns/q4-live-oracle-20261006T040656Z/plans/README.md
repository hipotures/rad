# Oracle plans and observed execution

The frozen full-future policy is in the final oracle-v3 source and patch. It precomputes a per-layer/per-expert next-use index from the RAM-resident tape, then selects exchanges online at logical main routed-layer boundaries. The issue frontier is 64 invocations; full-future victim and reuse queries remain unrestricted. A rolling measured duration estimate selects copy lead. This is not a static list triggered by recorded wall-clock timestamps.

Every issued live action is retained in `raw/<label>/raw/oracle-admissions.bin`: logical trigger and target, incoming layer/expert, physical destination class slot, actual selected victim, staging/copy/publication timestamps, publication event, later uses and victim-absent demand. `oracle-layers.bin` records the full batch demanded at every logical main event and its actual local/CPU/mapped service. `oracle-native.bin` preserves original native admission traffic. Readers and binary schemas live in `scripts/inspect_oracle.py` and `tapes/schema.json`.

Offline capacity-only and transfer-modeled plans are separate JSON in `phase-b/`. They are not measured speed and cannot be substituted for live transactions. Current and oracle execution use the same original per-device physical cache allocation; five charged same-class spares are withdrawn only after timed decode starts.
