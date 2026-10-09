# Fused product packets: selected width, chunk width and bit-volume envelope

Status: **EXACT SYMBOLIC SIZE CONTROLS AND CONDITIONAL ANALYTICAL COST
COMPARISONS**. No packet layout, native product supplier, improved multiplier
oracle or exponent is supplied. The toy parameters are not an accepted
campaign profile. The result leaves small packets open while separating
them from fusion of all the original selected axes.

## Distinct dimensions and the actual paid allowance

Use E for the current native selected width, s for the number of missing
axes fused in ONE bilinear packet, d for the outer selected width and
K=Theta(d^c) for the root chunk width. K remains fixed in descendants.
One packet has D=2^s coefficient coordinates, each with a complete Q-bit
record. Its baseline volume is proportional to DQ. The inherited local
native allowance is

```text
O(V*((E K)^tau+1)).
```

It is not `O(V*s^tau)`. In particular at E=Theta(d) it permits a root
power `d^alpha`, where `alpha=tau*(1+c)`. The retained parameter band has
alpha<1. For a smaller child E, comparisons use that child's E and the
same K; the root power cannot be assigned to every descendant.

The named three-product tensor algorithm uses 3^s scalar leaves. Relative
to D baseline coordinates its multiplication volume factor is

```text
lambda(s) = 3^s/2^s = (3/2)^s.
```

For an actual Q-bit scalar multiplier with time C_mul(Q), the normalized
packet product bill is of the form

```text
lambda(s)*C_mul(Q+O(s))/(Q),
```

plus paid source sums, output decoding, complete copies, layouts and
temporaries. It is neither 3^s alone nor an uncharged scalar product.
The [minimum-rank review](partial-product-character-independent-review.md)
shows that 3^s is the count of this particular algorithm, rather than a
general tensor-rank lower bound. The [packing discriminator](nonhomomorphic-xor-packing-boundary.md)
separately proves a 3^s ordinary-product volume lower bound for linear
bit-exponent placements and exact small results for common nonlinear
placements at s=2,3.

## Componentwise packets and complete polynomial records use different rows

For a coefficientwise p-bit field packet, using the previously established
`C_mul(Q)=O(Q log Q)` gives `C_mul(p)/p=O(log p)`. If d=p^epsilon and
`s=gamma*log2(d)`, then at the root

```text
lambda(s)*log p = O(d^(gamma*log2(3/2))*log d).
```

This fits the root native allowance with asymptotic margin when
`gamma*log2(3/2)<alpha`. It does not fit for the original shape
`s=Theta(E)=Theta(d)`: exponential packet growth exceeds every polynomial
choice of K. Splitting those same missing axes into smaller packets and
tensoring the SAME three-product algorithm still makes 3^E total leaves.
A small-packet bound alone does not repair all the missing axes.

A complete polynomial record has a different bit size. For r coefficients
with p-bit components, source-sum guard s and signed radix padding, retain

```text
Q = O(r*(p+s+log r)),    log2(r)=Theta(p/d).
```

For `s=o(p)`, its previous-multiplier ratio is `O(log Q)=Theta(p/d)`.
Charging this whole-record product to a native adapter gives the condition

```text
lambda(s)*(p/d) <= O((E K)^tau).
```

At the root, d=p^epsilon and `s=gamma*log2(d)` yield the power
`gamma*log2(3/2)+1/epsilon-1`. This is a much larger bill than the p-bit
componentwise product. The two formats cannot be compared as equivalent.

The original OUTER polynomial-product row has its own allowance, however.
It contributes `V*(p/d)` with the previously established multiplier, and
the declared target time permits `V*p^(1-a)`. A fused product in that row
would need

```text
gamma*log2(3/2) <= 1-a/epsilon.
```

Thus a whole-polynomial packet can fail the NATIVE adapter allowance
while fitting a conditional OUTER product-row allowance. Such a fit is a
cost comparison, not a full changed assembly. Improving a row that was
already below the dominant transform bill does not establish a larger
kappa.

If a new complete induction independently supplies
`C_mul(Q)=O(Q log^(1-a) Q)` on genuinely smaller operands, the corresponding
outer-row criterion becomes `gamma*log2(3/2)<=1-a`. This is a separate
hypothesis. The original polynomial-product interface uses the previous
multiplier; this report does not substitute an improved oracle. Every
actual signed operand length, the complete child bit volume, exact
recovery and strictly smaller global multiplication size must be derived
from the proposed assembly before that induction can be used.

The literal complete-record controls in
[partial_polynomial_product_packets.py](../../code/complex/partial_polynomial_product_packets.py)
are useful arithmetic evidence for the guarded signed radix interface.
They do not establish the new native packet placement or either all-size
time comparison.

## Algebraic format bounds compared with the same allowance

The [general Gaussian-dyadic quotient discriminator](../complex/dyadic-quotient-channel-volume.md)
gives `N/D=Omega(s)` for a faithful fully materialized monic univariate
quotient representing D independent channels. With the same complete
record width in each coordinate, that implies a volume factor Omega(s).
For s=Theta(d), alpha<1 excludes such root-volume traffic from the native
allowance. For s=O(log d), the lower bound can fit the polynomial allowance.
This is only a necessary volume comparison; it does not construct an
embedding, small coefficients, a decoder or a cheap product.

