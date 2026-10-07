# Frozen schedule and trace contract

The online schedule is the unchanged v3 deadline/first-feasible scheduler in the
common information-v2 binary. It is not a list of operations fired at recorded
seconds. A main verifier routed-layer batch has logical ID `window * 48 + layer`.
Its token positions, speculative lanes, T-by-10 routing IDs and float32 weights
remain intact. MTP invocation, proposal, acceptance, rollback and catchup work
remain in the full replay tape, but MTP expert residency is unchanged.

All oracle arms use E=64. Incoming first demand is visible only through min(E,I);
incoming utility counts also stop at I and the inherited 768-invocation utility
cap. Victim next-use and publication-time reselection see V, including the five
initial donor choices. The common P channel protects the complete current
verifier window. FULL ends at the recorded finite tape, with no guard tail.
An absent bounded next-use is unknown, with the frozen causal heat-log fallback.

The same five class-compatible physical slots are withdrawn inside timed decode
in every oracle arm. K=24 ownership is retained. Classes are 3,072,000,
3,584,000 and 3,993,600 bytes; device 1 has no layer in the largest class. Copy
workers stage immutable RAM weights, issue a real same-device H2D transfer,
observe completion, and publish only at a legal reader boundary. Rolling
observed event/copy costs determine issue lead; the eligibility ceiling remains
64. A copy that misses its target never suppresses demand: CPU or mapped-host
fallback still executes. Drain and 17,305,600-byte spare restoration are charged.

REPLAY_CURRENT keeps the original native adaptation and original active capacity.
Oracle arms become the sole exchange authority for the full 48-main-layer scope.
All arms share the tape machinery, full future-index preparation in startup RAM,
buffered observations and original memory envelope. Index setup time is reported
separately; no expert weights are prepopulated for oracle timing.

The authoritative actual schedule is each attempt's `raw/oracle-admissions.bin`,
not an offline model plan. `trigger`, `target`, `published_at`, class bytes,
incoming/victim identities, slot/oldslot, copy completion and publication host
timestamps permit ownership, readiness and lifetime audits. Native traffic is in
`raw/oracle-native.bin`, actual service is in `raw/oracle-layers.bin`. Their schemas
are retained in `scripts/inspect_oracle.py`; the tape schema and work validation
are in `scripts/tape.py`. They are the unchanged schemas from replay v3.

`phase-a/protocol.json` freezes the 32K blocks; `phase-c/transfer-protocol.json`
freezes the selected larger-context blocks. Every resolved per-attempt command,
environment, native executable identity and initial-state attestation is retained.
Offline curves are development simulations and are not actual measured TG.

Native decode_ms is captured before final commit wait, scheduler drain/restoration and trace flush. The full client request wall includes those operations. Restoration/drain timer fields overlap in the inherited implementation; do not sum them into a fabricated corrected decode metric.
