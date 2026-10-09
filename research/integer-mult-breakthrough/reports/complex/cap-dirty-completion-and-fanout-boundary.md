# Dirty cap-block completions and the terminal reader boundary

The `k5` cap-aware rank reductions admit exact in-place Gaussian-dyadic scalar
completions. They retain all four banks of a `j3` parity block and all eight
banks of a `j4` block. Three output channels are read, while one or five kernel
banks remain necessary for the declared inverse. A separate monotone
whole-source-cube reader chronology loses its optimistic rank deficit even
when only the final source cube's shared readouts are charged.

The sources are
[`paired_cap_dirty_completion.py`](../../code/complex/paired_cap_dirty_completion.py)
and
[`paired_cap_fanout_flags.py`](../../code/complex/paired_cap_fanout_flags.py).
The first has no imports beyond the standard library; the second imports only
the first. Both use exact rational arithmetic and binary label ranks. The
coordinator's cap-channel derivation is separately reviewed in
[`cap-channel-proof-independent-review.md`](cap-channel-proof-independent-review.md).
This package contains finite scalar words, geometric witnesses and a scoped
negative architecture. It contains no complete native side supplier or
multiplier.

Each input bank in a local parity block is an already paid aggregate
`g_u=sum_{outside J} x_(u,outside)`. Input aggregation and its dirty auxiliary
stock are not provided by a local matrix inverse. The input and output selector
orders in every certificate are explicit. The side sign is `-f5(overlap)`;
changing to the central sign changes read coefficients without changing rank.

For `j3`, parametrize the parity class by two selector bits. The block is
`(J4-4X11)/8`, has rank three, and kills the constant character. Its four
actual rows sum to zero. Retain its first three actual rows and the constant
kernel row. The resulting four-bank completion has determinant `-1/8`.
For `j4`, parametrize a parity class by three bits. The block is minus the
projector onto the three characters of weight two. Antipodal rows are equal;
its four distinct rows sum to zero. Retain the first three actual rows and
all five kernel characters, of weights zero, one and three. This eight-bank
completion has determinant `-32`. Both determinants are units in `Z[1/2]`.

The word generator uses integer Euclidean row shears and only power-of-two
unit scales. Every exchange is four paid scalar gates, including its sign
correction. There is no odd-denominator inverse and no uncharged bank
permutation. The generator is deterministic, with no shortest-word claim.
It independently reconstructs the complete forward matrix and inverse, all
target rows, and every retained kernel direction. The literal payload tests
use all four Gaussian fields, hence all eight real/imaginary components per
bank. Removing a parked bank, an inverse mutation or a decoder contribution
is rejected.

| Parity block | Retained banks | Read channels | Parked banks | Forward gates | Inverse gates | Forward prefix L1 | Inverse prefix L1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `j3` | 4 | 3 | 1 | 51 | 51 | 8 | 16 |
| `j4` | 8 | 3 | 5 | 186 | 186 | 16 | 32 |

Every coefficient-multiplication temporary is included in those prefix
bounds. The maximum extra coefficient-grid bits are three in both forward
words, two in the `j3` inverse and three in the `j4` inverse. These are scalar
linear-map charges relative to the actual incoming grid. They are not a
global address-phase precision bound. Dirty-bank restoration is exact at the
endpoint; it does not justify omitting inverse-prefix temporaries.

All scalar gates must act at the identical actual common cap representative,
including its phases and affine routing. Scalar gates commute with a common
address operator, which justifies the scalar four-field check. Equal frame
dimension or an isomorphic label span is insufficient. This package does not
materialize the large Gaussian address matrices of those cap representatives.
The arbitrary-subspace `L_E` compiler is a separate inherited algebraic
interface, and its complete native routing/guard contract remains charged.

The aggregate input support dimensions are three at `j3` and two at `j4`;
their common cap has dimension five. A closed component that enters this cap,
performs the word/read/inverse there and returns to the original input frames
therefore pays respectively `16` and `48` total entry/return ranks per parity
block. The all-`J` weighted sum for these two block sizes is `800`. This is a
named closed wrapper bill, not a necessary surcharge on all global
chronologies. A monotone component may instead postpone its inverse until
full, use already paid transitions, or restore parked data through a different
chronological word. Such a claim needs its literal common-frame schedule.

Independent completion of all proper blocks retains raw/live/parked counts
`211/141/70` when every `J` is available. The seventy parked directions are
twenty from `j3` and fifty from `j4`. Independent completions do not implement
a 141-role physical word. At nine coordinate pairs the unavailable `j0`
reduces raw/live counts to `210/140`; parking remains seventy. Shared parking
and delayed dirty births are open mechanisms, with exact later restoration
and frame payments required.

The actual-row decoder helps, but it still broadens the target flag. For one
fixed pair of source and target cubes, a single raw target pattern spans three
target-label directions at `j3` or two at `j4`, including the free outside
selector bits. Each retained actual row serves its own patterns and the
missing dependent row's patterns; its fanout span is four in either case. A
Fourier channel serves the whole target parity class and has span five. The
exact support and decoder checks include every source/target entry, rather
than inferring a frame from scalar rank alone.

