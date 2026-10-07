# diagnostic-router-fresh-v1

State: DIAGNOSTIC_ONLY.
Frozen source: `bc505f4636c6d3e37c4c85eef74ea60aaccb0181`. Binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/diagnostic-router-fresh-v1/strata`; SHA256 `bb12e367bdabca726934a0b1972279b671668bfb2df5d7176ed2dbd097488e39`.

Both frozen JSON configurations print at startup. The shared launcher checks source/binary identities, uses private host 127.0.0.1, supports an explicit port override, refuses collisions, and performs no build or update. Model weights are shared read-only.

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/diagnostic-router-fresh-v1/start-32k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/diagnostic-router-fresh-v1/start-128k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/diagnostic-router-fresh-v1/stop.sh
```

Diagnostic replay only; rates must not enter clean speed tables:
```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/diagnostic-router-fresh-v1/diagnose-episodes.sh --experiment YOUR_NEW_DIAGNOSTIC --attempt v1 --reproduction
```

Use one server at a time and new versioned output directories. Existing attempts refuse overwrite. The --reproduction switch is permitted only after the hard deadline and cannot extend the active campaign. No normal user launcher changes.

Shared Session launch backend exercised in linked smoke/benchmark/diagnostic flows. This does not assert every thin shell alias was separately invoked.

Actual process/startup/warmup evidence is linked in ../../launch-index.json. The thin aliases are syntax checked during final audit; generated replay wrappers are not claimed to have been separately timed.
