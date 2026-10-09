# Independent partial-overlap rank and query review

This is a read-only source and mathematical review of the coordinator's
[partial-overlap runner](../../code/obstructions/partial_overlap_fourier_rank.py)
and [proof/report](../obstructions/partial-overlap-ranks-and-separable-copy-budget.md).
It imports and executes no producer code and supplies no new measurements.
The rank identity and the stated separable-query obstruction are accepted
within the explicit characteristic-zero and architectural scopes.

## Interpolation and rank

Put k=2t+1. The sum of coefficients of degrees zero through t in
(1+x)^r(1-x)^(k-r) is a polynomial in r of degree at most t. At every
positive odd r<k, the degree-k generating polynomial is palindromic:
reversal multiplies it by (-1)^(k-r)=1. Since k is odd there is no middle
coefficient. Its two coefficient halves have the same sum, while its
value at x=1 is zero. The lower half sum therefore vanishes. At r=k
it equals 2^(k-1). These t distinct roots and the final value uniquely
give 2^(k-1) binom((r-1)/2,t). This validates the full-cube low-degree
Walsh expansion without assuming the sought identity at even inputs.

For a j-bit proper overlap, the absent k-j relative signs are minus one.
The coefficient of a degree-l Walsh character is the full coefficient
2^(1-k) times

    sum_(a=0)^(t-l) (-1)^a binom(k-j,a)
      = (-1)^(t-l) binom(k-j-1,t-l).

The finite alternating-binomial identity is Pascal cancellation. For
negative or excessive indices the coefficient is zero, including a
truncation beyond all k-j terms. The nonzero range is exactly
max(0,j-t)<=l<=min(t,j), so the rank is the stated sum of binomial
multiplicities. Walsh inversion is valid over Q/C. Reduction modulo a
finite characteristic can remove nonzero coefficients and is outside
this rank conclusion.

Extending a j-bit response across omitted source bits only repeats its
columns and preserves row rank. For j>0, positive odd intersections
vanish because j<k. The matrix separates into two disjoint parity
blocks. Flipping the same one bit in input and output preserves XOR
and exchanges their parities, giving equal blocks and rank r_j/2 each.
The runner's small rational elimination controls this claim separately;
its larger cases are explicitly spectral, rather than elimination runs.

All proper supports jointly span every Walsh character of degree at
most t: for a character L, choose J=L, whose coefficient at degree |L|
is nonzero. No larger-degree character occurs. This independently
validates the joint dimension 2^(k-1), without treating that smaller
joint scalar span as a complete native query circuit.

## Fixed-query charge and its boundary

Within the reported model, each address-independent copied scalar row
followed by scalar target decoders contributes an outer product of rank
at most one. Thus each parity query needs at least r_j/2 independent
complete rows, even if one row supplies many target readers. This is
an independent-row count, not a distinct-reader count. Arbitrary old
dirty responses can cancel but cannot raise the source-signal rank of
one such row.

For nonempty J, the target's functional on Q is nonzero: it evaluates
nontrivially on the paired coordinate-difference directions belonging
to J. Therefore Q intersection T-perp has codimension one. Sign parity
gives the two query hyperplanes; distinct J give distinct functionals.
At the fixed actual canonical representatives, each complete Q-to-query
normalization consequently pays one rank, even if either subspace is
degenerate. This uses the already accepted actual F_E interface and
does not identify different Gaussian gauges for free.

When p>=k+1 all highest proper supports exist. At j=k-1, the nonzero
degree band consists only of l=t, so r_j=binom(k-1,t). The three-core
bill is at least 3k binom(k-1,t)/2^k times v. Its value at k=3 is 9v/4,
and its ratio under k to k+2 is (k+2)/(k+1)>1. It therefore exceeds the
retained master's unspent 2v rank deficit for every odd k>=3. Under the
stated role/endpoint ledger this prevents first-moment contraction.

The inference requires separately normalized address-independent rows
at fixed Q/query frames and the retained master. Rank alone does not
force separately materialized complete payload vectors in a changed
circuit model. Shared or evolving frames, address-dependent encodings,
paid row/field packing, direct mixed-helper reads, and joint geodesic
preparations remain outside. The new
[singleton quotient component](singleton-quotient-roots-and-paid-copies.md)
is consistent with this obstruction: its singleton fee is constructive,
while an extension by separate highest-proper copied queries already
fails. No universal circuit, native, or kappa claim follows.

The independent protocol pins exact reviewed bytes and records that
no producer execution, formal verification, or new timing was performed.
