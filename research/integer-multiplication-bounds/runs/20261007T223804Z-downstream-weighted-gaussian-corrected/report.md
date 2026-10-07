# Corrected weighted Gaussian certificate

The exact checker passed **1,099,640 rational matrix-transition identities**,
including nonzero periodic aliases and nearest-rounding ties. The complete
[certificate](results/certificate.json) includes both strict assembly witnesses:

- Unchanged paired graph `R=509194`, `a_bit=296/10^11`:
  `kappa=5/2^61`, exactly `5/4` times the advertised `2^-59` baseline;
  minimum margin `340540119/156250000000000000000000000`.
- Aligned global pair ordering `R=494250`, `a_bit=305/10^11`:
  `kappa=133/(100*2^59)`; minimum margin
  `925602471/400000000000000000000000000`.

Both witnesses preserve strict positive Gaussian, guard, recurrence, layout,
prime-selection, and rounding slack. The second requires the parent branch's
independent finite construction/frame/restoration certificate. The first uses
the starting finite graph and changes only the Gaussian power estimate,
width, and transform dimension.

See the [complete derivation](../../reports/downstream-weighted-gaussian.md)
and [source](../../code/downstream_gaussian.py). Independent critical review
confirmed the similarity orientation, periodic aliases, contraction,
Neumann accuracy constants, and proof-only use of the diagonal weights.

The original output directory was accidentally named with a future timestamp;
the protocol records its actual command and the byte-preserving relocation
to this correctly timestamped attempt. The completed certificate was not
rewritten during relocation. A later refinement adds an independent exact
logarithm enclosure to the checker and is validated in a fresh run.
