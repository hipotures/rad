# Paid affine translations for the Gaussian phase interface

Status: **CONDITIONAL RESULT** obtained by specializing an existing streaming
construction, with **EXACT FINITE CONTROLS** of the specialized address word.
This supplies a routing component under explicit assumptions, not a new
native network or multiplication exponent.

Arbitrary symmetric Gaussian phase changes can have affine Fourier support.
The [independent phase review](general-quadratic-phase-review.md) exhibited a
rank-two triangle form whose radical phase forces a translation. This note
accounts for that translation using the original packed selected-bit router,
with constant Boolean controls. It retains the paid binary routing exponent.

## Conditional streaming statement

Assume the original fixed-tape complete-stream operations:

1. Swap two disjoint equal-width L-bit address chunks in `O(V*L^tau)` time,
   with spectators and complete payloads restored, for fixed `0<tau<1`.
2. Rotate a later complete chunk by an offset determined only by preceding
   fields, in linear stream time apart from the documented offset work.
3. Apply any fixed permutation of two specified address bits in `O(V)` time.

Take the original complete three-chunk rectangle, arbitrary spectator lengths,
and R-bit payload records. Put `L=f*K`, `K>=6`, `0<=rho<K`, and selected
positions `j_i=rho+i*K`. There is a fixed-tape procedure performing

```text
y_(j_i) <- y_(j_i) xor 1,  for every 0<=i<f,
```

that fixes every other address coordinate and every payload bit. In particular,
the arbitrary temporary chunk z is restored. If there are M records,
`V=M*R`, `A=ceil(log2(2V))`, and
`delta=min(1,80*(f-1)*2^(-K))`, the complete time ledger is

```text
O(V*(L^tau+1) + M*A^3 + delta*M*A*(R+A)).
```

Under the original fixed-family assumptions `A=O(p)`, R larger than every
fixed polynomial in p, `f<=d<=p`, and `K/log(p)->infinity`, this simplifies to
`O(V*(L^tau+1))`. These hypotheses and full volumes are part of the statement.
A random-access permutation certificate alone would not supply this cost.

The three chunks can be existing distinct slots. The unused source-control
chunk becomes a spectator in this specialization. No initially zero scratch
address, postselected subcube, or extra free row is assumed. A use at ambient
dimension below three needs a separately charged spare chunk or another
procedure and is outside this stated contract.

## Literal word and correctness

First omit the last selected position. In one local segment, let u and w be
its target and temporary integers. Use the following chronological word,
with every predicate evaluated at the current value:

```text
u <- u - [w even]
w <- w - [u even]
u <- u + [w even]
w <- w + [u even]
w <- w + [u odd]
u <- u + [w odd]
w <- w - [u odd]
u <- u - [w odd]
```

This is the original eight-rotation word with control equal to one. On each
integer parity square it flips the parity of u, preserves its quotient under
division by two, and restores w exactly. Each integer is updated four times
by at most one; the original conservative displacement bound eight applies.

Apply each line simultaneously to all positions `j_0,...,j_(f-2)`. A line
targeting y is one cyclic rotation by
`+/- sum_i 2^j_i*[z_(j_i)=specified parity]` modulo `2^L`; a line targeting z
is analogous. Each offset depends only on the other chunk, so every rotation
is a bijection. Their composition S fixes the spectator coordinates.

Let B contain addresses for which a used guard value g in either y or z lies
outside `10<=g<=2^(K-1)-11`. At an address outside B, each segment begins in
`[20,2^K-21]`. Bounded displacement keeps it inside its segment, so no carry
or borrow passes into another segment. Therefore S agrees with the desired
selected-bit NOT permutation T on the complement of B. All lower spectator
bits and bits above the used segments remain fixed there.

T preserves all guard values and hence B. Since S and T are bijections and
agree outside B, S also preserves B. The correction `T*S^(-1)` consequently
fixes the complement and permutes B. The omitted top selected bit is supplied
by the fixed two-bit permutation that negates its target bit and fixes its
companion. T and that last NOT act on disjoint selected positions.

For each of the `2*(f-1)` used guards, exactly twenty of its `2^(K-1)` values
are excluded. Complete chunk ranges make this count independent of payloads
and spectators. The union bound gives `|B|<=delta*M`. The correct ideal map
preserves the entire arbitrary z chunk, not just its selected bits.

## Complete fixed-tape charges

