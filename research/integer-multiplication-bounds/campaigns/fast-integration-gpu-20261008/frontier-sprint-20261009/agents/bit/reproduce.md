# Reproduce the frozen binary frame candidate

Prerequisites: Python 3 standard library and the immutable PR163 source tree at
`15c702a929b7d640107a95e196186ad74e876c82`. The sprint's frontier scout obtained
that source using GitHub CLI; [source-inputs.json](source-inputs.json) records
every mathematical dependency's size and SHA-256. A clean source export can be
used; Git metadata is unnecessary. The original producer search is not run.

To recover the immutable source in a fresh directory using an authenticated
GitHub CLI:

```bash
gh api repos/chafreaky/integer-mult-bounds/tarball/15c702a929b7d640107a95e196186ad74e876c82 \
  > pr163-source.tar.gz
mkdir pr163-source
tar -xzf pr163-source.tar.gz -C pr163-source --strip-components=1
```

The replay's source-hash gate validates the retained files after extraction.
The acquisition here was performed by the frontier scout; the binary lane
replayed its immutable export and did not repeat network acquisition.

From the sprint directory, substitute a clean extracted source path and a fresh
output directory:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python3 -B agents/bit/code/verify_bit_frames.py \
  --source <immutable-pr163-tree> \
  --source-pins agents/bit/source-inputs.json \
  --plan agents/bit/fixtures/binary-component-pairs-p12-frames.json \
  --output <fresh-output-directory> \
  --integer-decoder
```

The command checks source hashes before import; reconstructs exact rational
frames, the scalar decoder, all physical register chains and the complete paid
profile; replays every formal F2 and defining-integer variable; rejects four
adverse controls; derives every new finite prime witness; and encloses the full
binary moment with fallback. On this host the pinned frozen replay took about
15 seconds and 615 MiB peak RSS. Thread pools are restricted to one.

Expected scientific values are `R=23368`, `W=26888`, `m=72`, rank mass
`1934000`, deficit `1936`, maximum child `60`, 1,848 changed operation frames,
1,176 distinct new bases and a maximum selected Gram determinant of 63 bits.
The accepted fine coarse point is `37187295064613/62500000000000000`; the
retained-atom conservative ordinary point is `594440184179/10^15`.

For the measured first batch, run [bit_frame_search.py](code/bit_frame_search.py)
with `--policy control`, then `singletons`, `components` and `component-pairs`
against the same immutable source. The accepted component-pair settings were
`--order largest-first --passes 4 --max-nodes 256 --seed 20261009` at the shared
trial saving `0.000594653772288656`. Each job used one CPU worker, so the three
variants ran concurrently. Results and source/configuration fingerprints are
preserved in the lane's evidence archive and compact batch summary.

The final kappa, exported-word reflection and the independent assembly belong
to the sprint's baseline and transfer lanes. This command alone does not claim
those results or a publication-ready multiplication bound.
