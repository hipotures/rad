# Blocked Gaussian and conditional assembly checks

The [certificate](results/certificate.json) passed 9,040 exact chirp
identities across 640 boundary blocks, three exact dyadic Gaussian-surrogate
blocks with signed packed integer multiplication, and two rigorous
rational-interval true-Gaussian block checks.

Strict conditional assembly witnesses:

- Unchanged upstream graph `R=509194`: `kappa=5/2^60`, with exact minimum
  `682447869/156250000000000000000000000`. This is `5/2` times the
  advertised starting `2^-59` and exceeds `2^-58`.
- Aligned global pair ordering `R=494250`: `kappa=133/(50*2^59)`, with
  exact minimum `1854922221/400000000000000000000000000`.

The new dimension is `epsilon=499/1000`; `delta=1/10000` and
`beta=999/1000`. Gaussian margin is `9/10000`, guard margin is `1/500`,
and the replacement explicit Gaussian cutoff is `b>=2^8000`.
All remaining recurrence, leaf, layout, and precision margins are strict.

The all-size construction is the
[blocked Gaussian proof](../../reports/downstream-blocked-gaussian.md)
combined with the
[weighted Neumann proof](../../reports/downstream-weighted-gaussian.md).
The composed witness additionally needs its separate campaign finite
circuit/frame/rank certificate. The unchanged graph's finite witness is
the pinned starting graph. The full upstream multiplication theorem remains
assumed, and novelty beyond the checked sources is not established.
