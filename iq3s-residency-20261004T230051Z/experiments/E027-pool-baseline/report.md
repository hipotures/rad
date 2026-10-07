# E027: P1 paired standard-workload confirmation

State: COMPLETE_FROZEN_BASELINE. Selected policy: **fixed100us**, unchanged CURRENT binary.

| Family | Context | Policy | Valid/attempts | PP | TG | TTFTs | Walls | Decode VMCPU% | CPUentries |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| standard | 32k | default | 3/3 | 3603.2 | 148.8 | 7.994 | 35.513 | 95.8 | 34264 |
| standard | 32k | sleep100us | 3/3 | 3613.2 | 166.9 | 7.989 | 32.478 | 26.8 | 34264 |
| standard | 128k | default | 3/3 | 3988.1 | 124.8 | 32.262 | 65.095 | 98.7 | 42755 |
| standard | 128k | sleep100us | 3/3 | 3985.6 | 144.2 | 32.346 | 60.740 | 29.6 | 42755 |

Actual input/output IDs and per-pair checks are in summary.json. Early endings excluded from fixed-length table, retained in application_metrics. Fresh-server paired3replicates; no extras or favorable retries.

Different documents/tasks and application latency matter; all natural EOS kept.

One-Hz phase boundaries use clientTTFT, not exactGPUkernel timing.

Actual engine outputIDs captured by common Python wrapper, enginebinary unchanged.

Wait timings unavailable in headline; diagnostic event binary separate.

No logical expert file-read counter inferred from physical processreadbytes.

## Independent confirmation and policy selection

Reused the complete E026 independent code/math/prose matrix at both profiles; no unchanged point repeated. All three32K workload families improve latency, code/prose128K improve, math128K is neutral. CPU-positive completion costs increase, but no serious consistent request regression was observed. A new adaptive synchronization policy is not justified by these data. No dense/coarse threshold sweep performed.

## Safety and scheduling mechanism

Targeted test:8000batches/67200jobs across default/100us, including32-job worker bursts, zero-job periods,120/800us gaps,25ms idle periods and eight construction/destruction cycles perpolicy. Every output element finite and exactlyzero forzero immutable weights, watchdog/nohang/nojobloss. Existing random0–4job stress40s total and real nativeIQ layers0/1/2/12 passed. Exact commands/logs/source and standalone test binary hashes are in safety/. Existing seq_cst epoch/sleepers/CV protocol is unchanged; this finite stress is not a proof over all interleavings.

P0 event traces additionally preserved every outputID, routerID, path, cache/heat state, slot-byte class and first-head bit atbothprofiles (diagnostic-v1/*/strict-parity.json). Clean pairedP1 checks preserve output/MTP/normalrouting. Prior full suite limitations remain: four existing missingfixture/VMmlock failures, not newly repaired or hidden.

## Usable baseline

No source rebuild, new weights or capacity change. Source `6f32ec070f23ced9f50e704d854d775da52591ab`; binarySHA `eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d`. K25/pcie.28/workers15/spec4/minp.5/INT8/prefillauto/suffix0/promptcache0; max32768 or131072, KVresident32768 wherevalid.

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/p1-baseline/start-32k.sh --host 0.0.0.0 --port 8080
```

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/p1-baseline/start-128k.sh --host 0.0.0.0 --port 8080
```

Stop: `/srv/ai/research/iq3s-residency-20261004T230051Z/variants/p1-baseline/stop.sh`. Only one server at a time. Research launcher prints/verifies frozen config and owns PID identity; original normal user launchers remain unchanged. Default bind remains127.0.0.1; explicithost override changes no inference settings. Later replay: `reproduce.sh --experiment NEW_EXPERIMENT --attempt v1 --reproduction` after campaign completion; refuses overwrite and active-campaign deadline bypass.

P2 may now begin using **p1-baseline as its only normal control**. A new policy OFF build must reproduce mathematics/capacity and be measured separately if binary layout differs.

## Launcher and historical checks

Actual saved128K alias bound0.0.0.0:18080, healthREADY, exactly4096input/64output, zero reuse, correct100us environment. Ownedstop returned0 and left both GPUs free (launcher-smoke/). No64-token throughput included. Warmup audit passed all6pairs. Historical E002 versus P1 is NOT_CONTROLLED_A_B: same saved inputs, but oldserial cachehistory versus newfreshserver perreplica changes later output/routing. See historical-protocol-check.json; do not attribute that difference to pool100. Existing pipeline averages are in mechanism.md.
