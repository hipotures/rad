# Complete product packet operands, prefixes and parameter scales

Status: **EXACT FINITE SCALAR AND POLYNOMIAL PACKET CONTROLS**, with
**SCOPED CONDITIONAL COST ENVELOPES**. The arithmetic of a fused partial
kernel is correct on complete polynomial records. The inexpensive small
packet region is real, but no complete transform/product chronology or
contracting recurrence is supplied. The inherited full-size packet remains
outside its local budget. No new kappa is asserted.

## What the packet actually multiplies

Let `s` be the number of partial product axes and `D=2^s` records in an
orbit. Each record is a Gaussian negacyclic polynomial with `r`
coefficients, whose signed component precision is `p` bits. The
[partial product algebra](partial-gaussian-product-fusion.md) extends to
this coefficient ring because every identity uses only Gaussian-dyadic
scalars, addition and multiplication in a commutative ring.

The transform-avoiding recursion has exactly `3^s` record-product leaves.
Its cost per original record therefore carries `(3/2)^s`, rather than
`3^s`. Source linear forms contain sums of at most `2^s` original fields,
so leaf components gain at most `s+O(1)` bits. A generic Gaussian product
uses three real polynomial products via the sums of real and imaginary
parts. A packet known to have real operands throughout uses one real
product at each leaf. This real-only shortcut must not be inherited by
generic Gaussian intermediates.

A complete real polynomial product is computed by signed-radix packing.
For leaf arrays of length `r` with absolute coefficients at most `L`,
every ordinary convolution coefficient is bounded by `r L^2`. Choose
`B=2^w>2rL^2`, encode the whole array as `sum_j a_j B^j`, multiply the two
signed integers, and recover all `2r-1` balanced digits. Fold coefficient
`j+r` negatively into coefficient `j` only after full decoding. This
handles both signed carries and the modulus `T^r+1`.

Thus a product operand has length

    Q = O(r [p+s+log(2r)]),

not merely `p+s`. The finite source uses the safe bounds
`w<=2(p+s)+bit_length(r)+4` and `Q<=r w+2`, including a sign bit.
Intermediate positive and negative coefficients are retained. Omitting
the convolution growth guard is explicitly rejected.

Using only the previously established signed-integer multiplier
`M0(Q)=O(Q log(2Q))`, the leaf contribution per original payload bit has
upper form

    O((3/2)^s * (1+(s+log(2r))/p)
      * log(2r[p+s+log(2r)])).

A factor three is present for generic Gaussian records. It is a constant,
not an extra `3^s` tensor multiplier. Integer record encoding, all signed
digits, negacyclic folding and Gaussian recombination are still paid.
The exact Python arithmetic controls do not constitute a fixed-tape
implementation of those conversions. The baseline multiplier is not the
improved algorithm being constructed; treating a full-record product as
a free improved oracle would change this envelope and require a new
well-founded recurrence.

## Every prefix and recyclable buffer is charged

The [scalar prefix source](../../code/complex/partial_product_prefix_audit.py)
observes every source sum, all three real-product Gaussian temporaries,
intermediate recombination, decoder doubling and subtraction. Integer
packet inputs of signed width `p` have leaf operand bound `p+s+2`.
A conservative complete dynamic numerator bound is `2p+4s+4` bits.
Padding intermediate scalar values to one endpoint grid gives the bound
`2p+5s+4`. The endpoint fractional grid is `s`; literal multiplication
of two inputs padded to that grid has temporary grid `2s` before exact
removal of known zeros. Endpoint precision alone does not justify
omitting this multiplication temporary.

These controls use integral input numerators. For a general input base
grid `P0`, bilinearity doubles that base grid: the complete product
endpoint has `2P0+s` fractional bits. A linear Gaussian guard cannot be
reused unchanged. Polynomial products also add the convolution growth
`log(2r)` to component numerator guards. Full outer accuracy, rounding
and final integer carries remain separate obligations.

The explicit scalar array word counts complete source slice buffers,
three retained child outputs, source-sum buffers, both output halves and
final concatenation. Let `E(D)` be its maximum recyclable coefficient
buffers beyond the two existing input arrays. A size-one product uses
one output buffer. For larger `D`, the worst branch or output assembly is

    E(D) = max(4D+E(D/2), 11D/2).

It gives `E(D)=8D-5` for `D>=2`. Including both inputs, the peak is exactly
`10D-5` logical coefficient array slots. A fixed set of scalar working
registers and complete signed-integer product buffers is additional, with
its bit widths charged above; this exact array count is not a total
arithmetic-register peak. The final endpoints keep
both input arrays and the complete output, `3D` buffers. Dead buffers
are explicitly retired in this logical schedule; the count is not a
measurement of CPython heap retention and not a claim that arbitrary
dirty workspace was uncomputed. Lifting the schedule to `r`-coefficient
records plus complete integer-product temporaries gives linear peak
storage `O(D r[p+s+log(2r)])` for an already contiguous packet. Paid
orbit extraction and return are not part of that result.

