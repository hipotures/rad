# persistent-v2-diagnostic

Frozen source: `9f01f074633bb631590fb112acdcd1a98c00d18b`; binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/persistent-runtime-v2-diagnostic-fixed/strata`. Configs are printed and hashes verified at every startup. No rebuild/update during launch. Uses saved IQ3_S files and fixed K=25 / PCIe 0.28.

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v2-diagnostic/start-32k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v2-diagnostic/start-128k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v2-diagnostic/stop.sh
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v2-diagnostic/benchmark-32k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v2-diagnostic/benchmark-128k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v2-diagnostic/reproduce.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
```

Use one server at a time. The original normal user launchers are unchanged. A benchmark refuses to overwrite an existing attempt. Fresh research launches obey the absolute deadline. The explicit --reproduction flag is only permitted after that deadline for a later user replay; it does not extend the active campaign. Diagnostic variants are not headline speed builds.
