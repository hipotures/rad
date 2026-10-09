# Reproduce the fixed actual binary construction

The complete path uses standard-library Python and was exercised on Python
3.14.4. Its source inputs are two immutable exports. An older Python runtime
minimum has not been established. Syntax compatibility alone is not a runtime
validation. Keep assertions enabled and use one numerical-library thread.

Acquire both exports using GitHub CLI in fresh directories:

```bash
gh api repos/eumemic/integer-mult-bounds/tarball/98c115b53742b6613ad630de4d493f37b0119da7 \
  > source168.tar.gz
mkdir source168
tar -xzf source168.tar.gz -C source168 --strip-components=1
gh api repos/huxint/integer-mult-bounds/tarball/29892e2fe8a90714ef61bd8cbfb1a74bec6f8fd4 \
  > source170.tar.gz
mkdir source170
tar -xzf source170.tar.gz -C source170 --strip-components=1
```

The source gate verifies the listed files before importing external code.
Both snapshots are downloadable; no original annealing search is needed.
The exact scalar module, frame/alias plan and arc bytes are recoverable from
the source snapshots and the retained complete gzip fixtures.

From this candidate directory, choose a fresh output directory:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python3 -B code/replay_168_paired_lifetime.py \
  --source168 <clean-source168-tree> \
  --source170 <clean-source170-tree> \
  --fixture . \
  --output <fresh-output-directory>
```

The command checks compressed/decompressed fixture hashes and every authored
code fingerprint; rebuilds the actual scalar graph from the pinned annealed
pair module, nested-prefix module and two support-disjoint output fusions;
reruns deterministic carrier compilation and requires its arcs to equal the
frozen witness; and checks all five graph/word/frame/gauge/partner-chronology
output hashes. Matching adjacency construction interns frame IDs, so skipping
that deterministic compiler stage would renumber equivalent frames. The
reproduction preserves the exact original interning order.

It then loads the fixed 2,186 changed frames and 1,760 physical aliases, checks
complete role and target chains, actual death/birth deadlines and opcode
binding, replays every source and physical dirty F2 variable, rejects semantic
and frame controls, independently eliminates both frame presentations,
derives all 24,288 exact Gram-factor witnesses, and encloses the complete paid
moment and atom inequalities. It performs no frame/lifetime optimization.

Expected values are physical R=18,732, W=22,252, m=72, rank mass 1,600,208,
deficit 1,936, maximum child 60, coarse `161677519/250000000000`, and ordinary
`5049351199992013407/7812500000000000000000`. The coarse successor
`646710077/10^12` must reject. The exact frame/alias plan hash is
`b84ce113f75e4f64211bb942494e993c6e1306baddf8ed5565e664560036f2de`;
the exact profile hash is
`1731ef8c09620a0cf3e0d5dcb95c7039c6db66c7deef4b4b93006995adf45deb`.

The command writes fresh full receipts and prime witnesses. Complete
published evidence remains gzip-compressed; the archive manifest binds each
unchanged original. Independent reflected review and the final complex,
precision, row-stock and transfer certificate are separate validations.
