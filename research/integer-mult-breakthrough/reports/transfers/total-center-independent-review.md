# Independent single-total center/null scalar review

The single-total feature basis has a uniformly dyadic inverse for every
ambient size `h>=7`, with entries on grid `1/4` and absolute value at most six.
The complete reversible scalar word and central decoder pass an independent
replay. A conditional common-frame scalar guard has four extra fractional bits
at any inverse prefix and two at its endpoint. These results do not establish
physical address compatibility, native routing, a complete phase primitive or
an exponent improvement.

The input is the immutable
[total-center-local-words.json](../../fixtures/complex/total-center-local-words.json),
SHA256 `11d8de267891f2ee4cc19ec503c93c73c9d06416995e32278b9e3de9bd63dfc7`.
It retains the producer source hash, all 21-bank base gates, the five-bank
border gates, matrices, exact coefficients and row/source orders. The reviewer
imports no producer source. It imports only this track's previously published
rational arithmetic, literal scalar replay and temporary-observation helpers,
pinned by the effective source protocol.

## Basis and all-size inverse classes

For the five-subset source slice, the feature at pair label `(0,1)` is the
literal total `T=sum_S x_S`. Every other feature is pair incidence
`P_ij=sum_{S containing i,j} x_S`. Each source contributes to exactly ten
ordinary pair features, hence

```text
P_01 = 10 T - sum_{(i,j) != (0,1)} P_ij.
```

This identity uses integers; it does not divide by five. Replacing `P_01` by
`T` keeps `q=binom(h,2)` features. The original ordinary pair-incidence minor
need not have a dyadic inverse, so replacing the row is material.

The base at `h=7` has all 21 five-subsets as pivot sources. The reviewer
reconstructs its feature matrix directly, checks both inverse products and
computes its absolute determinant as `2^12` using exact fraction-free
elimination. The largest inverse entry is six already at this base.

For each new point `j>=7`, append the five sources obtained by deleting one
point from `{0,1,2,3,4}` and adding `j`, followed by
`(0,1,2,i,j)` for `5<=i<j`. Append pair rows `(i,j)`. The diagonal block is

```text
B_j = [[J_5-I_5, U_j], [0,I_(j-5)]],
```

where every column of `U_j` has its first three entries one and the last two
zero. Its determinant is four. Its inverse first five-by-five block is
`-I_5+J_5/4`; the extra-column entries are `1/4` on the first three rows and
`-3/4` on the next two. Lower-left blocks are zero. Thus the complete pivot
determinant has absolute value `2^(2h-2)`.

There is a finite closed inverse-class proof, rather than a denominator
extrapolation from small dimensions. Write the upper block between new points
`j<ell` as `u_j e_j^T`, with `u_j=(1,1,1,0,...)`. Then `B_j^-1 u_j` is
`(-1/4,-1/4,-1/4,3/4,3/4,0,...)`. The functional `e_j` reads a bottom identity
coordinate in the later block; it therefore annihilates every such transformed
`u`. Every path through two consecutive new-point blocks vanishes. The
remaining base-to-new paths have only four classes: the first five columns,
the extra columns with old point five or six, and all later extra columns.

The reviewer computes these classes directly from the immutable 21-by-21 base
inverse and the feature incidence. All 609 base and class coefficients lie on
grid `1/4` and have absolute value at most six. Together with the border and
cross-block formulas, this proves the bound for all `h>=7`. Full two-sided
inverse products are also checked at `h=7,8,10,16`. This is an ordinary
coordinate-null completion, distinct from the invariant spectral split ruled
out by the `5/14` projector in the
[spectral channel report](odd-weight-spectral-channels.md).

Let `M` be the pivot minor and `G` the nonpivot feature columns. The complete
bank basis is

```text
B = [[M,G], [0,I]],       B^-1 = [[M^-1,-M^-1 G], [0,I]].
```

The identity coordinates remain present. Dropping them would change the
dimension, dirty state and inverse contract. Every feature column has at most
11 nonzero unit entries. Thus every full inverse coefficient is at most 66 in
absolute value and its row-L1 norm is at most `66v`, where `v=binom(h,5)`.
Its mathematical endpoint grid is `1/4`.

## Complete word and central decoder

The complete word processes the base and then each border in increasing
maximum-point order. Each block is transformed locally before its outputs
gather from later, still-original pivot inputs. Nonpivot sources are added
only at the end. The inverse reverses this complete sequence, preserving the
future-input timing. Every literal coefficient, including 2, 3 and 4 inside
the local word, is retained and its multiplication temporary is observed.

The four-worker repaired run at actual UTC
`2026-10-09T01:01:42.708457+00:00` passes 329 complete basis columns at
`h=7,8,10`, four arbitrary dyadic dirty fields per size and both full endpoint
directions. It takes about 1.640 seconds. The scalar word sizes are 248, 624
and 2,743 operations. There are no extra scalar data banks. The `h=16` case
checks the closed inverse only; no complete 4,368-bank word is claimed to have
been replayed. [Protocol and compact outcomes](../../runs/20261009T010142Z-transfer-total-center-review/).

