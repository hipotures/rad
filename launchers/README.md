# Starter and launcher index

User-owned serving scripts and their exact configuration are durable source.
The imported [IQ3_S 128K starter family](iq3s-128k-20261004/README.md) contains:

| Starter | Configuration |
|---|---|
| [start-helper-priority.sh](iq3s-128k-20261004/start-helper-priority.sh) | [helper-priority.json](iq3s-128k-20261004/configs/helper-priority.json) |
| [start-layer-split-v0138.sh](iq3s-128k-20261004/start-layer-split-v0138.sh) | [layer-split-v0138.json](iq3s-128k-20261004/configs/layer-split-v0138.json) |
| [start-layer-split-v0139-pcie028.sh](iq3s-128k-20261004/start-layer-split-v0139-pcie028.sh) | [layer-split-v0139-pcie028.json](iq3s-128k-20261004/configs/layer-split-v0139-pcie028.json) |

The scripts and configs are copied verbatim from `/srv/ai/launchers/`. They
retain executable bits and original runtime paths. The [manifest](iq3s-128k-20261004/manifest.json)
records the binary identities. Weights, binaries and environments remain
outside Git; a fresh clone requires those dependencies. Import validation
checks script syntax and copied identities, not a new GPU serving run.

[YASD installation and verification](yasd/README.md) is also preserved.

The original laboratory also has 53 `start-128k.sh` files, already tracked
before this import. They are variant/campaign entrypoints, including diagnostic
and experimental versions. Their names are not interchangeable serving defaults.
Read the [laboratory launcher index](../iq3s-residency-20261004T230051Z/launch-index.md)
and each campaign protocol before choosing one.

