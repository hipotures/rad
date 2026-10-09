# Independent frozen-control and selected-bit reversal review

## Assessment

The coordinator's extension of the eight packed additions to an arbitrary frozen-control mask is analytically sound under its stated conditional routing interfaces. Its three-shear bit reversal is exact and preserves complete target/companion spectators. The two-terminal-guard subslot layout can preserve the original address volume while reserving the guards needed to avoid a separate top-selected-bit gate.

This is proof and source inspection, not an independent execution of the coordinator's producer, a compiled fixed-tape measurement, an all-size precision theorem, or a new multiplier exponent. The source's finite controls cover selected-bit reflection; general frozen masks are justified by the local Boolean argument. The complete Gaussian network, child layout and transfer remain separate obligations.

Reviewed producer: [general_control_bit_reversal.py](../../code/obstructions/general_control_bit_reversal.py). It imports only our frozen [native_gl_review.py](../../code/transfers/native_gl_review.py), SHA256 `1ae606d030f1f71ebe2d2497399601f1cdc6e59aa4e3209527533ecf57432d19`. The exact producer hash and immutable result hash are recorded in this review's accompanying receipt.

## Why an arbitrary mask is allowed

For each used selected position j_i, let `c_i=G_i(x)` be Boolean. The logical chunk x must remain fixed throughout this complete eight-rotation word. For several immutable controls the same condition applies to all chunks G reads. A line that changes target y can use `G_i(x)` and the current selected parity of companion z; it must not inspect y. A line changing z can use G and the current parity of y, and must not inspect z. Swapping chunk positions changes only the stored logical-name permutation, not this dependence rule.

Fix an input control x. The old eight-step argument is then literally the same argument for a vector of fixed Boolean controls c_i. Each isolated segment ends with its selected parity toggled by c_i and the whole arbitrary companion segment restored. Its intermediate displacement is bounded by eight, independently of how the Boolean values were computed. The target and companion guard intervals, their twenty excluded values per segment and the union bound are therefore unchanged. They depend on complete target/companion ranges, not on control distributions or record values.

Each physical modular addition is a bijection because its offset never reads its own target. Away from the bad set, packed additions agree with the isolated segments. The ideal selected-mask XOR fixes every guard and all spectators, so it preserves the bad set. Bijection plus equality off the bad set proves that the actual word also preserves the bad set. The correction `T S^-1` is therefore a permutation of exactly the marked exceptional records. Its inverse lines use current reverse-order target/companion values and the same frozen-control G, rather than a mask recomputed from a mutable target.

The existing full-key/full-payload exception sorting bill remains necessary. If mask generation costs `C_G(A)` elementary metadata steps, the complete offset and correction interface must charge that computation and its temporary metadata. A safe conservative extension of the retained bill is

`O(V(L^tau+1) + M(A^3+C_G(A)) + delta M A(R+A))`,

with a fixed multiplier for the eight lines. `M*C_G(A)` is not a free RAM lookup. For selected-bit reflection, a direct fixed-tape metadata routine can copy and reverse the specified bits with an `O(A^2)` bound, including head returns; this fits the existing `M A^3` allowance. No record payload needs to be inspected by G.

## Three-shear reversal

On two equal g-active selected subvectors, let R be the linear bit-reversal map, so `R^2=I`. In chronological order,

`x ^= R(y)`, `y ^= R(x)`, `x ^= R(y)`

gives `(x,y) -> (R(y),R(x))`. Each primitive has an individually frozen control during its own eight rotations and restores a distinct complete companion z before the next primitive. The control is allowed to change between completed primitives. The exact reversal is an involution, so repeating the same three shears supplies its inverse.

The linearity condition matters. An arbitrary nonlinear involution R need not satisfy the distributive cancellation in this calculation. The producer retains an exact nonlinear-involution counterexample; this prevents promoting the three-shear identity to arbitrary permutations.

The reviewed producer performs 24 literal rotations and three current-record repair permutations on 2,048 complete four-field toy records, preserves the prefix and suffix, and replays the inverse. Its separate K=6 controls enumerate 65,536 low target/companion pairs, sample 1,024 full mask addresses and 512 complete reversal addresses. These are producer evidence inspected here, not independently rerun measurements. The toy K=1 record test is deliberately distinct from the native K>=6 guard theorem.

## Same-volume two-guard geometry and its limits