Independently derive the central decoder from the ordinary pair formula

```text
alpha_ij(target) = (1/4)*[i,j in target] - (3/32)*|{i,j} intersection target|.
```

Eliminating `P_01` gives coefficients `alpha_ij-alpha_01` for retained pair
features and `3/8+10 alpha_01` for the total. The latter is exactly one of
`3/8,-9/16,1`. Every decoder coefficient has denominator dividing 32. The
reviewer checks all 67,081 ordered source/target entries at `h=7,8,10` against
`(intersection-1)(intersection-3)/8`, including diagonal one and every distinct
odd-intersection zero. No selected-entry comparison is substituted for this
complete finite control.

Classifying a target by its overlap 0, 1 or 2 with pair `(0,1)` gives the three
decoder row-L1 values

```text
(15h-43)/32,
(3 binom(h-5,2)+68)/32,
(2 binom(h-5,2)+25(h-5)+32)/32.
```

Their maximum is checked against every finite target. These exact decoder
values improve on the earlier denominator-256 mixed scatter component, but
do not independently establish a complete phase-layer precision guard.

## Conditional uniform scalar prefix guard

Assume all complete roles have the same actual address operator, common
mathematical grid `2^-P` and component bound `A`. The local prefix audit uses
complete symbolic coefficient rows and includes each `coefficient*source`
temporary. The base forward word has no extra fractional bits and row-L1
prefix bound 52. Its inverse has two fractional bits and row-L1 bound 70.
The corresponding border bounds are 0/2 fractional bits and 8/7 in row-L1.

The full forward word therefore has zero extra fractional bits and component
bound `(52+h+v)A`: future original inputs, extra bottom columns and nonpivots
are all counted. A simple conservative inverse prefix bound is

```text
70 (1+6q^2)(1+v) A,        extra fractional bits <= 4.
```

To see the magnitude bound, undoing nonpivots first gives each pivot input
bound at most `(1+v)A`. Every completed trailing block is an exact part of
the closed inverse and is bounded by `6q` times this value. A current block
reads at most `q` such original fields through unit cross/extra shears, giving
the factor `1+6q^2`; its literal local prefix multiplies the bound by at most
70. This is conservative polynomial control, not a measured optimal guard.

The grid induction is sharper than multiplying a denominator bound by the
number of blocks. All bottom identity coordinates stay on grid `2^-P`.
New-point cross-block reads select precisely those bottom coordinates. Each
border inverse therefore starts on grid `2^-P` and reaches at worst
`2^-(P+2)`. Base cross reads may use returned first-five fields on grid
`2^-(P+2)`, so the final base inverse reaches at worst `2^-(P+4)`. The exact
full endpoint is on grid `2^-(P+2)` by the closed inverse formula. The
physical implementation can keep the wider fixed grid; this argument grants
no free Fraction reduction, reencoding or binary normalization.

Finite dirty-field observations remain within these stated bounds. They are
controls of the conditional scalar lemma, not a proof that a native address
word has the same scratch usage. Different actual source frames require paid
adapters; the earlier
[independent common-frame counterexample](center-basis-independent-review.md)
still applies. Multiplication buffers, exchange implementation, phase children,
all live ancestor/companion fields and row allocation remain separate charges.

## Failure provenance and reproduction

The first reviewer attempt at `00:59:46` incorrectly asserted a base maximum
of `3/2`. The immutable fixture and producer already state six, which the
direct inverse check confirms. This is a reviewer bound assertion failure,
not a counterexample to the producer's component. The failed attempt is kept
at [its original run](../../runs/20261009T005946Z-transfer-total-center-bound-failed/).
The rejected reviewer source hash is
`2fc64a7051425c8753353f2b17f573f6b452bd3869f09a4052effbcaf92eca83`.
Reverse the retained
[one-line correction patch](../../fixtures/transfers/total-center-base-bound-correction.patch)
from the final source to reconstruct it. This recovery was executed and
hash-checked; the [receipt](../../runs/20261009T010142Z-transfer-total-center-review/results/source-recovery.json)
binds both source versions. Original raw attempts are unchanged.

The bounded check uses only Python's standard library, this track's retained
scalar helper source and the pinned literal producer fixture:

```bash
python3 research/integer-mult-breakthrough/code/transfers/total_center_review.py --workers 1 --small
```

Omit `--small` and use `--workers 4` for the complete four-size experiment.
Optional `--output <fresh-directory>` rejects an existing path. All effective
source/config/fixture hashes and seeds are recorded in the protocol. The
final reviewer source SHA256 is
`a29dc80f82c5e6030c09023bcddc04f2c24f5621ef92541a087f71fdc9117dc6`.

This accepts the scalar basis and decoder, proves their stated uniform
coefficient classes, and gives a conditional all-size scalar prefix lemma.
Physical release chronology, native complexity, an improved child ledger,
all-size multiplication transfer and formal verification remain open.
