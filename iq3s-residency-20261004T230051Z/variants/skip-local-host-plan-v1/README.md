# skip-local-host-plan-v1

State: CLEAN_EXPERIMENTAL_OR_CONTROL.
Frozen source: `039ea29916d3155514688fb6d5a5de6129d69675`. Binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/skip-local-host-plan-v1/strata`; SHA256 `58aab77cd65222e9396d68b428591b44118172c1353a6e8e01f67b94ccfb649c`.

Both frozen JSON configurations print at startup. The shared launcher checks source/binary identities, uses private host 127.0.0.1, supports an explicit port override, refuses collisions, and performs no build or update. Model weights are shared read-only.

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/skip-local-host-plan-v1/start-32k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/skip-local-host-plan-v1/start-128k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/skip-local-host-plan-v1/stop.sh
```

Later explicit replay (after the recorded campaign deadline):
```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/skip-local-host-plan-v1/benchmark-32k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/skip-local-host-plan-v1/benchmark-128k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/skip-local-host-plan-v1/reproduce.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
```

Use one server at a time and new versioned output directories. Existing attempts refuse overwrite. The --reproduction switch is permitted only after the hard deadline and cannot extend the active campaign. No normal user launcher changes.

Shared Session launch backend exercised in linked smoke/benchmark/diagnostic flows. This does not assert every thin shell alias was separately invoked.

Actual process/startup/warmup evidence is linked in ../../launch-index.json. The thin aliases are syntax checked during final audit; generated replay wrappers are not claimed to have been separately timed.