Split each relevant old slot into two full equal `(g+1)K` subslots. Each subslot contains g active K-chunks and one existing terminal K-chunk. All eight-addition offsets use only its g active selected positions, so every used guard segment ends below that terminal selected position. These are complete Cartesian address ranges; unused bits cannot be assumed zero. Every shear needs another distinct existing equal-width complete subslot as its companion. Borrowing that address slot does not create a scalar scratch bank, but its full volume is already part of the stream and must be retained.

If the old slot length is not exactly `2(g+1)K`, its remainder must be named and paid. Preprocessing the two terminal selected bits costs two elementary C passes per old slot, plus any remainder passes. It is not a full `C_K` transform. No extra full address dimension is added by reserving chunks already present.

For reflection, G reads only active selected control bits. The completed ideal reversal is therefore independent of the terminal guards, and it commutes with the precomputed terminal selected-bit C factors. The intermediate rotations may move guards; exact completed restoration is what permits the factorization. An arbitrary standalone frozen mask is allowed to read control guards, but that broader operation does not automatically commute with their precomputed C gates. Such a mask requires a separate factorization proof before the same Gaussian preprocessing can be reused.

Assigning every live network role, preserving row prefixes and complete dirty fields, compacting active child axes around the two holes, charging leftover chunk swaps, and proving the original stopped-depth/precision budget remain explicit integration obligations. Exact address reversal alone supplies none of those. In particular, allowing reversal can escape an aligned-cut obstruction, but the additive two-order scan family has an independent algebraic exclusion; the new routing theorem does not produce a kappa improvement by itself.

## Primary source and record

The retained primary source is `05-layers.tex`, immutable revision `adc7f1241b42e322a6451854ab7e4b4c146bf78a`, SHA256 `20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594`, path `preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/05-layers.tex` in `openai/math`. The reviewed derivation uses its eight-addition, guard, complement-invariance and complete exceptional-key arguments directly; it does not inherit a general RAM permutation cost.

The accompanying [source-based review receipt](../../runs/20261009T045225Z-transfer-general-control-review/results/receipt.json) records source/input hashes, review timestamp and the absence of an independent producer rerun. The coordinator's raw directory label `20261009T0446Z-general-mask-first` is not its start time; the inspected immutable protocol records actual start `2026-10-09T04:47:19...`. This review does not rewrite either original.

## Double-guard geometry supplement — 2026-10-09T04:57:37.400712+00:00

The appended coordinator geometry is accepted analytically for every fixed h>=2 and g>=1, with e=2h(g+1)+u and 0<=u<2h. In the first `2gr` ranges, every missing active range is one of at most `2r` terminal guards in the first r old slots. Equally many active donor ranges lie outside that prefix. Swapping each hole with a donor, calling the ONE full active child on `2gr` axes, and reversing the swaps preserves every complete K range and leaves no guard or remainder inside the child. C tensor symmetry permits the resulting order of its active axes. The exact ratio `2gr/e<=r/h` therefore preserves the same positive-power majorant; r=h decreases by `2h+u`. Fewer than `4h` one-selected-bit local C passes pay both terminal guards and the remainder.

This geometry does not force two separate g-wide children; if only that interface exists, the factor `2^(1-p)` in its moment must be charged. It also does not by itself give logarithmic recursion depth: repeated rank-h children may decrease width only additively. The retained stopped-budget, row transfer and endpoint precision obligations still apply. The coordinator's masks must omit the internal guard-selected position when using the same h-row network across both active bands.

Source [double_guard_reversal_layout.py](../../code/obstructions/double_guard_reversal_layout.py), SHA256 `529d8a87eb122461e4adf443259e567b86de3a68f6db4bac7828972ecff06b29`, was inspected without execution. Its reported 4,160 finite cases are producer evidence, distinct from this all-h proof review. The fresh [geometry receipt](../../runs/20261009T045737Z-transfer-double-guard-review-repair/results/receipt.json) pins its immutable protocol and results; the earlier review protocol and receipt remain byte-identical.

A [publication-setup failure](../../runs/20261009T045642Z-transfer-double-guard-review/report.md) is retained: the first receipt script expected the actual-start durable run ID as a raw directory, but the raw evidence still uses `work/obstructions/20261009T0451Z-double-guard-first`. It failed before producer execution or mathematical review writes. This fresh receipt uses that exact raw namespace and records its protocol start 2026-10-09T04:51:13.586618+00:00. No scientific source repair occurred.
