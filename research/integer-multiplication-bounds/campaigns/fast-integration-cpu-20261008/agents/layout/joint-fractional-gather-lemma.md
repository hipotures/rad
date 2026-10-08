# One-pass fractional embedding, joint gather and paired-grid alignment

Written 2026-10-08. This is a fixed-tape movement/interface lemma for the CPU
campaign's packed tensor candidate. It replaces d source-core embedding passes
and d selector exposures with joint scans. Accuracy of the packed forward and
inverse kernels, sparse repair and the terminating multiplication recurrence
are separate dependencies. This file does not claim a complete kappa.

## Parameters and long-record accounting

Let `S=product_i s_i` be the original prime-box volume and `T=product_i t_i`,
where each t_i is a power of two, `3/4<=sigma_i=s_i/t_i<1`, and `T/S<2`.
Let `B=log2(T)`, `d=Theta(B^epsilon)` with fixed `1/2<epsilon<1`, and choose
precision `Q=Theta(d^18)`. The logical bit volume is `V=Theta(TQ)=Theta(n)`.
Choose a binary packet side lambda dividing each t_i; eventual polynomial lambda
is smaller than every axis because each axis is superpolynomial in B.

All metadata values have O(B) bits. Even conservatively computing d rational
floor values with ordinary quadratic-bit division per output record costs
`O(d B^2)` bit steps. This is absorbed by O(Q), since `17epsilon>2`.
There is no claim that a d-axis payload pass has become constant: the algorithm
below performs only one payload scan and pays separately for its small metadata.
Incremental mixed-radix counters provide an optional stronger bound. Initialization
and field/length descriptors are polynomial in B,Q and are explicitly charged.

## A product of monotone injections

In axis i, split the source interval into fractional cores

`J_(i,k)=[floor(sigma_i k lambda), floor(sigma_i (k+1)lambda))`,
`0<=k<t_i/lambda`.

These cores partition `[0,s_i)` in increasing order. Each length is at most
lambda. Map source coordinate `j=lo_(i,k)+u` to the ordinary binary padded
axis coordinate `k lambda+u`; the unused local slots are zero padding.
This one-dimensional injection is strictly increasing. Consequently its Cartesian
product preserves lexicographic order of ALL source records, including zero-valued
records: occupied target slots enumerate precisely the original source stream.

One physical scan now constructs the whole binary T-record output:

1. Enumerate its axis-major mixed-radix address with lengths t_i.
2. Compute k_i,u_i and the actual fractional core lengths.
3. If every `u_i<|J_(i,k_i)|`, read the NEXT source record and write it.
4. Otherwise write one zero record without advancing the source head.

Exactly S records are read, T records are written, and the source head never
moves backward. Returning the input/output heads and clearing temporary metadata
adds only their stream/descriptor lengths. The tape set is fixed independently
of d. A source containing an actual zero still advances the source head at its
occupied slot; occupancy is structural rather than value-dependent.

After this embedding, the source cores already occupy binary target-coordinate
fields `[k_i,u_i]`. Apply ONE known coordinate-bit permutation G that gathers all
k_i fields before all u_i fields. This produces complete lambda^d source packets
in target-core order, with explicit zeros in each source core's unused suffix.
G is a paid binary-slot router, not an oracle for fractional-key sorting.

The inherited arbitrary-coordinate router costs
`O(V B^tau polylog(Q))+poly(B,Q)`. For short scalar records it uses the previously
reviewed three spectator cohorts: an unused complete field is first placed at
the suffix with the OLD interchange interface, supplying paid superpolynomial
records; each cohort avoids that entire field; its placement is undone. All
coordinates, including the polynomial-axis bits if they participate in G, are
covered by the restoration contract. The present lemma does not assume the
original polynomial suffix remains untouched by G or construct its own paid
records with the new router itself.

## Joint nearest-index selection in an inverse packet

The compression selector is `q_j=floor(t_i*j/s_i+1/2)`. It is strictly increasing
on source coordinates because t_i/s_i>1. For a fixed target packet origin k_i
and source fractional core J_(i,k_i), its local target positions are
`q_j-k_i lambda`.

On source outputs whose selector positions remain inside the supplied target
packet, the product of these increasing one-axis maps preserves lexicographic
order. A single forward packet scan can therefore select all required records,
and a single product occupancy embedding writes them into padded source fine
fields. It may read unselected target records while advancing; total traffic is
bounded by the input and padded output packet lengths. It does not expose one
axis or seek a full tensor separately for each source coordinate.

