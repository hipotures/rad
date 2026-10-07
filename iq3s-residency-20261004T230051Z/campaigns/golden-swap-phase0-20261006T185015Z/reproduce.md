# Reproduction and inspection

Run from this campaign directory. No training or replacement-policy comparison is implemented. Original attempts are immutable; later model recordings require an explicitly separate reproduction directory and retain the frozen source/input references.

```bash
cd /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z
PYTHON=/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python
python3 scripts/progress.py
python3 scripts/inspect_prompt.py
python3 scripts/inspect_prompt.py code-archive --full
"$PYTHON" scripts/run.py check
```

Identity checks verify the capture binary SHA256, exact source SHA and clean source, unchanged model/pack/PLE/MTP/profile stat identities against the previously fully hashed model manifest, payload hashes, idle GPUs and native configuration. An unexpected identity mismatch fails visibly. The runner does not update, build, download, change drivers/host/affinity or touch normal launchers. No sudo.

For a new bounded recording, use a new output directory (it must not exist):

```bash
"$PYTHON" -u scripts/run.py task --task code-archive --reproduction --output-dir "$PWD/replays/archive-new"
"$PYTHON" -u scripts/run.py screening --reproduction --output-dir "$PWD/replays/screen-new"
"$PYTHON" -u scripts/run.py core --reproduction --output-dir "$PWD/replays/core-new"
```

Each explicit reproduction has its own60min deadline andT+50 request cutoff; it never resets the original campaign deadline. It copies runner/validator/progress tools, model identity and fixed manifests, while preserving immutable references to original payloads/IDs. Frozen queue order and source-group roles remain unchanged. Reserved evaluation is excluded from default fitting; there is no fitting script in Phase0.

Each episode uses a fresh server, the exact saved4096-input/64-output warmup and one greedy2048-cap request. Native generation and current residency are preserved. `STRATA_POOL_SPIN_US=100`, K24, PCIe.28,15workers,MTP4/.5,INT8KV and streaming/residency settings are verified. Oracle mode is off and tape mode is record. All expert contributions are computed. Capture timing is explicitly instrumented.

Startup+warmup is capped at180s; request wall at240s. Decode sampling stops at natural EOS,output cap or approximately60s after first generated output. Client disconnect is the existing safe cancellation path; it does not interrupt kernels directly. The legacy native tape marks cancellation invalid and may not flush a reusable tape,so a time slice/hard timeout is retained as INVALID_TRACE rather than claimed replay-ready. Normal output-cap tapes record complete logical windows and the exact emitted prefix. The intentional slice does not prove the whole application task was solved.

Logs are preserved. Every episode prints start/finish, and a flushed heartbeat appears every20s,including startup. Current progress is atomic JSON plus readable STATUS.md and append-only progress.jsonl. Native children are identified by exact executable and PID/creation time. Shutdown first signals the owned frontend for normal cleanup,then escalates only within its owned process group. Unrelated jobs are never killed; GPU conflicts fail visibly.

Validate one recorded tape, or regenerate descriptive statistics and reporting after all owned inference has stopped:

```bash
"$PYTHON" scripts/validate_traces.py raw/code-archive
"$PYTHON" scripts/analyze.py
"$PYTHON" scripts/budget_report.py
"$PYTHON" scripts/render_report.py
"$PYTHON" scripts/audit.py
```

The validator checks native FNV and SHA256, counts/shapes/window dependencies, actual prompt/output IDs, MTP counts, main local/CPU/mapped totals and native event coverage. The source-backed QSA repair checks only active `min(position+lane+1,2051)` indices; unused capacity is preserved and ignored semantically. Active IDs must be ascending,unique and in bounds. The original failed validator/result are retained. No model rerun was made for it. The second correction handles natural EOS inside a fully committed final verifier window: header emission count bounds the emitted prefix,actual IDs must match,and the final emitted ID must be the native configured EOS with no earlier EOS. The original failed check is preserved.

The offline analysis preserves simultaneous batches, computes layer-aware histograms/cosine/JS,window inter-use gaps and batch-level distinct-expert reuse distances, and saves future victim-return values only under a labels namespace. End-of-tape nonreturns are right-censored. No labels cross requests; no next-use value is treated as a runtime feature or exact counterfactual eviction regret.

Stop only an owned run using its campaign directory:

```bash
"$PYTHON" scripts/run.py stop
# For a reproduction, run its copied scripts/run.py stop from that reproduction directory.
```

Existing compatible historical tapes are immutable references in provenance/compatible-existing-tapes.json. Their original output budgets,start protocols,engine versions and prior exposure remain labelled; extended256K traces are not new Phase0 calibration. No live oracle/replay matrix or predictor training was performed.
