# Two-copy shared-release discriminator

## Question and controlled model

The coherent fitting-rank argument gives a penalty twice the rank of a shared
scalar defect. Multiplication by the number of tensor copies requires additional
separability premises. Could entangled frame choices defeat the product-frame
charge in a small complete fixed-word example?

This discriminator fixes the h2, two-source, one-arbitrary-dirty-helper
side-inside word. Its central scalar matrix is the all-ones matrix, and the side
is identity minus that matrix. The exact ten-gate word restores both sources
and the dirty helper and adds the identity to the sinks. Source labels are the
two coordinate lines tensored with the full copy space; sources start in those
frames and end in the full frame. Sinks start in the zero frame and end in the
orthogonal source-label frames. The dirty helper starts at zero and ends at full.
The dimension is four with two copies, so the baseline capacity is 5*4=20.

The comparison uses all 25 products of two two-dimensional subspace frames,
versus all 67 canonical diagonal-subspace frames L_E in four dimensions. The
latter domain includes 42 additional frames. Its subspace counts by dimension
are 1,15,35,15,1. Neither domain is the complete set of 2,295 four-dimensional
Lagrangian frames, and Gaussian phases are separate from this geometric model.

## Evidence and result

The complete min-sum variable-elimination algorithm returns minimum rank 20
in both domains. The complete selected four-dimensional domain uses induced
width three, 101,662,450 candidate evaluations and a 4,265,086-byte factor and
decision payload preflight. The four-worker executions took approximately
0.076 seconds for all 67 frames and 0.005 seconds for the 25 product frames;
compiler and environment metadata are retained in each protocol. Every
backtracked assignment is replayed against the complete objective and its
chronological endpoint charge. The scalar word is independently replayed.

This is a useful negative result for the fixed word and selected frames. It
does not prove a general tensor-copy factor, exclude other circuit words, or
establish a native Gaussian circuit or a multiplication exponent.

The [bounded replay](../../code/obstructions/verify_entangled_release.py)
compiles the retained OpenMP patch in a temporary directory, checks the one-copy
minimum 10 and both two-copy minima 20, validates all selected Lagrangians,
checks the complete subspace counts and replays the actual frame paths. The
factor engine has separate exhaustive serial/parallel controls in
[its verifier](../../code/synthesis/verify_echo_elimination.py). That verifier
does not repeat the larger 135-frame width-four experiment.

## Retained implementation failure

The first 67-frame run succeeded before the product-only path was exercised.
That path then failed because the binary basis routine was called without its
required dimension argument. The corrected source adds that argument. The
[zero-context recovery patch](../../fixtures/obstructions/entangled-product-basis-correction.patch)
recovers the original source SHA256
`14db465c322e20597206be33514e17fe9e2ce4319128f6fb81dcee6483a3c7c5`
from the corrected source SHA256
`3b0b0c073a5fdc6bbbd86987db34c0999a4479efee19c42989a4dad7c7a57e68`.
A fresh isolated import reproduced the original TypeError. Its recorded log is
the reproduction log; the original terminal exception was not captured.
The successful initial 67-frame record is unchanged and retains its original
source identity. The repaired product run has its own output directory.

## Reproduction and provenance

Python's standard library, a C++17 compiler, GNU patch and OpenMP are needed:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/verify_entangled_release.py
python3 -B research/integer-mult-breakthrough/code/obstructions/entangled_release_probe.py --copies 2 --frames all-LE --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/entangled
python3 -B research/integer-mult-breakthrough/code/obstructions/entangled_release_probe.py --copies 2 --frames product --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/product
```

The discovery runs are [the complete selected domain](../../runs/20261009T005100Z-release-entangled/report.md)
and [the repaired product domain](../../runs/20261009T005143Z-release-product-repaired/report.md).
Temporary binaries, factor inputs and downloaded dependencies are excluded from
Git. Exact source closures, compiler flags, memory preflight and results are
retained in the protocols and complete text evidence. OpenAI Codex assisted the
design and implementation; this is internal research review, not peer review
or formal verification.
