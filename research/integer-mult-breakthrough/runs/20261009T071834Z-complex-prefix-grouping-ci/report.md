# Bounded prefix and width-grouping reproduction

Status: **PASS BOUNDED EXACT CHECKS**. Two independent portable checks
ran concurrently with one worker each. The prefix check passed 144
complete physical forward/inverse basis columns and 288 Gaussian fields.
The grouping check passed 72 complete records and 966332 literal tape
operations, including inverse after changed payloads and both negatives.

Both producer hashes and the imported prefix dependency stayed unchanged.
The launch receipt records exit status, times and exact output. Generated
row payloads are deterministically recoverable rather than committed.
The original same-ID work files remain unchanged.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/prefix_activity_shape.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/activity_width_grouping_tapes.py --workers 1 --bounded
```

Scope: exact finite arithmetic and width tape movement. The initial
prefix route, complete fast zeta supplier, precision transfer and exponent
remain open. See [the construction](../../reports/complex/activity-width-tape-grouping.md).
