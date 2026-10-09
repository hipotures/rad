# Independent review of the finite conditioned-frame screen

The retained 16 conditioned-frame fixtures pass an import-free exact replay.
Their physical operators, inverses and Gaussian-dyadic block normal forms agree.
Independent enumeration of all 135 three-bit Lagrangian subspaces also verifies
every retained dominance row. This supports the negative result within the
specified finite family. It does not independently classify all 138,240
screened physical edges or provide a native compiler or exponent claim.

The reviewed producer source is `code/complex/conditioned_frame_screen.py`,
SHA256 `2d9dd976cd6471c166e2cf2d795eb42517da1a0f2bf9f48519ebfcc9c0c6d9b6`.
The literal fixture is
[conditioned-frame-cases.json](../../fixtures/complex/conditioned-frame-cases.json),
SHA256 `51922bc6fc6d9037f75f576f939177cd708b9a4534aa56982f31ff422b018d1d`.
The [producer report](../complex/conditioned-common-frame-boundary.md) defines
the complete finite scope and retains the original phase-sign failure.

## Independent executable reconstruction

The fixture covers each rank 0, 1, 2 and 3 for each of the four predicates:
singleton address, two-bit conjunction, odd parity and one address bit. These
retained examples have identity parent Clifford operators and use right
conditioning by `(1+i)^-1` on the selected records. The review verifies that
literal contract rather than assuming it.

For each symmetric binary graph code, the reviewer directly constructs

```text
G[a,b] = 2^-3 sum_x (-1)^((a xor b) dot x) i^(q(x)),
q(x)   = sum_i A_ii x_i + 2 sum_{i<j} A_ij x_i x_j mod 4.
```

It verifies exact unitarity, builds the conditioning diagonal and its inverse,
and compares every retained coefficient against `D G*` and `G D^-1`.
Separately, each recursive block is reconstructed as a product of the literal
two-by-two factors `(1+i)/2` on equal bits and `(1-i)/2` on unequal bits.
Input/output address lists and every scale are applied explicitly. Their
complete stock must contain every address exactly once. Both normal forms
agree with the physical matrices, with uniform ranks matching the fixture.

Gaussian-unit extraction in this reviewer uses the exact rational norm:
`norm(z)=2^e`, followed by four direct candidate comparisons
`z=i^s(1+i)^e`. It does not reuse the producer's repeated integer-division
routine or its phase-sign formula. All 100 canonical units with valuations
from -12 through 12 and fourth-root phases from 0 through 3 round-trip. Zero
and the nonunit scalar 3 are rejected.

The four-worker run starts at the recorded actual UTC in
[its protocol](../../runs/20261009T005035Z-transfer-conditioned-frame-review/protocol.json)
and takes about 0.168 seconds. It checks 2,048 complete forward/inverse matrix
entries, 128 complete basis vectors and 64 arbitrary Gaussian-dyadic dirty
fields, each containing all eight records. Every exact inverse restores the
input field. These are complete finite stream checks, not selected output
coordinates.

Two additional controls isolate the earlier phase mistake. The correct
representation of `1/2` is `i(1+i)^-2`. The failed minus-denominator convention
instead represents `-1/2`. Removing the first nontrivial fixture wrapper also
changes the actual physical matrix. Neither control is treated as an accepted
operator or a free normalization.

## Dominance audit and proof scope

The optional full-data audit independently enumerates three-dimensional
isotropic subspaces of the six-dimensional binary symplectic space from all
independent triples. It obtains 135 subspaces, independently builds the 64
symmetric graph subspaces, and computes each distance by exact union rank.
This reproduces the baseline dominator ranks without producer imports or
its breadth-first generator.

The four raw producer files supply 2,160 distinct candidate rows and 17,976
admitted edges. Every candidate has a nonempty interface. The reviewer checks
the complete conditioning/parent index stock, every retained dominator rank,
each componentwise inequality and the reported uniform block profiles. It
checks the expected admitted counts 792, 1,824, 7,680 and 7,680. All pass.
The [retained review result](../../runs/20261009T005035Z-transfer-conditioned-frame-review/results/summary.json)
pins each raw producer file by hash.

Source inspection supports the classifier's soundness: disjoint square support
blocks are required; every nonzero entry must be a Gaussian-dyadic unit;
dephased cross ratios must be signs; the complete sign rows must form the
correct binary Walsh group; explicit input and output coordinates are retained;
and a reconstructed complete operator is compared with the original. The
finite executable review checks these resulting matrices for the 16 retained
examples. It does not rerun or independently replace the complete classifier.

Within the producer's reported uniform profiles, every admissible edge of a
candidate has rank at least that of one existing Clifford frame. Tensoring
multiplies both widths by the same factor. Hence any terminal multiset also
preserves the inequality. This conclusion uses actual uniform ranks; it does
not substitute average rank for a nonlinear finite tensor moment. Gaussian
wrapper arithmetic, its temporary precision and paid routing can only add to
the conditioned interface's cost. The argument applies to this fixed family
and terminal geometry; it does not exclude changed shared chronology, joint
source geometry or other nonunitary frames.

## Reproduction and limitations

The bounded portable check requires only the retained reviewer source, its
config and the literal producer fixture, all standard-library inputs:

```bash
python3 research/integer-mult-breakthrough/code/transfers/conditioned_frame_review.py --workers 1
```

For the optional full retained-row audit, regenerate the producer's four raw
files by its documented commands and pass their directory:

```bash
python3 research/integer-mult-breakthrough/code/transfers/conditioned_frame_review.py \
  --workers 4 \
  --dominance-directory research/integer-mult-breakthrough/work/complex/20261009T002708Z-conditioned-frames \
  --output /tmp/fresh-conditioned-frame-independent-review
```

Use a fresh output directory; an existing directory is rejected. The pinned
config records the fixture and producer identities. Raw input files are not
represented as present in the Git clone; the producer's registered text archive
or deterministic regeneration is required for the optional audit. Completed
review protocols and compact outcomes remain durable.

This is independent finite algebraic validation, geometry recomputation and
source review. Full tensor-column routing, complete physical dirty chronology,
native scalar wrappers, fixed-grid temporary guards, all-size transfer and
formal verification remain open. The negative screen offers no exponent
improvement toward the breakthrough target.
