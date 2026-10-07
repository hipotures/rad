# pool-p0-default

Frozen source: `6f32ec070f23ced9f50e704d854d775da52591ab`; binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/control/strata`. Configs are printed and hashes verified at every startup. No rebuild/update during launch. Uses saved IQ3_S files and fixed K=25 / PCIe 0.28.

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/pool-p0-default/start-32k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/pool-p0-default/start-128k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/pool-p0-default/stop.sh
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/pool-p0-default/benchmark-32k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/pool-p0-default/benchmark-128k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/pool-p0-default/reproduce.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
```

Use one server at a time. The original normal user launchers are unchanged. A benchmark refuses to overwrite an existing attempt. Fresh research launches obey the absolute deadline. The explicit --reproduction flag is only permitted after that deadline for a later user replay; it does not extend the active campaign. Diagnostic variants are not headline speed builds.
