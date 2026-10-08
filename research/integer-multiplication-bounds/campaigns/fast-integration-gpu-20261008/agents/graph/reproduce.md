# Graph search reproduction

Acquire PR36 at its pinned revision with the GitHub CLI, extract it into
external storage, and keep it read-only. The authored wrappers take its
root explicitly; they do not depend on machine-local import state.

All runs set `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`,
`MKL_NUM_THREADS=1`, `VECLIB_MAXIMUM_THREADS=1` and
`NUMEXPR_NUM_THREADS=1`. Eight process workers include their sequential
native C++ children in the same eight-slot allocation.

Full binary DAGs, labels and logs remain external; compact outcomes and
selected changed witness identities live under `results/`. Exact command
and source hashes are recorded in each run's protocol.

The eventual common rational bases, finite alphabets and copied-stream
tape interfaces remain mathematical transfer dependencies.
