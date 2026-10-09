# Multiplicative field ordering is not a large prefix-affine route

Status: **SCOPED ALL-SIZE ALGEBRAIC OBSTRUCTION**, with exact finite controls.
This concerns a particular direct routing interface, not all finite-tape
algorithms, guarded nonlinear permutations, or fixed-kernel convolution.

The synthesis track's [cyclic Walsh core](../synthesis/finite-field-cyclic-core.md)
orders nonzero field elements by powers of a primitive element. Its Gaussian
chirps and trace Gram maps still need their own paid operations. The following
test addresses only the nonlinear power-ordering part. An invertible binary
linear change of the output field coordinates preserves each nonzero cube
sum. An arbitrary linear change of input address coordinates need not preserve
these aligned chunks and is not covered by the prefix claim.

## Exact boundary

Let F be a field of order D=2^N and alpha a primitive element. Index the field
by ordinary N-bit integers and define

```text
P(i)=alpha^i,  0<=i<D-1;
P(D-1)=0.
```

For N>=3, no aligned binary prefix chunk of size at least four is mapped
affinely into the polynomial-coordinate vector space. An affine map here is
a constant vector plus an F2-linear map of the remaining low address bits.
The claim includes affine maps that are not required to be globally invertible.

Consider any binary axis cube avoiding the last exceptional index. Its varying
bit positions form J and its fixed-bit integer is s. Characteristic two gives

```text
xor_{A subset J} P(s+sum_{j in A}2^j)
  = alpha^s * product_{j in J}(1+alpha^(2^j)).
```

Every factor is nonzero: the primitive order is D-1 and 0<2^j<D-1 for N>=2.
The cube sum is therefore nonzero. The XOR of the images of any affine
q-dimensional binary cube is zero for q>=2, because its constant and every
linear term occur an even number of times. Thus every nonexceptional
two-dimensional subcube already contradicts affinity.

An aligned chunk avoiding zero has such a subcube. A chunk containing zero
and of dimension at least three has a two-dimensional subcube avoiding zero.
The only remaining chunk is the final four-address chunk. Its image sum is

```text
alpha^(-3)*(1+alpha+alpha^2).
```

It could vanish only if alpha has order three. That occurs at N=2, where the
entire four-address permutation is indeed affine; it cannot occur for a
primitive element when N>=3. This proves every case, including the separately
retained zero address.

The zero-first convention used by the cyclic producer also satisfies the same
claim: outside its first chunk the images are consecutive powers. Their sum is
`alpha^(s-1)*(1+alpha)^(2^q-1)`, which is nonzero. The first four images are
`0,1,alpha,alpha^2`, with nonzero sum unless alpha has order three. Larger
first chunks contain an ordinary nonexceptional four-cube.

Within a **single direct prefix partition whose pieces each use one affine
map**, the maximum legal piece size is two. Such a partition needs at least
D/2 pieces. This count is not a bound on the number of stages of a composition
of affine and nonlinear operations. It is not a lower bound on native tape
time. A different order, nonlinear guarded route, or retained multiplicative
layout may have a different cost and requires its own proof.

## Exact experiments and negative controls

The [independent source](../../code/obstructions/singer_prefix_routes.py)
uses polynomial reduction and verifies a complete nonzero power cycle in each
field. A complete cycle establishes that every nonzero residue is a unit,
so the tested quotient is a field and the chosen element is primitive.

Four workers tested N=2,3,6,8,10,12 in 0.233 seconds. They checked all 2,720
aligned chunks of size at least four and 80,985 nonexceptional two-dimensional
axis cubes. The single degree-two whole chunk is the positive boundary; every
tested chunk at higher degree is non-affine. Every field permutation and its
inverse, every reference payload, the product formula, and the final-zero
formula are checked exactly. No numerical tolerance is used.

Checking only the XOR of the whole field would wrongly suggest affinity: that
sum is zero, yet the smaller cube witnesses reject the map. The source retains
this control and an explicit failed local-affine payload prediction. Its
payload scatter is a reference oracle, never a paid native implementation.

A separate [zero-border attempt](../../runs/20261009T001519Z-singer-zero-borders/protocol.json)
checks the zero-first convention and retains an explicit degree-four affine
input-plane counterexample to arbitrary prelinear overgeneralization. That
plane maps to an affine output plane even though the aligned chunks do not.
The [bounded verifier](../../code/obstructions/verify_singer_routes.py) replays
both conventions and this scope control.

The [attempt](../../runs/20261008T235553Z-singer-prefix-routes/protocol.json)
pins all source, field-generation and clock information. Its
[full compact result](../../runs/20261008T235553Z-singer-prefix-routes/results/full.json)
contains the primitive polynomials, all counts and final-chunk witnesses.

## Consequence and next discriminator

The cyclic reduction cannot import a free prefix-conditioned linear address
relabeling for P. The [independent cost review](../transfers/field-cyclic-independent-review.md)
separately accepts the cyclic algebra and states the complete primitive cost
needed for an exponent saving. An O(V*N) full-payload router would consume the
potential saving in that unchanged outer architecture.

A useful next test is a paid nonlinear route or a layout retained across
multiple outer rounds, with complete record movement and conversion counts.
The present proof leaves both open. It does not reject the exact cyclic
factorization or establish a general routing lower bound.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/verify_singer_routes.py \
  --workers 1 --bounded
```

This is an independently developed mathematical deduction with OpenAI Codex
assistance. It is not external peer review or formal verification.
