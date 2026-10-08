# Scoped exclusion: a uniform inverse halo inferred from forward bandwidth

Status: exact rational counterexample family, with independent numerical
Gaussian controls. This rejects the stated uniform halo inference. It does
not reject regular/exception splitting or every packed tensor inverse.

## Exact family with contractive completed maps

Let `S` be the upper shift and

```
D_j=2^(j^2), M=D*(I+S/2)*D^-1.
```

Then `M_(j,j+1)=2^(-2j-2)`, the row diagonal-dominance gap is at least
`3/4`, and

```
(M^-1)_(0,h)=(-1)^h*2^(-h*(h+1)).
```

Every normalized completed map `M^-1/2` is a row-norm contraction: its
absolute inverse row sum is at most `sum_(h>=0)2^(-h*(h+1))<2`.
The tensor product of `d` such normalized maps therefore remains a
contraction. For an impulse displaced by `h` in one axis and by zero in the
others, its output magnitude is exactly `2^(-d-h*(h+1))`.

The full tensor chirp reserve for side `L` is `dL^2` bits. If
`Q=dL^2`, an approximation at target `2^-Q` must keep displacements
`h` of order `L*sqrt(d)`. A uniform halo with constant replicated-volume
condition `dR/L=O(1)` cannot do so. This failure persists with exact
arithmetic, stable completed maps, a constant row gap and strictly bounded
forward bandwidth.

The retained cases are:

| d | L | Q | Tested halo | Necessary halo lower bound |
|---:|---:|---:|---:|---:|
| 4 | 16 | 1024 | 4 | 31 |
| 8 | 32 | 8192 | 4 | 89 |
| 16 | 64 | 65536 | 4 | 255 |
| 32 | 128 | 524288 | 4 | 723 |

The exact normalized coefficient at the first omitted displacement `h=5`
is `2^(-d-30)`, far above the respective target. The table is retained in
`../runs/20261008T1306Z-phase-edge/results/certificate.json`.

## Gaussian manifestation near a true phase edge

At `s=10000`, `t=10004`, `u=2500`, physical index `c=1250` has
`beta_c=-1/2` exactly and `u*theta=1`. The nearest forward path in the
inverse from row `c` to column `c+h` has magnitude
`exp[-pi*h*(h+1)]`; longer opposite-direction paths are vastly smaller.

The independent 190-digit direct principal solves checked `h=6,8,11,16`
at precision targets `Q=512,2048,8192,32768`. In each case, a halo as
large as an entire proposed chirp-limited core still omits a coefficient
far above `2^-Q`. The computed coefficient agrees with the nearest-path
formula to at least 120 relative decimal digits; original-matrix residuals
are below `10^-175`.

These are finite principal Gaussian blocks with remote aliases omitted;
they are numerical controls, not directed interval certificates or complete
cyclic proofs. The exact rational family supplies the scoped mathematical
exclusion. The new global locality lemma independently explains the same
physical radius `Theta(sqrt(Q/(u*theta)))`.

## Reproduction

From the repository root:

```sh
python3 -B research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/inverse/code/phase_edge_obstruction.py \
  --output /tmp/phase-edge-obstruction.json
```

Only the standard library is required. The checker imports no external
producer. Its exact source identity is recorded in the retained certificate.