| Existing 128K entrypoint | Script |
|---|---|
| `campaigns/q4-conditional-admission-20261006T010859Z/launchers/conditional` | [start-128k.sh](../iq3s-residency-20261004T230051Z/campaigns/q4-conditional-admission-20261006T010859Z/launchers/conditional/start-128k.sh) |
| `campaigns/q4-conditional-admission-20261006T010859Z/launchers/control` | [start-128k.sh](../iq3s-residency-20261004T230051Z/campaigns/q4-conditional-admission-20261006T010859Z/launchers/control/start-128k.sh) |
| `campaigns/q4-live-oracle-20261006T040656Z/launchers/control` | [start-128k.sh](../iq3s-residency-20261004T230051Z/campaigns/q4-live-oracle-20261006T040656Z/launchers/control/start-128k.sh) |
| `campaigns/q4-multigpu-20261005T164628Z/launchers` | [start-128k.sh](../iq3s-residency-20261004T230051Z/campaigns/q4-multigpu-20261005T164628Z/launchers/start-128k.sh) |
| `campaigns/q4-pool-spin-20261005T184831Z/launchers` | [start-128k.sh](../iq3s-residency-20261004T230051Z/campaigns/q4-pool-spin-20261005T184831Z/launchers/start-128k.sh) |
| `campaigns/q4-residency-v2-20261005T202441Z/launchers/control` | [start-128k.sh](../iq3s-residency-20261004T230051Z/campaigns/q4-residency-v2-20261005T202441Z/launchers/control/start-128k.sh) |
| `campaigns/q4-residency-v2-20261005T202441Z/launchers/early-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/campaigns/q4-residency-v2-20261005T202441Z/launchers/early-v1/start-128k.sh) |
| `campaigns/q4-residency-v2-20261005T202441Z/launchers/history-v2` | [start-128k.sh](../iq3s-residency-20261004T230051Z/campaigns/q4-residency-v2-20261005T202441Z/launchers/history-v2/start-128k.sh) |
| `variants/compatible-fast-v2` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/compatible-fast-v2/start-128k.sh) |
| `variants/compatible-policy-off` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/compatible-policy-off/start-128k.sh) |
| `variants/compatible-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/compatible-v1/start-128k.sh) |
| `variants/control` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/control/start-128k.sh) |
| `variants/device-plan-ids-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/device-plan-ids-v1/start-128k.sh) |
| `variants/device-plan-ids-v2` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/device-plan-ids-v2/start-128k.sh) |
| `variants/diagnostic-compatible-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-compatible-v1/start-128k.sh) |
| `variants/diagnostic-coordination-off-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-coordination-off-v1/start-128k.sh) |
| `variants/diagnostic-coordination-on-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-coordination-on-v1/start-128k.sh) |
| `variants/diagnostic-device-plan-ids-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-device-plan-ids-v1/start-128k.sh) |
| `variants/diagnostic-device-plan-ids-v2` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-device-plan-ids-v2/start-128k.sh) |
| `variants/diagnostic-direct-parts-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-direct-parts-v1/start-128k.sh) |
| `variants/diagnostic-direct-parts-v2` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-direct-parts-v2/start-128k.sh) |
| `variants/diagnostic-frequency-v5` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-frequency-v5/start-128k.sh) |
| `variants/diagnostic-gpu-router-v2` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-gpu-router-v2/start-128k.sh) |
| `variants/diagnostic-plan-compare-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-plan-compare-v1/start-128k.sh) |
| `variants/diagnostic-pool-wait-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-pool-wait-v1/start-128k.sh) |
| `variants/diagnostic-router-fresh-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-router-fresh-v1/start-128k.sh) |
| `variants/diagnostic-skip-local-host-plan-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-skip-local-host-plan-v1/start-128k.sh) |
| `variants/diagnostic-v5` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-v5/start-128k.sh) |
| `variants/diagnostic-v6` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-v6/start-128k.sh) |
| `variants/diagnostic-v7` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-v7/start-128k.sh) |
| `variants/diagnostic-v8` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-v8/start-128k.sh) |
| `variants/diagnostic-wide-gate-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/diagnostic-wide-gate-v1/start-128k.sh) |
| `variants/direct-parts-off-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/direct-parts-off-v1/start-128k.sh) |
| `variants/direct-parts-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/direct-parts-v1/start-128k.sh) |
| `variants/frequency-v1-ready` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/frequency-v1-ready/start-128k.sh) |
| `variants/host-plan-off-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/host-plan-off-v1/start-128k.sh) |
| `variants/p1-baseline` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/p1-baseline/start-128k.sh) |
| `variants/p1-pool-default` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/p1-pool-default/start-128k.sh) |
| `variants/persistent-signal-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/persistent-signal-v1/start-128k.sh) |
| `variants/persistent-v1-fixed-off` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/persistent-v1-fixed-off/start-128k.sh) |
| `variants/persistent-v1-fixed-on` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/persistent-v1-fixed-on/start-128k.sh) |
| `variants/persistent-v1-off` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/persistent-v1-off/start-128k.sh) |
| `variants/persistent-v1-on` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/persistent-v1-on/start-128k.sh) |
| `variants/persistent-v2-diagnostic` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/persistent-v2-diagnostic/start-128k.sh) |
| `variants/persistent-v2-off` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/persistent-v2-off/start-128k.sh) |
| `variants/persistent-v2-on` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/persistent-v2-on/start-128k.sh) |
| `variants/pool-p0-100` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/pool-p0-100/start-128k.sh) |
| `variants/pool-p0-default` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/pool-p0-default/start-128k.sh) |
| `variants/pool-p0-diag-default` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/pool-p0-diag-default/start-128k.sh) |
| `variants/pool-p0-diag-sleep100us` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/pool-p0-diag-sleep100us/start-128k.sh) |
| `variants/pool-wait-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/pool-wait-v1/start-128k.sh) |
| `variants/skip-local-host-plan-v1` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/skip-local-host-plan-v1/start-128k.sh) |
| `variants/ud-q4-k-xl` | [start-128k.sh](../iq3s-residency-20261004T230051Z/variants/ud-q4-k-xl/start-128k.sh) |
