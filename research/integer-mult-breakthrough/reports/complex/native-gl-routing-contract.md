# Paid GL routes for compact Gaussian frame interfaces

Status: **CONDITIONAL NATIVE ROUTING RESULT**, obtained by applying an existing
fixed-tape routing lemma, with separately retained **EXACT FINITE PAYLOAD
CONTROLS**. This closes a specific compiler obligation under the stated input
contract. It does not complete a scalar network, a canonical multiplication
primitive, a recurrence, or a new kappa certificate.

The [compact compiler](scalable-actual-frame-interfaces.md) and
[right-reflected gauges](right-reflected-actual-frame-gauges.md) output actual
Gaussian normal forms. Besides one rank-r C child, their words contain binary
GL routes, affine translations, and fourth-root chirps. Polynomial-time
construction of these descriptors does not perform the complete payload
permutations. The following bill is for those payload operations.

## Existing result and its retained hypotheses

The primary source is `openai/math` revision
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`, file
`preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/05-layers.tex`,
SHA-256 `20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594`.
It is the campaign's immutable input `original-layers`. Read the section
*Packed changes of selected address bits*, lemma
`packed-selected-bit-rectangle`, and its subsequent fixed-basis application.
The source explicitly proves variable-control row additions; this is not a
new constant-control conjecture.

Assume its three paid fixed-tape primitives: complete equal-width address
chunk exchange at cost `O(V L^tau)` for fixed `0<tau<1`, ordered cyclic
rotation with controls in preceding fields, and a fixed permutation of two
specified address bits in `O(V)`. These primitives restore spectators and
retain every payload bit. This investigation applies their stated contracts;
it does not independently reprove their underlying routing algorithms.

Each invocation has three distinct complete address slots of width `L=fK`,
arbitrary complete spectators, M records, R payload bits per record, and
`V=MR`. Each slot's selected bits occupy positions `rho+jK`, with `K>=6` and
`0<=rho<K`. Define `A=ceil(log2(2V))` and
`delta=min(1,80(f-1)2^-K)`. The primary lemma supplies

```text
target_(rho+jK) ^= source_(rho+jK), 0<=j<f,

