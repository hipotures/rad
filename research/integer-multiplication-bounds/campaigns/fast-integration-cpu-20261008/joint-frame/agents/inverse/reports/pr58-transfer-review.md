# Independent transfer review of the PR58 joint dual-suffix witness

Reviewed source: public [PR58](https://github.com/CrocSwap/integer-mult-bounds/pull/58),
tested head `bc2f7ed4c20dc18898305ab17165c0c995cbb804`, acquired by the
coordinator into an immutable campaign snapshot. This review reads the
compiler, serialized words, full profile assembly, original finite proof,
mixed-width row theorem, and semantic-guard proof. It does not execute a
second unchanged full producer suite. The scout's separate replay is not
represented as this reviewer's computation.

The new local word is compatible with the inherited framed residual
interface, conditional on that interface acting on complete arbitrary
payload strings and on the accepted rational frame semantics. Its full
XOR cost remains an explicit fixed node cost. The native characteristic,
row stock, and unchanged complex guard pass an independent exact ledger.
This supports substituting the new native saving into the campaign's
already reviewed transfer; the arithmetic target alone is not an all-size
proof or an executed fast integer multiplier.

## Local algebra and arbitrary dirty roles

Within a region, all XOR endpoints are first raised to the same containing
address frame. A row map `R` on physical roles then commutes with a common
address permutation `P`: `(R tensor I)(I tensor P)=(I tensor P)(R tensor I)`.
This statement holds for every address and every payload bit. It therefore
extends the finite binary row identity to arbitrary payload width and
spectators. The payload row arithmetic is over F2; the rational address
metric and prime-field address arithmetic have a different role.

Independent desired rows, independent retained input rows, and standard
unit-row completion form a square invertible binary matrix. Literal row
elimination, with each swap expanded into three XORs, implements it on
arbitrary dirty inputs. Distinct physical inputs and designated outputs
matter. A feasible continuation suffices; matching optimality is irrelevant
to correctness and to the moment of the actually selected word.

Reclaiming a retired role removes its source-dependent signal by actual
compatible XORs. Its unknown dirty component persists. Let `L` include the
whole invertible auxiliary schedule and its physical address transports,
`V` the source injection, and `J` the target scatter. The framed scalar
identity is `J L V=I`. Chronological execution

```
L, J, L^-1, V, L, J, L^-1, V
```

adds `J L d` and `J L(d+Vx)` to the target. They sum to `x`; both source
and arbitrary `d` return. No physical slot is asserted to become zero.
Reverse order and transpose each elementary XOR to obtain the other
orientation. The finite words check all source, target and dirty basis
columns; linearity extends those columns to all strings in the same finite
address cube. Lifting the framed identity to arbitrary chunk widths still
uses the inherited physical residual compiler. This review does not replace
that general contract with the finite bitset replay.

## Complete charges and exact native moments

The independent ledger counts the literal stored word, rather than using
role savings as a proxy for work:

| Local dimension | Sources | Dirty roles | Mixer XORs | Scatter XORs | Complete wrapped XORs |
|---|---:|---:|---:|---:|---:|
| 23 | 1,771 | 30,790 | 112,498 | 10,626 | 474,786 |
| 25 | 2,300 | 40,446 | 149,289 | 13,800 | 629,356 |

Each complete count is `4*|L|+2*|J|+2*|V|=4*|L|+14*v`.
Signal-clearing XORs are already in `|L|`. Replication in the two-factor
network pays

```
2300*474786 + 1771*629356 = 2,206,597,276 XORs.
```

This is the complete **local-wrapper** charge, not a purported exact count
of every global data-front, basis, endpoint-copy and scheduler instruction.
Those retained operations are separately paid by the inherited residual
implementation. The input words also contain 1,561,953,529 replicated
literal frame events, including repeated zero-rank raises. The event count
is not a recursive-child count.

At a node of logical payload volume `V`, each complete role stream has
volume `V/W`. Thus literal local XORs contribute at most
`c_X*(2206597276/W)*V`, where `c_X` pays reading both streams, writing and
rewinds on the fixed tapes. Address transports, scalar corrections,
copying, parking, short remainders and descriptor evaluation contribute
their own fixed `K_residual*V`. They are not erased by a smaller `W`.
The word is fixed at dimensions 23/25 and is compiled before varying the
input length; the research matching and elimination are not runtime
subroutines of the multiplier. All new local charges enter

```
F(e) <= (1/W) sum_t n_t F(t floor(e/m)) + K_bit,
K_bit >= c_X*2206597276/W + K_residual,
m=575, W=150593466.
```

No number of tapes, alphabet size or record-width exponent grows because
of this fixed finite word. The fixed-tape residual contract must actually
supply `K_residual`; asserting an uncharged nonlinear address operation
would invalidate this recurrence.

The ledger independently rebuilds **all** child multiplicities: complete
data-pair profile, endpoint copies, two replicated internal profiles,
exteriors and source growths. It obtains rank mass `86589396050`, deficit
`1846900`, and maximum child 529. No same-width child or omitted exterior
is introduced. With `a=1187740349/25000000000000`, a different exact
logarithm/exponential enclosure proves

```
(1/(575*W)) sum_t n_t*t*exp(a*log(575/t)) < 1,
1-F(a) > 2.4818697e-15.
```

The next point `a+10^-14` has lower characteristic greater than one.
The strict gap pays any fixed `K_bit`: induction chooses a sufficiently
large leading constant. It does not pay an extra factor depending on `e`
or an omitted full-payload loop. Floors decrease the positive power
potential. Unequal-depth stopped complex trees retain their actual
volume-weighted child potential, rather than a surrogate uniform depth.

## Product row stock and precision interfaces

All dirty roles are included in `W`. Halving requires 9 bit levels and
20 complex levels; role bit lengths are 28 and 30. Thus the actual joint
stock is `W_bit^D_bit * W_complex^D_complex`, with coefficient
`9*28+20*30=852`. The retained row degree 2000 gives exact positive gap
`2000-(51/25)*852=6548/25`; suffix slope is 8000. Maximum-only reservation
would be insufficient. Padding is once at the complete preceding-row
boundary, by less than two; no node introduces another multiplicative
row padding. Both row-selection ranges are disjoint from the chunk bits.
Completed bit adapters return their stock before a subsequent complex
split. Arbitrary padded scratch and active-row masks remain present until
that boundary, then zero rows may be cropped.

BIT adapters manipulate whole raw encodings and must be exact for every
dirty string. During an adapter, a string need not represent a complex
number. No complex arithmetic reads it until the completed permutation
has restored the encoding. Hence the 2,206,597,276 XORs are time charges,
not numeric additions in the complex arithmetic guard. Charging them as
zero time would be wrong; adding them to a complex addition chain would
describe a different program.

The complex branch and its actual fixed scalar upper bound remain
`G=4793351472`, `Wc=537696432`, `mc=784`, `s=421548223824`.
Independently recomputing

```
E = 64*(Wc+mc+G+1)^3,
B = s+E,
literal = 2*G*Wc^2+8*s+4*Wc+4+32*mc,
C0 = 32*mc*B^2
```

proves `literal<E`, `2B(mc-756)>=s+E` and `C0>2B+18`.
The variable-width internal guard is
`A(e)<=A(756 floor(e/784))+s floor(e/784)+E<=2Be`.
Completed children expose only their true width increment; internal fine
grids are not repeatedly concatenated. The entire layer uses the fixed
grid with `Delta<=C0*d`, coefficient `C1=1`, and no eager truncation.
For the campaign's long digits `Q=Theta(d^18)`, all fixed constants are
eventually absorbed. Actual cutoffs change when a constant changes; the
asymptotic exponent does not.

## Induction, prime setup and the proposed integration

The PR58 CRT moduli certify finitely many rational minors; they are not
the prime lengths used by the multiplier. The unchanged fixed I+J basis
and original envelope mean the same bounded-minor argument applies to
the new, explicitly extracted transitions. Actual address primes must
avoid all finitely many denominator and nonzero-pivot factors. The finite
list can be fixed in the program; eventual larger primes avoid it. The
campaign's eligible-prime theorem, distinct lengths, search cost and
binary/prime volume comparison remain separate expenses. An unexplained
modular agreement or probable-prime assertion cannot replace them.

The campaign transfer also retains guarded tree CRT routing and its
restored dirty banks, packed forward and inverse cells, source-closed
sparse repair, every free-axis cyclic band-LU repair, deferred transform
reservoirs, final normalization, and exact recovery. Their structural
hypotheses do not depend on this local producer being the earlier one.
The new primitive changes `a` and fixed node constants; the same row
coefficient and scalar guard continue to suffice. Metadata and setup
remain explicitly paid, and packed children are handled by the same
algorithm under strong induction, not an assumed improved oracle.

For example, `epsilon=999999/1000000`, `q=epsilon*a` and
`kappa=99999*a/100000` have strict gaps

```
a-kappa = 1187740349/2500000000000000000,
epsilon*q-kappa = 9501923979740349/25000000000000000000000000,
(19/20)*(717/10000000)-q = 515135838740349/25000000000000000000.
```

Their target is `118772847159651/2500000000000000000`, above PR58's
headline by `4454909651/2500000000000000000`. This is exact prospective
arithmetic. Promotion requires the coordinator's complete updated cost
ledger, all error/recovery contracts, and explicit inherited hypotheses.
The small strict margins and extremely large fixed constants prevent a
practical runtime interpretation.

The supported conclusion is a conditional transfer of the new finite
word through the accepted interfaces. No new unconditional bound, formal
verification, practical speedup, or globally optimal compiler is asserted.

## Reproduction and evidence

Run `code/verify_transfer_ledger.py` with `--inputs` pointing to the pinned
PR58 snapshot and a fresh `--output`. The receipt hashes all input words,
profiles and certificate, records complete local charges, reconstructs
native multiplicities and provides outward rational moment bounds.
The verifier imports no upstream arithmetic implementation. Source-only
criticism of framed operations and tape scheduling is distinct from that
executable evidence. See [reproduce.md](../reproduce.md) for exact commands,
acquisition requirements and the bounded Gaussian certificates.