Selection at packet faces needs an explicit qualification. A floor plateau can
make `floor(sigma_i(k lambda+u))` equal the next source-core start at the last
target positions. Nearest-index selection can likewise leave the supplied
target core at source-core ends. Such outputs are not claimed correct by this
unhaloed packet. A sufficient margin includes two rounding positions PLUS the
true kernel radius in the appropriate scaled coordinate. The paired-grid repair
or separately supplied halo must provide them.

## The second grid and the paid global rotations

For a target-grid shift `a=lambda/2`, set
`c_i=floor(sigma_i a)` and use relative source intervals

`J'_(i,k)=[floor(sigma_i(k lambda+a))-c_i,
           floor(sigma_i((k+1)lambda+a))-c_i)`.

They partition `[0,s_i)` exactly: the final endpoint equals s_i because
`sigma_i t_i=s_i`. They have length at most lambda, so the same joint embedding
applies. Source coordinates used by their kernel are GLOBAL coordinates
`c_i+relative_j`, reduced modulo s_i when necessary. Kernels retain these exact
origins and sigma_i; no unsupported translation covariance is assumed.

Obtaining a coordinatewise cyclic source shift would normally cost d scans.
Instead encode c_i as one mixed-radix integer
`C_s=sum_i c_i product_(h>i) s_h`. Left-rotate the COMPLETE scalar source stream
by C_s. On a relative coordinate j with every `j_i+c_i<s_i`,

`decode_s(encode_s(j)+C_s)=(j_i+c_i)_i`.

Thus one flat rotation supplies exactly the desired shifted source on every
packet away from source-period cuts. Disagreement requires an axis overflow;
the source domain's union bound is `sum_i c_i/s_i`. Its images also lie at
coordinate cuts. The construction must exclude neighborhoods of those cuts,
not assume this flat rotation is globally equal to independent axis rotations.

A flat left rotation has a literal fixed-tape implementation: copy its first
C_s records to one temporary tape; copy the remaining suffix to the output;
rewind the temporary tape and append its prefix; return/clear the heads.
Traffic, including all head returns, is O(SQ). Counter/header work is charged
within the above metadata bound. The global target rotation uses the same
implementation with radices t_i and shift a in each axis.

For grid1 expansion, left-rotate source, embed shifted fractional cores, apply
G, compute packets, undo G and right-rotate the TARGET stream by
`C_t=encode_t((a)_i)`. For grid1 compression, reverse the source/target roles
appropriately: its target input is left-rotated, its output is depadded and
right-rotated in the SOURCE prime-box stream. Grid0 uses no shift. Both results
therefore have the same canonical global output order before their validity
masks and sparse repaired values are merged.

The forward side lambda_F can be larger than the inverse phase-exception strip.
Accordingly include original physical period-cut neighborhoods of width
`O(lambda_F+kernel_radius)` explicitly. Their volume density is at most a
constant times `sum_i lambda_F/s_i`, superpolynomially small, but it must be
part of the sparse SOURCE-packet accounting. The inverse's thinner phase strips
alone do not justify all forward flat-rotation boundaries.

## Final source assembly and fractional paired faces

After a compression packet operation, write a complete binary fine field and
restore G. A single lexicographic occupancy deletion scan removes exactly the
padding slots introduced by the corresponding fractional embedding, yielding
the source-prime stream in increasing coordinate order. This is the inverse
of the monotone injection. Grid1 additionally performs its paid flat source
rotation, then uses the separately classified cut masks.

For source-grid validity, the two grids have fractional boundaries rather than
literal equal source side lengths. Consecutive grid0/grid1 boundaries are
separated by at least `sigma_i lambda/2-1`. If this exceeds2R, radius-R bad
strips of the two grids are disjoint in the SAME axis. Consequently an output
bad in both grids requires two different axes. If each axis has at most
`2R t_i/lambda` bad source indices per grid, the product-space bad intersection
is bounded by the sum over ordered pairs i!=j of

`bad0_i * bad1_j * product_(h!=i,j) s_h`.

For sigma_i>=3/4 this is a constant times `d(d-1)(R/lambda)^2 S`.
The small-side negative `(s,t,lambda,R)=(13,16,4,1)` has overlapping same-axis
bad strips; the separation premise is indispensable. Rounding margins must be
included in R. This fractional bound replaces a literal lambda^d formula when
source core lengths differ by one.