## Native selected width is a different parameter

The actual native local budget is `V(EK)^tau`, not `V s^tau`. Here `E`
is the selected width of the native call, `K=floor(d^c)` is fixed from
the root width `d`, and `s` belongs to the fused product packet. A new
interface must derive the relation between them.

The inherited internal shape has `E=ms` for a fixed interface dimension
`m`, `E>=d^beta`, and `tau(1+c/beta)<lambda<1`. In that shape the leaf
inflation `(3/2)^s` is exponential in `E`, while the native local budget
is polynomial in `E`. It cannot serve as a full-size replacement. The
[Gaussian-dyadic quotient degree floor](dyadic-quotient-channel-volume.md)
also costs too much there, under its complete uniform-width coefficient
stream premise: `s/(EK)^tau` grows at least as
`d^(beta(1-tau)-c*tau)`, with a positive exponent.

These exclusions do not cover smaller packet axes. For example,
`s=gamma log2(d)` contributes `d^(gamma log2(3/2))`; its scalar product
factor can fit a polynomial allowance if the remaining precision,
layout and product exponents also fit. Since
`(3/2)^5<2^3`, the exact bound `log2(3/2)<3/5` gives an elementary
sufficient margin without decimal logarithm assumptions. A root-width
native allowance has exponent `tau(1+c)`, whereas a logarithmic-width
call with the same root `K` has allowance exponent `c*tau`, up to
logarithmic factors. These are different comparisons.

Local fit does not construct the needed topology. Splitting a full
`s=Theta(E)` missing kernel into logarithmic packets leaves a remaining
transform or recombination. Three-product processing of a fixed fraction
of the root axes is still exponentially expensive. The retained joint
core's [mixed-output moment obstruction](../obstructions/partial-output-normalization-boundary.md)
also remains valid until a full fused workload replaces its linear output
contract. Packet arithmetic alone does not remove that normalization.

The scale identities above were checked against the immutable primary
`05-layers.tex` at public revision
`ca8725485a822769f24c2e4e9b8955b31a42b044` of
[GamingPuzzled/integer-mult-bounds](https://github.com/GamingPuzzled/integer-mult-bounds/blob/ca8725485a822769f24c2e4e9b8955b31a42b044/upstream/build/sections/05-layers.tex),
SHA-256 `20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594`.
The campaign's existing read-only acquisition identifies the PR127 head.
Only parameter definitions and generic local budget are used here; its
headline result is not adopted as evidence for a new campaign mechanism.

## Exact finite evidence and reproduction

The [scalar run](../../runs/20261009T052005Z-complex-product-prefix-full/report.md)
uses four workers with `(s,p,real)` equal to `(1,4,true)`, `(2,8,false)`,
`(4,16,true)`, `(6,32,false)`. Actual real-product counts are `3,27,81,2187`;
largest product operands are `4,11,18,36` conservative signed bits.
Peak logical buffers are `15,35,155,635`, exactly `10D-5`.
Its only imported reference is the frozen scalar algebra source; all
prefix and buffer observations are new.

The [complete polynomial run](../../runs/20261009T052659Z-complex-polynomial-packets-full/report.md)
uses four workers with `(s,r,p,real)` equal to `(1,3,3,false)`,
`(2,5,8,true)`, `(3,7,16,false)`, `(4,3,4,false)`. It independently compares
literal Gaussian transforms and polynomial products, the signed tensor,
and the packed three-product word. All 260 counted endpoint real/imaginary fields and
2394 completely decoded real polynomial coefficients pass. Actual
integer-product counts are `9,9,81,243`; largest actual operand lengths
are `19,88,246,36` signed bits. The insufficient radix guard negative
fails as required. The standalone source imports no producer.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/partial_product_prefix_audit.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/partial_polynomial_product_packets.py --workers 1 --bounded
```

Use four workers without `--bounded` for the retained full finite sets.
Fresh optional output paths are required. Configurations pin sources,
seeds and primary parameter provenance. No external package is needed.

The next credible mechanism must explain where only a small partial
packet remains, how its full record layout is achieved, and how the whole
source/product/output chronology changes the complete child profile.
Until that mechanism exists, a local fitting packet is a component
hypothesis rather than a route certified to cross `kappa=1e-4`.

The transfer track's independent
[packet size and prefix review](../transfers/fused-packet-size-envelope.md)
accepts the conservative scalar prefix bounds and reconstructs the
`10D-5` logical array-slot peak by read-only inspection. It retains the
additional scalar and metadata charges and independently separates native
selected width, root chunk width, polynomial operand size and the outer
product row. Its exact symbolic envelope checks do not rerun these
producers or implement packet payload operations. The frozen review has
SHA-256 `7adecdfb13d7518d8616f64613cec7028873f7a915c1141b06c4ad35ced5fe2d`.

Attribution: the complex track derived and executed the exact scalar and
polynomial packet words. The transfer track supplied the independent
analytical review and its separate symbolic envelope. All work is
AI-assisted internal research, not formal verification or external peer
review.
