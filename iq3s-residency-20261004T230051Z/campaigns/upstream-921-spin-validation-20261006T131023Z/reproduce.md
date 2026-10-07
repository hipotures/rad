# Reproducibility

All commands run from this campaign directory. Original measurements use released
v0.1.40.1, commit 82f46a8c8f475f001ad76d92f58f4a4f8ffb0253. The native tree is
identical to v0.1.40. The binary is `build/strata`, SHA256
`09f70d953f6d0009bdd555d06b72363aa9442fdb6f8f1a25250c6bf6a578dd94`.
Full native GGUF, pack, tokenizer, MTP, and expert-profile hashes and immutable
file-stat manifests are in `provenance/model-*.json`.

```bash
cd /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/upstream-921-spin-validation-20261006T131023Z
PYTHON=/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python
"$PYTHON" scripts/run.py verify --full-model-hash
"$PYTHON" -u scripts/run.py campaign --cell IQ3_S-32k --reproduction
```

For the full four-cell campaign, omit `--cell`. `--reproduction` creates a new
`replays/<UTC>/` tree with its own eight-hour deadline; it never overwrites the
original measured arms. Each arm uses a fresh server, explicitly removes the
spin override for A or sets it to exactly 100 for B, and verifies the actual
native child environment. Full per-key environment hashes make drift auditable
without publishing credentials. Only the spin key may differ within a pair.
The frozen original orders are reused. No model/config/kernel tuning occurs.

The runner checks the GPU process list, binary/source/model identity, context,
K, PCIe fraction, worker count, MTP, KV, suffix lookup, prompt reuse and serial
execution before requesting inference. It prints every arm and result.
Startup/request/arm/shutdown timeouts are bounded. It identifies owned processes
by PID plus creation time and only stops those processes. Interrupted or failed
arms remain on disk, and the runner refuses silent overwrite or retry.

The original campaign can resume only while its original absolute deadline is
valid and with an identical parent environment. A failed pair requires an
objective protocol audit and an invalid-pair ledger entry before a replacement;
at most two predeclared replacement slots per cell may be used. Outputs that
diverge and poor performance are never exclusion reasons.

The original build commands are stored verbatim in
`provenance/build-commands.json`; `build.log`, `build/CMakeCache.txt` and
`build/compile_commands.json` preserve compiler details. GGML/llama.cpp is pinned
to 3cf03257f219afbe7334045ff7c6a06ac68c627d, retrieved with `gh api` and preserved
as a hashed tarball. The frozen binary is authoritative for exact reproduction;
a rebuild may have a different hash and must be separately documented.

```bash
"$PYTHON" scripts/analyze.py --require-complete
"$PYTHON" scripts/render_report.py
"$PYTHON" scripts/audit.py
```

The statistical script uses only valid A/B pairs. It computes median paired
B/A ratios separately from ratios of raw arm medians, all raw distributions,
exact sign counts, a two-sided exact sign-flip test on log TG ratios, and seeded
paired bootstrap intervals. Workload-family rows are descriptive. Token-level
and 1 Hz telemetry observations never inflate the sample count.

To stop an owned run from this directory, use `scripts/run.py stop`. For a
replay, its ownership ledger is inside its replay directory; verify its process
identities before stopping. Never kill unrelated GPU jobs.

Isolated replay analysis and owned cleanup (use the directory printed by the runner):

```bash
"$PYTHON" scripts/analyze.py --root /absolute/path/to/replays/TIMESTAMP --require-complete
"$PYTHON" scripts/run.py stop --run-dir /absolute/path/to/replays/TIMESTAMP
```

Replays retain their own frozen orders, payload references, protocol, timing,
invalid ledger and configuration identities. Model/binary paths still reference
the original frozen artifacts. The original report renderer describes the
original campaign; replay statistics are written into the replay directory.
A later original audit checks the recorded completion time against the original
eight-hour limit, rather than treating a later audit as additional measurement time.
