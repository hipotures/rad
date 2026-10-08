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
The campaign protocol records the original start, historical deadline,
explicit user-authorized extension to2026-10-08 10:00:00 UTC and live-job status;
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

## New structural interfaces and targeted reproduction

The independently reviewed arbitrary-source router, linear semantic guard
and bulk principal-window resampling have separate proof reports and
completed run protocols. They do not rerun the accepted bit/complex
baseline. The bulk review distinguishes exact selector/tape payload
controls from the analytic Gaussian error proof. Restore the complete
finite candidate files from the sixth external archive if reproducing
searches, rather than treating compact rankings as the original inputs.

Run the new standalone phase and tape discriminators into fresh outputs:

```bash
python3 -B research/integer-multiplication-bounds/code/alternating_quadratic_phase.py --output "$RAD_WORK_ROOT/derived/fresh-alternating-phase/certificate.json"
python3 -B research/integer-multiplication-bounds/code/quadratic_phase_counter.py --output "$RAD_WORK_ROOT/derived/fresh-quadratic-counter/certificate.json"
python3 -B research/integer-multiplication-bounds/code/review_bulk_resampling.py --output "$RAD_WORK_ROOT/derived/fresh-bulk-stream/certificate.json"
```

The first two controls were exercised completely during the campaign:
219,024 exact phase entries and457,412 complete counter addresses.
They support the new alternating-phase hypothesis only; the complete
odd-ground network and tape/guard transfer remain separate obligations.
The third command is the independent bulk stream control exercised
over84,824 complete output records. Its accepted all-size analytic
scope and limitations are in reports/review-bulk-resampling.md.

For final exponent arithmetic use the exact argv and input identities
in the current composition and independent review protocols. Keep the
old compact and balanced checkpoints under their original interfaces.
Parameter cutoffs are exact numeric obligations, while prime existence,
strict logarithmic absorption and unchanged full-machine interfaces
still have separate eventual thresholds.

The sixth milestone's complete archives are
`evidence/20261008T0330Z-structural-transfer-topic` (136 files) and
`evidence/20261008T0322Z-structural-transfer-external` (2073 files).
The terminal six-role refinement adds
`evidence/20261008T0339Z-refinement-topic` (12 files) and
`evidence/20261008T0339Z-refinement-external` (455 files).
These preserve full candidate definitions, completed successes, initial
import failures and meaningful negatives. Four large candidate-protocol
tables, the new phase case table and the final refinement candidate
protocol are gzip-only. Restore a needed plain copy from its exact
manifest-relative path; existing originals remain unchanged.

```bash
python3 - <<'PYRESTORE'
import gzip
from pathlib import Path
topic = Path('research/integer-multiplication-bounds')
groups = {
    '20261008T0330Z-structural-transfer-topic': [
        'runs/20261008T020031Z-finite-pair-block-orders/results/candidate-protocol.json',
        'runs/20261008T021514Z-finite-retained-schedule-repair/results/candidate-protocol.json',
        'runs/20261008T022630Z-finite-cutoff-cohort/results/candidate-protocol.json',
        'runs/20261008T024520Z-finite-association-repair/results/candidate-protocol.json',
        'runs/20261008T030740Z-alternating-quadratic-phase/results/certificate.json',
    ],
    '20261008T0339Z-refinement-topic': [
        'runs/20261008T030610Z-finite-cutoff2-refinement/results/candidate-protocol.json',
    ],
}
for archive, relative_paths in groups.items():
    for rel in relative_paths:
        target = topic / rel
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(gzip.decompress((topic / 'evidence' / archive / (rel+'.gz')).read_bytes()))
PYRESTORE
```

The current R472879 follow-up uses the unchanged independent assembly
checker. Its full finite promotion and fresh arithmetic commands are in
runs/20261008T032418Z-review-refinement472879/protocol.json and
runs/20261008T033303Z-review-semantic-bulk472879/protocol.json.
The bounded new algebra and counter reproduction paths were actually
exercised; accepted older baseline checks were not repeated.

The independent alternating primitive control is also archived intact in
`evidence/20261008T0343Z-alternating-primitive-topic` (3 files). Its fresh
source and written review distinguish the actual fK layout, selected-only
word exchanges and upstream bit-volume convention from the initial
producer algebra. It does not certify a new complete odd-ground network.


## Seventh checkpoint: odd h51 and completed structural discriminators

