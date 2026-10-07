# Frozen P1 real-prompt baseline



No source rebuild, new weights or capacity change. Source `6f32ec070f23ced9f50e704d854d775da52591ab`; binarySHA `eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d`. K25/pcie.28/workers15/spec4/minp.5/INT8/prefillauto/suffix0/promptcache0; max32768 or131072, KVresident32768 wherevalid.

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/p1-baseline/start-32k.sh --host 0.0.0.0 --port 8080
```

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/p1-baseline/start-128k.sh --host 0.0.0.0 --port 8080
```

Stop: `/srv/ai/research/iq3s-residency-20261004T230051Z/variants/p1-baseline/stop.sh`. Only one server at a time. Research launcher prints/verifies frozen config and owns PID identity; original normal user launchers remain unchanged. Default bind remains127.0.0.1; explicithost override changes no inference settings. Later replay: `reproduce.sh --experiment NEW_EXPERIMENT --attempt v1 --reproduction` after campaign completion; refuses overwrite and active-campaign deadline bypass.

Manual start streams both server and engine logs to the terminal, including startup, generation progress and request timings. Files remain saved under the printed `LOGS` directory. For a server already started with an older launcher, run `./logs.sh` in a second terminal; Ctrl-C stops the viewer without stopping the server. Benchmark sessions retain file-only logs.

Manual start also persists the existing Monitor API at 1 Hz under the printed `UI_MONITOR_LOGS` directory: `metrics.jsonl`, `metrics.csv`, and deduplicated completed-request `requests.jsonl`. This uses cached API data, with no extra GPU/PSS polling or engine change. For an already running server, `./record-ui.sh` attaches a recorder without restarting it; Ctrl-C stops only collection. The recorder exits when that server process exits. Disk readings are system-wide and PCIe RX/TX are UI aggregates, not per-expert SSD attribution. The initial snapshot preserves only the UI history still available when collection starts.

The P0/P1/P2 follow-up is complete. This is the recommended real-prompt baseline: fixed `STRATA_POOL_SPIN_US=100` on the unchanged CURRENT executable. Persistent residency was implemented and tested separately, but its decode results were slower. It is not enabled by these launchers.

Fresh-start standard-workload medians with 4096 generated tokens: 32K PP 3613.2 / TG 166.9 tok/s; 128K PP 3985.6 / TG 144.2 tok/s. Independent code, math and prose workloads are documented in E026; math at 128K was approximately neutral. CPU-positive wakeup waits increase, so these numbers do not certify every workload.
