# Independent weighted-union product and consumption review

Status: **ANALYTICAL AND SOURCE REVIEW**, accepted within the stated
algebra, direct-incidence and literal arithmetic scope. No producer
module was imported or rerun for this receipt. A shorter Z word, native
activity codec, changed integer assembly and larger exponent remain
unsupplied.

The principal reviewed source is
[weighted_union_product_basis.py](../../code/complex/weighted_union_product_basis.py),
SHA-256
`596bfd8bcaa2f3df7fe718f08e9ff12f621262ba37877e7750b9c0f73a8c7cf1`;
its [report](../complex/weighted-union-product-basis.md) has SHA-256
`49608b26e3fd7e6303b5b6ce61decc78ea69a497225ebdc88582b6a665ef1883`.
The complete signed-record dependency is
[partial_polynomial_product_packets.py](../../code/complex/partial_polynomial_product_packets.py),
SHA-256
`b9fff086ff47cf80cdb0073bd9cc62f4d3b62f45236fbaf2794a5bdd529bc0f7`.
The review binds the preserved source/report identities rather than
an unpinned latest version.

## Product identity and exact consumption

In the canonical one-axis q algebra, the unit is u=(1,1) and t=(1,-1)
has square -u. Setting y=t-iu gives `y^2=-2iy`. With c=-2i and commuting
generators, the y-subset coordinate product is therefore

```text
m(f,g)[S]=sum_(A union B=S) c^|A intersection B| f[A]g[B].
```

This identity holds over any commutative Gaussian coefficient ring,
including complete negacyclic polynomial records. Its nonzero structure
coefficients are Gaussian integers. Evaluating y_j at 0 or c gives
`E=Z diag(c^weight)`, where `Z[S,A]=1[A subset S]`. These evaluations are
an invertible dyadic change of coordinates because c is a unit in
`Z[i,1/2]`. The exact product and decoder are

```text
m(f,g)=diag(c^-weight) Z^-1 ((Ef)*(Eg)).
```

Every weighted-union input of grid P has true output grid 2P. Thus the
literal decoder divisions by 2^|S| have exact divisibility on the complete
product, coefficient by coefficient. Their temporary denominators still
belong to the word. Neither this identity nor a reference integer divide
provides physical output normalization or a smaller product oracle.

The source conversion from the original q coordinates is

```text
B=[[alpha,beta],[1/2,-1/2]],
B^-1=[[1,1-i],[1,-1-i]],
alpha=(1+i)/2, beta=(1-i)/2.
```

It sends u to the new constant basis vector, and t to i times that vector
plus the y vector. Direct multiplication yields E B=C exactly, including
phase and dyadic scale. Consequently canonical consumption requires
`B_s^-1 m(B_s a,B_s b)`, with both input conversions and the output inverse.
Deleting those conversions changes the product on ordinary canonical
inputs. A natural y-coordinate integer algorithm would need a separate
loading, polynomial embedding, decoding and carry proof.

The presentation in s variables is a free multivariate Gaussian-dyadic
algebra of dimension 2^s. It is outside the earlier single-variable monic
quotient degree theorem. That escape does not make its weighted-union
multiplication an ordinary integer product; the current word pays the
evaluation and decoding transforms.

## Classical covering-product attribution

Let `S_c=diag(c^|A|)`, c=-2i. Since
`|A|+|B|-|A union B|=|A intersection B|`, the same product is exactly

```text
m(f,g)=S_c^-1 ((S_c f) *_cover (S_c g)).
```

