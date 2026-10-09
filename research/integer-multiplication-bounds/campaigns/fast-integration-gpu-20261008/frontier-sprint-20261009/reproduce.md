# Reproduction and recovery

Run from the sprint directory, using Python 3.11 or newer (recorded environment: Python 3.14), Git and an authenticated GitHub CLI for read-only source acquisition. The finite evaluators and authored scripts use the Python standard library. Exact source archives remain immutable; each evaluator runs in its own writable export. Set `OMP_NUM_THREADS=1` and `OPENBLAS_NUM_THREADS=1` for any installed numerical libraries.

## Acquire the immutable inputs

```bash
python3 code/fetch_snapshot.py eumemic/integer-mult-bounds bfc5466b028923a1f8655602994ea56c70b5c329 pr120-bfc5466
python3 code/fetch_snapshot.py GamingPuzzled/integer-mult-bounds 628fcab57063370cbf03c0fb54472348e7b68368 pr160-628fcab
python3 code/fetch_snapshot.py eumemic/integer-mult-bounds d14e29157bc905be1ced0776dd893d0714013f3a pr161-d14e291
```

The acquisition script refuses existing destinations. Existing local snapshots should be checked against [artifact-manifest.json](artifact-manifest.json), not overwritten. GitHub archive hashes identify the captured archive bytes; tree revisions pin reproducible content even if GitHub later recompresses an archive.

The original user-supplied PDF is identified in [input-manifest.json](input-manifest.json). Its extracted complete text is retained in the evidence archive. The original PDF and input ZIP have no known downloadable public URL; their byte-for-byte recovery remains dependent on the supplied local input package.

## Historical E1 construction batch

Follow [the lane reproduction recipe](agents/complements/historical-e1-report.md). It regenerates an unchanged control plus three distinct alternate frame constructions, full paid profiles and modular dirty replays. Independent reflected replay and final kappa are not claimed for unsuccessful E1 variants.

## Focused current baseline

Copy `work/repos/pr161-d14e291` to a fresh ignored writable path and run these commands from the copy:

```bash
make paired-cube-verify
python3 research/paired-cube-bit/paired_cube_bit_word.py --p 12 --check
python3 research/paired-cube-bit/check_paired_cube_bit.py --dir research/paired-cube-bit/out --p 12
```

The baseline lane also supplies independent exact integer dirty-state response and interval/assembly code. The first conditionally accepted combined candidate has tested recovery recipes in the [baseline](agents/baseline/review-binary-component-pairs.md), [geometry](agents/geometry/README.md), [assembly](agents/assembly/reproduce.md), and [transfer](agents/transfer/reproduce.md) lanes. Its frozen science and checker hashes are bound in [accepted-first-candidate.json](reports/accepted-first-candidate.json). It is below the user's publication threshold. Focused checks do not establish the inherited all-size Clifford, uniform recurrence, recovery or fixed-tape assumptions. Broad `make verify` is reserved for a frozen publication candidate under the upstream contribution policy.

## Accepted lifetime/fused scientific checkpoint

The independently accepted final saving is `61728289/100000000000`.
Its [immutable identity](reports/accepted-lifetime-fused-candidate.json) binds
141 author sources, 24 inputs, the additional reviewer proof source and all
executed finite/arithmetic receipts. It is a conditional research result and
does not meet the current publication threshold.

Run the ordered acquisition, construction and independent review commands in
the [binary review](agents/baseline/review-paired-both-lifetime.md),
[binary construction](agents/bit/candidates/binary-168-paired-lifetime-p12/reproduce.md),
[signed winner](agents/signed/reports/fused168-finite-historical-winner.md),
[reflected winner](agents/geometry/fused168-joint-winner-review.md),
[transfer recovery](agents/transfer/reproduce.md), and
[independent arithmetic recovery](agents/assembly/reproduce.md).
These handoffs distinguish a complete executed finite replay from a bounded
recovery check. Frozen downloaded sources are recoverable from the immutable
GitHub repository/revision and file inventories in the frontier lane; authored
changes and compact fixtures are retained in Git.

The essential 24 original input files and six arithmetic/binding/recovery
receipts also have complete, byte-preserving copies in
`evidence/accepted-lifetime-fused-inputs-20261009T0954Z`. Its compressed manifest
records every original path, size and SHA-256. From the repository root:

```bash
python3 tools/archive_workspace.py verify-text --destination research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/frontier-sprint-20261009/evidence/accepted-lifetime-fused-inputs-20261009T0954Z
```

Decode a named `.gz` file into the corresponding original relative path under
the sprint, using a fresh destination and verifying the manifest's original
SHA-256. Preserve existing originals. The lane recipes also reconstruct these
exports directly; a decoded receipt alone does not rerun its mathematical
checker. After reconstructing the recorded source/input layout, from the
sprint directory:

```bash
python3 code/bind_lifetime_fused_checkpoint.py --output work/recovered-lifetime-fused-binding.json
```

The binder refuses an existing output. It rechecks every source/input and
finite-review pin, equality of independently recomputed arithmetic, both full
distributions, 47 positive slacks, seven positive margins and strict absorption.
The scientific digest must be
`4432be0a906b7e09cc356846453fb5240505d948c166394a406badc7577f7b93`.
Its frontier observation fields may differ on a new run; its mathematical
identity must not. The coordinator exercised this binding and verified all
30 whole gzip copies against the originals. Broad contribution verification
was not run for this below-threshold historical candidate.

The [executed reviewer dependency supplement](agents/assembly/configs/historical-lifetime-git-recovery-supplement.json)
pins the additional imported `review_rebuilt168_ceiling.py` against the already
executed acceptance export. Restore that authored source from Git along with
the other lane code; the original accepted scientific digest and receipts are
unchanged.

The portable transfer package's three small `inputs/` JSON files follow the
same whole-file evidence policy. Restore their exact bytes from
`agents/transfer/evidence/portable-lifetime-fused-inputs-20261009T1021Z/inputs/`
to `agents/transfer/publication/lifetime-fused-frames/transfer/inputs/` before
running that package. Check original sizes and hashes in the compressed
manifest, refuse to replace a differing existing file, and keep the authored
source and metadata unchanged. The original files remain ignored; their gzip
copies are versioned. This is a declared recovery step, not an installed or
machine-local dependency.

## Current comparison

```bash
python3 code/refresh_frontier.py
```

This collects all pages and current source heads through `gh`. It deliberately leaves mathematical comparison unresolved until certificate and assumption assessment is completed. A successful API response alone is not a publication gate. The [frontier lane](agents/frontier/README.md) records pinned certificates and full draft-inclusive comparisons. Freezing and both live publication guards require the accepted final score to be at least `101/100` times the current comparable maximum, including retained main.
