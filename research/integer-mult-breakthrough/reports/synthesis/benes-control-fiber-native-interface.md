# Selected-only control-fiber compaction

Status: **EXACT FINITE ADDRESS AND GAUSSIAN OPERATOR COMPONENT**, with a
**CONDITIONAL NATIVE ROUTING INTERFACE**. This changes the activity layout.
It supplies neither a shorter subset-zeta scalar word, a faster recursive
zeta supplier, nor a multiplication exponent.

## Question and leverage

Can a tensor row addition be restricted to its active columns without
permuting every complete control or inactive chunk? A full-chunk prefix
codec has a correct mathematical shape, but its initial permutation was
unpriced. Here the complete control chunks stay fixed and only selected
action bits move. This avoids interpreting a variable-length chunk
permutation as a free coordinate rename.

For a fixed control vector, a column is active when both selected control
bits match a fixed pattern. All three nonmatching control patterns remain
in the original cube. With f columns the exact activity volume is
`a ~ Binomial(f,1/4)`. If a hypothetical eight-row Z3 word had eleven
additions, the idealized activity profile would have substantial exponent
leverage. No such word has been found. The ordinary twelve-addition word
does not contract the corresponding uniform power moment; routing and
precision improvements alone cannot supply its missing saving.

## Real slots and canonical labels

The input has three consecutive bands of f complete K-bit chunks and
twelve additional real K-bit guard chunks, all within the existing address
cube. Here f is a power of two at least four. The selected position of a
chunk is K-1. Guard chunks can hold arbitrary address values.

Place the guards so each of twelve quarters contains f/4 active complete
chunks followed by one complete terminal guard. At most twelve full-K
swaps place the guards. The resulting active role intervals differ from
the canonical bands by only a constant number of positions. At most 48
additional swaps correct band roles, hence at most 60 full-K swaps per
placement. The executed cases use 15,18,20,21 swaps at f=4,8,16,32.
The all-size bound is conservative and does not assert that 21 is optimal.

The placement does not sort within-band labels. All three actual label
orders are retained. The corrected masks reconstruct the two canonical
control vectors from these orders, classify each original action column,
then conjugate the desired action permutation by the tracked action
order. After the inverse stock placement, active action bits occupy the
canonical first a chunks. No growing payload shuffle is hidden in that
metadata computation.

## Benes chronology

The alternating-cycle construction routes any permutation on f power-of-two
wires in `2 log2(f)-1` stages. A stage pairs wires at distance 2^k.
The linear selected-position permutation P moves index bit k to the high
index bit, putting each pair into corresponding contiguous action halves.
P fixes every allocated guard selected position and every unselected bit;
its physical map uses the explicit gapped selected-position list.

On complete action and control1 bands, first use the three identity XOR
shears and then the three P/P^-1 shears. Together these six words produce
`(P action,P^-1 control1)` and restore the third complete band. They operate
only on the gapped active selected positions. Internal guard positions have
zero mask; the final guard position is outside the allowed mask.

At the completed alignment boundary, decode control1 by P, reconstruct
both canonical control label orders, and compute that stage's switch mask.
Control2 has stayed unchanged. For action quarters q0,q1,q2,q3, execute

```text
q0 ^= mask0 & q2, borrowing q1
q1 ^= mask1 & q3, borrowing q0
q2 ^= mask0 & q0, borrowing q3
q3 ^= mask1 & q1, borrowing q2
q0 ^= mask0 & q2, borrowing q1
q1 ^= mask1 & q3, borrowing q0
```

Each donor differs from both the target and the complete borrowed quarter.
The two external control bands remain fixed throughout these six words.
A donor can change between words, but stays fixed during its own eight
rotations and exceptional correction. Masks are recomputed only from the
current immutable donor and external controls, never from temporarily
contaminated target or companion fields. The final six inverse alignment
words restore both complete control bands.

Thus a stage uses eighteen packed XOR words, each with eight modular
rotations and a complete-record exceptional correction. The actual finite
implementation executes all of them. Reverse stage order gives the true
inverse. Every borrowed complete slot is arbitrary and restored at each
word endpoint; no zero address scratch or additional scalar bank is used.

## Gaussian child and complete fibers

Let `G(c)=[[1,0],[c,1]]` act on the selected action bit of each active
column. Controls and every unselected plane remain fixed. Selected-only
compaction makes the a active bits the selected positions of the first a
canonical complete K-chunks. For every fixed complete control vector,
high inactive action chunks and guard address, those low chunks form a
complete `2^(aK)` child cube. All K-1 unselected bits of each child chunk
remain spectators. Every record is retained, including a=0 identity sectors.

The exact child is

```text
G(c)^tensor a = diag(c^weight) Z_a diag(c^-weight).
```

The same compaction and its actual inverse conjugate this child to the
original canonical `G(c)^tensor f` activity operator. No control chunk,
inactive symbol or full record is discarded. Fibers of different widths
can occur in their natural prefix order; a native variable-width traversal
and its metadata/head/return bill still need binding. Equal-width grouping
is not asserted to be free or necessary.

