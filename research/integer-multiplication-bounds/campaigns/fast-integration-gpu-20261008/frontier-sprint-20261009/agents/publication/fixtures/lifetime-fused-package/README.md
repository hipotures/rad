# Historical lifetime/fused frames checkpoint

`balanced-lifetime-fused-168-170-20261009` combines an actual binary physical-lifetime construction with an actual signed full-fusion construction, coherent aliases and raised complex frames. Its conditional final saving is exactly `61728289/100000000000`. The directory name `research/lifetime-fused-frames` denotes this immutable identity. A stronger construction requires a new identity.

This checkpoint falls below the subsequently observed public frontier and the required 1% relative publication improvement. It is retained for scientific reproduction. No current record, release acceptance or hosted CI success is claimed. The original source-bound author and independent reviews contain the full 141-source/24-input acceptance; this compact package preserves executable component closure, small exact fixtures, their proofs and independent checks. The arithmetic subset verifies eight actual files and the canonical original metadata; it does not rerun the complete original source closure or live frontier.

`SOURCE.json` lists every packaged file except itself, including hashes, modes and provenance. The immutable supplier trees are PR168 at `98c115b53742b6613ad630de4d493f37b0119da7` and PR170 at `29892e2fe8a90714ef61bd8cbfb1a74bec6f8fd4`. Later versions of those pull requests are distinct constructions. Original licenses, notices and relative source paths are retained under `sources/`. The binary adaptation's direct PR163 source is credited in `binary/adapted-source-provenance.json` and `binary/NOTICE.md`.

All checks use standard-library Python. The declared minimum is Python 3.11; the exercised interpreter was CPython 3.14.4. Full finite reflection uses approximately 1 GiB peak memory. Run from the repository root, using a fresh external output directory:

```bash
PACKAGE_DIR=research/lifetime-fused-frames
CHECK_WORK=$(mktemp -d "${TMPDIR:-/tmp}/lifetime-fused-check.XXXXXX")
export PYTHONDONTWRITEBYTECODE=1
python3 -B "$PACKAGE_DIR/binary/code/replay_168_paired_lifetime.py" \
  --source168 "$PACKAGE_DIR/sources/pr168" --source170 "$PACKAGE_DIR/sources/pr170" \
  --fixture "$PACKAGE_DIR/binary" --output "$CHECK_WORK/binary"
python3 -B "$PACKAGE_DIR/complex/code/reconstruct_complex.py" \
  --source-root "$PACKAGE_DIR/sources/pr168" --data-dir "$PACKAGE_DIR/complex/data" \
  --output-dir "$CHECK_WORK/complex"
python3 -B "$PACKAGE_DIR/complex/code/check_pr165_signed_control.py" \
  --export "$CHECK_WORK/complex" --exact-core "$PACKAGE_DIR/independent/code/exact_aliased_core.py" \
  --output "$CHECK_WORK/scalar.json"
python3 -B "$PACKAGE_DIR/complex/code/audit_scalar_bounds.py" \
  --export "$CHECK_WORK/complex" --exact-core "$PACKAGE_DIR/independent/code/exact_aliased_core.py" \
  --output "$CHECK_WORK/scalar-bounds.json"
python3 -B "$PACKAGE_DIR/complex/code/enclose_finite_export.py" \
  --export "$CHECK_WORK/complex" --interval-code "$PACKAGE_DIR/complex/code/interval_moments.py" \
  --saving 617664283/1000000000000 --saving 617664284/1000000000000 \
  --output "$CHECK_WORK/moments.json"
python3 -B "$PACKAGE_DIR/independent/code/portable_complex_reflection.py" \
  --root "$PACKAGE_DIR" --export "$CHECK_WORK/complex" --output-dir "$CHECK_WORK/reflection"
python3 -B "$PACKAGE_DIR/transfer/verify_transfer.py" \
  --check "$PACKAGE_DIR/transfer/transfer-certificate.json"
python3 -B "$PACKAGE_DIR/independent/code/review_public_fused.py" \
  --directory "$PACKAGE_DIR/transfer" --output "$CHECK_WORK/independent-arithmetic.json"
```

The binary and complex constructors regenerate the complete fixed plans, including the large graph and literal word, from compact fixtures and pinned source modules. They perform no search for a different plan. Native finite correctness, exact dirty-scalar algebra, full paid moments and conditional all-size assembly have separate proof scopes. The full mathematical assumptions and precision/router/row bills are in `transfer/PROOF.md`; the native binary geometry and prime units are in `binary/proof.md`.

Retain the original finite excluded-prime sets. Newly tested selected presentations add no excluded prime above `2^80`; this does not assert that every inherited frame presentation is invertible at every prime above that threshold. The uniform weighted compiler, projector adaptation, restored wrappers, compensated physical births, completed-core reuse and analytic/tape/recursion contracts remain conditional assumptions. Finite execution does not prove the complete multiplication theorem.

No broad repository contribution gate was run for this checkpoint after its publication threshold closed. A future qualifying contribution requires independent acceptance, an exact current-frontier check, the complete upstream contribution policy and a separate explicit release freeze.
