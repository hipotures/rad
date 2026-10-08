# Reproduction

Run commands from the repository root. Python 3 with its standard library
is sufficient for this subtree. Assertions must remain enabled. All output
paths must be fresh. Use one CPU process and one native-library thread.

The complete read-only public PR58 snapshot is pinned at
`bc2f7ed4c20dc18898305ab17165c0c995cbb804`. It is obtainable from
`CrocSwap/integer-mult-bounds` through `gh` or Git fetch of public pull/58.
The campaign coordinator's input manifest records the actual acquisition.
If recovering elsewhere, obtain that exact commit in disposable storage,
not in this durable authored subtree. The independent ledger writes no
upstream file, and imports no upstream implementation.

```bash
python3 -B research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/joint-frame/agents/inverse/code/verify_transfer_ledger.py \
  --inputs research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/joint-frame/inputs/pr58-tested-bc2f7ed4c20dc18898305ab17165c0c995cbb804 \
  --output <fresh-ignored-work>/transfer-ledger.json
```

Expected: complete local XOR charge 2,206,597,276; exact reconstructed native
multiplicities; characteristic below one at the pinned saving and above one
at the next grid point; joint row gap 6548/25; unchanged complex guard
inequalities. This bounded command was executed. It does not execute the
complete producer, profile every matrix, or prove general tape interfaces.

For a representative rigorous positive and negative Gaussian certificate:

```bash
python3 -B research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/joint-frame/agents/inverse/code/dyadic_interval_lower.py \
  --source 4093 --target 4096 --alpha 64 --target-bits 512 --seed 202610081752 \
  --output <fresh-ignored-work>/admissible.json
python3 -B research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/joint-frame/agents/inverse/code/dyadic_interval_lower.py \
  --source 127 --target 128 --alpha 2 --target-bits 128 --seed 202610081752 \
  --mode drop-wrap --output <fresh-ignored-work>/drop-wrap.json
```

Expected statuses are `RIGOROUS_TARGET_CERTIFIED` and
`RIGOROUS_TARGET_DISPROVED`. The former proves error below 2^-575;
the latter proves error above 2^-21. Both were executed. To replay an
already retained receipt, without executing Decimal:

```bash
python3 -B research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/joint-frame/agents/inverse/code/dyadic_interval_lower.py \
  --verify-certificate research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/joint-frame/agents/inverse/runs/20261008T1753Z-interval-lower-drop-wrap127/results/certificate.json \
  --output <fresh-ignored-work>/drop-wrap-replay.json
```

The queue controller is a live-execution helper and requires a specific
currently owned worker to pause. Its archived PID is not authorization
to signal any live process. Independent reproduction needs no pausing:
the flags and frozen source in each run's `protocol.json` suffice.

Completed JSON receipts and protocols are also archived with
`python3 tools/archive_workspace.py pack-text`, keeping the original files.
The archive manifest gives source hashes and omitted/non-text roles. Large
execution inputs remain downloadable or deterministically regenerable; no
compiled binary, environment, downloaded checkout or raw cache is required
to recover these standard-library computations.

The final SUM23/PAIR25 review freezes every scalar ledger and mapping input
in `runs/20261008T200929Z-future-complement-joint-transfer/`. From the
repository root, replay its complete 47-obligation arithmetic mapping with:

```bash
RAD_INVERSE_FINAL=research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/joint-frame/agents/inverse/runs/20261008T200929Z-future-complement-joint-transfer
python3 -B "$RAD_INVERSE_FINAL/code/check_changed_cpu47_mapping_v2.py" \
  --native "$RAD_INVERSE_FINAL/fixtures/joint-complete-moment.json" \
  --literal-ledger "$RAD_INVERSE_FINAL/fixtures/joint-literal-ledger.json" \
  --cpu38 "$RAD_INVERSE_FINAL/fixtures/joint-cpu38-arithmetic.json" \
  --output <fresh-ignored-work>/joint-map.json
```

Expected status begins `EXACT CHANGED47 MAP AND SUPPLEMENTS PASS`, with
all 47 obligations mapped exactly once and
`kappa=47682490470327/10^18`. This replay checks
the exact published inputs and numerical margins. The written report
supplies the separate conditional geometry and strong-induction arguments.
The complete producer, literal-word and CRT-profile replays additionally
require the original SUM23/PAIR25 words and profile receipts; their source
hashes, full gzip archives and precise original paths are identified in the
report and frozen protocol. Those tests were completed before shutdown.

The completed large Gaussian case has source 65521, target 65536,
alpha 32, target precision 2048 and seed 202610081925. Its frozen source is
`runs/20261008T192558Z-resume-s65521-a32-q2048-complete/code/dyadic_interval_lower.py`.
Replay the complete certificate using `--source 65521 --target 65536
--alpha 32 --target-bits 2048 --mode complete --seed 202610081925` and a
fresh output path. It certified every retained residual and every omitted
lifted cyclic alias in 508.061 seconds; finite success does not establish
the all-size sufficient precision conditions. The final artifact manifest
records the complete RHS/solution-array hash and official whole-file gzip.

For a short compiled full-cube guard discriminator, compile the frozen
`runs/20261008T193046Z-four-target-outer1-inner1-complete/code/compiled_reflection_four_recycle.cpp`
with `g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic`, placing the binary in
fresh ignored work. Run `--family mixed-small --outer-guard 1 --inner-guard 1
--output <fresh-ignored-work>/complete.json`, and repeat with
`--omit-outer-repair` and a different output path. The completed runs gave
`PASS` and `EXPECTED_NEGATIVE`; each visits the full 131072-record address
cube. The frozen source also includes its required native CRT kernel.

The final shutdown index distinguishes completed certificates from the
two canceled cases and the four unstarted queue configurations. Canceled
cases require complete reruns in fresh directories and support no
mathematical conclusion. Do not reuse historical PIDs or invoke a queue
controller merely to reproduce an individual mathematical experiment.
