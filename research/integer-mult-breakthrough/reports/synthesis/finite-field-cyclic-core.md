# Exact finite-field cyclic core for the Gaussian tensor

## Result and mathematical leverage

The nonzero Walsh coordinates can be reordered into a cyclic convolution
of length `L=2^N-1`. The zero coordinate remains a separate, invertible border
component. An exact complete word sends `(x,y,r)` to
`(x, y+C_N x, C_N r)` for arbitrary Gaussian-dyadic source, sink and dirty
helper values. It uses three cyclic cores and six real fixed-kernel integer
products; those products are implemented directly with signed radix packing.
No improved multiplication oracle is assumed.

This is an exact algebraic mechanism and finite certificate, not a native
fixed-tape algorithm or exponent improvement. Its attraction is an all-size
field-character identity with only linear space. The central open issue is
whether its particular fixed kernels and multiplicative address layout admit
a cheaper independent native algorithm or a different coupled recurrence.

## Field ordering and core

Let `F=GF(2^N)`, `D=2^N`, and choose a primitive element `a`. Fix a polynomial
basis of `F`. Let `G` be the invertible binary trace Gram matrix, so
`Tr(u*v)=u^T G v`, and put `dual=G^{-1}`. The standard Walsh exponent obeys
`x dot y = Tr(dual(x)*y)`.

Order input nonzero addresses as `a^{-j}` and output nonzero addresses as
`G a^i`, for `0<=i,j<L`. Then the nonzero Walsh block is

`K[i,j]=k[i-j]`, `k[t]=(-1)^Tr(a^t)`, with indices modulo `L`.

The ordered full Walsh matrix is

`W_ordered=[[1, ones^T],[ones,K]]`.

The additive character is nontrivial. Its full-field sum is zero, so
`sum k=-1`. For every nonzero cyclic shift `s`, multiplication by `1+a^s`
permutes the nonzero field elements. Therefore

`sum_j k[j]k[j+s]=-1`, while at `s=0` the sum is `L`.

It follows that `K^T K=D I-J`. Since `K ones=-ones`, the exact inverse is

`K^{-1}=(K^T-J)/D`.

Thus the inverse is also cyclic, with kernel `(k[-t]-1)/D`, whose integer
numerators are zero or minus two and whose denominator is dyadic.

## The zero coordinate and Gaussian chirps

Define reversible border shears `B` by `x_nonzero -= x_zero` and `A` by
`x_zero -= sum(x_nonzero)`. Then

`W_ordered = A diag(D,K) B`.

The lower block is `K*(x_nonzero-x_zero*ones)=K*x_nonzero+x_zero*ones`.
The upper block after `A` is
`D*x_zero-sum(K*x_nonzero+x_zero*ones)=x_zero+sum(x_nonzero)`.
Every zero coordinate is independent; no zero-initialized border cell is
assumed. The inverse reverses and inverts each operation, including `D`.

For `alpha=(1+i)/2` and `C=[[alpha,beta],[beta,alpha]]`, `beta=(1-i)/2`,

`C_N=alpha^N diag((-i)^popcount(x)) W diag((-i)^popcount(y))`.

[The source](../../code/synthesis/finite_field_cyclic_reduction.py) includes
both input and output permutations, both fourth-root chirps, global Gaussian
normalization, the two border shears, and their exact inverses. The complete
source/sink/dirty chronology is

`C_N on x; y+=x; C_N^{-1} on x; C_N on dirty r`.

The first and third cyclic kernels are forward; the middle is inverse.
The helper is transformed, not assumed clean or restored to its initial
coordinates. This is the explicit required dirty `C_N` endpoint of the word.

## Noncircular integer convolution

Clear the common dyadic denominator of each real and imaginary input
component. A forward core has integer kernel `+/-1`; an inverse core has
integer kernel `0/-2` and final division by `D`. For input coefficient bound
`A` and integer kernel bound `Kmax`, every ordinary convolution coefficient
has magnitude at most `L*A*Kmax`.

Choose `b=max(1,bit_length(2*L*A*Kmax))` and radix `B=2^b`. Encode each signed
polynomial at `B` and compute one actual signed integer product. Decode
`2L-1` digits with centered residues in `[-B/2,B/2)`. The strict coefficient
bound makes this decoding exact even for negative inputs. Folding coefficient
`i+L` into `i` gives the cyclic product. Each Gaussian core needs two such
real products. The implementation records actual operand/product bit lengths,
digit spacing, denominators and the coefficient bound, and rejects a leftover
high digit. This is an explicit executable convolution, rather than a call to
the transform being reduced.

The integer operand length is approximately `L*(payload_bits+N+guard_bits)`.
With whole coefficient records this is the current transformed volume, so
these six products cannot simply be designated smaller recursive calls. The
fixed m-sequence kernel could be cheaper than a general product, but no such
algorithm is established here.

## Finite evidence and precision witness

Four workers tested primitive polynomials `11,19,37,67` in binary encoding
for `N=3,4,5,6`, using generator two. Each geometry enumerated every nonzero
element, checked all standard-dot/trace pairs, core autocorrelation, and both
full address permutations. Independent random signed Gaussian components
with seed `20261008+N` matched direct cyclic sums and inverse recovery.

