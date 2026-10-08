# Independent physical band-LU and external-bank scale review

Reviewed 2026-10-08 around 13:43 UTC. The changed argument is
[physical-band-lu.md](../inverse/reports/physical-band-lu.md); this review
checks its written induction rather than rerunning its factor implementation.

## Banded elimination and precision

For positive diagonal and strict row diagonal dominance, the reported leading
Schur complement inequality is correct: its row gap is at least the original
gap plus `|A_ik|*(1-offsum_k/A_kk)`. The same triangle calculation bounds the
remaining absolute row sum by the original row sum minus that positive term.
Thus successive no-pivot Schur complements retain positive diagonals and a
uniform row gap, while their row norms do not increase. Ordinary line bands
retain their half-bandwidth w. The argument applies to lifted local windows;
a full cyclic wrap band would require a separately handled border.

The rounded elimination backward-error argument is sound. At one pivot, the
rounded multiplier reconstructs the pivot-column entry within `2 eta` when
the pivot is at most2. Updating with that *same* rounded multiplier and then
rounding the Schur entry reconstructs the trailing entry within eta. There
is no additional multiplier error in the trailing reconstruction. The lower
prefix factor has identity on the as-yet-uneliminated block, so errors supported
on trailing rows/columns embed into the original matrix without amplification.
At most w previous pivots affect a row, each altering at most w trailing
entries and its pivot column. This gives `||Delta||<w(w+2)eta` at every partial
stage. Applying exact Schur preservation to the partially perturbed original
matrix closes the claimed pivot and multiplier induction.

The stored reciprocal can be treated as an exact changed diagonal of U_eff.
This gives a small matrix perturbation rather than an unproved entrywise
roundoff stability assertion. Forward and backward substitution errors are
triangular residuals; multiplying them by the bounded stored L and the bounded
inverse of A_eff proves a polynomial-in-w absolute solution error. The generous
`2^12(w+1)^2 eta max(1,||b||)` allowance is compatible with the stated bounds.
Temporary doubled fractional precision remains O(P), and P=Q+O(log w) suffices
for the factor/application contribution.

Coefficient approximation, omitted remote aliases and the physical matrix
tail are separate perturbations. Both inverse norms below2 give resolvent
cost at most `4 epsilon_A ||b||`. They must share the final error budget with
the principal-window locality approximation. The report states this explicitly.
No blocking flaw was found in the changed diagonal-dominance or precision proof.

## Long-Q external-bank consistency

Use actual address length `B=Theta(log n)`, dimensions `d=Theta(B^epsilon)`,
working precision `Q=Theta(d^18)` and digit payload of order Q. Then a padded
box of T coefficients satisfies TQ=Theta(n). The minimum main axis width is
`ell=Theta(B/d)`, not Q/d. In particular ell/Q tends to zero; arguments relying
on the historical p=Theta(B) relation must be restated.

The changed compact-control fields have G=O(log Q) and H=dG. For every fixed
epsilon<1, `H/B=O(B^(epsilon-1) log B)` tends to zero and
`ell/log Q` tends to infinity. Thus the complete front/back banks fit in an
o(1) fraction of main coordinates; reserving
`O(log d+d log Q/ell)` whole axes is o(d). The complementary A group has enough
whole donor axes for the second B group. Complete transformed A frequency
coordinates remain independent binary address fields; the completed layer's
identity-on-dirty-bank contract is what permits their use.

The product-row stock Q^2000 needs O(log Q) address bits up to its fixed degree,
whereas a complete axis has ell bits. Consequently eventual available row
space dominates that fixed stock. A temporary row pad by at most2 is removed
after each completed layer, as required to avoid accumulated factors. Prime,
factor and descriptor setup polynomial in Q and in axis lengths has logarithm
O(B^(1-epsilon)+log B), hence n^o(1). The new packet volume has logarithm
Theta(d log d), which dominates an entire fixed-degree axis catalogue for
epsilon>1/2. These are all eventual comparisons; their finite cutoff may be
astronomical.

These inequalities support the long-Q transfer under the explicit inherited
external-field compiler and selected-bit router contracts. They do not prove
those machine contracts from a numerical PASS, certify CRT keys by themselves,
or make uncharged advice available. Component-grid rounding still needs the
inherited disk margin and complete-layer contraction error argument.

## Sparse repair cost qualification

With u=Theta(Q/d), direct physical Gaussian bandwidth has w^2=O(d). A genuine
gathered source-patch fraction rho=O(d^-3), including duplicates and halos,
permits d axis factorizations costing
`O(rho*n*d*w^2*Q^zeta)=O(n*d^-1*Q^zeta)` and sorting cost
`O(rho*n*d*B)=O(n*B/d^2)`. For fixed epsilon>1/2 and sufficiently small zeta,
these are absorbable. The total bit volume n already includes Q: charging
another Q would double-count precision. Counting only exceptional OUTPUTS
would be insufficient; the coordinating agent owns the separate source-closure
proof and controls.
