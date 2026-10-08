# Reproduce bounded complete Gaussian and integer recovery checks

Run from the RaD repository root. The work root below is ignored. Python 3.10+
and the downloadable pinned mpmath 1.3.0 dependency are sufficient. The retained
receipts were produced with Python 3.14. Respect the coordinator's current
CPU allocation; every worker uses one native thread.

```bash
LAYOUT=research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/layout
LAYOUT_WORK=research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/layout/reproduce-fresh
mkdir -p "$LAYOUT_WORK"
python3 -m pip install --no-deps --target "$LAYOUT_WORK/deps" mpmath==1.3.0
export PYTHONPATH="$LAYOUT_WORK/deps"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 "$LAYOUT/code/check_full_gaussian_integer_pipeline.py" --workers 2 --config "$LAYOUT/configs/full-gaussian-integer-pipeline.json" --output "$LAYOUT_WORK/ordinary"
python3 "$LAYOUT/code/check_full_gaussian_integer_pipeline.py" --workers 2 --config "$LAYOUT/configs/full-gaussian-cyclic-cuts.json" --output "$LAYOUT_WORK/cyclic-cuts"
python3 "$LAYOUT/code/check_source_transform_composition.py" --workers 4 --config "$LAYOUT/configs/source-transform-large-family.json" --output "$LAYOUT_WORK/source-normalization"
```

Each output directory must be fresh. The two complete-pipeline commands
produce four rows each and check 4,728 coefficient positions in each batch.
The ordinary rows compare the recovered carried radix value with Python's
independent product. The cyclic rows instead compare modulo `radix^S-1`,
and actually rerun the suffix convolution with the twist removed. The source
normalization family evaluates eight independent probes per one-dimensional
case with all `S'/J'/D'` scales and both frequency conventions.

For the larger changed families, use `full-gaussian-integer-pipeline-large.json`,
`full-gaussian-cyclic-cuts-large.json` or
`source-transform-unequal-family.json` as the respective configuration.
These cost substantially more CPU and are not required for the bounded initial
reproduction. Their direct source DFT checks explicitly list sampled frequency
indices; their coefficient recovery comparison still checks the entire cube.

Freeze the producer before launching if other work will edit it:

```bash
cp "$LAYOUT/code/check_full_gaussian_integer_pipeline.py" "$LAYOUT_WORK/producer.py"
python3 "$LAYOUT/code/check_full_pipeline_precision_threshold.py" --workers 2 --producer "$LAYOUT_WORK/producer.py" --config "$LAYOUT/configs/full-gaussian-precision-threshold.json" --output "$LAYOUT_WORK/precision-threshold"
```

The matched precision family fixes primes, targets, alpha, input seed, digit
count and reference frequency probes. Only the dyadic work grid changes.
The low-grid rows preserve coefficient recovery failures, while the higher
grids are required to reproduce the ordinary product. This is a finite
precision discriminator; its observed threshold is not an all-size bound.

Historical receipts retain producer hashes. Reconstruct an earlier exact
producer by copying the current pipeline source to a fresh work file and
applying its small reverse patch, for example:

```bash
cp "$LAYOUT/code/check_full_gaussian_integer_pipeline.py" "$LAYOUT_WORK/producer-initial.py"
patch "$LAYOUT_WORK/producer-initial.py" < "$LAYOUT/fixtures/full-pipeline-initial.patch"
sha256sum "$LAYOUT_WORK/producer-initial.py"
```

The expected hash is listed in `configs/gaussian-pipeline-provenance.json`.
The small cyclic batch and pre-cyclic larger family have separate patches.
`fixtures/source-transform-three-images.patch` similarly reconstructs the
source-transform attempt whose fixed three-image setup fails the requested
precision; that failure is meaningful retained evidence.

These commands exercise the complete arithmetic reference composition. The
producer's dense Gaussian passes and finite array layouts do not constitute
a fast fixed-tape kernel implementation. Source-level movement ledgers and
the campaign's independent physical proofs must be interpreted separately.
