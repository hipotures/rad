# frequency-v1-ready

State: CLEAN_EXPERIMENTAL_OR_CONTROL.
Frozen source: `6f32ec070f23ced9f50e704d854d775da52591ab`. Binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/frequency-v1/strata`; SHA256 `81be146d9e2bf47334ca39d5dace8269aede9a7caea24c5125c48639f4f76d07`.

Both frozen JSON configurations print at startup. The shared launcher checks source/binary identities, uses private host 127.0.0.1, supports an explicit port override, refuses collisions, and performs no build or update. Model weights are shared read-only.

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/frequency-v1-ready/start-32k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/frequency-v1-ready/start-128k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/frequency-v1-ready/stop.sh
```

Later explicit replay (after the recorded campaign deadline):
```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/frequency-v1-ready/benchmark-32k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/frequency-v1-ready/benchmark-128k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/frequency-v1-ready/reproduce.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
```

Use one server at a time and new versioned output directories. Existing attempts refuse overwrite. The --reproduction switch is permitted only after the hard deadline and cannot extend the active campaign. No normal user launcher changes.

Shared Session launch backend exercised in linked smoke/benchmark/diagnostic flows. This does not assert every thin shell alias was separately invoked.

Actual process/startup/warmup evidence is linked in ../../launch-index.json. The thin aliases are syntax checked during final audit; generated replay wrappers are not claimed to have been separately timed.
