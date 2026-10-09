# Analytical reviews of the odd-line interface and materialized-side bound

These are independent mathematical and source-scope reviews. They do not
claim an independent rerun of the producer's finite experiments or formal
verification. The previously completed
[central review](closed-center-independent-review.md) retains its narrower
weight-one-modulo-four controls unchanged.

## Every odd label and the affine unit

The complex-track source `closed_center_interface_review.py`, SHA256
`fd5861c9734abb73d898ad90b2fc6e6c365ae572da7b91ac9e83db3e84abfc39`,
and its [report](../complex/closed-center-and-odd-line-independent-review.md)
propose the relative interface for any odd label T. Put
`ell=((weight(T)-1)/2) modulo2`. Independently,

```text
F(d xorT)/F(d)=(-i)*(-1)^(ell+d dotT).
alpha*(-i)=beta.
```

Thus `F*C_T^-1` has coefficient `2*beta*F(d)` on the affine support
`d dotT=ell`, and zero elsewhere. Using output and input coordinates
`S*a+c*T` and `M*b+(c xor ell)*T`, the difference is
`eta xor ell*T`, where `eta=S*a xor M*b` is perpendicular to T.
The XOR weight correction is a multiple of four because `eta dotT=0`.
The extra phase is `(-i)^(ell*weight(T))=i^ell`. The dual-basis chirps and
normalization `2*beta*alpha^h=alpha^(h-1)` remain unchanged.

This proves the stated affine flip and global unit for every odd T,
including alternating perpendicular forms. For f selected columns the
unit is `i^(ell*f)` and each quotient column flips. The packed Gaussian
operator has `(h-1)*f` literal C factors, while the bulk selected child
width is h-1 with f columns. Those are different recorded dimensions.
The producer's report now makes that distinction explicit without changing
its immutable source or raw certificate. I accept the analytic interface
under the paid complete affine routing and chirp contract; a no-offset
rejection of weight3 does not contradict it.

The extension creates no free payload permutation or phase gate. Its use
inside the generic central-release proof requires the exact actual F
operator after every adapter, including these units. B's scalar coefficients
still act entrywise without being raised to f. Native precision, addressing
and row budgets need separate integration.

## Separately materialized closed side channels

The coordinator's source `materialized_side_release_bound.py`, SHA256
`e84dcb6eb5afbcc10f36b73733c7f2ab42035c7b3ba76d2261a340190c6c04fb`,
and [report](../obstructions/materialized-side-release-bound.md) assume a
scalar K of rank at most q and a side I-K factored through d materialized
scalar channels. The rank inequality is sound over the data field:

```text
v = rank(I) <= rank(K)+rank(I-K) <= q+d.
```

Under its separate chronological premise, each such channel starts in
full, visits a genuinely proper sink-compatible Lagrangian frame and
returns to full. Both distances are positive integers, so each excursion
costs at least two. Adding these costs to the complete central charge gives

```text
Wh-2v+2qh+2d >= Wh+2q(h-1).
```

The comparison must retain the complete paid physical stock W. Additional
helper banks require their own initial/final full-frame costs; enlarging W
without those charges would invalidate the comparison. Reusing already
counted central helpers avoids this accounting issue.

I accept this conditional obstruction with its stated scope. The scalar
factorization premise is needed: address-dependent data mixing need not
factor through d scalar values per address. The closed excursion premise
also excludes direct source-to-sink geodesics and shared chronology. Joint
center/side computation, open endpoints and general column-coupled frames
are not ruled out by the argument. A general f-column lower bound does not
follow from this per-column lemma.

The scientific consequence is to avoid sweeping separately materialized
side bases merely to reduce scalar rank. A new mechanism must remove a
named premise while preserving complete dirty outputs and paid stock.
This receipt neither independently reruns the coordinator's controls nor
claims a lower bound on general reversible circuits or integer multiplication.
