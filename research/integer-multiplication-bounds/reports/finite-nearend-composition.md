# Near-end singleton ground choices and composed estimates

This checkpoint shows why the actual retained-role singleton gain matters:
after the independently reviewed phase-cell estimate is composed, equal
grounds50, 50, 50 with R485360 beat the previously accepted52, 48, 52 motif.
The phase-only strict exponent is9638040483941/10^30. The separately
reviewed exact packed recurrence further supports
4819020256931/(5*10^29), more than 5.555952085351 times the pinned2^-59
baseline. These claims retain the upstream conditional multiplication
interfaces. Later pairing candidates have already lowered R further; this
report preserves this earlier completed mathematical checkpoint.

## Ground screen

The fresh actual-role checks moved the singleton immediately before the
last full paired block at several h=2 mod4 grounds. They retained the
global pairing alignment and used unchanged scalar, positive-envelope,
controller, and physical-target checks.

| Ground | Gap | Exact R | Earlier checked R |
|---|---:|---:|---:|
|42|19|279306|279846|
|46|21|372874|373336|
|50|23|485360|486200|
|54|25|618352|619002|
|58|27|773730|774822|
|62|29|953062|not in earlier cohort|

The full h48 and h52 gap sweeps had already found no improvement to the
accepted R426624 and R549120 counts. Their original attempts included an
invalid extra gap; that failure and retained partial results are preserved
separately from the successful missing-case repair. They are not silently
treated as uninterrupted complete sweeps.

## Exact composition

The composer selected the least checked R for every available ground,
formed every ordered p,q,p motif, and evaluated both the reviewed LU and
phase estimates. It kept exact rational eta, certified logarithm/saving
enclosures, complex saving and guard inequalities. Additions-only rankings
were not used as transferred results.

For p=q=50, v=19600, m=125000 and R=485360:

```text
W   = 388009283200000
L   = 2881200000000
D   = 1767136000000
s   = 48501158632864000000
eta = 23/631262500
```

The strict LU value is160634297209/(25*10^27), versus the earlier
6412736146231/10^30. The phase value improves the earlier52, 48 phase value
9619086947915/10^30 by exactly
9638040483941/9619086947915, about 0.19704 percent. The next phase-scored
pair is50, 52 at 9621971568139/10^30. These rankings explain why merely
keeping the earlier unequal factors would miss the singleton improvement.

The equal-ground finite witness has complete small dirty side invocations,
equal and asymmetric three-stage exchange calibration, full h50 matching,
source/target and physical-frame checks. The independent dense reviewer
reconstructed all 63562800 partial coefficients, 434730 disjoint physical
additions, 465760 fresh-destination copies and 2709640 physical frame
transitions; all passed. See
[independent singleton review](review-singleton-witness.md).

The coordinating agent independently checked 64 selected phase conditions
and 120 ceilings, then the exact packed recurrence. Their generic phase and
packed composers keep those analytic interfaces separate from this finite
ground-selection screen. This report does not claim a new full machine
implementation or remove inherited conditional assumptions.

## Persistence and reproduction

The fresh ground results are in
[h42](../runs/20261008T001315Z-finite-singleton-42-near-end/results/certificate.json),
[h46](../runs/20261008T001315Z-finite-singleton-46-near-end/results/certificate.json),
[h54](../runs/20261008T001315Z-finite-singleton-54-near-end/results/certificate.json),
[h58](../runs/20261008T001315Z-finite-singleton-58-near-end/results/certificate.json) and
[h62](../runs/20261008T001315Z-finite-singleton-62-near-end/results/certificate.json).
Their arguments, source hashes, maps, compiled hashes, frame/target checks,
exact timings and regenerable external logs are retained in the run protocols.

[finite_nearend_composition.py](../code/finite_nearend_composition.py) and
[the exact composition certificate](../evidence/20261008T0058Z-phase-singleton-complex-compact/runs/20261008T002145Z-finite-nearend-composition/results/certificate.json.gz)
retain all selected source witnesses, input hashes, exact bounds and the
ordered factor ranking. Certificate SHA256:
7464136bb620777ebce224acecb30ac9b8d592ac4cfc04eaa8a9ab7a1874a673.

Run from the topic directory with the campaign math environment, BLAS/OMP
threads1, and a fresh output:

```bash
python -B code/finite_singleton_reuse_scan.py --reference "$REFERENCE" \
  --h 42 --kind global --parameters 19 --workers 1 --output "$FRESH_RESULT"
python -B code/finite_nearend_composition.py --baseline-motif "$BASE_MOTIF" \
  --candidates "$CANDIDATE_42" "$CANDIDATE_46" "$CANDIDATE_54" \
  "$CANDIDATE_58" "$CANDIDATE_62" "$SINGLETON_TRANSFER" \
  --output "$FRESH_COMPOSITION"
```

The next step is to compose the strongest independently promoted new
pairing vector and repeat ground selection when fresh h48/h52 witnesses
change. All active search candidates remain separate from this completed
transfer checkpoint.

Complete row-level certificates are published as intact gzip evidence.
Local original JSON remains unchanged. Follow the topic reproduction guide
to restore missing JSON before running certificate-consuming commands.
