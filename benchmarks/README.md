# Historical benchmark archive

This directory contains actual durable files imported from `/srv/ai/benchmarks`,
which is the earlier part of the same RaD research workspace. The later
[residency laboratory](../iq3s-residency-20261004T230051Z/README.md) remains
alongside it in this repository.

Reports, authored scripts/CUDA kernels, configurations, source patches, compact
results and plots are retained. Large execution files remain local; see the
[workspace map](../docs/workspaces.md) and [source manifest](../docs/external-workspaces.json).

| Investigation | Report |
|---|---|
| `qwen-hardware-characterization/run-20261004T104353Z` | [Report](qwen-hardware-characterization/run-20261004T104353Z/report.md) |
| `qwen38-flash-next-20260829-105917` | [Report](qwen38-flash-next-20260829-105917/REPORT.md) |
| `qwen38-flash-next-mtp-gpu-20260830T223005Z` | [Report](qwen38-flash-next-mtp-gpu-20260830T223005Z/REPORT.md) |
| `qwen38-flash-next-phase2-20260829-211320` | [Report](qwen38-flash-next-phase2-20260829-211320/REPORT.md) |
| `qwen38-flash-next-phase3-iq4xs-20260830-080504` | [Report](qwen38-flash-next-phase3-iq4xs-20260830-080504/REPORT.md) |
| `qwen38-flash-next-runtime-opt-20260830T155104Z` | [Report](qwen38-flash-next-runtime-opt-20260830T155104Z/REPORT.md) |
| `strata-qwen38/iq3s-v0138-2x4090` | [Report](strata-qwen38/iq3s-v0138-2x4090/report.md) |
| `strata-qwen38/iq3s-v0138-replay-v0131-32k` | [Report](strata-qwen38/iq3s-v0138-replay-v0131-32k/report.md) |
| `strata-qwen38/pr578-dual4090` | [Report](strata-qwen38/pr578-dual4090/report.md) |
| `strata-qwen38/pr578-dual4090/original-pr578-checkpoint` | [Report](strata-qwen38/pr578-dual4090/original-pr578-checkpoint/report.md) |
| `strata-qwen38/pr578-dual4090-refresh-20261004T124028Z` | [Report](strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/report.md) |
| `strata-qwen38/q4-max-sweep` | [Report](strata-qwen38/q4-max-sweep/report.md) |
| `strata-qwen38/q4-v0132` | [Report](strata-qwen38/q4-v0132/report.md) |
| `strata-qwen38/q5-best-q4-single-v0132` | [Report](strata-qwen38/q5-best-q4-single-v0132/report.md) |
| `strata-qwen38/q5-cpu-fallback-v0132` | [Report](strata-qwen38/q5-cpu-fallback-v0132/report.md) |
| `strata-qwen38/q5-loader-patch-v0132` | [Report](strata-qwen38/q5-loader-patch-v0132/report.md) |
| `strata-qwen38/q5-ple-q8-v0132` | [Report](strata-qwen38/q5-ple-q8-v0132/report.md) |
| `strata-qwen38/q5-speed-256k-best-q4-v0132` | [Report](strata-qwen38/q5-speed-256k-best-q4-v0132/report.md) |
| `strata-qwen38/q5-speed-best-q4-v0132` | [Report](strata-qwen38/q5-speed-best-q4-v0132/report.md) |
| `strata-qwen38/results` | [Report](strata-qwen38/results/report.md) |
| `strata-qwen38/threeway-32k-128k-longdecode-20261004T212330Z` | [Report](strata-qwen38/threeway-32k-128k-longdecode-20261004T212330Z/report.md) |

Other retained records include [Q6/MTP preparation](qwen38-flash-next-q6-mtp-prepared/README.md),
[hardware source and build procedure](qwen-hardware-characterization/README.md),
[MoE profile headers](moe-profiles/compact-results/),
[CPU placement tasks/results](squares-cpu-penalty-test08/),
[Buun launch script](run-buun-qwen38-128k.sh) and [bounded historical Buun logs](buun-logs/).

The reports retain their original dates, status, methodology and limitations.
Importing them does not turn old benchmark settings into defaults for a fresh
task or create a new measurement. Source/configuration paths embedded in the
historical files address their original workstation locations.

For 128K serving entrypoints and their exact configs, use the [starter index](../launchers/README.md).
