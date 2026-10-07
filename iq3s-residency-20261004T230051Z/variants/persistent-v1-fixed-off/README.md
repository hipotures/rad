# persistent-v1-fixed-off

Frozen source: `23e58175d0a3e3f5f60b70ea8bb76ee1bd96a3a0`; binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/persistent-runtime-v1-fixed/strata`. Configs are printed and hashes verified at every startup. No rebuild/update during launch. Uses saved IQ3_S files and fixed K=25 / PCIe 0.28.

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-fixed-off/start-32k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-fixed-off/start-128k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-fixed-off/stop.sh
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-fixed-off/benchmark-32k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-fixed-off/benchmark-128k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-fixed-off/reproduce.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
```

Use one server at a time. The original normal user launchers are unchanged. A benchmark refuses to overwrite an existing attempt. Fresh research launches obey the absolute deadline. The explicit --reproduction flag is only permitted after that deadline for a later user replay; it does not extend the active campaign. Diagnostic variants are not headline speed builds.
