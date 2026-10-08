# Delayed clones with descendant positive frames

A delayed explicit clone can use the existing positive envelope of its first
output-chain user. This broadens the unused-controller construction from
1,431 to **16,454 compatible clones** on the h51 reference graph. Actual
physical roles decrease from 502,134 to **485,680**. The full changed graph
passes the existing scalar, forward, reverse-complement, designated-target,
physical-rank and literal gate-count checks. Independent transfer and giant
replay are pending; these numbers are a finite screen until that review.

## Construction

Start with an exact selected controller flow on the original graph. Choose
an addition P=A+B whose capacity is unused and whose output value has at
least two controller chains. Select one complete output chain. Let F be the
existing envelope at that chain's first gate. P is an input there, so its
old frame is contained in F. All subsequent gates on the chain have frames
containing F by the old selected-link constraints.

Find a gate Q using the same formal value B, with unused controller capacity,
whose frame is contained in F and whose execution precedes the chain's first
gate. Q may execute after P. Insert an explicit identical addition P' just
before that first gate, assign it F, and move the whole chosen output chain
to P'. Retain all original controller links. Add P_A to P'_A and Q_B to P'_B.
The previous unused-capacity proof applies: both new links join the same
formal value, their source frames are contained in F, and their predecessor
capacities and new recipients are distinct. One extra sum adds two links
and saves one physical role.

The implementation reindexes original active nodes in their original
frame-dimension/node-ID execution order and inserts clones before their first
uses. Source triples remain the first v node IDs. All original frames are
the original Space objects; only clone frames differ from the formal source
support envelope. A conservative capacity and formal-child conflict filter
keeps simultaneous edits compatible. New descriptions are regenerated and
every selected source, chronological order, recipient capacity, parent
capacity and frame inclusion is checked before compilation.

## Why the enlarged clone frame is valid

F is an existing E(C,V) frame. Its restricted rational form is positive and
nondegenerate. It contains the actual source span of P because the old P
frame is contained in F. Both clone input source frames are therefore
contained in F. Every later frame on the moved complete chain contains F;
unchanged logical input/output paths carry it to an unchanged designated
target frame. Consequently F is orthogonal to every designated target reached
through that chain. Source-copy frames remain the original triple lines.

Forward inclusions are checked on the actual physical program. Reverse paths
use the corresponding orthogonal complements, so inclusion reverses in the
same manner as the accepted positive-envelope construction. The ambient
rational form remains nondegenerate (h is not 9). No unrelated generic
verifier is weakened. In particular the old equality
`node frame = envelope of all formal sources` is not imposed at clones;
it is replaced by explicit source containment plus the copied existing frame.
The independent small rational timeline checks the actual assigned frames
directly by exact elimination.

The dirty L/J/L-inverse/V identity, central correction, full data endpoints
and first/third stage matching do not depend on equality of clone frames to
their formal support. Their scalar maps are unchanged. Every node addition
and every physical copy is still cancellation-free. Complete h12 arbitrary
dirty-register and center bases pass in both orientations.

## Evidence

| Ground | Original roles | Fixed-frame clone roles | Delayed-frame clone roles | Delayed clones |
|---:|---:|---:|---:|---:|
| 8 | 665 | 665 | 641 | 24 |
| 12 | 3,804 | 3,787 | 3,674 | 130 |
| 20 | 23,839 | 23,738 | 23,020 | 819 |
| 51 | 502,134 | 500,703 | 485,680 | 16,454 |

The small control is
[runs/20261008T052800Z-finite-clone-descendant-small](../runs/20261008T052800Z-finite-clone-descendant-small/).
All changed logical/physical/target/frame checks pass. The improved h12
witness also passes complete dirty/center bases and an independent rational
physical timeline.

The full h51 result is externally retained under the campaign work root at
`derived/finite/20261008T052900Z-finite-clone-descendant51/certificate.json`.
Its complete original bytes are 10,971,005 bytes, SHA256
`a695bc00ea377f9c559ee52d17fa8a3a3eae972eaa73a60094b001340a3e8666`.
The complete byte stream needs gzip publication; it is not a Git-resident row
dump. The compact outcome is
[compact-certificate.json](../runs/20261008T052900Z-finite-clone-descendant51/results/compact-certificate.json).
The compiled hash is
`eb34b7ccee4439e5758643b25cc81260442a8723e5987b3d7f97b0b74ef1422f`.
The run takes 67.805 seconds and peaks at 4,160,492 KiB RSS, with no swap.

The old parent is unchanged candidate
`52ce3ca9416394668daacec55e648096fd419747f393391c9bfb7fdcd039f878`,
base2, positions eight zeros, twenty-six 23s, then seventeen zeros.
Its exact logical and compiled hashes are reconstructed and compared with
the frozen input, without repeating its old large physical verification.
All original source provenance and all 16,454 explicit edits, first-use frame
owners, selected whole chains and predecessor users are in the full result.

The complete changed physical histogram sums exactly to s=Wm-D. The deficit
D and decreasing-rank L are unchanged; W uses the new actual role count.
The current uniform-shrink saving lower endpoint is approximately
`3.29233344033e-9`, with an exact rational enclosure retained separately
from the parent's newer rotated/batched objective. That newer objective
must consume the actual changed histogram, not a presumed unchanged one.

Added sums replace the same number of scalar copies, so the literal mixer
operation count `c+R-v` is unchanged. The certificate nevertheless recomputes
the whole G and E guard with the new W, and checks strictly
`2GW^2+4s+4W+4 < E = 64(W+m+1)^3`.

## Sources and recovery

[finite_clone_descendant_frame.py](../code/finite_clone_descendant_frame.py)
has SHA256 `074c69f161eb25454b7351f3fc5b218935d49c7b1448d3547bd11ec2fce0a2c1`.
The unchanged frame constructor, planner, compiler and target checker are
imported from the already pinned campaign sources. The complete baseline
case is recoverable from the published previous full search archives.
[finite_clone_descendant_export.py](../code/finite_clone_descendant_export.py)
exports exact integer selected links, explicit clone placement and frame-owner
IDs, node/description hashes and a distinct candidate identity, for independent
reconstruction without a solver or baseline replay in the reviewer.

Representative commands, using the campaign math environment and immutable
original upstream commit bcd4ebde8692383539f8a48734e5fbf3a18a32c2, are:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -B code/finite_clone_descendant_frame.py \
  --reference "$REFERENCE" --h 8 12 20 --dirty-ground 12 \
  --output "$FRESH_SMALL_OUTPUT"
python -B code/finite_clone_descendant_frame.py \
  --reference "$REFERENCE" --candidate "$BASELINE_CASE" \
  --output "$FRESH_EXTERNAL_OUTPUT"
```

Both commands were exercised. All outputs must be fresh. Original protocols,
logs and bytes are preserved. The separate multi-chain repeated-round small
test reached no additional profitable second round at h8, h12 or h20; that
negative does not constrain this delayed-frame mechanism. Next steps are
independent all-size proof and giant promotion, and the ongoing 300 distinct
nearby-ground delayed-frame screens.
