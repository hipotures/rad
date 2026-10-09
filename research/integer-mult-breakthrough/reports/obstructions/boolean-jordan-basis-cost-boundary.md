# Boolean Jordan bases: sequential cost and changed-basis obligations

Status: **LITERATURE-LED EXACT DISCRIMINATOR AND ANALYTICAL SCOPE BOUNDARY**.
The classical basis is credited below. No faster native transform or new
integer-multiplication exponent is established.

## Hypothesis and potential leverage

Boolean subset zeta is exp(U), where U adds each missing coordinate. A
symmetric Jordan basis turns U into short chain shifts. If both changes of
basis and their complete chain maps were cheaper than the original full
coordinate transform, this could change the scale of the supplier rather
than optimize an old public network. The cost of entering and leaving that
basis is the first discriminator; treating it as free would be circular.

The primary input is Murali K. Srinivasan, *Symmetric chains, Gelfand-Tsetlin
chains, and the Terwilliger algebra of the binary Hamming scheme*,
[arXiv:1001.0280v2](https://arxiv.org/abs/1001.0280v2), revised 2010-04-05.
The paper constructs an integral orthogonal symmetric Jordan basis. We use
the Boolean recursion in Section 3, equations (35)-(36). The paper does not
supply this campaign's fixed-tape transform or improved multiplier.

## Exact finite reconstruction

The independent standard-library source
[boolean_jordan_basis_cost.py](../../code/obstructions/boolean_jordan_basis_cost.py)
constructs the basis through six coordinates. It checks every basis column,
all orthogonal Gram entries, rank homogeneity, the complete upward chain
relations and the full Boolean-zeta action, not a sample of selected rows.
On a chain, the zeta coefficients are 1/r!, and the original Boolean basis
reconstructs integral endpoint columns. The actual full inverse is the
transpose divided by each column's squared norm.

Four workers completed run `20261009T105056Z-boolean-jordan-basis-cost` in
0.338 seconds. Source SHA256:
`9e2783048f2c39ed1f14657f884b39bbb521b2503a8ab71247396e9bbc1a31f2`.
Complete source bytes remain unchanged. Corrupting a chain and corrupting
inverse normalization both reject. This is exact rational finite evidence,
not formal verification or native timing.

## Sequential implementation cannot change the exponent

At dimension j, the number of symmetric chains is binomial(j,floor(j/2)).
Extending a chain of length ell produces ell-1 interior two-input blocks,
each requiring two additions in the explicit sequential construction. Its
two scalar boundary columns and all coefficient scalings are additional
costs. Summing interiors gives 2^j minus the number of chains.

Let T(n) count only these optimistic additions when applying the basis
recursion to arbitrary fields. The two recursive halves imply

    T(0) = 0,
    T(n) = 2 T(n-1) + 2(2^(n-1)-binomial(n-1,floor((n-1)/2))).

Consequently

    T(n)/2^n = sum_{j=0}^{n-1}(1-binomial(j,floor(j/2))/2^j)
             = n-Theta(sqrt(n)).

The final equality uses the central binomial coefficient's order 2^j/sqrt(j).
The same interior addition count applies to the explicit inverse blocks,
with their divisions separately charged. Thus even an optimistic two-way
basis bill remains Theta(n 2^n). Removing the explicit scalar/chain costs
does not produce a sublinear factor in n.

| Coordinates n | One basis direction: additions | Both directions | Direct zeta additions |
| --- | ---: | ---: | ---: |
| 1 | 0 | 0 | 1 |
| 2 | 2 | 4 | 4 |
| 3 | 8 | 16 | 12 |
| 4 | 26 | 52 | 32 |
| 5 | 72 | 144 | 80 |
| 6 | 188 | 376 | 192 |

These are complete counts of the named recursive realization. They are not
a lower bound for every algorithm applying the basis, every Jordan basis,
or a balanced tensor-product coupling scheme.

## Exact inverses are not automatically Gaussian dyadic words

An interior two-input matrix has coefficients (1,l-k) in its first row and
(-1,j-k-l+1) in its second. Its determinant is the old chain length ell.
Length three already requires odd-denominator inverse coefficients. The
finite complete inverse independently exposes odd denominators from n=3.

The target zeta endpoints remain integral. This does not make every
intermediate division an allowed Gaussian-dyadic scalar gate on arbitrary
dirty auxiliary input. A changed realization could retain residues, use a
different nonorthogonal basis or give a paid quotient/recovery mechanism;
those are different contracts. Orthogonal normalization additionally uses
non-dyadic square roots in general. Neither odd inverses nor these square
roots are silently imported into the fixed exact scalar gate model.

## Continuation criteria and reproduction

The unchanged sequential BTK route is refuted as a source of a sublinear
address-width factor. A balanced Clebsch-Gordan construction remains an
unproved alternative: it would have to supply the actual pair-block maps,
their total circuit and coefficient costs, complete layout, inverses and
precision. The finite block structure alone does not justify an optimistic
O(2^n polylog(n)) transform. Before an expensive search, derive a paid
per-merge complexity that genuinely beats the sequential recurrence.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/boolean_jordan_basis_cost.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/boolean_jordan_basis_cost.py --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/boolean-jordan
```

Use a fresh output path. Complete classical source inputs remain obtainable
from the pinned primary paper; no downloaded third-party source is copied
into authored code. Full run protocol and original certificate are retained
alongside a compact result and complete gzip copies. The application cost
and scalar-domain discriminators are this campaign's deductions from the
credited basis construction.
