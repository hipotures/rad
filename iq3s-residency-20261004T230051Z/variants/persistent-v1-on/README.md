# persistent-v1-on

Frozen source: `610ab414ad57a3bcbad1715b3bd1d0916f571148`; binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/persistent-runtime-v1/strata`. Configs are printed and hashes verified at every startup. No rebuild/update during launch. Uses saved IQ3_S files and fixed K=25 / PCIe 0.28.

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-on/start-32k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-on/start-128k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-on/stop.sh
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-on/benchmark-32k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-on/benchmark-128k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-on/reproduce.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
```

Use one server at a time. The original normal user launchers are unchanged. A benchmark refuses to overwrite an existing attempt. Fresh research launches obey the absolute deadline. The explicit --reproduction flag is only permitted after that deadline for a later user replay; it does not extend the active campaign. Diagnostic variants are not headline speed builds.

DIAGNOSTIC_ONLY: unexecuted floatvalidation blocker; usefixed source forreplay only.
