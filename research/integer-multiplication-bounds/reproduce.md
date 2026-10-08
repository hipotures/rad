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
Following explicit user steering, new CPU-bound queues target sixteen
processes in aggregate, including an independently reserved reviewer.
Earlier completed eight/twelve/fourteen-worker records retain their actual
historical settings. Exact verification is unchanged and every experiment
has a distinct candidate identity. Matrix workloads use a separately
declared allocation, without nested BLAS oversubscription.

## Current phase, singleton and complex witnesses

Use a fresh output for every command. The producer and independent reports
retain full exact invocation arguments and input hashes:

```bash
python3 -B research/integer-multiplication-bounds/code/downstream_phase_inverse.py --upstream "$REF" --output "$RAD_WORK_ROOT/derived/fresh-phase-inverse.json"
python3 -B research/integer-multiplication-bounds/code/downstream_phase_generator.py --upstream "$REF" --max-s 256 --output "$RAD_WORK_ROOT/derived/fresh-phase-generator.json"
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$MATH_PY" research/integer-multiplication-bounds/code/finite_singleton_certificate.py --reference "$REF" --full 50:23 --small 6 8 --output "$RAD_WORK_ROOT/derived/fresh-singleton-transfer.json"
python3 -B research/integer-multiplication-bounds/code/finite_phase_composition.py --upstream "$REF" --motif-certificate research/integer-multiplication-bounds/runs/20261007T2343Z-asymmetric-motifs-v2/results/certificate.json --phase-certificate research/integer-multiplication-bounds/runs/20261007T234812Z-downstream-phase-assembly-cutoffs/results/certificate.json --promoted-certificate research/integer-multiplication-bounds/runs/20261008T000730Z-finite-singleton-transfer/results/certificate.json --output "$RAD_WORK_ROOT/derived/fresh-phase-composition.json"
python3 -B research/integer-multiplication-bounds/code/finite_packed_composition.py --upstream "$REF" --phase-composition research/integer-multiplication-bounds/runs/20261008T001933Z-singleton-phase-composition/results/certificate.json --output "$RAD_WORK_ROOT/derived/fresh-packed-composition.json"
python3 -B research/integer-multiplication-bounds/code/downstream_complex_circuit.py --upstream "$REF" --h 8 --all-basis --output "$RAD_WORK_ROOT/derived/fresh-complex-basis.json"
python3 -B research/integer-multiplication-bounds/code/downstream_complex_certificate.py --upstream "$REF" --h 8 50 --global-exchange-h8 --output "$RAD_WORK_ROOT/derived/fresh-complex-sharing.json"
python3 -B research/integer-multiplication-bounds/code/downstream_complex_assembly.py --upstream "$REF" --bit-certificate research/integer-multiplication-bounds/runs/20261008T001933Z-singleton-phase-composition/results/certificate.json --complex-certificate "$RAD_WORK_ROOT/derived/fresh-complex-sharing.json" --output "$RAD_WORK_ROOT/derived/fresh-complex-assembly.json"
python3 -B research/integer-multiplication-bounds/code/review_complex_frames.py --h 8 10 12 --output "$RAD_WORK_ROOT/derived/fresh-complex-frames.json"
python3 -B research/integer-multiplication-bounds/code/review_complex_boundaries.py --output "$RAD_WORK_ROOT/derived/fresh-complex-boundaries.json"
python3 -B research/integer-multiplication-bounds/code/review_complex_assembly.py --certificate "$RAD_WORK_ROOT/derived/fresh-complex-assembly.json" --output "$RAD_WORK_ROOT/derived/fresh-complex-review.json"
```

The original shared-complex composition uses the independently promoted R485360
bit primitive and R629617 shared complex primitive. Full h50 finite maps,
frames and physical transitions, small complete dirty shears and bank
exchanges, all-size transfer arguments, exact parameter margins and 680
stopped decaying recurrences passed. The logarithmic parameter cutoff is
6640328716877726785; separate eventual prime, recurrence and retained
machine-interface thresholds remain. These commands regenerate finite
certificates and arithmetic audits, not a complete multiplication machine.

The newer independently promoted nonuniform R485237 bit graph is composed
by a thin adapter without repeating any complete finite graph. Both its
uncached independent finite replay and its independently re-enclosed
arithmetic pass. Reproduce this old-interface checkpoint with fresh outputs:

```bash
python3 -B research/integer-multiplication-bounds/code/downstream_promoted_complex_composition.py --upstream "$REF" --candidate research/integer-multiplication-bounds/runs/20261008T005350Z-review-singleton-positions/results/candidate-input.json --promotion-review research/integer-multiplication-bounds/runs/20261008T005350Z-review-singleton-positions/results/certificate.json --complex-certificate research/integer-multiplication-bounds/runs/20261008T003305Z-downstream-complex-sharing/results/certificate.json --previous-assembly research/integer-multiplication-bounds/runs/20261008T003550Z-downstream-complex-assembly/results/certificate.json --output "$RAD_WORK_ROOT/derived/fresh-promoted-composition.json"
```

This gives kappa 12053467103858103170301/(125*10^37), with common
logarithmic parameter cutoff 6637094462284810001 and the same separate
eventual source/absorption obligations. Full commands for the independent
promotion and refinement audits are retained in their run protocols.