For each rotation, swap its target after the controls when needed, perform the
ordered affine rotation, and undo the swap. The old descriptor construction
still applies after deleting the source-bit predicates. There are at most
sixteen whole-chunk swaps and eight rotations. The chunk-length list, logical
names and spectator order are restored after each completed step. Masks
inspect at most f selected positions and do not read payload values or their
target chunk. The original offset-work bound remains valid.

To repair B, scan all complete records with their rank counter, recover their
chunk addresses and strides, and extract only exceptional records. For current
address q, compute `q'=T*S^(-1)(q)` by reversing the literal eight rotations
with negated current offsets. Attach its full destination record rank. The
correction permutes B, so these keys are precisely the marked holes and are
distinct. Stable binary radix sorting of the extracted full records followed
by one full-stream reinsertion supplies the repair.

This is the original paid repair argument. Descriptor and inverse-mask work
cost `O(M*A^3)`. At most A radix passes cost `O(|B|*A*(R+A))`, including the
whole R-bit payload of each exceptional record. Full scans, resets, cleanup,
the top-bit NOT and chunk movement give the other terms. No exceptional
address is silently ignored and no nonlinear payload operation is relabelled
as an address permutation.

For arbitrary quadratic phase changes, perform one such translation for each
nonzero slot of the normal-form shift, at most h fixed invocations. Their
temporary chunks can hold arbitrary values and are restored between uses.
This adds no Gaussian child. The paid binary routing cost at a node is still
of the old form `O(V*((e*K)^tau+1))`; the K factor, stopping conditions and
binary exponent cannot be dropped in a new transfer. A larger final kappa
does not follow from this component alone.

## Discriminating finite evidence

The [self-contained verifier](../../code/transfers/packed_translation.py)
implements the chronological rotations, their literal inverse, guard tests,
exception correction, and final top-bit NOT. It checks complete arbitrary
temporary addresses, rather than testing a zero guard only.

Predicates inspect bits no higher than the last used selected bit. If
`P=2^(rho+(f-2)*K+1)`, adding arbitrary independent multiples of P to y and z
commutes with every rotation modulo `2^L`. It also commutes with the ideal
omitted-top NOT. Thus the failure of the unrepaired stage is determined by
the two residues modulo P. Exhausting these representatives gives an exact
failure fraction for the entire complete rectangle, while seeded full-range
and forced-safe-guard cases test the guard reasoning and repair.

Four workers checked 790,849 representative pairs and 28,672 complete-address
samples over seven configurations in 1.384 seconds. The native-contract
`K=6,f=3,rho=2` case has unrepaired failure fraction `1/32`; at
`K=8,f=3,rho=0` it is `1/128`. In the latter case, input `(y,z)=(0,0)` maps to
`(16776705,16776960)` before repair instead of `(257,0)`. Omitting repair
therefore corrupts both the target and arbitrary temporary chunk.

Small guard widths below six are separate negative-control models, outside
the streaming theorem's contract. Their exact unrepaired fractions are `1/2`
at `K=2,f=3`, `1/4` at `K=3,f=3`, and `15/64` at `K=4,f=4`. They help expose
the unpaid-correction shortcut and are not admissible native parameters.
The one-column boundary and one-used-position cases also pass; f=1 has no
exception bank and consists only of the final elementary NOT.

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/packed_translation.py \
  --workers 1 --small
```

The bounded path checks four configurations, 4,417 representative pairs and
1,024 complete-address samples. The [full run](../../runs/20261008T221209Z-transfer-packed-translation/)
pins the source, seeds, UTC execution interval and exact command. Omitting
`--small` and specifying `--workers 4 --output` at a fresh ignored JSON path
reproduces the full result. There are no external execution dependencies.

## Scope and provenance

The streaming construction and its three assumptions come from the immutable
[original layer source](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/05-layers.tex),
Section `Packed changes of selected address bits`, Lemma
`packed-selected-bit-rectangle`. Revision:
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`; SHA256:
`20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594`.
This is input `original-layers`, acquired through gh at the pinned revision.

The constant-control specialization, exact controls and this deduction were
authored with OpenAI Codex. This review does not reprove the three underlying
stream primitives, the all-size Gaussian precision guard, a scalar network,
or a complete multiplication transfer. It supplies a clearly charged affine
translation component for independent scrutiny of the proposed broader phase
architecture. No formal verification or external novelty claim is made.
