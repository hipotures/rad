# device-plan-ids-v1

State: UNSAFE_PLE_DEPENDENCY_REPRODUCER_ONLY.
Frozen source: `aa3a9d0652bf52985e2359433354135e3f22c160`. Binary: `/srv/ai/research/iq3s-residency-20261004T230051Z/builds/device-plan-ids-v1/strata`; SHA256 `29ae85fa24b75ca737615696ac044c1ca35913a9078d65d5dfc4b365c7cdbf1e`.

Both frozen JSON configurations print at startup. The shared launcher checks source/binary identities, uses private host 127.0.0.1, supports an explicit port override, refuses collisions, and performs no build or update. Model weights are shared read-only.

This variant is retained for reproducing its documented failure, not advertised as a ready server or throughput candidate. Use the corresponding repaired variant for inference.

Later explicit replay (after the recorded campaign deadline):
```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/device-plan-ids-v1/benchmark-32k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/device-plan-ids-v1/benchmark-128k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/device-plan-ids-v1/reproduce.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction
```

Use one server at a time and new versioned output directories. Existing attempts refuse overwrite. The --reproduction switch is permitted only after the hard deadline and cannot extend the active campaign. No normal user launcher changes.

Shared Session launch backend exercised in linked smoke/benchmark/diagnostic flows. This does not assert every thin shell alias was separately invoked.

Actual process/startup/warmup evidence is linked in ../../launch-index.json. The thin aliases are syntax checked during final audit; generated replay wrappers are not claimed to have been separately timed.