All `3D` independent Gaussian initial columns, their real and imaginary
directions, and two normalization placements were exactly replayed:

| N | D | Complete direction/placement checks | Late basis peak | Early basis peak |
| ---: | ---: | ---: | ---: | ---: |
| 3 | 8 | 96 | 8 | 2 |
| 4 | 16 | 192 | 16 | 4 |
| 5 | 32 | 384 | 32 | 4 |
| 6 | 64 | 768 | 64 | 8 |

Matched single-source corruption controls omitted the zero-coordinate scale,
omitted the zero-border sum, or truncated one inverse-kernel coefficient;
each failed exact source/sink/dirty comparison. The basis hashes agree for
both normalization placements.

The transfers agent independently reconstructed the complete field/core,
chirps, borders, inverse and three-bank word without importing this producer.
Its [retained independent review](../transfers/field-cyclic-independent-review.md)
accepts the exact finite algebra and separately charges signed coefficient
slicing/packing. It confirms that native permutation and transpose costs,
and a self-consistent asymptotic transfer, remain unproved. This is internal
mathematical review, not formal verification or external peer review.

The late word has a concrete temporary-range problem: the source `x_zero=1`
reaches value `D` at the zero-coordinate scale, although its source endpoint
is one and its Gaussian sink entries are small. Moving global `alpha^N`
normalization earlier reduces this observed real/imaginary peak to
`2^floor(N/2)`. This is a useful repair for that witness, not a universal
fixed-point prefix guard. It still requires paid temporary precision and exact
denominator growth. Bounds from unitary endpoints alone would miss the late
peak.

The completed [positive run](../../runs/20261008T234022Z-synthesis-field-cyclic/report.md)
retains complete receipts. An earlier
[failed attempt](../../runs/20261008T234008Z-synthesis-field-cyclic-failed/report.md)
stopped on peak instrumentation for all-zero banks before any certificate;
the repaired attempt uses a fresh identity. The minimal reconstruction patch
and source hash preserve that failure separately.

The failed source SHA256 is
`3173c948d34a95d4d6213c0983c32bca732a779566e52c521321af902d514b31`.
Applying [the reconstruction patch](../../fixtures/synthesis/field-zero-peak-failure.patch)
to the corrected source produces these exact bytes. A fresh independent
reconstruction reran `probe(3)` and retained the complete KeyError traceback;
the missing record on all-zero inputs is now a bounded regression control.
The original attempt has only its protocol. Its exception was observed in
terminal output; no original raw stderr capture is claimed.

## Native obligations and next discriminator

The executable verifier treats address permutations as explicit finite
Python list operations. A native circuit must pay for translating polynomial
addresses to multiplicative order and back, or retain a compatible layout
across the surrounding construction. Primitive-polynomial selection, field
enumeration, kernel generation, signed packing, folding/extraction, temporary
precision, and dirty movement are also paid costs. Primitive polynomials here
are fixed only for the four tested sizes; the algebra applies to any supplied
finite field with a primitive element, not to a certified uniform generator.

The current word is a reduction to same-volume fixed-kernel multiplication,
with no proved positive kappa. Under the unchanged outer architecture, a
bitsliced use of an assumed multiplier saving can lose a factor from the
outer logarithmic scale; this needs a complete characteristic moment, not an
informal bootstrap. A useful next experiment is an independent algorithm for
these signed field-character kernels, or an architecture that can keep
multiplicative layout and make the required product calls strictly smaller.

## Reproduction

The core source and bounded verifier use Python's standard library only.
Use a fresh output path from the repository root:

```bash
python3 -B research/integer-mult-breakthrough/code/synthesis/finite_field_cyclic_reduction.py --workers 4 --output research/integer-mult-breakthrough/work/synthesis/<fresh-field>/results
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_field_cyclic.py --output research/integer-mult-breakthrough/work/synthesis/<fresh-check>/check.json
```

The bounded entrypoint checks `N=3` complete columns, all-zero instrumentation,
mixed negative dyadic convolution, an insufficient radix guard and an invalid
field polynomial. A `--bounded` flag on the experiment also runs only `N=3`.
No dependency outside the retained source closure is needed.

The [completed bounded receipt](../../runs/20261008T235002Z-synthesis-field-ci/results/check.json)
pins the four-file closure and all controls. A reconstructible failed source
can also be generated without modifying the accepted source:

```bash
patch -o research/integer-mult-breakthrough/work/synthesis/<fresh-failure>/finite_field_cyclic_reduction.py research/integer-mult-breakthrough/code/synthesis/finite_field_cyclic_reduction.py research/integer-mult-breakthrough/fixtures/synthesis/field-zero-peak-failure.patch
PYTHONPATH=research/integer-mult-breakthrough/code/synthesis python3 -B research/integer-mult-breakthrough/work/synthesis/<fresh-failure>/finite_field_cyclic_reduction.py --bounded --workers 1 --output research/integer-mult-breakthrough/work/synthesis/<fresh-failure>/results
```

Create the ignored `<fresh-failure>` directory first. The second command is
expected to fail with the preserved instrumentation KeyError and never
produce an accepted certificate.