The new h51 witness is reproduced with the exact commands and input hashes
in `runs/20261008T041200Z-review-odd51/protocol.json` and
`runs/20261008T043000Z-review-odd51-bulk/protocol.json`. Those targeted new
finite and assembly paths were exercised completely; previously accepted
h28 and analytic baselines were not replayed. The complete new complex
controller review has its own protocol under
`runs/20261008T0415Z-review-complex-controller/`.

Full completed external text is in
`evidence/20261008T0453Z-odd-network-external` (1401 files), and full topic
text is in `evidence/20261008T0454Z-odd-network-topic` (111 files). These
include all original 309-case and 420-case candidate definitions and
certificates, memory failures and repaired/partial outcomes. Each archive
has an `archive-manifest.jsonl.gz` listing original paths, complete sizes,
and hashes. Original files are unchanged. Live workers, telemetry and
new incomplete controls are excluded. Completed process IDs are historical
records and cannot authorize control of live processes.

The two large row-level tables listed below are gzip-only. Restore a
needed table from the topic archive, then use its original protocol.

```bash
python3 - <<'PYRESTORE'
import gzip
from pathlib import Path
topic = Path('research/integer-multiplication-bounds')
archive = topic / 'evidence/20261008T0454Z-odd-network-topic'
paths = [
    'runs/20261008T040600Z-finite-clone-gates-small/results/certificate.json',
    'runs/20261008T043500Z-lowrank-bruhat-bound/results/certificate.json',
]
for rel in paths:
    target = topic / rel
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(gzip.decompress((archive / (rel+'.gz')).read_bytes()))
PYRESTORE
```

For any external archived case, decompress its manifest-relative path into
a fresh execution directory and compare the declared original SHA256.
The new contiguous Bruhat recurrence controls are research evidence with a
separate full transfer review; they are not part of the seventh checkpoint's
accepted uniform h51 multiplication witness.


## Eighth checkpoint: full middle calls and explicit clone promotion

The targeted new root finite and complete arithmetic commands were exercised
fully, with original input/source hashes retained in:

- `runs/20261008T051931Z-review-explicit-clone-repair/protocol.json`
- `runs/20261008T052819Z-review-axis-assembly/protocol.json`
- `runs/20261008T054255Z-review-uncapped-assembly/protocol.json`

Use the pinned mathematical environment and a fresh output path. Exact
long fractions require the explicitly recorded `PYTHONINTMAXSTRDIGITS=0`.
The full-middle reviewer checks the p^2600 row reservoir; the earlier
capped checker is preserved separately and uses p^100. Accepted baselines
were not repeated. All conditional and eventual thresholds are stated in
[the current composition](reports/uncapped-middle-composition.md).

Completed text is archived under `evidence/20261008T0541Z-axis-clone-external`
(986 files), `evidence/20261008T0541Z-axis-clone-topic` (101 files), the two
`20261008T0548Z-uncapped-assembly-*` supplements, and
`evidence/20261008T0550Z-axis-clone-nested-external` (26 files). Original
paths, sizes and SHA256 values are indexed by complete gzip manifests.
Every copy passed `verify-text --check-originals`; originals were unchanged.
The external archive was published in its own scoped commit because the
combined source/evidence would exceed the ordinary20MiB commit budget.
Each complete source remains intact; no payload was split.

Restore a required gzip-only topic table before invoking its saved command:

```bash
python3 - <<'PYRESTORE'
import gzip
from pathlib import Path
topic = Path('research/integer-multiplication-bounds')
archive = topic / 'evidence/20261008T0541Z-axis-clone-topic'
paths = [
    'runs/20261008T050900Z-finite-clone-recovered51/results/certificate.json',
    'runs/20261008T051000Z-finite-clone-plan-export/results/selected-links.json',
    'runs/20261008T051200Z-finite-clone-recovered-cohort/results/terminal-summary.json',
    'runs/20261008T052800Z-finite-clone-descendant-small/results/certificate.json',
]
for rel in paths:
    target = topic / rel
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(gzip.decompress((archive / (rel+'.gz')).read_bytes()))
PYRESTORE
```

The full delayed-frame producer certificate and selected-link artifact are
external archive members under their original `derived/finite/052900` and
`053400` run names, including the complete UTC prefix. They are preserved
new candidates, not finite inputs to the accepted full-middle composition.
Restore external members into a fresh task-owned execution directory and
compare the manifest's original hash. Live workers and telemetry are
excluded; archived PID values are historical evidence only.
