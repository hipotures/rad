# Unchanged PR127 package reproduction

The unmodified finite author runner passed at the pinned revision. All package hashes remain unchanged and the downloaded Git checkout is clean. This is reproduction of finite checks; the retained analytic and native assumptions are not proved by this run.

See [analysis](../../reports/obstructions/pr127-reproduction-and-birth-reuse.md) and [source pins](../../configs/obstructions/pr127-source-pins.json).

```sh
git clone --filter=blob:none --no-checkout --single-branch --branch research/shrunk-birth-reuse https://github.com/GamingPuzzled/integer-mult-bounds.git <fresh-external-source-directory>
git -C <fresh-external-source-directory> checkout --detach ca8725485a822769f24c2e4e9b8955b31a42b044
cd <fresh-external-source-directory>
python3 -B research/shrunk-birth-reuse/run_checks.py
```

The configured package/base hashes are checked before running. Full stdout, stderr, acquisition metadata and raw GitHub snapshots are retained in the ignored reference directory and receive an exact selected-file gzip copy. The downloaded repository is excluded from that copy. No authored dependency patch is required.
