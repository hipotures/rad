# General symmetric quadratic phases: rank interface and scoped limits

Status: EXACT FINITE EVIDENCE and an elementary mathematical derivation.
The scalar network, tape integration and complete child distribution are
separate obligations. This report asserts no multiplication exponent.

## Question and prior context

Can a phase transition be compiled when its binary matrix is symmetric
but is not a difference of nested orthogonal projectors? The potential
leverage is a larger frame-synthesis space with edge cost determined by
rank, including alternating and degenerate differences. This does not
by itself supply a better circuit or a favorable recurrence.

Binary quadratic descriptions of Clifford operations are established;
see Jeroen Dehaene and Bart De Moor,
[The Clifford group, stabilizer states, and linear and quadratic operations over GF(2)](https://arxiv.org/abs/quant-ph/0304125v1),
18 April 2003, especially Sections II-IV. This primary paper supplies
context for the wider representation, rather than a fixed-tape
multiplication theorem. No external implementation was copied.

The local read-only library already proves the alternating projector
case in [its producer](../../../integer-multiplication-bounds/reports/alternating-quadratic-phase.md)
and [independent review](../../../integer-multiplication-bounds/reports/review-alternating-quadratic-phase.md).
Those sources include the Gauss sign, actual selected-bit counter scan,
paid selected-word shears, and r inherited ordinary children. They do not
automatically certify an enlarged grouped child for a new interface.

## Quadratic lift and radical

Let A be a symmetric binary n by n matrix. A lift q into Z/4 obeys

    q(x+y)=q(x)+q(y)+2*x^T*A*y mod4,   q(0)=0.

It can be written `sum_i l_i*x_i + 2*sum_{i<j} A_ij*x_i*x_j`, where
`l_i mod2=A_ii`. The even part of each l_i is meaningful. Composing two
Fourier-diagonal phase frames subtracts their lifts, whose polar matrix
is the binary matrix difference. Equal polar matrices can still differ
by an even linear phase, which must be implemented.

Define `K_q=H_n diag(i^q) H_n` with normalized binary Walsh H_n.
Its convolution coefficient at address difference z is

    2^-n * sum_x i^q(x) * (-1)^(z dot x).

On R=ker(A), polarization vanishes, so q restricted to R is additive
and even: `q(r)=2*ell(r)`. Summing over the radical shows that the
Fourier coefficient is supported on the affine set

    {z : z dot r=ell(r) for every r in R}=z0+im(A).

This radical contribution is an address translation. It is not a free
omission when rank(A)=0. The retained negative control uses q(x)=2x_0:
the exact operator is X_(e0), whereas dropping the translation gives I.

Choose a complement U of R, and an invertible matrix M whose columns
are a basis of U followed by a basis of R. The address coordinates are
`M^T z`; their inverse physical map is `M^-T`. The restricted matrix
`B=U^T A U` is nonsingular, with rank r=rank(A). In these coordinates
K_q factors into the r-dimensional quotient operator and the radical
translation. Both address adapters still require paid movement.

## Exact Gaussian-dyadic quotient factorization

Write qbar(a)=q(Ua), and `G=sum_a i^qbar(a)`. For a character d, shifting
a by B^-1 d proves

    sum_a i^qbar(a) (-1)^(d dot a) = G * i^-qbar(B^-1 d).

Consequently the quotient kernel is

    Kbar(a,b)=G/2^r * i^-qbar(B^-1(a+b)).

Put `D(a)=i^-qbar(B^-1 a)` and let `P_L` map address b to Lb.
Polarization gives

    Kbar=(G/2^(r/2)) * D * H_r * P_(B^-1) * D.

The ordinary dyadic kernel is
`C=((1+i)I+(1-i)X)/2`. With `S(a)=i^wt(a)`, its tensor identity gives

    Kbar = [G/(1+i)^r] * D * S * C^tensor r * S * P_(B^-1) * D.

The bracketed scalar is always a Gaussian unit. To prove this without
retaining irrational coefficients, reduce the bilinear form by congruence
into norm-one axes and alternating hyperbolic pairs. Each norm-one axis
has lift coefficient 1 or 3 and Gauss sum 1+i or 1-i. Each hyperbolic
pair has Gauss sum +2 or -2. Their product is G, and

    (1-i)/(1+i)=-i,   2/(1+i)^2=-i.

Thus `G/(1+i)^r` belongs to `{1,i,-1,-i}`. This argument also proves
`|G|=2^(r/2)`. An alternating lift may require a negative Gauss sign;
the retained hyperbolic example has q(a,b)=2a+2b+2ab and G=-2.

For f repeated columns, all chirps and translations repeat columnwise
and the constant is the f-th power of this unit. The algebra uses one
C tensor on rf selected bits, or r inherited calls on f selected bits.
Grouping those rf bits into a single recursive child requires the paid
grouped-field interface and its guard transfer. This report does not
infer that transfer from the matrix identity.

Canonical matrix lifts must be subtracted in Z4. If A is the old matrix
and B the new matrix, then the actual difference lift is
`q_(A xor B)+2*sum_i [A_ii=1 and B_ii=0]*x_i`. The independent transfer
review retains this correction and rejects its omission.

## Finite independent evidence

The original [checker](../../code/complex/quadratic_rank_interface.py)
imports no old producer or sibling-agent implementation. A direct integer
Walsh transform supplies its reference. The candidate independently
reduces the symmetric form into orthogonal blocks, computes its Gaussian
unit, and evaluates the ordinary C tensor with quotient chirps, the actual
dual address change and the radical translation.

Four workers completed [the attempt](../../runs/20261008T215649Z-complex-general-quadratic/):

| Dimension | Cases | Sampling | Exact matrix entries |
| --- | ---: | --- | ---: |
| 3 | 512 | All symmetric matrices and even linear lift choices | 32768 |
| 4 | 2048 | Seed 20261009 | 524288 |
| 5 | 256 | Seed 20261010 | 262144 |
| 6 | 128 | Seed 20261011 | 524288 |

All 2944 cases and 1343488 entries pass. Lift polarization and the
canonical versus directly summed Gauss factors are checked separately.
Wrong symmetry, diagonal parity, omitted radical shifts and omitted
Gaussian units are falsifiable controls. These are finite exact checks,
not a formal proof package.

The coupled-transfer track supplies an independently implemented
[literal general-phase review](../transfers/general-quadratic-phase-review.md),
including bulk columns, arbitrary complete payload fields and exact inverse
restoration. Its producer imports neither this implementation nor the old
alternating verifier. This strengthens the component evidence without
turning it into an all-size multiplication theorem.

## Physical overhead and remaining constraints

For a fixed motif, M, B and every quadratic coefficient are fixed finite
data. Their selected-word adapters decompose by Gaussian elimination into
a fixed number of paid shears and three-shear swaps. They must preserve
unused chunk bits, outer prefixes, complete coefficient fields and dirty
scratch. An arbitrary address permutation is not a zero-cost operation.

The diagonal chirps have only fourth-root phases and preserve coefficient
grid and modulus. General quadratic scanning replaces the prior paired
neighbor read by a fixed number of aligned neighbor reads. Toggling a
selected bit j updates q by a constant plus twice a fixed binary linear
combination of the current other selected bits. Aggregate carry traffic
remains linear in complete record count for fixed n. Existing counter
evidence handles actual chunk spacing and spectator fields; the dense
neighbor extension and new guard constants require explicit review.

More precisely, when selected coordinate i toggles from s to 1-s at one
column, its Z4 update is
`(1-2s)*l_i + 2*sum_(j!=i) A_ij*x_j`. Reading every fixed neighbor under
aligned counter heads is a fixed amount of work. A complete lexicographic
address rectangle has fewer than twice as many bit flips as records;
within-bank returns and bank resets cost at most a constant multiple of
that carry length. Counter initialization for each complete fiber is also
bounded by its record count. This extends the existing selected-mask scan
argument; it does not assume a random-access read at distance fK.

The radical's affine offset is implemented through the separately paid
[constant-control packed translation](../transfers/paid-packed-translations.md).
Independent scrutiny of that specialization observes that every rotation
is bijective because its offset depends only on the other complete chunk.
Outside the guard exception bank B it equals the ideal selected NOT T.
Since T preserves B and both maps are bijective, preservation of B follows
globally, and the correction T*S^-1 is valid on the whole bank. The last
selected NOT and every affine bank call are separately charged. This
acceptance retains the original router's complete companion-chunk and
fixed-tape assumptions; it is not a free address permutation.

Under that interface, an edge needs r ordinary f-axis children and
nonrecursive work `O(V*((f*log p)^tau+1))` plus fixed polynomial setup,
where V is logical bit volume. A lawful grouped rf child may improve the
moment profile, but its contract must be proved with actual selected
fields and recursive parameters. Unit chirps do not increase modulus;
their number still enters the scalar-operation guard.

Two scoped obstructions survive. Under unchanged monotone membership
semantics, requiring `A_n u=u` for every contributing source direction
and `A_n s=0` for every downstream target gives a contradiction at any
nonzero `u in U_n intersect M_n`. Thus the stored weighted-tree witness
cannot disappear merely by allowing nonprojector symmetric matrices.
Paid changes or different chronology can alter those premises.

Also the prior [closed symmetric rank lemma](../../../integer-multiplication-bounds/reports/downstream-pair-star-central-negative.md)
already applies to arbitrary symmetric differences in characteristic two:
if `sum Delta_i=0`, then `sum rank(Delta_i)>=2 dim span im(Delta_i)`.
It follows by factoring each symmetric Delta_i as U_i G_i U_i^T and
observing that the row space of concatenated U is totally isotropic for
the nondegenerate block form diag(G_i). A full-gather/undo center path
with the same target annihilation requirements retains this lower bound.

The next structural discriminator is a legal network with lower paid
edge ranks, altered target chronology, or noncommuting Clifford frames.
The last option changes the relevant geometry and needs a new source,
target and dirty restoration contract.

## Reproduction

```sh
python3 -B research/integer-mult-breakthrough/code/complex/quadratic_rank_interface.py \
  --n 3 --mode exhaustive --output /tmp/fresh-general-quadratic.json
```

Only Python's standard library is used. Output paths must be fresh.
The run protocol records every seed, configuration, source hash,
Python version, memory limit and command.
