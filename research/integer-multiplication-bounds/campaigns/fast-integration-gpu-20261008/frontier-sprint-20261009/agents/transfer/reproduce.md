# Reproducing paid transfer arithmetic and recovery

All transfer arithmetic uses Python's standard library, tested with Python3.14.4. Source producer helpers need Python3.11 or newer; no untested runtime minimum is claimed for every imported source. Use one CPU process per command and fresh output paths. The transfer commands import no upstream arithmetic implementation.

## Public mathematical package

The13decoded-file historical package has10readable committed files and3complete mathematical inputs preserved through the repository's gzip publication path. Restore exact unchanged bytes before the verifier; existing files are checked and never overwritten:

```bash
python3 -B agents/transfer/code/restore_portable_inputs.py \
  --package agents/transfer/publication/lifetime-fused-frames/transfer \
  --archive agents/transfer/evidence/portable-lifetime-fused-inputs-20261009T1021Z
python3 -B agents/transfer/publication/lifetime-fused-frames/transfer/verify_transfer.py \
  --check agents/transfer/publication/lifetime-fused-frames/transfer/transfer-certificate.json
```

The portable input metadata SHA stays `dca3d0146ef6080dd5b9daf96ec145e604951b8180d8eefceacad9c59214e2c9`, certificate SHA stays `b19f42ee545d981c15a0c2f9eec6716e7bd80f0ec9ca7878587d897cd4a812a6`. Recovery changes no scientific path/hash/parameter. This checks complete characteristics, fallback, atom, scalar/router/precision/rows,47conditions and7margins. Finite words, prime eligibility, geometry and all-size interfaces have distinct prerequisites. Pinned171comparison is historical; current publication fails.

## Full historical source and finite-review closure

`artifact-manifest.json` maps191records to obtainable source commits, durable readable files or complete gzip evidence. It preserves author141source/24input identity plus explicitly supplemental6review receipts/10sources. Recover source tarballs with GitHub CLI; example:

```bash
gh api repos/eumemic/integer-mult-bounds/tarball/98c115b53742b6613ad630de4d493f37b0119da7 \
  > work/transfer/pr168-98c115b.tar.gz
mkdir -p work/frontier/pr168-98c115b/extracted/eumemic-integer-mult-bounds-98c115b
tar -xzf work/transfer/pr168-98c115b.tar.gz --strip-components=1 \
  -C work/frontier/pr168-98c115b/extracted/eumemic-integer-mult-bounds-98c115b
```

Repeat for the five snapshots used by the historical group:16315c702a,1657518fed,16898c115b,1694895ba1,17029892e2. Exact repository/commit/cache-root mappings and per-file hashes are in the manifest. Never substitute a current branch. Downloaded source trees remain ignored; preserve their Apache-2.0 notices.

Then recover every original derived input from archived bytes, reading no original derived work:

```bash
python3 -B agents/transfer/code/recover_transfer_artifacts.py \
  --manifest agents/transfer/artifact-manifest.json --source-cache . \
  --output-root work/transfer/fresh-recovery/sprint \
  --report work/transfer/fresh-recovery/recovery.json
python3 -B work/transfer/fresh-recovery/sprint/agents/transfer/code/certify_lifetime_fused.py \
  --sprint work/transfer/fresh-recovery/sprint \
  --config work/transfer/fresh-recovery/sprint/agents/transfer/configs/lifetime-fused-168-170.json \
  --output work/transfer/fresh-recovery/author-receipt.json
python3 -B work/transfer/fresh-recovery/sprint/agents/assembly/code/bind_fused_reviews.py \
  --sprint work/transfer/fresh-recovery/sprint \
  --config work/transfer/fresh-recovery/sprint/agents/transfer/configs/lifetime-fused-168-170.json \
  --binding work/transfer/fresh-recovery/sprint/agents/assembly/configs/fused-lifetime-review-binding.json \
  --output work/transfer/fresh-recovery/finite-binding.json
```

`--source-cache` may point to another portable cache root with the same manifest-relative downloaded-source layout. The bounded test recovered191records/183unique files exclusively from source caches, readable source and committed gzip bytes; both commands then passed. This repeats mathematical arithmetic and receipt/input binding. It does not pretend to rerun expensive all-column finite executions; their original checked receipts/code/proof and ordered sibling commands are retained.

Full finite binary reproduction is in `agents/bit/candidates/binary-168-paired-lifetime-p12/reproduce.md`; complex producer/search/replay recovery is in `agents/placement/reproduce.md`. Original and reflected independent finite gates are indexed by `agents/assembly/configs/fused-lifetime-review-binding.json`. The additional old168cover proof is explicitly preserved outside the unchanged author141record inventory.

## Separate ceilings and targets

```bash
python3 -B agents/transfer/code/assess_sink168.py \
  --config agents/transfer/configs/sink168-fd25adb-ceiling.json \
  --output work/transfer/fresh-sink-assessment.json
python3 -B agents/transfer/code/derive_frontier_targets.py \
  --config agents/transfer/configs/current-target168-4a3c769.json \
  --output work/transfer/fresh-current-targets.json
```

The first needs pinned fd25adbsource plus regenerated body/literal sink events. Its86/24identity binds declared arithmetic inputs; body-generator recovery is a separate supplement, not a silently expanded original identity. No new source is accepted through saved profiles. The target command reads the decoded pinned certificate only and derives exact necessary/sufficient transfer grids; no old supplier counts are carried forward.

For the historical79source ceiling, use `code/assess_frontier.py` with `configs/rebuilt168-top169-ceiling-v2.json`. The initial74source config/receipt is preserved as arithmetic-only with missing licensed PR117closure. First161/163composition uses `code/certify_unified.py` and `configs/unified-first.json`;165integration uses `code/certify_integrated.py` and its distinct config. Their earlier completed records are archived separately.

## Evidence and boundaries

Completed compact transfer results/failures are full gzip copies under `evidence/completed-transfer-20261009T1020Z/`; additional historical protocol/finite receipts are under `evidence/supplemental-finite-closure-20261009T1021Z/`. Archive manifests verify compressed/decoded hashes and full UTF-8 copies. Downloaded source trees, clean execution trees and environments are excluded.

Fresh relocated public checks passed normal execution, optimized-Python rejection, frame-byte corruption, mass-preserving profile corruption and the updated source floor rejection, then exact restoration. Independent full141/24 arithmetic and supplemental finite binding reproduce from clean trees. All-size ordinary/restoration, tensor/Clifford/shared-core, router/layout/bulk, finite prime setup, analytic grid/recovery and fixed-tape hypotheses remain conditional. No practical input threshold, current record, upstream publication or broad suite is inferred.
