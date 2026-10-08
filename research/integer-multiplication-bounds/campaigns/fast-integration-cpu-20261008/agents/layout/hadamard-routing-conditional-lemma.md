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

## Physical premise remains unresolved

The required additional premise is a completed native H0 layer on each chosen
target mask, with its physical exposure and restoration paid without the BIT
router that the proposed circuit is intended to replace. No such premise is
proved here.

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