The unweighted covering product and its transform/product/inverse
evaluation are classical. Björklund, Husfeldt, Kaski and Koivisto,
[Fourier Meets Möbius: Fast Subset Convolution, STOC2007](https://www.cs.helsinki.fi/u/mkhkoivi/publications/stoc-2007.pdf),
Section2.5 equations(15),(17), give that product and evaluation;
Section2.2 records the subset-lattice transform and inversion. The
primary PDF was inspected directly on 2026-10-09. The Gaussian weight
is an elementary diagonal conjugation, not a new covering convolution.
The paper's arithmetic and RAM implementation bounds are not a native
fixed-tape supplier for this campaign.

The present analysis concerns the actual q-to-y conversion,
representation-specific incidence ranks, complete polynomial fields,
precision and native integration limits. Novelty of any broader
contribution still requires a separate literature review. The named
covering algebra and its zeta algorithm must not be advertised as new.

## Slice rank and direct formula incidences

Multiplication by e_A has exactly the rows indexed by supersets of A.
Columns indexed by subsets of the complement of A give an identity
minor. Its rank is therefore exactly `2^(s-|A|)`. The output slice S is
zero outside subsets of S, and on those coordinates is the tensor of
`[[0,1],[1,c]]`, with inverse `[[-c,1],[1,0]]`. Its rank is `2^|S|`.

For any separable Gaussian scalar product formula, each incident term
contributes rank at most one to a fixed coordinate slice. Summing the
slice ranks yields lower bounds 3^s on each input form incidence count
and on the output incidence count. The E evaluation and decoder attain
them. This is a genuine basis-dependent algebraic difference from the
canonical q coordinates, whose every slice has rank 2^s and whose three
direct incidence floors are 4^s.

I also independently accept the
[canonical slice and small fixed-error proof](../complex/product-slice-wire-boundary.md).
The local signed slices have Gram 2I, so their s-fold tensors H satisfy
`H H^T=D I`, D=2^s. For M=H/D, `M^-1=H^T`. Entrywise Gaussian L1 error
epsilon gives `||M^-1 E||_infinity<=D^2 epsilon`; a strict bound below
one preserves every slice rank. This proves the incidence floor for an
EXACT separable formula of that fixed perturbed tensor. It does not
exclude input-dependent rounding or a native program whose guaranteed
payload errors have not been converted to one fixed bilinear tensor.

These are direct formula incidence statements. Shared/layered Z circuits
and full polynomial record multiplication have different operation
models. Neither 3^s nor 4^s may be charged as independent physical payload
passes without an actual implementation premise.

## Conversion and literal guards

The explicit factorization
`B=L_beta diag(alpha,-beta) U_-i` is correct. Each nonzero lower shear
is a diagonal conjugate of Z_1; an upper shear follows by address
exchange. This gives two same-width Z calls as a reduction for B, with
all routes, weights, buffers and guards retained. It is useful if an
independent cheaper Z supplier is proved. It is not a same-width
self-recursive C recurrence with an uncharged mass of two.

B has cross ratio `B00*B11/(B01*B10)=-i`. A full-support binary Clifford
kernel has only plus/minus-one cross ratios after its row/column chirps
cancel. Monomial gauges and permutations cannot remove the mismatch.
A narrower C child or a single Z tensor has structural zeros, whereas
B_s is dense. These are valid single-same-bank shortcuts to exclude.
For a serial C profile with monomial wrappers, column support is at
most `2^(sum r_j)`, so dense B_s requires `sum r_j>=s`; its normalized
power moment cannot contract for exponent at most one. Helpers or a
different complete chronology remain outside that claim.

Using complex L1 norm, the stated literal bounds check independently:

```text
||B_s|| <=2^s,       ||(2B)^tensor s|| <=4^s,
||B_s^-1|| <=3^s,   ||E|| <=3^s,    ||Z^-1|| <=2^s.
```

Partial weighted Z passes respect the same E bound: a processed j-axis
row has bound at most `3^j 2^(s-j)<=3^s`. The three-real-product Gaussian
recombination has complex coefficient bound at most 5r times the squared
operand bound. For inputs of bound A, the literal new-basis prefix is
therefore at most `5r*18^s*A^2`. The paid canonical numerator word starts
with numerator B of bound 4^s, then E of bound 3^s, so its product and
decoder/output inverse are at most `5r*864^s*A^2`. The source's coarse
5s and 10s plus logarithmic-r/multiplication margins suffice for those
named component stages.

For input grid P, the new-basis decoder temporary can reach 2P+s, with
true output grid 2P. Canonical B adds s input bits, products double the
grid, and decoding can reach 2P+3s; the canonical q endpoint has known
grid 2P+s. Complete fixed-format padding may create additional temporary
bits, as stated in the report. Actual full integer product temporaries
are priced by the whole packed operand, not by one coefficient bound.
The source separately checks decoder divisibility and known canonical
trailing zeros; it does not infer those facts from numerical sampling.

These bounds cover the displayed literal word. An unsupplied faster Z/B
implementation must prove its own complete local prefixes and endpoint
interfaces. Geometric-width norm/grid ledgers can help under their stated
contracts; they do not automatically verify the activity codec.

## Capacity and remaining obligations

The conditional g-gate activity model has
`w~Binomial(f,2/D)` and parent width hf. Jensen's inequality for
0<sigma<1 gives the stated sufficient moment bound
`g*(2/(hD))^sigma`. For h=3 and hypothetical g=11, the exact inequality
`11^5000<12^4999` leaves useful raw slack at sigma=4999/5000. That is an
honest target-capacity discriminator if the word and complete native
activity profile actually exist. The campaign has supplied neither in
this frozen package. A g=12 same-profile first moment is one and cannot
claim positive saving from this bound.

The unknowns include the actual shorter reversible word, inactive
alphabet and complete row geometry, prefix route, variable population
grouping, every dirty/guard/companion endpoint, weights, fixed-tape
payload motion, stopping, precision and all missing child multiplicities.
The allowance is the actual `V(EK)^tau`, and an outer integer assembly
must pay its own input and consumption maps. The suggested scalar
threshold is not an accepted complex root or multiplication exponent.

## Provenance, finite scope and failure preservation

The producer's complete algebra/coefficient/record cases and bounded
replay are observed in its immutable run receipts. This independent
review did not repeat their computation. The original failed source is
`dbc7544f136e6e0d215a663db2e5b72c6cb9437424d982bd34be5d4927155565`.
The preserved current-to-original patch has SHA-256
`aadf090be5d57bed8bde95006a949297913122e8b5b1208e37b08fe0e9c0f2e5`
and renames the local matrix back to the function-shadowing identifier.
The author's bounded receipt records exact source recovery and a
reproduced TypeError. It correctly accepts no mathematical output from
that failed attempt. This receipt pins the patch and both source hashes;
it does not relabel the author's recovery run as an independent one.

The proof/source inspection requires no extra executable CI. Existing
bounded producer checks exercise the finite word. A complete changed
supplier and loading/recovery assembly remain the decisive next task.

Attribution: independent AI-assisted internal mathematical and source
review. No formal verification or external peer review was used.
