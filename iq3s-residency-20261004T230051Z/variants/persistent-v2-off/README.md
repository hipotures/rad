# persistent-v2-off

Frozen source: `93e31983c5735453e1f8be5fe143cb4a3f0538b9`; binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/persistent-runtime-v2-fixed/strata`. Configs are printed and hashes verified at every startup. No rebuild/update during launch. Uses saved IQ3_S files and fixed K=25 / PCIe 0.28.

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v2-off/start-32k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v2-off/start-128k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v2-off/stop.sh
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v2-off/benchmark-32k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v2-off/benchmark-128k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v2-off/reproduce.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
```

Use one server at a time. The original normal user launchers are unchanged. A benchmark refuses to overwrite an existing attempt. Fresh research launches obey the absolute deadline. The explicit --reproduction flag is only permitted after that deadline for a later user replay; it does not extend the active campaign. Diagnostic variants are not headline speed builds.