## Source replication and factor generation remain paid

The union of bad OUTPUTS alone is not a sparse-input guarantee. Expanded source
packets must be counted with their multiplicity. For the model `R/lambda=d^-3`,
pairwise radius-R face packets expanded by another radius R have total source
volume at most

`16 d(d-1)(R/lambda)^2 (1+2R/lambda)^(d-2) T = O(T/d^4)`.

For phase strips of relative width `delta=d^-4`, expanded by an exceptional
radius with `theta R_exc<=d^-7`, the summed source volume is

`d(delta+2theta R_exc)(1+2R/lambda)^(d-1) T = O(T/d^3)`.

This counts duplicated records, not only their distinct union. The actual
packet generator, kernels and shrinkage need their separate proof/check.
The coordinating agent owns that sparse-repair construction.

Axis factor catalogues are not free random-access advice. One may read each
axis's ENTIRE polynomial(t_i,Q)-size catalogue for each cell: its logarithmic
size is O(B^(1-epsilon)), whereas the cell has logarithmic volume
Theta(d log lambda)=Theta(B^epsilon log B). For epsilon>1/2, the latter dominates
any fixed setup polynomial degree. Even d catalogue scans per cell are therefore
absorbed eventually by its actual fine-field payload. Construction of the
axis catalogues themselves is polynomial in t_i,Q and remains n^o(1).

Tensor weights and kernel products must also avoid d full-Q arithmetic
operations per coefficient. Use a fixed-tape LIFO stack of rounded PREFIX
products. At a mixed-radix carry recompute only the changed suffix from its
retained parent prefix, never update a long-running product by multiply/divide.
When every radix is at least2, the number of prefix products constructed is
at most twice the emitted tensor coefficient count, plus initialization.
Sequential factor pages and their rewinds amortize to complete emitted fibers.
Rounding errors accumulate along a depth-d product, not along all coefficients;
their magnitude/reserve bounds are the analytic kernel's responsibility.

## Exact controls, negatives and reproduction

[check_joint_fractional_embedding.py](code/check_joint_fractional_embedding.py)
independently checks one-pass occupied order, both shifted floor-origin maps,
the true global mixed-radix rotation and a binary coordinate gather model.
[Its result](results/fractional-core-embedding.json) passes280 cases in1--4 axes,
575536 target writes,310554 sequential source reads and406853 safe selector
outputs. It retains73607 boundary selector exclusions rather than declaring
them correct. The wrong fixed-length end truncation and the floor-plateau
example are explicit negatives.

[check_joint_selector_and_fractional_faces.py](code/check_joint_selector_and_fractional_faces.py)
checks increasing joint nearest selectors and final source provenance, plus24
fractional paired-face cases in2/3/5/9 dimensions and the small-side negative.
[The result](results/joint-selector-fractional-faces.json) retains exact counts.

[check_joint_grid_packets.py](code/check_joint_grid_packets.py) independently
checks2237312 packed global rotations,1545429 safe exact matches, expanded
source-volume inequalities and actual one-integer Kronecker convolutions on
interior coordinates. [Its result](results/joint-grid-packets.json) retains a
boundary carry negative and a within-cell fine-bit-flip negative. The first
development alias fixture used the most significant axis rather than the least
significant axis and was corrected; it is not an external mathematical failure.

Run each script with `--workers 4 --output <fresh ignored directory>` from the
repository root, with OMP_NUM_THREADS, OPENBLAS_NUM_THREADS and MKL_NUM_THREADS
set to1. Python3.14.4 and the standard library suffice. Seeds, source digests and
case timings are in the compact results. The largest rotation branch took
3.672seconds; the fractional embedding uses exact provenance labels, not true
Gaussian arithmetic. Finite gather calls model the independently pinned binary
router contract and do not supply another proof of that native primitive.

The separately authored analytic dependencies are
[forward packet precision](../inverse/reports/packed-forward-precision.md),
[regular Laurent interface](../inverse/reports/regular-laurent-interface.md) and
[global Gaussian locality](../inverse/reports/global-gaussian-locality.md).
Native movement provenance is the historical RaD arbitrary-routing review at
commit `6b32837aee0561af85e4efaca21af07b9f2749d2` and the current campaign scout's
public source snapshots. The one-pass fractional product embedding, flat joint
grid shift with explicit cut exclusions and joint selector/assembly are
campaign-derived interfaces; worldwide novelty is not claimed.
