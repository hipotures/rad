# Singleton neighborhoods using actual retained roles

The completed219-case neighborhood found a positive-frame graph with
484264 physical roles at ground 50. This improves the earlier fully
promoted gap 23 graph's485360 roles by 1096. Every case was evaluated with
the unchanged exact map, physical scalar/frame and target verifiers. The
winner has since passed the separate complete uncached review, including
small dirty-scratch and three-stage exchange controls; its downstream
composition is coordinated separately.

## Construction and useful negatives

Start with positions 22 for common points 0/1, 23 for points 2-47 and 24 for
points 48/49. This was the first50-case sweep's initial485316 witness.
Test 100 individual near moves, 49 paired near moves, 50 individual
three-step backward moves, and 20 first/middle-position controls. The
candidate identity is SHA256 of the exact ground, base, position vector and
pinned reference commit. The 50 earlier planned IDs, baseline and anchor
are excluded; the final219 are pairwise distinct.

The final winner moves point48 to position 0, leaving point49 at 24:

```text
positions = [22,22] + [23]*46 + [0,24]
candidate = 6a112b577b3feb05a94dcdfee41c449777edf0894e7fb73513ad805a5b141bd4
R         = 484264
compiled  = 91788d65aebb8fc9fb12a20350004f6cd766f5c36b6a226e9495bdd8a3ac55b5
```

This demonstrates why an additions proxy can discard useful circuits.
Earlier paired and coordinate-descent searches tended to preserve global
common-point symmetry. Breaking it at one singleton creates additional
valid retained-controller chains despite losing some common-subexpression
sharing. The complete role expression c+q-selected_links is the decisive
measurement. It is not enough to minimize c alone.

Intermediate complete finite screens included485230 at first-pair
position 21 and 485193 with both endpoint pairs at 22. Moving point0 to0
gave484350. The eventual point48 move was stronger. These exact candidates
and negatives remain in the full case records rather than being replaced
by a best-only search log.

## Throughput and resources

The 219 exact cases completed in 766.030 seconds, 1029.202 verified cases per
hour. The pool began with 16 active workers and changed to15 to leave one
core for independent review. Every evaluation used one CPU process and
BLAS/OMP threads1; each process had a6 GiB address-space cap. The campaign
RAM ceiling was96 GiB. Capacity changes and read-only resource snapshots
are retained. The process IDs in checkpoints are all observed worker IDs,
not a claim that every retained idle process was active at that instant.

Mean per-case phases, including different candidate structures and worker
cache histories:

| Phase | Seconds |
|---|---:|
|Positive envelopes|26.335|
|Physical compile and checks|14.759|
|Controller flow|5.707|
|Global scalar map|1.796|
|Constructor/local checks|0.713|
|All physical targets|0.219|

The coordinating50-case pilot measured uncached serial73.782 verified
cases/hour, cached serial84.915/hour, and 12-process cached840.150/hour.
Those phases used distinct matched cases, so the ratio is a useful measured
throughput comparison, not an identical-input speedup experiment.

The next420-case queue starts from the final484264 vector, excludes all
270 earlier planned IDs, and uses the independently controlled direct
envelope constructor. It prioritizes individual early positions 0/1/2,
paired early moves, early prefixes and seeded multi-coordinate changes,
seed109. Its source and protocol are immutable while it runs. It preserves
all the original verification calls. New exploratory winners are separate
from the completed219-case promotion.

## Persistence and recovery

The source is
[finite_singleton_neighborhood.py](../code/finite_singleton_neighborhood.py),
with unchanged evaluation/cache logic imported from
[singleton_sensitivity.py](../code/singleton_sensitivity.py).
The complete attempt is
[run20261008T004828Z](../runs/20261008T004828Z-finite-singleton-neighborhood/protocol.json).
Its readable winner and compact metrics are retained with the run. Full
per-case JSONs and resource snapshots are deterministically regenerable
and reside externally under the exact paths in the protocol; publication
uses complete gzip evidence copies when required by the repository audit.

The immutable winner JSON SHA256 is
02f86b24c896d6764b059853dcdaf113fc26f4589a30ddce973e5d48a8cb5641.
The source, candidate generator, full position vectors, input hashes and
per-case verification metadata suffice to reconstruct every graph and
physical compiler schedule. There is no irreplaceable input payload.

From the topic directory, with the pinned math environment and a fresh
output directory:

```bash
python -B code/finite_singleton_neighborhood.py --reference "$REFERENCE" \
  --anchor "$FIRST_SWEEP_ANCHOR" --predecessor "$FIRST_SWEEP" \
  --max-workers 16 --reserve-file "$RESERVATION" \
  --worker-address-space-gib 6 --deadline "$ATTEMPT_DEADLINE" \
  --work-root "$CAMPAIGN_WORK" --run-dir "$FRESH_OUTPUT"
```

Only the task-owned process group is terminated at the 30-minute attempt
bound. Completed checkpoints survive an interruption. No frozen upstream
input, live evaluator source, unrelated process or previous result is
modified.
