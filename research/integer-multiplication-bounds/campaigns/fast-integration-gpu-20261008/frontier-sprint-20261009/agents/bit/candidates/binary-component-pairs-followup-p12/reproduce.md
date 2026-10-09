# Reproduce the distinct follow-up

Requirements: Python 3 standard library, about 620 MiB of RAM, assertions
enabled, and the immutable source export. The original producer search is not
required. Source hashes are checked before importing retained code.

Recover the source in a new directory with the GitHub CLI:

```bash
gh api repos/chafreaky/integer-mult-bounds/tarball/15c702a929b7d640107a95e196186ad74e876c82 \
  > pr163-source.tar.gz
mkdir pr163-source
tar -xzf pr163-source.tar.gz -C pr163-source --strip-components=1
```

The complete immutable frame plan is retained as gzip evidence. In a fresh
clone, recover it from this candidate directory without overwriting an existing
plan:

```bash
set -C
gzip -dc -- evidence/fixed-plan-20261009T0901Z/frames.json.gz > frames.json
sha256sum frames.json
```

The expected SHA-256 is recorded below. The original local plan remains
unchanged and is ignored; a clone recovers the same bytes from the archive.
Then use a fresh output directory:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python3 -B code/verify_bit_frames.py \
  --source <immutable-pr163-tree> \
  --source-pins source-inputs.json \
  --plan frames.json \
  --output <fresh-output-directory> \
  --integer-decoder
```

The exercised portable replay took 13.999 seconds with peak RSS 615,100 KiB.
Expected output status is `EXACT_FINITE`, with 1,896 changed frames, maximum
chosen Gram determinant size 63 bits, rank mass 1,934,000, deficit 1,936,
318,132 edges, and all four adverse controls rejected. The exact coarse saving
is `59503737587021/10^17`; the adjacent `10^-18` point rejects. Exact moments
and all new prime witnesses are regenerated rather than trusted.

The frame plan SHA-256 is
`eeb54883858786e7244052633461c1cc119e51a8c5ba2bf1ff1d3b1b9102aa8b`.
The profile SHA-256 is
`cd729506b2c4bfefeafbdd82ed0ac1f35be32b3a864c33dae201e1fb7235907d`.

This bounded replay exercises rational geometry, the complete local paid row,
formal variables, prime witnesses, and stopped native moment. Independent
reflected replay and the final transfer certificate remain separate checks.
The completed full receipts are published as gzip evidence; their manifest
records hashes of the unchanged original execution files.
