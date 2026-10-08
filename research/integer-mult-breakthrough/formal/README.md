# Formal positive-mixing lemmas

This is a real Lean 4.31.0 / Mathlib proof package, not a wrapper around saved
Python PASS flags. `coverage.json` lists every exported theorem and its scope.
GitHub Actions compiles the proofs and audits their transitive axioms.

## Mathematical coverage

For any nonempty finite index type and a real matrix M with nonnegative
entries and every row sum at least one, there is no strictly positive vector
c for which M c < c in every coordinate. The proof selects a smallest
coordinate; it does not assume irreducibility or a positive eigenvector.

The package also proves that the obstruction survives any finite list of
such levels and any additional nonnegative work. This is universal over
finite sizes, matrices, positive vectors and lists, rather than a finite
sample of numerical matrices. Exact boundary witnesses show why row mass,
nonnegative entries and positive potentials matter.

The formalized argument is the named lemma and finite-level extension in
`../reports/transfers/positive-type-mixing.md` at commit
`d1ef326f0fc8b6f888887d8132e0854d3d92b5b2`. Subsequent research claims do not
silently become part of this formalization.

**Not covered:** concrete moment/root enclosures, their linkage to a physical
network, dirty-memory semantics, fixed-tape transfer, any new kappa, or an
all-size integer-multiplication theorem. In particular, this package alone
does not prove that either frozen native profile has its root below 1e-4.
Python continues to replay the separate exact arithmetic certificates.

## Reproduce

With elan installed, from this directory:

```sh
lake exe cache get Mathlib/Data/Finset/Max.lean Mathlib/Data/Fintype/Basic.lean Mathlib/Data/Real/Basic.lean Mathlib/Algebra/Order/BigOperators/Ring/Finset.lean Mathlib/Tactic/NormNum.lean Mathlib/Tactic/FinCases.lean Mathlib/Algebra/BigOperators/Fin.lean
python3 verify.py --self-test
python3 verify.py
```

`lean-toolchain`, `lakefile.toml` and `lake-manifest.json` pin Lean, Mathlib
and every transitive source dependency. Do not run `lake update` as part of
normal verification. The verifier checks actual dependency Git revisions.

A fresh build is followed by `#check` and `#print axioms` for every listed
theorem. Only `propext`, `Classical.choice` and `Quot.sound` are accepted.
Missing theorem output, any other axiom, proof placeholders and native
proof-evaluation shortcuts are rejected. Build output and actual theorem
types/axiom lists are preserved in the Actions artifact.

Negative controls check that a false equality is rejected, a missing proof
fails, and a deliberately injected custom axiom is rejected by the auditor.
These temporary rejection examples are not imported by the proof library.

## Continuous verification

`.github/workflows/lean.yml` is a separate, path-filtered workflow. It does
not mutate `tools/ci_checks.json`, run on a research server, or trigger a
Python-version matrix for Lean. The original Python workflow is unchanged.
Pushes affecting the formal package run it automatically. Manual dispatch
through GitHub requires the workflow on the default branch. Artifacts last
14 days; permanent scientific evidence still belongs in version control.

The file and axiom audits are safeguards, not a security sandbox or an
independent proof checker outside Lean's trusted computing base. Mathlib
build caches are retrieved from the pinned dependency's official cache;
this package's proofs are built on the fresh runner.

## Attribution

The research note and its authors retain their attribution. Formalization
and CI integration were prepared with OpenAI assistance. The argument is a
standard minimum-coordinate comparison; no novelty claim is made. Lean and
Mathlib contributors retain their original licenses and credit.