T_add = O(V((fK)^tau+1) + M A^3 + delta M A(R+A)).
```

Every other address bit and every complete R-bit payload is preserved as a
record permutation. The third slot's entire address value is restored,
including unselected guard bits, for arbitrary initial values. The slot need
not be clean or have undergone an earlier phase correction.

The long-record simplification requires `A=O(p)`, R exceeding every fixed
polynomial in p, `f<=d<=p`, and `K/log(p)->infinity`, within one fixed
parameter family. Indeed, after division by V the extra terms are
`A^3/R` and `delta A(1+A/R)`, both tending to zero. This gives
`T_add=O(V((fK)^tau+1))`. A short R, small K, or growing interface family
cannot silently inherit that simplification.

## Actual movement and exceptional repair

The original eight rotations use the unchanged source bit as Boolean control
and current target/companion parities. A rotation's offset does not depend on
its target. Moving that target after the controls and restoring the original
slot order costs at most sixteen complete chunk exchanges over the whole
word. Thus arbitrary slot ordering is admitted; no additional predecessor
restriction is imposed on a GL row addition.

The highest selected position is implemented separately by the elementary
two-bit XOR. For the remaining positions, carry-free guard intervals give
the exact desired XOR off an explicit exceptional set. Both the desired map
and rotation word preserve that set. Correction uses the literal inverse
rotation word and the desired XOR to compute destination record ranks.
Stable binary radix passes move all R payload bits and the full destination
key, followed by a complete-stream reinsertion. This is the source of the
`delta M A(R+A)` charge. No bad address is dropped, and a numerical value is
never treated as a free permutation key.

The original descriptor bound is `M A^3`. It includes counter recovery of
complete mixed-radix addresses, current inverse masks, signed rank updates,
rewinds, and cleanup. The exceptional list is not a new set of clean scalar
roles: it stores complete extracted payload records while the full stream is
held for reinsertion. Its movement and temporary storage belong to the paid
routing primitive.

## GL composition and fixed versus growing h

For an invertible h-by-h binary matrix P, Gaussian row reduction yields a
chronological word of elementary transvections. A row exchange is expanded
into three additions. At most

```text
g_h <= h(h-1)+3(h-1)
```

additions suffice. Reversing this self-inverse gate word implements the
inverse route. At each gate, any third distinct existing complete slot is a
legal companion, because the gate restores it before the next gate.
The exact conditional cost is therefore

```text
O(g_h [V((fK)^tau+1) + M A^3 + delta M A(R+A)]).
```

For fixed `h>=3`, put `e=hf`. This is
`O_h(V((eK)^tau+1))` under the long-record/guard hypotheses above. Two GL
routes per compact normal form and at most h affine translations have the
same fixed-h order. The reflected reverse interface may retain an additional
rank-zero monomial stage; its complete route and phase pass remain paid.

For growing h, the gate count cannot be hidden in the time constant.
With the conservative bound `g_h=O(h^2)`, the leading movement cost is
`O(V h^(2-tau)(eK)^tau + V h^2)`, besides descriptor and repair terms.
Long records can absorb polynomial metadata per record; they do not absorb
additional complete payload passes. If h grows as a power of e, this changes
the time exponent. No faster large-h GL decomposition is established here.

## Address companion, physical roles, and incomplete boundaries

The third slot is an **address dimension in the same role stream**. For an
h-slot interface with `h>=3`, the companion is one of those already present
full slots. No scalar helper bank, extra W role, clean row, or additional
endpoint is created. A transvection may temporarily use this slot's arbitrary
address guard bits, while its raw record payloads are moved intact. After
repair, the companion address is exactly restored and every payload is at
the intended XOR destination. Thus there is no omitted companion-frame
transition at the gate endpoint.

An unrestored scalar birth carrier cannot simply be borrowed as a third
address slot. That would require a different joint-stream shape and a proof
of its complete physical input/output word. This note makes no such claim.

The route requires three complete slots of equal fK-bit width. A complete
inactive spectator block can supply one only when the actual stream shape
certifies that full range and the correct lengths. Padded row counts,
arbitrary fixed subsets, or an already selected partial record do not supply
it automatically. If a new independent address block were added, its full
volume and eventual endpoint would have to enter the stock ledger; it is
not a free spare.

The `f=1` boundary uses just the elementary two-bit XOR and needs no temporary
slot. With fewer than three complete slots and `f>1`, one can apply f
elementary XORs at cost `O(V f)`. That fallback fits the desired packed
movement bill only when `f<=O((fK)^tau+1)`, or when a separate paid stopping
argument allows its cost. This investigation does not assume that inequality.

The original row-splitting construction explicitly retains a complete suffix
in every role, including padded rows. A new joint chronology must supply the
same shape contract itself. Successful scalar or Pauli algebra is not a
substitute for that allocation proof.

## Unit chirps and numerical guard

For a quadratic descriptor
`q(x)=c+sum a_i x_i+2 sum b_ij x_i x_j mod4`, the f-column phase is

```text
i^[f*c + sum_j (sum_i a_i x_ij + 2 sum_(i<l) b_il x_ij x_lj)].
```

Every column constant is multiplied by f. In the published compact normal
form, `global_unit_exponent` is the sum of the input/output quadratic
constants. It is an audit field, not an additional phase gate: applying it
again would double the actual global phase. That aggregate also scales by f
when comparing tensor operators. Applying a column constant only once is incorrect. A direct
fixed-tape scan computes this exponent from the record address, then applies
the resulting unit to every coefficient field in the complete record. This
takes `O(V + M poly(A))` for fixed h; a safe cubic per-record metadata bound
fits the original long-record contract. Every scalar component, auxiliary
field, and polynomial coefficient is retained.

Multiplication by a fourth-root unit merely exchanges real/imaginary
components and changes signs. It introduces no denominator bits and no
component-magnitude growth. The signed encoding must contain the same safe
integer/sign reserve used by the coefficient guard, so negating the most
negative machine integer is never invoked. Transient bit strings in routing
are returned to exact encodings before coefficient arithmetic resumes.
Address permutations also have zero numerical charge, while their complete
payload time and buffers remain part of the paid primitive.

This statement does not eliminate a child's internal precision reserve.
The [endpoint-aware guard](../transfers/endpoint-aware-guards.md) requires the
actual scalar prefixes, complete child endpoints, and all temporaries.
The compact interface has one child on r selected slots with f columns,
namely rf literal C factors. Its profile rank is r with f columns; its
recursive selected-axis count is rf. At `r=h` this child has the parent's selected width. A decreasing row
budget, paid leaf, complete row stock, and a compatible moment inequality are
still required to terminate it. A legal route alone proves none of them.

## Exact finite controls and recovery

The self-contained [verifier](../../code/complex/native_gl_routes.py) imports
no producer or old routing implementation. It transcribes the variable-control
word, literal inverse, guard test, full exceptional correction, GL row
reduction, and complete four-field Gaussian payload operations. Python array
scatter and sorting are explicit reference oracles. Their measured runtime
is not native tape time.

The [full run](../../runs/20261009T025918Z-complex-native-gl-full/) used four
workers and completed in 8.999 seconds. It checked 1,122,561 exact quotient
representatives, 10,240 seeded full-address samples, and 344,320 complete
four-field payload records under GL routes and inverse routes. The latter
includes all 262,144 records of a native `K=6,f=1,h=3` rectangle. Small K
multi-column complete arrays are controls outside the native guard contract;
the native `K=6,8,f=3` address-word controls separately exercise admissible
guarded parameters.

At `K=6,f=3,rho=0`, omitting repair fails on exactly `1/128` of the complete
three-slot address range. The input `(x,y,z)=(65,0,0)` yields
`(65,262017,262080)` before repair instead of `(65,65,0)`. At K=8 the failure
fraction is `1/512`. Higher target/companion quotient translations commute
with the word, and unused source bits do not affect its controls, justifying
the complete-range quotient counts. Full payload correction and inverse
round trips restore all four fields and arbitrary spectators.

The first [bounded attempt](../../runs/20261009T025806Z-complex-native-gl-bounded/)
failed its required omitted-repair negative: it contained only f<=2, so
there was at most one packed position before the top bit. Those cases did
not expose cross-segment interference. This is a negative-control coverage
failure, not an accepted false XOR. The failure and original source bytes
are retained. The [repaired bounded run](../../runs/20261009T025847Z-complex-native-gl-negative-repair/)
adds an admissible K=6/f=3 case and passes 73,729 representatives plus 256
complete records in 0.398 seconds. The exact
[recovery patch](../../fixtures/complex/native-gl-missing-negative-recovery.patch)
recovers source `2295ca66638697439e73c423bd7e88aa57d6139d1c6e94139ba7fcc119fa3d8e`
from current source `fc1b0bcc04fbc5bcaeb43b1db3e7fc16acd9d03d2d8a9fe87f7329b71eb79f54`.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/native_gl_routes.py \
  --workers 1 --bounded
```

This bounded entrypoint has no fixed output path or external execution
dependencies. The full reproduction omits `--bounded`, uses `--workers 4`,
and can save a certificate with `--output <fresh-path>`, which uses exclusive
creation. Protocols pin source, config, seeds, environment, commands, actual
UTC launch times, and before/after source hashes.

The original framework supplies the streaming lemma and its cost proof;
the compact compiler integration, independent finite transcription and this
scope audit were developed with OpenAI Codex. The primary source is
[available at the pinned revision](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/05-layers.tex).
No formal verification or external novelty claim is made. Independent
campaign critique is pending before integrating this contract into a whole
native primitive.
