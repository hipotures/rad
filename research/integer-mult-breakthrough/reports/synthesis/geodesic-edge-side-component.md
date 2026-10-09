# Geodesic edge-helper side component

One arbitrary dirty helper per orthogonal side term gives a complete
**framed** `y+=x` construction without the side-output return fee. The
initial source and final sink address frames are prescribed. Separately
adapting this framed shear to a raw-input canonical `C_h` invocation spends
its endpoint saving. The result is a useful constructive component, not
a new integer-multiplication exponent.

For odd-weight labels, let `K` have diagonal1 and vanish on every distinct
nonorthogonal labeled pair. The side `Q=I-K` then has only orthogonal
nonzero entries. For each such ordered pair `(T,U)`, reserve one arbitrary
dirty side helper `z_TU`. There are `M` side helpers and `v` center helpers;
the actual stock is `W=3v+M`.

All sinks and dirty helpers start at the identity operator. Sources start
at their literal `C_U` operator. The center early and late echoes use the
closed feature release already verified by
[closed_center_release.py](../../code/synthesis/closed_center_release.py).
Supply both central scatters before any sink leaves zero. Also subtract
`Q_TU z_TU` from each sink at zero. Move each side helper zero to its source
line, inject that source, and retain the sources at their line through all
injections.

Process side terms in fixed source order. For each target maintain
`E_T=span(previously processed neighbor labels)`. Its next source label
`U` satisfies `U orthogonal T`, so the enlarged frame still lies in
`T^perp`. Move the sink to that enlarged actual frame and move its helper
from line `U` to the **identical chosen operator**. Add `Q_TU` times the
helper, then move the helper to full. Finally complete the sink to its
kernel frame, complete the sources to full, and subtract each full source
from every helper that received it. All virtual dirty values restore;
their physical endpoint is `C_full` times the original virtual value.

Each side helper's path has width charges

```text
1 + (dim(E_T)-1) + (h-dim(E_T)) = h.
```

The sink paths telescope to `h-1`, including the final completion. Every
side helper therefore follows a zero-to-full geodesic. The complete rank
is `Wh-2v+2qh`, with no extra `2v` closed side-output charge.

[geodesic_edge_side_splice.py](../../code/synthesis/geodesic_edge_side_splice.py)
performs literal physical coordinate-color checks at h3. The f1 case
checks all120 physical input columns; f2 checks all15 origin bank columns
and uses common-XOR covariance for all960 columns. Every source, sink,
center helper and side helper is retained. Omitting a helper's final
source subtraction gives an exact counterexample. All scalar gates check
the same actual coordinate Gaussian frame through the explicit word.

For triples with `K(T,U)=(intersection(T,U)-1)/2`, the abstract larger
ledgers count every ordered nonzero side edge, every nested binary span
and all frame transitions:

| h | v | q | M | W | Rank deficit |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 9 | 84 | 9 | 3192 | 3444 | 6 |
| 12 | 220 | 12 | 24420 | 25080 | 152 |
| 16 | 560 | 16 | 182000 | 183680 | 608 |

Those larger cases are scalar identity and exact `L_E` geometry/ledger
checks. This producer does not execute their noncoordinate Clifford
frames. A separately authored canonical-frame API supplies literal
representatives and bounded relative-operator checks, including radical
subspaces; integration and independent physical replay are separate.

[certify_geodesic_edge_moment.py](../../code/synthesis/certify_geodesic_edge_moment.py)
uses exact outward rational logarithm and exponential intervals. At
`b=1/5000` all three **declared ledger profiles** have normalized moment
strictly below1. Their exact characteristic roots lie respectively in

```text
h9:  [262601438,262601439] / 10^12
h12: [811625163,811625164] / 10^12
h16: [408477357,408477358] / 10^12.
```

This independently reproduces the coordinator's parallel capacity screen;
it is not a new profile or a broader exhaustive parameter sweep. The
receipts are the
[edge-side run](../../runs/20261009T014025Z-synthesis-geodesic-edge-side/report.md)
and [exact moment run](../../runs/20261009T014140Z-synthesis-geodesic-edge-moment/report.md).
Their immutable protocols preserve source hashes, worker counts, exact
input hashes and standard-library interval methods.

The canonical conversion is essential. Write `A=C_T`, `F=C_h`, and let
`X_T=A^2` be the selected address XOR. The framed identity shear has the
literal physical data block

```text
F * [[A^-1, 0], [X_T, A^-1]].
```

Raw-input source encoding and final sink repair/cleanup require two
width-one calls per label when done separately. They change the complete
charge to `Wh+2qh`. The positive framed moment above consequently cannot
be assigned to a canonical `C_h` recurrence. A joint signed exchange with
the same endpoints would instead have a monomial off-diagonal physical
block; such a whole exchange remains to be constructed with every helper
and gauge charged. A tensor-product fitting kernel is also a distinct
candidate, but its naive per-edge side requires `O(v^4)` storage.

Reproduce the retained discriminator from the dedicated worktree root:

```bash
python3 research/integer-mult-breakthrough/code/synthesis/geodesic_edge_side_splice.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/<fresh-actual-UTC>-edge-side/results
python3 research/integer-mult-breakthrough/code/synthesis/certify_geodesic_edge_moment.py \
  --workers 4 --input <completed-edge-side>/certificate.json \
  --output research/integer-mult-breakthrough/work/synthesis/<another-fresh-actual-UTC>-edge-moment/results
```

No native tape, bounded-precision, full-primitive or multiplication
transfer theorem is supplied here. The old master histogram is not
inherited.
