# Reproduction and resume

The campaign is active. This document will be extended with exercised commands,
exact environments, input identities and finite-witness/transfer checks.

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
