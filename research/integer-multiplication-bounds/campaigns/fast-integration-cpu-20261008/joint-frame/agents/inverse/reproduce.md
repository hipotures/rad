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
