# Bounded actual rank-search and corruption verification

Status: PASS BOUNDED COMPLETE RANK SEARCH CERTIFICATES. The reusable standard-library entrypoint replays both complete n=2 graph/full binary searches, both complete Gaussian-residue projective searches, and both unquotiented/projective F3 controls. It also checks field axioms, all full-domain metric triangles, complete dirty-helper columns, strict capacity, and five matched corruption controls. It passed in approximately 0.77 seconds.

Run `python3 -B research/integer-mult-breakthrough/code/synthesis/verify_rank_search.py` from the repository root; optional `--output` must name a fresh file. The [retained receipt](results/check.json) includes all effective source hashes and exact bounded state counts. Original receipt: `work/synthesis/20261008T223523Z-rank-ci/check.json`.

The entrypoint exercises actual finite searches without the larger 463,590-state case. It does not certify physical Gaussian lifts, independent residual monomial gauges, an all-size recurrence or a larger kappa. See [combined proof, scope and controls](../../reports/synthesis/global-helper-rank-search.md).
