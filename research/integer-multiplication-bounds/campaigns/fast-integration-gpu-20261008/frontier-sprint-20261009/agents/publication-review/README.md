# Independent publication-script audit

Scope: independently inspect and locally test the portable publication generator,
embedded runtime, and synthetic safeguards against section 8 of the sprint brief.
This audit does not accept a scientific candidate or authorize a real publication.
Only the root coordinator can freeze candidate science and publish RaD changes.
The current exact 1% policy version passes 44 authored, 14 independent safety,
and seven independent policy tests. The initial index-mutation finding is repaired.
The earlier 40/14 receipt remains a historical snapshot.

- [Current policy audit](reports/publication-policy-audit-20261009.md): exact 1%
  threshold, fresh source hashes, and independent boundary tests.
- [Policy receipt](results/policy-audit-20261009.json): all three passing suites and
  unchanged source hashes before/after execution.
- [Original audit](reports/publication-audit.md): historical findings and repaired gap.
- [Independent negative tests](code/test_independent_publication.py): mock-only GitHub
  control flow, including a successful checker that changes the staging index.
- [Final receipt](results/final-audit-receipt.json): unchanged before/after source
  hashes, passing counts, and complete-log hashes.
- [Text evidence](evidence/20261009T0818-publication-audit/): complete original and
  repaired test logs with a gzip manifest.
- [Initial receipt](results/initial-audit-receipt.json): exact inspected source hashes
  and the initial failing regression.

Execution files and full test logs belong in `../../work/publication-review/`.
Run from any directory using the script's absolute or otherwise resolved path:

```bash
PUBLICATION_REVIEW_WORK=<sprint>/work/publication-review \
python3 <sprint>/agents/publication-review/code/test_independent_publication.py
```

The independent tests import the neighboring publication lane's synthetic fixture
and mock command backend. Neither backend contains a subprocess/network path.
They call the Python object's `execute('publish')` exclusively with that backend;
this never launches a generated script's publication mode. Real CLI/bootstrap
checks, when reported, use only generated `--check` / `--self-test` or the blocked
synthetic `--dry-run` fixture. No GitHub PR, fork, or submission branch was created.
