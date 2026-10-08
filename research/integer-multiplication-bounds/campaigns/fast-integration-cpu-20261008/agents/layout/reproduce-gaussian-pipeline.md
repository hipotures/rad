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

The later complete physical-CRT control freezes the inverse agent's executable
API and both source dependencies. It actually moves arbitrary digit payloads
through its compiled F_u events, repairs and reverse maps:

```bash
cp "$LAYOUT/code/check_full_gaussian_integer_pipeline.py" "$LAYOUT_WORK/producer.py"
cp "$LAYOUT/../inverse/code/compiled_crt_payload_api.py" "$LAYOUT_WORK/"
cp "$LAYOUT/../inverse/code/compiled_crt_pipeline_bankleaf.py" "$LAYOUT_WORK/"
cp "$LAYOUT/../inverse/code/crt_guard_controls.py" "$LAYOUT_WORK/"
python3 "$LAYOUT/code/check_full_pipeline_compiled_crt.py" --final-inverse --producer "$LAYOUT_WORK/producer.py" --crt-api "$LAYOUT_WORK/compiled_crt_payload_api.py" --config "$LAYOUT/configs/full-gaussian-compiled-crt-final-inverse.json" --output "$LAYOUT_WORK/actual-CRT"
```

Use `full-gaussian-compiled-crt-cyclic.json` for the changed actual-CRT cyclic
cut control. The reverse API compiles its forward address template separately
and includes that cost. This program still uses charged reference Gaussian
matrix passes.

The actual joint packed forward stage and its complete multiplier composition
are reproduced separately:

```bash
python3 "$LAYOUT/code/check_joint_packed_forward_stage.py" --workers 2 --config "$LAYOUT/configs/joint-packed-forward-stage.json" --output "$LAYOUT_WORK/joint-forward"
cp "$LAYOUT/code/check_joint_packed_forward_stage.py" "$LAYOUT_WORK/forward.py"
python3 "$LAYOUT/code/check_full_pipeline_packed_forward.py" --producer "$LAYOUT_WORK/producer.py" --forward-stage "$LAYOUT_WORK/forward.py" --config "$LAYOUT/configs/full-pipeline-packed-forward-0.json" --output "$LAYOUT_WORK/packed-forward-integer"
```

The whole multiplier replaces each of its three forward expansions by actual
signed tensor integer products and paired-grid interior assembly. Every
remaining output is explicitly repaired. It preserves a separately charged
periodic reference and retains Gaussian inverse compression as a matrix
reference. Work-grid reserves are generated at sufficient setup precision;
no finite repair fraction is asserted to prove an all-size density estimate.

An optional exact integer child backend accelerates the changed larger 3D
cell family. The dependency is pinned and downloadable:

```bash
python3 -m pip install --only-binary=:all: --no-deps --target "$LAYOUT_WORK/deps" gmpy2==2.3.0
python3 "$LAYOUT/code/check_forward_gaussian_fractional_cells.py" --workers 1 --config "$LAYOUT/configs/forward-three-dimensional-L128-gmp.json" --output "$LAYOUT_WORK/large-GMP-cell"
```

The earlier builtin-child attempt was stopped for execution budget before an
accuracy receipt. Its CPU and resident-memory observation is retained and
does not constitute a numerical failure. Both native integer backends use
exact signed arithmetic; GMP runtime is not a fixed-tape complexity bound.
