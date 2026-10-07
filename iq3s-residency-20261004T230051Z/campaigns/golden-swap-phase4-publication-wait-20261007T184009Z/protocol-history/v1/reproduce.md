# Planning-package validation and later execution

This package prepares a future experiment. The only executable supplied now
checks the plan and frozen input identities; it does not build, start a server,
create an experimental clock, or run inference.

From the RaD repository root:

```bash
python3 iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase4-publication-wait-20261007T184009Z/code/check_plan.py
```

On the original host, with no concurrent GPU work or headline timing, additionally
verify the tape, initial-state sidecar, parent binary and inspected local source:

```bash
python3 iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase4-publication-wait-20261007T184009Z/code/check_plan.py --local-inputs
```

The optional local check uses recorded paths in the manifest, refuses detected
GPU work, and reads/hashes inputs without modifying them. On another host,
recover inputs and record relocated paths in a new execution manifest; do not
edit the historical input identities. The selected binary tape has no identified
independent backup and cannot be recovered from its hash alone.

The planning validation receipt is [checks/plan-validation.json](checks/plan-validation.json).
It documents the checks actually run, with scope limited to this package. It is
not a successful runtime, safety, overhead, or experiment result.

When the operator requests execution, give the execution agent this instruction:

> Execute GOAL.md in this campaign through all five steps, within its new
> four-hour clock. Preserve the frozen protocol and attempts, implement and
> validate the required instrumentation, run the bounded paired experiment,
> report attribution or the actual blocker, then audit, commit, push and verify.

Use the existing campaign directory, `workspace.json` and `RAD_WORK_ROOT` for
external outputs. Create `runs/<execution-UTC>/` and its protocol/clock before
substantive execution; never use another campaign's writable build/output root.
Resolve paths from the repository root and manifest, not from an arbitrary cwd.

Runtime/build/analysis commands must be authored, identity-checked and tested
in Step 2. Phase 3 reproduction is a reference implementation, not a command
to run this unimplemented Phase 4 instrumentation. Test result regeneration
from retained traces in a fresh namespace; count any matching live smoke or
reproducer toward the three-attempt cap. All raw text publication and final
Git audits follow the root AGENTS.md.