## Useful computational throughput

The completed fifty-candidate benchmark is indexed in
[the throughput report](reports/computational-throughput.md). Its original
source keeps the historical twelve-worker allocation. Subsequent targeted
queues use `finite_singleton_neighborhood.py` with a sixteen-worker maximum.
Choose fresh run locations and explicitly recorded deadlines:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$MATH_PY" research/integer-multiplication-bounds/code/finite_singleton_neighborhood.py --help
python3 -B research/integer-multiplication-bounds/code/fast_frame_envelope.py --reference "$REF" --h 8 12 --output "$RAD_WORK_ROOT/derived/fresh-envelope-equality.json"
```

The initial cache controls compare complete cached/uncached verifier
results on two different small vectors. All large global map/frame/flow
checks execute afresh. Candidate IDs are SHA256 of canonical JSON containing
the ground size, base, complete position vector and pinned upstream commit.
Every completed case is immutable; checkpoints are separate atomic updates.
Before adopting the direct envelope constructor, compare every Space field
and target check against the original. A pending optimization is never
treated as a verified research improvement.

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

The h9 fixture calibrates numerical recovery only. Its exact positive
eight-dimensional quotient exists, but the retained count screen has
negative motif deficit; it provides no improved composed bound. The h8
pure-pair rank-seven control uses `--initialization seven-color` and is
independently exact-reconstructed. GPU discovery remains separate from
deterministic acceptance.

## Restore gzip-only row-level certificates

Six full node/choice tables exceed the ordinary readable-result role policy.
Their complete UTF-8 JSON is preserved as gzip evidence, with hashes and
framing checks. Restore them in a fresh clone before commands which consume
these optional finite/negative checkpoints; existing originals are skipped.

```bash
python3 - <<'PYRESTORE'
import gzip
from pathlib import Path
topic = Path('research/integer-multiplication-bounds')
archive = topic / 'evidence/20261008T0058Z-phase-singleton-complex-compact'
for run_id in (
    '20261008T000730Z-finite-adaptive-cores50',
    '20261008T000730Z-finite-adaptive-gap23-cores50',
    '20261008T002145Z-finite-nearend-composition',
    '20261008T002400Z-finite-complement-schedule-small',
    '20261008T002730Z-finite-adaptive-complements50-gap23',
    '20261008T002730Z-finite-adaptive-complements50',
):
    rel = Path('runs') / run_id / 'results/certificate.json'
    target = topic / rel
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(gzip.decompress((archive / (str(rel)+'.gz')).read_bytes()))
PYRESTORE
```

The original-source path in an archive manifest describes the local evidence
source; it does not mean an omitted plain JSON is present in the Git clone.
The gzip copies are complete, without sampling or split payloads.

## Evidence recovery and resume

Completed text logs and row-level JSON are archived under `evidence/`, with
source sizes, SHA256 values, original external locations and gzip checks.
Original local bytes are unchanged. Git preserves reports, compact certificates,
exact source, locks and protocols. Downloaded repositories/PDFs, environments,
GPU NPZ files and binaries are external and separately obtainable/regenerable.
The campaign protocol records the immutable deadline and live-job status;
archived PID/session records do not authorize controlling live processes.

## New compact input and current reviewed composition

Acquire the separate immutable input without modifying the old reference:

```bash
gh repo clone CrocSwap/integer-mult-bounds "$RAD_WORK_ROOT/repos/fresh-compact-reference"
git -C "$RAD_WORK_ROOT/repos/fresh-compact-reference" checkout --detach 6e564879f51ae16f23d392e9e196c605f36d90df
```

The compact producer and independent generic review commands are retained as
argv arrays in runs/20261008T014759Z-downstream-generic-compact473026/protocol.json
and runs/20261008T015019Z-review-compact-generic473026/protocol.json.
Replace only checkout/environment/output paths in a fresh reproduction.
Their complete inputs are the immutable candidate copy and review at
20261008T014255Z-review-singleton-final420, complex producer copy/audit at
20261008T013158Z-review-complex28, existing complete h8 calibration,
and earlier compact assembly. No row sampling is used.

For the full finite bit reproduction use the exact command in
[its independent report](reports/review-singleton-final420.md).
Complex/count reproductions and the unchanged all-even transfer are in
[the h28 report](reports/review-complex28.md). The compact review reports
retain standalone exact address, recurrence and arithmetic invocations.
The original-clock policy remains authoritative. Reproduction after this
campaign uses fresh output locations and must not reinterpret old run clocks.

The fifth checkpoint's complete completed JSON/text evidence is in
`evidence/20261008T0212Z-compact-verified-topic` (93 files) and
`evidence/20261008T0212Z-compact-verified-external` (1178 files).
The external namespace includes complete case-level evaluations, terminal
logs, failed-attempt traces and the stopped earlier telemetry stream.
It excludes live outputs. Each manifest records original byte identities.
Use `tools/archive_workspace.py verify-text --destination <namespace>` to
check copies; to restore an external case, decompress its manifest-indexed
gzip into a fresh work root at the same relative path. A gzip PID/session
record is historical evidence and must never authorize live process control.
