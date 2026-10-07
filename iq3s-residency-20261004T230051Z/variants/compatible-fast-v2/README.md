# compatible-fast-v2

State: CLEAN_EXPERIMENTAL_OR_CONTROL.
Frozen source: `4440118f1fa098e6ff8abcfc67b591a9037b14c7`. Binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/compatible-fast-v2/strata`; SHA256 `6464d947cc1b20089c59bb03f680073eed653a6cfde92d35c3f6969f7887ae6e`.

Both frozen JSON configurations print at startup. The shared launcher checks source/binary identities, uses private host 127.0.0.1, supports an explicit port override, refuses collisions, and performs no build or update. Model weights are shared read-only.

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/compatible-fast-v2/start-32k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/compatible-fast-v2/start-128k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/compatible-fast-v2/stop.sh
```

Later explicit replay (after the recorded campaign deadline):
```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/compatible-fast-v2/benchmark-32k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/compatible-fast-v2/benchmark-128k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/compatible-fast-v2/reproduce.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
```

Use one server at a time and new versioned output directories. Existing attempts refuse overwrite. The --reproduction switch is permitted only after the hard deadline and cannot extend the active campaign. No normal user launcher changes.

Shared Session launch backend exercised in linked smoke/benchmark/diagnostic flows. This does not assert every thin shell alias was separately invoked.

Actual process/startup/warmup evidence is linked in ../../launch-index.json. The thin aliases are syntax checked during final audit; generated replay wrappers are not claimed to have been separately timed.
