# Lean verification in RaD

The breakthrough branch includes a separate Lean workflow at
`.github/workflows/lean.yml` and a package under
`research/integer-mult-breakthrough/formal/`.

The package formalizes the positive-type-mixing obstruction for arbitrary
nonempty finite real matrices: nonnegative entries and row sums at least one
preclude strict contraction of every coordinate of a positive vector. Its
finite-level composition extension, nonnegative-work extension and exact
boundary examples are also kernel-checked.

It does not formalize a new integer-multiplication exponent, concrete moment
roots, source-profile linkage, physical circuit framing or all-size transfer.
See the package README and coverage.json for precise statements and exclusions.

The independent workflow uses an isolated GitHub-hosted Ubuntu runner. It
pins Lean 4.31.0 and Mathlib, builds the actual proofs, requires axiom-audit
output for all listed theorems, and executes deliberate rejection controls.
The only accepted axiom dependencies are Lean's propext, Classical.choice and
Quot.sound. Reports and logs are uploaded even after proof/audit failure.

The existing Python CI and its active verifier registry are unchanged.
No CPU/GPU research service or local workspace is accessed by this workflow.
The installation is branch-local until deliberately integrated elsewhere;
adding the workflow does not configure branch protection or merge any PR.

Publish Lean sources using the narrow tools/lean_archive_audit.py wrapper.
Keep compiled output and downloaded dependencies ignored. See
research/integer-mult-breakthrough/formal/README.md for reproduction commands.
