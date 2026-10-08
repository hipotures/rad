# A dimensional halo budget and sequential catalogue interface

Written 2026-10-08, CPU campaign. This is an all-size volume/accounting lemma,
not a numerical multiplication improvement. The underlying Gaussian accuracy,
principal-window inverse and arbitrary coordinate router remain separately
conditional inputs from the pinned historical RaD construction.

## Exact growing-dimensional volume

Let axis i have core side L_i and symmetric halo A_i. Its persistent replicated
tensor volume, relative to the unreplicated box T, is exactly

`V_halo/T = product_i (1+2A_i/L_i)`.

Put `H=sum_i 2A_i/L_i`. For `0<=H<1`, expansion into elementary symmetric
polynomials gives `product_i(1+x_i)<=sum_{k>=0} H^k=1/(1-H)`:
each elementary symmetric sum is bounded by H^k. Thus H<=1/4 gives volume
at most 4T/3, uniformly in the growing dimension. Binary choices
`L_i=2^ceil(log2(8D(A_i+1)))` suffice in D dimensions.

The sole conclusion needed for constant volume is a summable relative halo
budget. The statement that every side is polynomial in precision is insufficient:
fixed `2A_i/L_i=1/4` gives `(5/4)^D`. For D=128 this exceeds 2^40.
Padding all axes independently to the next binary length can give 2^D even
when the unpadded ratio is bounded. Only the currently exposed field may receive
temporary binary padding; removing that padding before the next exposure keeps
temporary volume below twice the persistent volume.

Early cropping is safe for this volume bound only in completed axes. It divides
the volume by the corresponding `(1+2A_i/L_i)`; retaining the other axes' input
halos is an independent correctness obligation.

## A sharper source-halo fit for the historical near-one interface

Suppose `rho=t/s=1+theta<=5/4`, `theta>=1/(4d)` and D<=d. The exact nearest-index
window endpoints for target halo `[kL-A,(k+1)L+A)` are

`ceil((2(kL-A)-1)/(2rho))`,
`ceil((2((k+1)L+A)-1)/(2rho))`.

The difference of these ceilings is at most `ceil((L+2A)/rho)`. Choosing a binary
`L>=8d(A+1)` yields `theta L>=2(A+1)>2A+rho`, so the source window has at most L
indices and can be padded to L. Simultaneously the target halo budget satisfies
`sum_i2A/L<=1/4`; total target volume is at most4T/3.

This improves a sufficient side bound from the historical convenient p^8 to a
side proportional to dA. It changes constants and polynomial local field sizes,
not an asymptotic multiplication exponent by itself. Reduced oversampling
theta<<1/d does not satisfy this source-fit premise; its source fields must have
separately charged persistent halos instead of silently retaining length L.

## Paid sequential factor catalogue

In slab order `[X,J,Y,u]`, a coefficient page P_J can be computed once per axis,
then retained on a work tape while all spectator Y rows in the slab use it.
This avoids redoing setup. Every row still pays its sequential page reads and
rewinds. If the page has E_J precision records and a slab row has L records,
the page traffic is `O(V * max_J(E_J/L))` records, plus a bounded per-X rewind
of the complete catalogue. A page depending on J cannot be reused at another J.

For a banded cyclic or Schur solve with at most `ceil(theta L)+1` wrap blocks,
width w, a sufficient page-size estimate is

`E_J = O(L + (theta L+1)w^2)`.

Hence a bounded `theta w^2` and `w^2/L` give linear page traffic. This is a reuse
lemma; it does not certify the factors' conditioning, construction cost or
cyclic correction. Setup remains constructive and charged as an additive
polynomial in axis length and precision, required to be n^o(1).

## Finite discriminators and limitations

[The independent checker](code/exact_layout_discriminators.py) imports no historical
or public checker. [The compact result](results/initial-discriminators.json) records
four parallel processes with native-thread limits1, seed202610081 through202610084:

- eight exact dimensional budgets through D1024, including persistent crops;
- 1600 fine-field exposure cases and1,509,060 checked output records;
- 3500 catalogue cases, with315,013,501 paid coefficient visits;
- 2200 two-source-tape cyclic splice cases and2,056,224 checked records.

The source-period residue is used explicitly in the splice. With59 spectator
lines, a retained example charges116.019 record movements per payload record
for one alternating source head, versus a bound8 for two cached source tapes.
The source cache extraction is a separate paid full scan.

Changing a fine-field radix from4 to5 requires15 restored records; the stale
radix4 restoration emits12 and is rejected. Complete current-suffix blocks must
be interleaved to retain bit significance. A development run that interleaved
individual records reversed the exposed bits; this was repaired before promoting
the ordered exposure check. Another development run completed all branches but
failed compact serialization of a23928-bit rational numerator; the published
run retains exact comparisons internally and publishes bit lengths plus floats.
Neither failed attempt is an algorithmic counterexample to an external source.

These are finite combinatorial controls backed by the stated all-size accounting.
They do not simulate true Gaussian arithmetic, certify a full tape machine or
provide external human review.

## Reproduction and provenance

From the repository root, choose a fresh ignored output directory:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B \
  research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/layout/code/exact_layout_discriminators.py \
  --workers 4 --output research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/layout/fresh-discriminators
```

Python3.14.4, standard library. Slowest branch12.856seconds; other branches below
0.3seconds. Source SHA256 is in the result. Finite scheduling checks independently
reimplement ideas also used by Swapnil Jain's fine-field lemma at public commit
`c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007`
([source](https://github.com/Swapnil-jain/integer-mult-kappa/blob/c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007/notes/fine-field-lemma.tex)).
Historical volume, principal locality and catalogue interfaces are from RaD
commit `6b32837aee0561af85e4efaca21af07b9f2749d2`, reports
`review-bulk-resampling.md`, `review-arbitrary-routing.md` and
`downstream-phase-cell-inverse.md`. The summable anisotropic budget and sharper
source-halo fit here are the campaign's derived refinements; worldwide novelty
is not established.
