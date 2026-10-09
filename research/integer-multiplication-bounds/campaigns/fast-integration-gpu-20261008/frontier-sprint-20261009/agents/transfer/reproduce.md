# Reproducing the balanced-transfer review

Python 3 and its standard library suffice. Run the portable mathematical
gate from any directory; its default input root is the verifier's own
directory. From the sprint root:

```bash
python3 -B agents/transfer/publication/joint-balanced-frames/verify_transfer.py \
  --check agents/transfer/publication/joint-balanced-frames/transfer-certificate.json
```

This is a complete supplied-moment and paid-transfer arithmetic check.
Exact finite words, complemented reflection, eligible-prime presentations
and all-size interfaces have their separately named checks and hypotheses.
The portable folder includes both raw frame fixtures and all three exact
profile/scalar inputs. It makes no network access and imports no producer.

To repeat the research source-bound cross-check, recover the original
PR161 and PR163 tarball snapshots into their manifest-relative paths.
Use the GitHub CLI and exact recorded commits; do not substitute current
branch contents:

```bash
gh api repos/eumemic/integer-mult-bounds/tarball/d14e29157bc905be1ced0776dd893d0714013f3a \
  > work/transfer/recovered-pr161.tar.gz
gh api repos/chafreaky/integer-mult-bounds/tarball/15c702a929b7d640107a95e196186ad74e876c82 \
  > work/transfer/recovered-pr163.tar.gz
```

Extract into fresh ignored directories, verify the source pins, and
either recreate the manifest-relative layout or use a fresh exported
sprint tree. The coordinator's artifact manifest supplies the canonical
snapshot mapping. The full source-bound command is:

```bash
python3 -B agents/transfer/code/certify_unified.py \
  --config agents/transfer/configs/unified-first.json \
  --output work/transfer/fresh-unified-receipt.json
```

Every output must be fresh. `--sprint <fresh-export-root>` selects an
explicit clean source tree. The input config checks 75 source files and
seven mathematical files, including the actual selected frame bytes.
The independent code recomputes the complete moments, full finite-group
scalar/router/semantic/row bills, 47 constraints and seven margins before
comparing to the pinned upstream arithmetic body.

The unchanged-supplier negative investigation can be regenerated with:

```bash
python3 -B agents/transfer/code/check_balanced_composition.py \
  --output work/transfer/fresh-fixed-supplier-receipt.json
```

This demonstrates that the balanced layout and paid atom refinement of
the original coarse supplier remain below the PR163 claim. It is a
different candidate from the new binary frame composition.

For the independent sibling arithmetic review, follow
`agents/assembly/code/review_balanced_unified.py` and its recorded protocol.
It imports neither this lane's code nor the upstream checker.

The retained layout controls are in the PR163 snapshot's
`references/semantic-bulk/rad20/code/`:

```bash
python3 -B <pinned-rad-code>/review_balanced_transform.py --output <fresh-json>
python3 -B <pinned-rad-code>/review_arbitrary_routing.py --output <fresh-json>
python3 -B <pinned-rad-code>/review_bulk_resampling.py --output <fresh-json>
```

Their source revisions and hashes are in the unified config and their
fresh receipts. At most four independent workers are needed; nested
numerical threads can remain one. The arithmetic commands themselves
use one process and no numerical libraries.

The completed gzip evidence preserves the initial exact outputs and
clean/source-corruption/-O controls. Archive manifests list every full
source copy and SHA-256. They exclude third-party source snapshots and
execution copies; those are recovered by the commands and manifests above.