The source compares every within-control matrix coefficient in the
retained selected models. Off-control and off-spectator coefficients are
zero by the actual endpoint/frame identity. It also replays arbitrary
Gaussian-dyadic fields and the inverse `G(-c)`. This is not an enumeration
of the exponentially larger full guard cube.

## Finite evidence and preserved gap

The [contract](../../fixtures/synthesis/benes-control-fiber-contract.json)
pins all sources, concrete stock labels, negative witnesses and child
fixtures. Completed attempts are immutable:

| Attempt | Actual protocol start UTC | Evidence |
| --- | --- | --- |
| [Endpoint-only](../../runs/20261009T065823Z-synthesis-benes-control-fiber-probe/report.md) | 06:58:23.616010 | Semantic XOR endpoints; rotations not executed |
| [Literal changed matching](../../runs/20261009T072521Z-synthesis-benes-guarded-control-word/report.md) | 07:25:21.968030 | Literal rotations/correction; masks use placed band indices |
| [Canonical v3](../../runs/20261009T073016Z-synthesis-benes-canonical-control-v3/report.md) | 07:30:16.587779 | Corrected canonical control label reconstruction |
| [Gaussian fibers](../../runs/20261009T073622Z-synthesis-benes-gaussian-fiber-operator/report.md) | 07:36:22.633152 | Exact kernels, gauges, dirty fields and inverse |

V3 checks every selected address for each of four fixed control patterns
at f4/K1 and f4/K2: 16,384 cases per shape. Another 256 complete addresses
each at f8/K6 and f16/K6 bind real carry guards and unselected planes.
Omitting current control decoding, canonical label reconstruction or
exceptional correction fails with retained witnesses.

The Gaussian run checks 1,048,576 within-control kernel entries and
131,072 arbitrary dirty Gaussian values with inverses, for
`c=1,-1,i,(1+i)/2`. Each coefficient/shape has all four fixed control
patterns and the exact histogram `binom(f,a)*3^(f-a)` per pattern.
Omitting the required input gauge fails for the nontrivial coefficients.
The largest observed common denominator reserve is six bits in this
finite field test; this is a measurement, not an all-size precision bound.

Independent complex-track review identified the version-two matching gap.
Those bytes and successful own-matching results remain unchanged. V3
repairs the reusable canonical interface in a fresh source and run; a
bounded verifier reproduces the old version's disagreement with the
canonical consumer.

## Conditional native bill and remaining obligations

The frozen-control native routing extension permits a mask depending only
on immutable chunks outside the current target and companion. Each complete
word corrects all exceptional full records, preserving every payload field.
Conditional on its original stream/long-record contracts, an individual
word of complete slot width L has bill

```text
O(V*(L^tau+1) + M*(A^3+C_G(A)) + delta*M*A*(R+A)),
V=M*R, delta<=min(1,80*(L/K)*2^-K).
```

Here mask computation includes canonical label reconstruction and Benes
cycle coloring. A conservative polynomial per-record setup bound is
retained; it cannot be erased before establishing the complete long-record
condition. The fixed-slot word count is O(log f), and stock placement uses
four placements around one forward/child/inverse component, each with at
most 60 separately charged full-K swaps. This is a conditional analytic
bill, not a measured fixed-tape runtime. Small K1/K2 experiments rely on
exact correction and do not establish a sparse exception set.

The source does not yet supply the recursive Z_a time, whole-caller row
traversal, complete magnitude/rounding/scalar-temporary charges, or the
outer multiplication transfer. Full-width rounding grids and a genuine
nonunit endpoint norm contract remain required. The twelve allocated guard
axes must be processed by the changed Z primitive, not by importing a C
guard cost. Non-power-of-two selected widths require paid residual axes;
clean padding is not authorized by this construction.

The coordinate-independent saved metadata, if used, belongs to every full
record's cost and is erased/restored as required. The finite implementation
recomputes masks at completed word boundaries. It does not infer that a
poly(A)-time numerical permutation key is a cheap native payload route.

## Reproduction

The five authored sources and the contract are standard-library only.
The bounded [verifier](../../code/synthesis/verify_benes_control_fibers.py)
reads immutable inputs and optionally writes to a fresh output directory:

```bash
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_benes_control_fibers.py --component all
```

Expected output is `PASS BENES CANONICAL CONTROL FIBERS`; the completed
bounded attempt takes about 0.67 seconds and covers 256 literal full
addresses, 4,096 kernel entries, 256 dirty field values, nine gauge
negatives and the three retained address corruptions.

Each discovery source accepts `--workers 4 --output <fresh-directory>`;
its retained protocol records the exact tasks, seeds and source closure.
Ignored raw namespaces are listed in the contract. Originals remain
unchanged and are deterministically regenerable. Complete compressed
publication, when added by the coordinator, must identify original hashes
and any omitted data. No private dependency or installed solver is needed.

Next discriminator: supply a shorter scalar circuit or a changed activity
profile, then bind the full recursive native and numerical contract. This
component alone supports no larger kappa.
