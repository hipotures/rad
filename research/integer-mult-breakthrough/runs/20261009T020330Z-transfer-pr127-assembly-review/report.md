# Independent compact PR127 assembly review

Actual process start: 2026-10-09T02:03:30.856459+00:00.
Four workers complete four exact interval moment comparisons and one exact
aggregate assembly check in 0.302412 seconds. Outcome: PASS.

[Cross-run proof and scope review](../../reports/transfers/pr127-transfer-independent-review.md)
records the primary source head, inherited assumptions, input reduction and
complete reproduction closure. This is independent compact finite arithmetic
and analytical/source inspection. The full external word and all 47 constraints
are not independently replayed by this source. No all-size native or
unconditional exponent is proved.

The immutable raw protocol and summary are duplicated here without changes.
The raw directory is ignored `work/transfers/20261009T020330Z-transfer-pr127-assembly-review/results`; its compact source
evidence is fully retained and deterministically regenerable. No logs or large
measurements are omitted. The external full graph and pair list are downloadable
from pinned commit ca8725485a822769f24c2e4e9b8955b31a42b044.

Reproduce from the new worktree:

```sh
python3 research/integer-mult-breakthrough/code/transfers/pr127_transfer_review.py --workers 4
```

The bounded CI command uses `--workers 1` and passes the same four moment tasks.
