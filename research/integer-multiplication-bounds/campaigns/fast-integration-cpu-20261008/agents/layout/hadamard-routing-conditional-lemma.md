# Coordinate routing through normalized Hadamard layers: conditional scope

## Exact algebra and precision

For disjoint source/target pairs `(s_i,t_i)`, let `D` multiply the record at
address x by `(-1)^(sum_i x[s_i] x[t_i])`. With
`H0=(1/2)[[1,1],[1,-1]]` on each target, direct multiplication gives

`H0_targets D H0_targets = 2^(-m) P_CNOT`,

where m is the number of pairs and P_CNOT moves x to the address whose target
bits are XORed with their respective source bits. The parity is evaluated on
the physical address between the two complete target transforms. Each target
transform and the phase scan is a contraction in the maximum coefficient norm.
Disjoint pairs may be split into groups without changing the resulting map.

A permutation of b coordinate bits is a product of two involutions. On each
cycle, use reflections `A(i)=-i` and `B(i)=1-i`; their composition is the
one-step cycle rotation. An involution is a matching of disjoint coordinate
SWAPs, and each matching is three CNOT layers, with directions alternating.
Consequently any known coordinate permutation has a circuit with six CNOT
layers, twelve tensor H0 calls before any further physical splitting, and six
address-parity scans. The total deferred scalar restoration is `2^S`, with
`S=3(number of matching pairs across the two involutions)<=3b`.

Encode a Q-bit payload word as a bounded real dyadic coefficient, append a
zero imaginary component, and reserve P fractional bits. At most 2S individual
Hadamard bit factors occur. Even truncating after every individual factor
contributes at most one P-grid unit per factor; subsequent operations contract.
Thus the final coefficient error before restoration is at most `6b*2^-P`.
If `P>=Q+S+ceil(log2(12b))+2`, restoring the deferred scale and rounding recovers
every original Q-bit word exactly. A completed native H0 approximation requires
its own documented guard in addition to this calculation. Formatting, parity
evaluation and final recovery scan each record once; if Q dominates b, their
address work does not add a payload-volume factor b.

This word encoding is substantive only for long payload words. Representing
each individual payload bit as a Q-bit coefficient would multiply volume by Q
and is not authorized by this lemma. No arbitrary computed-key permutation or
nonlinear CRT residue update follows from this known-coordinate circuit.

## Earlier selected-mask premise and native internal dependence

The original six-CNOT construction requires a completed H0 layer on each
chosen target mask. No direct arbitrary-mask native layer is proved here.
The whole-mask construction below removes that external exposure requirement
by transforming every main-axis chunk, while retaining native internal BIT
basis changes.

Pinned public source `CrocSwap/integer-mult-bounds` at commit
`cb86e50e9a07685068874d8e4174b2e6c209b95c`, file
`upstream/build/sections/05-layers.tex`, supplies H0 on one common-offset bit
in each of consecutive equal-K chunks (lines7--16,889--896). Its complex
phase-frame residual basis changes are binary row additions (lines86--155),
implemented through packed BIT chunk-swaps (lines180--198,448--477). Therefore
the pinned completed complex layer already depends on BIT physical routing.
The source identities are credited; the coordinate-circuit transfer and its
explicit long-word precision test are a new campaign interface investigation.

Splitting a large target mask by original bit depth might produce ell groups
of at most d positions and avoid requiring b private complex carrier banks.
It still does not make arbitrary subsets consecutive, remove the internal BIT
dependency, or establish the needed row stock. Replacing native residual-basis
row additions by this CNOT identity would add complex recursive calls; the
resulting child count must be recomputed before claiming any saving. These are
remaining proof obligations, not asymptotic conclusions.

## Retained exact controls

`code/check_hadamard_coordinate_permutation.py` simulates actual integer-pair
Hadamard arithmetic on every address, computes both involutions independently,
and compares recovered words against a separate direct coordinate map.
Configurations are pinned in `configs/hadamard-coordinate-precision.json`.
The receipt `results/hadamard-coordinate-precision.json` covers:

