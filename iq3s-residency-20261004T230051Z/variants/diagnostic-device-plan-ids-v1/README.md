# diagnostic-device-plan-ids-v1

State: UNSAFE_PLE_DEPENDENCY_REPRODUCER_ONLY.
Frozen source: `5fe14e9321e779345041162b462036a3a83036ab`. Binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/diagnostic-device-plan-ids-v1/strata`; SHA256 `92dcaab562034e221b7594c599134b1d3c32b2c182dd2765c0a9141086f46417`.

Both frozen JSON configurations print at startup. The shared launcher checks source/binary identities, uses private host 127.0.0.1, supports an explicit port override, refuses collisions, and performs no build or update. Model weights are shared read-only.

This variant is retained for reproducing its documented failure, not advertised as a ready server or throughput candidate. Use the corresponding repaired variant for inference.

Diagnostic replay only; rates must not enter clean speed tables:
```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/diagnostic-device-plan-ids-v1/diagnose-profiles.sh --experiment YOUR_NEW_DIAGNOSTIC --attempt v1 --reproduction
```

Use one server at a time and new versioned output directories. Existing attempts refuse overwrite. The --reproduction switch is permitted only after the hard deadline and cannot extend the active campaign. No normal user launcher changes.

Shared Session launch backend exercised in linked smoke/benchmark/diagnostic flows. This does not assert every thin shell alias was separately invoked.

Actual process/startup/warmup evidence is linked in ../../launch-index.json. The thin aliases are syntax checked during final audit; generated replay wrappers are not claimed to have been separately timed.
