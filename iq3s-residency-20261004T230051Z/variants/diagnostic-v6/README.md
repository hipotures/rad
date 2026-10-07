# diagnostic-v6

State: INVALID_EVENT_CAPTURE_REPRODUCER_ONLY.
Frozen source: `0c54f64bbd3f960b5352ca1cf7e6f60f4bfaa9f3`. Binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/diagnostic-v6/strata`; SHA256 `403a0c08fbe329f1d0145f8f81d129158963fb5a2a784b426493101a430f2dd4`.

Both frozen JSON configurations print at startup. The shared launcher checks source/binary identities, uses private host 127.0.0.1, supports an explicit port override, refuses collisions, and performs no build or update. Model weights are shared read-only.

This variant is retained for reproducing its documented failure, not advertised as a ready server or throughput candidate. Use the corresponding repaired variant for inference.

Diagnostic replay only; rates must not enter clean speed tables:
```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/diagnostic-v6/diagnose-profiles.sh --experiment YOUR_NEW_DIAGNOSTIC --attempt v1 --reproduction
```

Use one server at a time and new versioned output directories. Existing attempts refuse overwrite. The --reproduction switch is permitted only after the hard deadline and cannot extend the active campaign. No normal user launcher changes.

Shared Session launch backend exercised in linked smoke/benchmark/diagnostic flows. This does not assert every thin shell alias was separately invoked.

Actual process/startup/warmup evidence is linked in ../../launch-index.json. The thin aliases are syntax checked during final audit; generated replay wrappers are not claimed to have been separately timed.
