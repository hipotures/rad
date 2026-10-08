# Reproduce the transfer discriminators

Use Python 3.11 or newer and the standard library only. From the repository
root, the bounded verification runs without creating evidence files:

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/coupled_moments.py \
  --workers 1 --cases 8
```

The first parallel experiment can be regenerated with a fresh output path:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B \
  research/integer-mult-breakthrough/code/transfers/coupled_moments.py \
  --workers 4 --cases 96 \
  --output research/integer-mult-breakthrough/work/transfers/REPLACE-FRESH-ID/results/full.json
```

The fixture is self-contained and includes every complete child multiplicity.
No local binary, downloaded checkout, model, private configuration or external
dataset is required to replay this arithmetic. Source provenance is retained
in the fixture. The original finite physical constructions are not regenerated
by this reproduction.

Expected checks: exact rank mass, deficit, maximum child and strict recursive
size decrease; outward rational moments exceeding one at `1e-4`; independent
root bracket replay; no strict positive type potential for retained complete
row moments; reducible and varying-level controls; and rejection of invalid
cost/potential hypotheses. Deleting high-rank complete payloads and substituting
nonlinear CRT with the known-coordinate router must produce the retained
fictitious-pass negatives. A generated JSON records exact enclosures, seeds,
worker allocation, source/fixture hashes and elapsed time.

All outputs must use fresh paths. Important completed evidence is published
through the repository's gzip archive path, with originals left unchanged.

## Deferred normalization

The exact finite-field semantic and capacity controls need no external inputs:

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/deferred_normalization.py \
  --workers 1 --cases 8
```

To regenerate the initial four-family run, use a fresh output path:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B \
  research/integer-mult-breakthrough/code/transfers/deferred_normalization.py \
  --workers 4 --cases 96 \
  --output research/integer-mult-breakthrough/work/transfers/REPLACE-FRESH-ID/results/full.json
```

Expected results include direct-convolution recovery, changed spectra after
nontrivial carries, a lawful redundant linear domain, explicit digit-width
charges for carry-free base changes, the length-four alias witness
`625 != 370`, its paid length-eight repair, and retained binomial coefficient
width measurements. This auxiliary finite model does not verify the actual
Gaussian-dyadic algorithm or an improved asymptotic exponent.
