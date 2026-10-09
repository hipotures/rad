# Reproduction and recovery

Run from the sprint directory, using Python 3.14 for the recorded environment, Git and an authenticated GitHub CLI for read-only source acquisition. The finite evaluators and authored scripts use the Python standard library. Exact source archives remain immutable; each evaluator runs in its own writable export. Set `OMP_NUM_THREADS=1` and `OPENBLAS_NUM_THREADS=1` for any installed numerical libraries.

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

## Current comparison

```bash
python3 code/refresh_frontier.py
```

This collects all pages and current source heads through `gh`. It deliberately leaves mathematical comparison unresolved until certificate and assumption assessment is completed. A successful API response alone is not a publication gate. The [frontier lane](agents/frontier/README.md) records pinned certificates and full draft-inclusive comparisons. Freezing and both live publication guards require the accepted final score to be at least `101/100` times the current comparable maximum, including retained main.