It also does not exclude all small child widths. At
`H=K^(tau/(1-tau))`, linear traffic in E satisfies
`E<=(E K)^tau` when E<=H. A root-only linear-width obstruction must not
be applied unchanged below that scale.

The [power-two cyclic quotient theorem](bilinear-ring-packing-boundary.md)
is stronger in its narrower faithful homomorphic format. It requires

```text
N/D >= 2^(2^(s-1)-s).
```

At the root, fitting a polynomial volume allowance requires
`2^(s-1)-s <= alpha*log2(d)+O(1)`, hence
`s<=log2(log2(d))+O(1)`. A logarithmic packet fails this bound, but some
log-log packets survive the necessary size test. This does not certify
their Gaussian-dyadic coefficient size or native conversions. The
negacyclic power-two obstruction and the separate full-linear-C convolution
obstruction keep their own narrower scopes.

Neither the general quotient nor the power-two theorem is a lower bound
on arbitrary nonhomomorphic, sparse, asymmetric, multi-product or payload
encodings.

## Exact symbolic discriminator and negative controls

The [standard-library checker](../../code/transfers/fused_packet_envelope.py)
uses toy parameters `tau=c=1/2`, `epsilon=1/16`, `a=1/1000` and
`d=2^L` for L=8,16,32,64. It evaluates integer/rational size inequalities
only. No D-element array, huge extension, product primitive or complete
payload is executed. Timings describe this small ledger computation.

With s=L, the componentwise bill `lambda(s)*16L` fits the unit-constant
native allowance at L=64. Omitting K wrongly predicts failure in that
same case. The whole-polynomial bill `lambda(s)*d^15` fails the native
allowance in all four cases, while the conditional outer product-row
comparisons fit. The F5 minimum-degree lower bound fits in all cases;
the power-two cyclic minimum degree fails for s=L and fits the smaller
declared log-log packet. Linear-width traffic fails at the root and fits
at the declared stopping width. These are exact declared inequalities,
not finite measurements of the proposed algorithms.

The [full four-worker attempt](../../runs/20261009T052048Z-transfer-packet-envelope/report.md)
started at 2026-10-09T05:20:48 UTC and passed all four symbolic cases in
0.045884 source seconds. The
[bounded one-worker attempt](../../runs/20261009T053903Z-transfer-packet-envelope-bounded/report.md)
also passes. Both preserve exact source/configuration pins, commands,
compact complete results and raw recovery paths. No failed scientific
attempt or source repair occurred.

## Independent scalar-prefix and logical-buffer review

Read-only inspection of
[partial_product_prefix_audit.py](../../code/complex/partial_product_prefix_audit.py),
SHA256 `12fdf73ca5d4b0963b42db1dd5b4ec55e4429e31823ff82508594ea2eedc4219`,
accepts its conservative scalar bounds for the named array word. This
review neither imports nor independently runs that producer.

Every leaf source component is a sum of at most 2^s original components.
The third real product of a Gaussian leaf adds one operand bit. A raw
decode prefix has at most a factor three per level before its next
halving. These observations imply the displayed conservative bounds
`R+s+2` for signed leaf operands, `2R+4s+4` for dynamic numerators and
`2R+5s+4` for common-grid/fixed-product numerators. A literal multiplication
of operands on grid s has a temporary grid 2s. Returning to the common
grid uses exact trailing zeros and must be paid in a physical routine;
it is not a free rational reduction.

The logical array-slot peak `10D-5` for D>=2 is also reconstructed. For
D=2, the final concatenation reaches 15 Gaussian coefficient slots.
For larger D, the third recursive product reaches `6D+K_buf(D/2)`,
where `K_buf(n)=8n-5` is the maximum extra array allocation beyond that
call's two input arrays. This gives `10D-5` and dominates the final
decode/concatenation peak. The final array endpoint holds 3D coefficients,
including both input arrays.

This is a recyclable ARRAY-slot ledger. Active scalar multiplication and
recombination registers, recursion/grid/index metadata and native payload
buffers are additional. It is not a Python heap measurement, an arbitrary
dirty uncomputation word or a proof of ten physical scalar roles. Paid
orbit gathering, long-record multiplication and a complete uniform
precision bound remain integration requirements.

## Provenance, reproduction and remaining leverage

The original paid allowance and complete polynomial record interface are
in [05-layers.tex](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/05-layers.tex)
and [08-assembly.tex](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/08-assembly.tex).
Their local immutable SHA256 values are respectively
`20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594`
and `763d7945b1e1ec4ebae9b799bcefcc45fa9bae6e2ffad799868a9c3d513dbd4a`.

Run from the breakthrough worktree root:

```sh
python3 research/integer-mult-breakthrough/code/transfers/fused_packet_envelope.py --workers 1 --small
python3 research/integer-mult-breakthrough/code/transfers/fused_packet_envelope.py --workers 4
```

Publication/reproduction closure is the checker and
[fused-packet-envelope.json](../../configs/transfers/fused-packet-envelope.json).
Optional `--output` requires a fresh directory. There are no runtime
dependencies on the independently reviewed producers.

A useful next mechanism must explain why only a small number s of missing
axes needs fusion, supply the actual record layout and operations, or
change the coupled product/transform recurrence. Preserving a small-packet
possibility is mathematically useful. It does not rescue the frozen
partial-output circuit or increase the current primitive's root.