| Address bits | Payload bits | Records | Deferred bits | Time seconds |
|---:|---:|---:|---:|---:|
| 12 | 96 | 4,096 | 33 | 0.143 |
| 18 | 256 | 262,144 | 51 | 16.257 |
| 20 | 512 | 1,048,576 | 48 | 102.268 |

All correct circuits recover every word. Using eight fewer fractional bits
than the deferred normalization requires fails on4,092,261,843 and1,047,348
words. Omitting parity phases and restoring one fewer normalization bit also
fail in every family. Source hashes, actual pair matchings, group widths,
read/write counts and exact maximum errors are retained. These are complete
finite algebra/precision checks, not executions of native C framing or
fixed-tape movement certificates. They do not imply an improved kappa.

Reproduce with Python's standard library only:

```bash
python3 "$LAYOUT/code/check_hadamard_coordinate_permutation.py" \
  --config "$LAYOUT/configs/hadamard-coordinate-precision.json" \
  --output "$LAYOUT_WORK/hadamard-coordinate-fresh"
```

Set LAYOUT to this durable agent directory and LAYOUT_WORK to its task-owned
ignored execution root. The output directory must be fresh.

## Whole-mask spectator cancellation removes external target exposure

Exact rational multiplication gives

`(CZ (H0 tensor H0))^3=SWAP/8`,

The normalized gate identity is standard: Bravyi and Maslov,
*Hadamard-free circuits expose the structure of the Clifford group*,
arXiv:2003.09412v2, equation34 (PDF page21), give the SWAP/CZ/H relation
from which the three-step identity follows. DOI:10.1109/TIT.2021.3081415;
primary source: <https://arxiv.org/pdf/2003.09412>. The factor1/8 here comes
from H0=H/sqrt(2). This campaign's contribution is the whole-address
spectator cancellation and charged long-word routing interface below,
rather than the underlying Clifford gate identity.

and Gaussian-dyadic multiplication gives `(S H0)^3=(1+i)I/4`. For any SWAP
matching, apply H0 to ALL address bits three times, each followed by the
address diagonal formed from CZ on each paired coordinate and S on every
unpaired coordinate. Each pair swaps; each spectator becomes scalar identity.
For the two involutions of a b-coordinate permutation with c cycles, the
complete six-H circuit is `2^(-3b) i^c P`. Its correction is exactly3b binary
places and the fourth-root phase `(-i)^c`. Deferring the scale preserves
contracting intermediate H0 and phase factors. The same P>=Q+3b+log2(12b)+2
word-recovery bound applies.

A whole-address H tensor on the campaign's original representation needs
ell common-offset passes over ALL consecutive equal-width main-axis chunks,
plus the ordinary distinguished-suffix transform. The latter costs
O(n log r)=O(n ell), since log r<2ell. The main calls preserve the full
polynomial record and all spectator rows. Pointwise diagonals use original
address bits and the coefficient-index counter; Q≫b charges that metadata
inside the word scan. This supplies external native framing without a
selected-target gather. It does not remove BIT basis changes inside native C,
and it does not make the finite complex-only moment its actual physical cost.

`code/check_whole_hadamard_matching.py` and its pinned helper execute all
signed complex-word butterflies, diagonal phases and recovery. Controls
cover14,19 and21 address bits, with16,384,524,288 and2,097,152 records.
Every word and final zero imaginary component is correct. Times are1.23,
84.28 and446.10 seconds. Eight missing normalization precision bits fail
on16,365,523,633 and2,094,403 records. Omitting spectator S phases fails in
every family; the global-phase omission is recorded as either a failure or
a neutral control when the correct phase happens to equal one.

These six whole-H passes are a constructive conditional physical interface,
not an independent faster native C implementation. The separate
[coordinate-cut rank lemma](coordinate-cut-rank-lemma.md) excludes a strictly
saving exact compiler consisting only of coordinate-aligned C/H children and
cut-preserving scalar overhead. Native changing/shared XOR frames remain
outside that scoped exclusion.
