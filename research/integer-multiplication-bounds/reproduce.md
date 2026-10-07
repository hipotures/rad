# Reproduction and resume

The campaign is active. The commands below were exercised for the retained
baseline, exact circuit/analytic witnesses, and numerical calibration.

Prerequisites currently detected: Linux x86_64, Python 3.14.4, Git, GitHub CLI
2.46.0, GCC 15.2.0, and uv 0.12.16. GPUs are optional unless an experiment
specifies otherwise.

The upstream input is obtainable from
<https://github.com/CrocSwap/integer-mult-bounds> at
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`. Use GitHub CLI to acquire it:

```bash
gh repo clone CrocSwap/integer-mult-bounds "$RAD_WORK_ROOT/repos/upstream-reference"
git -C "$RAD_WORK_ROOT/repos/upstream-reference" checkout --detach bcd4ebde8692383539f8a48734e5fbf3a18a32c2
```

Choose a writable task-owned `RAD_WORK_ROOT` before running the commands; on
the campaign host it is recorded in the artifact manifest. Do not reuse another
task's writable directory. The reference checkout is immutable input: modified
experiments use a separate checkout or authored code in RaD. Preserve the
campaign's original clock when resuming; never restart its ten-hour allowance.

## Isolated environments and baseline

Set `REF="$RAD_WORK_ROOT/repos/upstream-reference"` and choose an output path
under the task-owned external work root. From the topic directory:

```bash
uv venv --python 3.14.7 "$RAD_WORK_ROOT/envs/math"
uv pip install --python "$RAD_WORK_ROOT/envs/math/bin/python" -r configs/math-requirements.txt
MATH_PY="$RAD_WORK_ROOT/envs/math/bin/python"
git clone --no-hardlinks "$REF" "$RAD_WORK_ROOT/repos/baseline-validation"
cd "$RAD_WORK_ROOT/repos/baseline-validation"
PYTHONDONTWRITEBYTECODE=1 make verify
```

The clone is a writable regeneration copy; the original input stays unchanged.
All 85 tests and generated certificates/patches passed with clean Git status.
The math environment is needed for controller max flow and independent
SymPy elimination; standard-library-only analytical checkers do not need it.

## Exact finite and analytical witnesses

Return to the RaD checkout root. Replace `$OUT` separately for every attempt.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$MATH_PY" research/integer-multiplication-bounds/code/frame_reuse_positive_control.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$MATH_PY" research/integer-multiplication-bounds/code/frame_reuse_certificate.py --reference "$REF" --output "$OUT"
python3 -B research/integer-multiplication-bounds/code/downstream_gaussian.py --upstream "$REF" --output "$OUT"
python3 -B research/integer-multiplication-bounds/code/downstream_blocked_gaussian.py --output "$OUT"
python3 -B research/integer-multiplication-bounds/code/downstream_parameter_optimum.py --upstream "$REF" --roles 509194 494250 487650 --output "$OUT"
python3 -B research/integer-multiplication-bounds/code/downstream_banded_inverse.py --upstream "$REF" --output "$OUT"
python3 -B research/integer-multiplication-bounds/code/downstream_lu_assembly.py --upstream "$REF" --roles 509194 494250 487650 486200 --output "$OUT"
```

The controller certificate exercises the complete h50 scalar/frame graph and
small arbitrary-dirty-scratch/full-bank exchange checks. Analytical scripts
use rational identities, interval/series bounds and strict parameter margins.
The blocked checker has true Gaussian interval fixtures; its complexity proof
uses the unconditional 2021 integer multiplier, rather than timing Python's
integer implementation. Independent review commands are in the linked reports.
The strongest witness remains conditional on retained upstream interfaces.

For the accepted unequal tensor factors, choose fresh scan/composition
locations (the scan generates full exact circuit/frame checks):

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$MATH_PY" research/integer-multiplication-bounds/code/asymmetric_ground_scan.py --reference "$REF" --h 40 42 44 46 48 52 54 56 58 60 --workers 8 --seconds 1800 --run-dir "$RAD_WORK_ROOT/derived/fresh-ground-scan"
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$MATH_PY" research/integer-multiplication-bounds/code/asymmetric_motif.py --upstream "$REF" --ground-results "$RAD_WORK_ROOT/derived/fresh-ground-scan/summary.json" --output "$OUT"
python3 -B research/integer-multiplication-bounds/code/review_asymmetric_motif.py --certificate "$OUT" --output "$RAD_WORK_ROOT/derived/fresh-asymmetric-review.json"
```

The scan is bounded by this campaign's immutable deadline. A later
independent reproduction must explicitly adapt that deadline in a separate
recorded source revision; it must not silently resume this campaign with a
fresh ten-hour budget. The composition exercises unequal 6/8 and 8/6
dirty-scratch exchanges and exact scoring of all 121 declared pairs.
The independent command's complete arguments are recorded in its protocol.
The `h50,R486200` uniform reference requires the separately retained full
envelope certificate and review.

Thread variables cap each process, while `--workers 8` runs eight independent
single-thread circuit instances. Exact Python fractions, graph traversal and
max flow do not become sixteen-core computations through a BLAS setting.
The campaign computational ceiling was raised from twelve to fourteen CPUs
after measurements and user steering; remaining cores provide operating
headroom. Matrix workloads can use a separately declared allocation.

## Optional GPU discovery

On a compatible NVIDIA/CUDA host:

```bash
uv venv --python 3.14.7 "$RAD_WORK_ROOT/envs/gpu"
uv pip install --python "$RAD_WORK_ROOT/envs/gpu/bin/python" -r configs/gpu-requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$RAD_WORK_ROOT/envs/gpu/bin/python" research/integer-multiplication-bounds/code/gpu_label_search.py --h 8 --rank 14 --negative 0 --signature positive --device 0 --control --seed 109 --steps 20000 --seconds 300 --run-dir "$RAD_WORK_ROOT/derived/fresh-gpu-control"
```

This routine has a CPU derivative control, CPU/GPU equality checks, a 16 GiB
VRAM cap, source hashes, seeds and checkpoints. It is bounded by the immutable
campaign deadline. For future independent runs beyond this campaign, create a
new run/clock in a separate recorded adaptation. Numerical convergence does
not replace exact reconstruction or finite-network/frame/rank transfer.
The h24 discovery probes did not converge; they imply no nonexistence bound.

The new pair-feature branch has an independently checked affine projection
and a perturbed known rank-eight fixture. Its bounded search is reproduced
with fresh directories, for example:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$RAD_WORK_ROOT/envs/gpu/bin/python" research/integer-multiplication-bounds/code/pair_feature_search.py --h 9 --rank 8 --device 0 --seed 109 --noise .05 --iterations 2000 --seconds 180 --output-dir "$RAD_WORK_ROOT/derived/fresh-pair-control"
```

The h9 fixture calibrates numerical recovery only; its degenerate ambient
form is unsuitable for the retained finite motif transfer.

## Evidence recovery and resume

Completed text logs and row-level JSON are archived under `evidence/`, with
source sizes, SHA256 values, original external locations and gzip checks.
Original local bytes are unchanged. Git preserves reports, compact certificates,
exact source, locks and protocols. Downloaded repositories/PDFs, environments,
GPU NPZ files and binaries are external and separately obtainable/regenerable.
The campaign protocol records the immutable deadline and live-job status;
archived PID/session records do not authorize controlling live processes.
