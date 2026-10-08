# Candidate: factor reuse changes the segmented online boundary charge

Status at 2026-10-08 12:47 UTC: written candidate awaiting exact controls and
independent campaign criticism. This does not establish a new full exponent.

Swapnil Jain's public segmented inverse at commit
`c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007`,
[notes/segmented-inverse.tex](https://github.com/Swapnil-jain/integer-mult-kappa/blob/c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007/notes/segmented-inverse.tex),
states a per-output charge `w^3(1/lambda+theta)` for the cyclic boundary system.
Its matrix and factors depend on the axis, not on the tensor spectator line.
Factoring a block tridiagonal system costs cubic work per boundary, but applying
retained factors to each new right-hand side is quadratic per boundary. The
distinction is consequential when many spectator lines reuse one matrix.

For an axis with `s` physical positions, boundary density `h=O(1/lambda+theta)`,
boundary width `w`, precision `P`, and `F` spectator lines, the separated charge is

```
setup:  O(s*h*w^3*P^(1+delta))
online: O(F*s*h*w^2*P^(1+delta)).
```

The factor catalogue has `O(s*h*w^2*P)` bits, and can be scanned in boundary
order for each spectator line. An interleaved slab execution keeps only running
right-hand sides as per-line state; line-independent factors are read once per
slab and reused across its spectator rows. Catalogue traffic is at most the
displayed online charge and does not require random-access RAM.

In the multiplication regime, `s=2^(Theta(b^(1-epsilon)))`, `epsilon<1`,
and every other parameter is polynomial in `b=log n`. Even summing setup over
all `d=Theta(b^epsilon)` axes is `n^o(1)`. This claim concerns constructive
generated data, never uncharged advice. The catalogue must be regenerated from
pinned axis identities and parameters; its generation is included above.

Take longer digits with `P=Theta(Q)=Theta(b^(1+x))`, ordinary oversampling
`theta=Theta(1/d)`, and `u=alpha^2=Theta(Q/d)` with conservative constants so
`gamma=2du<=b'/4`. If `2epsilon<1+x`, then `u*theta` tends to infinity,
`w^2=O(Q/u)=O(d)`, and a whole phase cell has length `Theta(d)`. Its Gaussian
similarity needs `O(u/theta)=O(Q)` guard bits. The online boundary charge
`theta*w^2` is constant. Reduced oversampling `y>=epsilon` and extra recentred
cuts are therefore unnecessary for this particular reused-factor interface.

The completed RaD phase-cell inverse already contains the key quadratic online
boundary accounting. Credit belongs to that completed work and the established
Toeplitz/Schur/Woodbury tools. The new contribution being tested here is a
general reuse/precision statement and a simplified integration with longer
digits; this is not claimed to be worldwide novel.

Remaining obligations: independently check cyclic border formulas, table and
right-hand-side rounding, catalogue ordering under the full tape schedule, and
the unchanged complete cost rows. Even after acceptance this simplification
does not remove the butterfly or per-axis pass costs, so a stronger complete
exponent cannot be claimed solely from it.

## Independent exact finite controls

The authored standard-library checker `../code/reusable_cyclic.py` imports no
upstream producer. It generates rational directed cyclic block matrices with
strict row gap greater than `9/10`, removes the cyclic corner blocks, factors the
result, and builds a Woodbury border of width twice the block width. Each exact
returned right-hand side is checked by the original matrix residual, rather
than by agreement with a second invocation of the same solve routine.

The extended run retained in
`../runs/20261008T1254Z-reuse-extended/results/certificate.json` passed 80
exact right-hand sides (basis and arbitrary rational probes) and 240 rounded
table/application probes at 24, 48 and 96 fractional bits. Dropping the cyclic
correction failed in all four cases as required. The maximum observed error
was less than 8.37 units of the final rounding grid; the asserted finite bound
was the conservative `64*n^2*2^-P`. This is a control, not a proof of that bound
for every cyclic matrix.

| Cyclic block width | Matrix dimension | Factor multiply/subtracts | Online operations per RHS | Catalogue entries |
|---:|---:|---:|---:|---:|
| 3 | 36 | 610 | 558 | 600 |
| 4 | 40 | 1288 | 832 | 880 |
| 5 | 40 | 2100 | 1050 | 1100 |
| 6 | 42 | 3267 | 1332 | 1386 |

The exact factorization includes sequential banded setup and the small cyclic
border. Online operations include forward/back substitution, the border solve
and the dense border-correction catalogue scan. Four CPU workers were used
under one-thread BLAS/OpenMP limits; the complete extended check took 0.60
seconds. No longer sweep was launched merely to fill cores.

## Reproduction

From the repository root, with Python 3.9 or newer:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B \
  research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/inverse/code/reusable_cyclic.py \
  --workers 4 --profile extended --output /tmp/reuse-extended.json
```

Only this changed interface is exercised. The enormous finite multiplication
primitive, Gaussian coefficients and full machine theorem are not regenerated.
