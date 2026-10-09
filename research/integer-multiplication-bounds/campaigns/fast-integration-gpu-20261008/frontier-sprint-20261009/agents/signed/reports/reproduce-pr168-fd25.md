# Reproduce the fd25adb body, literal sinks and bounded negative batches

Run from the sprint root using Python 3.14.4 (the tested version), GitHub CLI,
and the standard library. The coordinator owns Git and source acquisition.
Each output directory must be new. Set OMP, MKL and OpenBLAS thread counts to
one before the four-worker batches. Source snapshots must remain unchanged;
the scripts disable bytecode writes and reject Python's `-O` mode.

If the immutable source snapshot is missing, recover the public source into
ignored task-owned input storage:

```bash
mkdir -p work/signed/recovered-inputs work/signed/recovered-fd25
gh api repos/eumemic/integer-mult-bounds/tarball/fd25adb7fbaa12ee761d02c733c54d1d2a7687ee \
  > work/signed/recovered-inputs/fd25adb.tar.gz
tar -xzf work/signed/recovered-inputs/fd25adb.tar.gz \
  --strip-components=1 -C work/signed/recovered-fd25
```

Use that recovered directory for `--source` below. Its consumed-file hashes
must match [the recovery manifest](../configs/pr168-fd25-recovery.json), and
the native producer verifies module, inherited source and matching pins.
The previously tested source location is shown here for clarity:

```bash
FD_SOURCE=work/frontier/pr168-fd25adb/extracted/eumemic-integer-mult-bounds-fd25adb
FD_BODY=work/signed/fd25-body-reproduce-fresh
FD_SINKS=work/signed/fd25-sinks-reproduce-fresh
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1

python3 agents/signed/code/regenerate_frontier_complex.py \
  --source "$FD_SOURCE" \
  --source-head fd25adb7fbaa12ee761d02c733c54d1d2a7687ee \
  --output-dir "$FD_BODY"
python3 agents/signed/code/check_pr165_signed_control.py \
  --export "$FD_BODY" \
  --exact-core agents/baseline/code/exact_aliased_core.py \
  --output "$FD_BODY/signed-audit.json"
python3 agents/signed/code/audit_scalar_bounds.py \
  --export "$FD_BODY" \
  --exact-core agents/baseline/code/exact_aliased_core.py \
  --output "$FD_BODY/scalar-coefficient-audit.json"
python3 agents/signed/code/export_terminal_sinks.py \
  --source "$FD_SOURCE" --body-export "$FD_BODY" --output "$FD_SINKS"
python3 agents/signed/code/check_terminal_sinks_exact.py \
  --body-export "$FD_BODY" --sink-export "$FD_SINKS" \
  --exact-core agents/baseline/code/exact_aliased_core.py \
  --output "$FD_SINKS/exact-signed-audit.json"
python3 agents/signed/code/enclose_terminal_sinks.py \
  --body-export "$FD_BODY" --export "$FD_SINKS" \
  --interval-code agents/signed/code/interval_moments.py \
  --saving 655831073/1000000000000 --saving 655861417/1000000000000 \
  --output "$FD_SINKS/exact-moment.json"
```

Expected exact result: c=20,686, q=3,157, carriers=10,237, M=32,972,
logical R=13,606, body physical R=11,296, actual sink physical R=11,254,
42 sinks, 2,310 aliases, W=13,894, rank=915,684 and deficit=1,320.
Both scalar orientations and every retained inverse pass. Both saving trials
are rejected. The rigorous root is strictly between 649333576 and 649333577
over 10^12. Full native source/header/module checks and native sink geometry
are run; independent reflected geometry is a separate geometry-lane command.

The local synthesis batch uses the retained PR162 alias/frame constructor
from obtainable PR165 head `7518fed2688baf25c7c32bae32674f3334b517da`. Recover
that public revision through `gh api repos/chafreaky/integer-mult-bounds/tarball/<head>`
if needed, and use its retained helper below. All helper and placement source
hashes are recorded in the original batch protocol and recovery manifest.
Readonly placement APIs are durable files in the separate placement lane.

```bash
python3 agents/signed/code/screen_pr168_fd25adb_local.py \
  --source "$FD_SOURCE" --export "$FD_BODY" \
  --plan work/frontier/pr165-7518fed/extracted/chafreaky-integer-mult-bounds-7518fed/research/paired-cube-plateau-162/references/pr162/make_plan.py \
  --exact-core agents/baseline/code/exact_aliased_core.py \
  --interval-code agents/signed/code/interval_moments.py \
  --placement-code agents/placement/code \
  --output work/signed/fd25-local-reproduce-fresh --workers 4 \
  --trial-saving 655831073/1000000000000
python3 agents/signed/code/screen_terminal_sink_candidates.py \
  --source "$FD_SOURCE" --body-export "$FD_BODY" \
  --output work/signed/fd25-obstruction-reproduce-fresh --workers 4
```

The original local batch deliberately retains its historical fd25 trial;
using the newer PR176 trial is a separate attempt with its own output ID.
The unchanged fresh-policy discovery root is approximately 0.0006480314713,
and the best face0 local change approximately 0.0006480590649; neither equals
the optimized public control. All six preliminary face0 sink candidates are
preserved in a complete eligibility census. The unchanged sink control
passes, while first/last/all-six additions fail actual 19-to-18 target-frame
retreats. Do not treat a failed sink set as a supplier.

This full sequence was exercised on the original frozen inputs, with every
large event array retained completely as gzip evidence. Reacquisition from
the public remote is a recovery instruction, not a claim of an additional
network download during this final handoff. Runtime bytes are preserved in
the archive; deterministic mathematical output hashes are checked separately.
