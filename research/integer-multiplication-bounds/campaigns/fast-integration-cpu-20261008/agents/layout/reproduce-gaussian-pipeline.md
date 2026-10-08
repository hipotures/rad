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

The earlier executed API contained one trailing space in its inverse-check
line, subsequently removed without changing behavior. To reproduce its exact
hash, restore that byte in an ignored copied API using
`code/restore_crt_api_trailing_space.py --path <copied-api> --expected-sha256
<receipt-api-sha256>`. For the initial input-only API, first apply
`fixtures/compiled-crt-api-before-inverse.patch`, then restore the byte. The
patch remains free of trailing whitespace; the helper verifies exact bytes.

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

The repaired rank-two oracle can be validated against the previous full-cell
sum before executing the complete L128 cell. Only the reference sum changes;
the entire packed input and integer products still run:

```bash
cp "$LAYOUT/code/check_forward_gaussian_fractional_cells.py" "$LAYOUT_WORK/forward-current.py"
cp "$LAYOUT_WORK/forward-current.py" "$LAYOUT_WORK/forward-legacy.py"
patch "$LAYOUT_WORK/forward-legacy.py" < "$LAYOUT/fixtures/forward-before-separable-oracle.patch"
python3 "$LAYOUT/code/check_forward_separable_oracle_repair.py" --producer "$LAYOUT_WORK/forward-current.py" --legacy "$LAYOUT_WORK/forward-legacy.py" --config "$LAYOUT/configs/forward-three-dimensional-L128-gmp.json" --output "$LAYOUT_WORK/separable-oracle-repair"
```

Global cyclic inverse reference controls retain the entire cyclic border and
charge every omitted alias through an analytic Gaussian tail. Reproduce the
bounded first family with:

```bash
cp "$LAYOUT/../inverse/code/cyclic_gaussian_reference.py" "$LAYOUT_WORK/cyclic_gaussian_reference.py"
cp "$LAYOUT/../inverse/code/regular_laurent_kernel.py" "$LAYOUT_WORK/regular_laurent_kernel.py"
python3 "$LAYOUT/code/check_cyclic_inverse_reference_family.py" --api "$LAYOUT_WORK/cyclic_gaussian_reference.py" --config "$LAYOUT/configs/cyclic-inverse-reference-family.json" --output "$LAYOUT_WORK/global-cyclic-inverse"
python3 "$LAYOUT/code/check_packed_laurent_inverse.py" --cyclic-api "$LAYOUT_WORK/cyclic_gaussian_reference.py" --laurent-api "$LAYOUT_WORK/regular_laurent_kernel.py" --config "$LAYOUT/configs/packed-laurent-inverse-repaired-and-radius.json" --output "$LAYOUT_WORK/packed-local-inverse"
```

The packed inverse command checks every core output against global physical
inverse solutions. It also retains a matched insufficient-radius failure.
The corrected internal anchor avoids untreated source-period cuts. Current
source freezes the input/output diagonal words and applies them by integer
dyadic products; the earliest retained cells used high-precision numerical
outer diagonal application after the same four exact packed products.
`packed-laurent-before-origin-guard.patch` and
`packed-laurent-before-tensor-norm.patch` reconstruct those exact producer
versions. Derived receipts explicitly correct their slightly omitted tensor
operator norm factor without altering the immutable raw receipts.

Use `cyclic-inverse-large-reference-family.json` or
`cyclic-inverse-strict-theta-reference-family.json` for the changed larger
global controls, and `packed-laurent-large-period-precision.json` for the
larger genuine packed inverse family. These controls remain numerical rather
than directed interval proofs. Bare `N^-1` does not include `J'`'s factor
one half or the full source compression's `D'`.

The complete multiplier with both directions supplied by genuine local cells
uses the same frozen sources and a separately charged repair reference:

```bash
python3 "$LAYOUT/code/check_full_pipeline_packed_both.py" --producer "$LAYOUT_WORK/producer.py" --forward-stage "$LAYOUT_WORK/forward.py" --cyclic-api "$LAYOUT_WORK/cyclic_gaussian_reference.py" --laurent-api "$LAYOUT_WORK/regular_laurent_kernel.py" --config "$LAYOUT/configs/full-pipeline-packed-both.json" --output "$LAYOUT_WORK/packed-both-integer"
python3 "$LAYOUT/code/check_tensor_catalogue_tapes.py" --config "$LAYOUT/configs/tensor-catalogue-tape-controls.json" --output "$LAYOUT_WORK/tensor-catalogue-tapes"
```

The first command checks every source coefficient after actual packed forward
and inverse cells, Gaussian selectors/normalization, synthetic FFT, suffix
twists, polynomial-record multiplication and final integer recovery. Every
unselected Gaussian output uses a charged reference repair. The second is an
exact independent word-head movement and rounded-prefix discriminator for
the growing tensor catalogue construction, not an arithmetic benchmark.

`full-pipeline-packed-both-cyclic-cut.json`,
`full-pipeline-packed-both-radius4.json` and
`full-pipeline-packed-both-higher-digits-radius4.json` preserve changed queued
whole-pipeline controls. A minimal one-CPU serial runner is
`code/run_scientific_serial_queue.py`; its JSON specifies complete argv arrays
and it retains each return status/log before starting the next distinct job.
Commands containing ignored frozen copies require those copies to be made
first. Do not name the runner copy `queue.py`, which shadows Python's standard
library queue module used by the forward producer.

For the further actual CRT integration, prepend the independent driver and
provide the already frozen physical API:

```bash
python3 "$LAYOUT/code/check_full_packed_both_actual_crt.py" --packed-wrapper "$LAYOUT/code/check_full_pipeline_packed_both.py" --crt-api "$LAYOUT_WORK/compiled_crt_payload_api.py" --producer "$LAYOUT_WORK/producer.py" --forward-stage "$LAYOUT_WORK/forward.py" --cyclic-api "$LAYOUT_WORK/cyclic_gaussian_reference.py" --laurent-api "$LAYOUT_WORK/regular_laurent_kernel.py" --config "$LAYOUT/configs/full-pipeline-packed-both.json" --output "$LAYOUT_WORK/packed-both-actual-CRT"
```

This performs actual CRT input and final inverse programs and pays the named
binary/source field conversions. A two-prime case has ordinary top nodes;
actual multi-target F_u execution is documented by the separate earlier
three-prime controls. Pending actual-CRT integration is not claimed as a
completed reproduction until its receipt is retained.

## Completed actual CRT plus packed-both composition

The ordinary and cyclic-cut configurations now pass both actual input CRT
programs, every full arithmetic coefficient and the actual inverse program.
Their results are `results/full-pipeline-packed-both-actual-crt-ordinary.json`
and `results/full-pipeline-packed-both-actual-crt-cyclic.json`. These are
two-prime ordinary top maps; they do not establish F_u execution.

The all-address normalized-H circuit has a separate conditional report at
`hadamard-routing-conditional-lemma.md`, standard-library source at
`code/check_hadamard_coordinate_permutation.py`, pinned configuration and
`results/hadamard-coordinate-precision.json`. Native C-only mask exposure
remains unproved; the exact finite circuit does not imply a new exponent.

Matched whole packed/actual-CRT precision attempts use
`code/check_packed_pipeline_precision_observation.py`, which retains producer
coefficient failures separately from component eligibility assertions.
A failed coefficient producer does not reach the final actual CRT inverse.
Only completed receipts are published as measured evidence.
