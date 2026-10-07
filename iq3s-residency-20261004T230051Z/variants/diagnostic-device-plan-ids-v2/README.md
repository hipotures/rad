# diagnostic-device-plan-ids-v2

State: DIAGNOSTIC_ONLY.
Frozen source: `053c4a6ea73ddc9a02c8bb7631d747f03cea954a`. Binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/diagnostic-device-plan-ids-v2/strata`; SHA256 `a157b12597ae34e078294c517cb96d52b95ff44a8faa67a4ea6ae1db97246ff8`.

Both frozen JSON configurations print at startup. The shared launcher checks source/binary identities, uses private host 127.0.0.1, supports an explicit port override, refuses collisions, and performs no build or update. Model weights are shared read-only.

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/diagnostic-device-plan-ids-v2/start-32k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/diagnostic-device-plan-ids-v2/start-128k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/diagnostic-device-plan-ids-v2/stop.sh
```

Diagnostic replay only; rates must not enter clean speed tables:
```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/diagnostic-device-plan-ids-v2/diagnose-profiles.sh --experiment YOUR_NEW_DIAGNOSTIC --attempt v1 --reproduction
```

Use one server at a time and new versioned output directories. Existing attempts refuse overwrite. The --reproduction switch is permitted only after the hard deadline and cannot extend the active campaign. No normal user launcher changes.

Shared Session launch backend exercised in linked smoke/benchmark/diagnostic flows. This does not assert every thin shell alias was separately invoked.

Actual process/startup/warmup evidence is linked in ../../launch-index.json. The thin aliases are syntax checked during final audit; generated replay wrappers are not claimed to have been separately timed.