Allowing every target cube with the same proper intersection makes these
flags larger. At `p9`, the retained actual-row fanout spans are nine at `j3`
and ten at `j4`. A common label subspace `E` contained in every recipient cap
has dimension at most nine or eight respectively. These dimensions describe
the nested `L_E` interface, not the ambient dimension of an arbitrary
Lagrangian. At `p12`, the corresponding fanout spans
are fifteen and sixteen; the maximum common-frame dimensions remain nine
and eight. Fourier fanout has still smaller admissible common frames. These
are upper dimensions, not constructions of free readers.

The second experiment tests a precise whole-cube readout schedule. Assume all
earlier source cubes' literal contributions remain in each target's
monotonically growing frame. The final source cube is `0,1,2,3,4`; the other
source cubes have been processed first in any order. For every recipient of
its representative `j3/j4` rows, the checker constructs `h-1` independent
actual previous source labels with nonzero side coefficient and dot product
zero with the target. The target's retained frame is therefore its full
hyperplane `T^perp` before these final reads. Its own cube and the final source
cube are omitted from those witnesses.

The checker handles the first `J` of each size and target parity zero. Paired
coordinate permutations cover all other `J`, while flipping one shared
selector coordinate exchanges the parity blocks and preserves every rank,
literal coefficient and chronological premise. Thus the weighted counts
below use exact symmetry, not an unreported full enumeration of all `J`.
Complete witness digests and representative original-source bases are
preserved; all witnesses regenerate from the frozen source.

A single channel carrier read into distinct final target frames must visit
each actual `T^perp`. Two different codimension-one binary subspaces have
Grassmann distance two. Starting at its dimension-five source cap, ending
at full, and making `n` such common-frame reads therefore costs
`h-5+2(n-1)`, rather than the geodesic `h-5`. Any order of distinct targets
pays the same extra `2(n-1)`. Unit phase or affine gauges can add work; they
cannot remove the distinct Lagrangian distances. This argument also allows
arbitrary intermediate Lagrangians, because triangle inequality bounds each
adapter between consecutive fixed reader frames.

The displayed geometric widths use one selected label column. The transfer
to the paired recurrence below retains its literal columnwise repeated-frame
interface. A general entangled cross-column supplier or a different primitive
pricing is a changed architecture. It is not excluded by multiplying this
single-column calculation without a separate tensor proof.

| Pairs `p` | Original banks `v` | Last cube's extra ranks per core | Retained three-core deficit | Deficit after only these reader charges |
| --- | ---: | ---: | ---: | ---: |
| 7 | 672 | 1,740 | -1,176 | -6,396 |
| 8 | 1,792 | 4,140 | -448 | -12,868 |
| 9 | 4,032 | 7,500 | 2,016 | -20,484 |
| 12 | 25,344 | 23,340 | 34,848 | -35,172 |

The retained deficit is `2v-3q(h-4)`, with `q=2p(p-1)` copied central stars.
Only this one final cube's `j3/j4` reader excess is subtracted; earlier
reader costs, kernel retirement, aggregation, scalar work and native passes
are all optimistically free in this exclusion. It is consequently a decisive
negative for the named monotone whole-cube ordering and separate common-frame
scalar readers. It is not a bound on interleaved reads, target-bank mixing,
copied readers, changed original ports, signal cancellation changing current
frames, shared parking, or birth reuse.

For context, a literal independently copied face-tree materialization uses
one source copy per available proper `J` for every original bank. It therefore
uses `15v/25v/30v/31v` side carriers at `p7/p8/p9/p>=10`. This is an executable
tree count, not a lower bound; shared zeta evaluation or existing-bank words
can change it. The number of aggregate roots and their kernel completion
stock must not be substituted for those paid input copies. Neither this
count nor the local cap support supplies the simultaneous actual target-frame
schedule required by a cheaper reader.

The full completion run is
[`20261009T092559Z-complex-cap-dirty-completion`](../../runs/20261009T092559Z-complex-cap-dirty-completion/report.md)
and passes all four parity cases in 0.063 seconds with four workers. The full
fanout run is
[`20261009T093929Z-complex-cap-fanout-flags`](../../runs/20261009T093929Z-complex-cap-fanout-flags/report.md)
and passes all four paired-coordinate sizes in 3.496 seconds with four workers.
The config/manifest bind the original source snapshots, complete certificates,
logs and bounded reproductions. A compact publication summary omits only the
long generated elementary-word arrays and links to the unchanged complete
original; the source regenerates every omitted gate.

```bash
python3 -B research/integer-mult-breakthrough/code/complex/paired_cap_dirty_completion.py --workers 4
python3 -B research/integer-mult-breakthrough/code/complex/paired_cap_fanout_flags.py --workers 4
python3 -B research/integer-mult-breakthrough/code/complex/paired_cap_dirty_completion.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/paired_cap_fanout_flags.py --workers 1 --bounded
```

No random seed, external source import or optional package is required.
Optional `--output` exclusively creates a new certificate file. The useful
next mechanism is a complete interleaved or jointly mixed readout that avoids
the terminal reader premise while explicitly carrying all parked dirty data
and paying its source/target frame history. Scalar rank alone cannot justify
a new parameter sweep or an exponent claim.
