# Scoped review of the PR39 hybrid basis

Rohan Arun's [PR39](https://github.com/CrocSwap/integer-mult-bounds/pull/39),
research head `50e54ece17afa4bd3cccd1927e9cdea5098038c2`, fixes L25=I+J
and retains unrestricted rational GL23 in the reversed (23,25) family.
This source review was completed at 2026-10-08 13:10 UTC. It inspects
the written general argument and the finite checker logic; it does not rerun
the 2300-triple C++ checker, certify a new graph, formally verify the theorem
or provide external human peer review.

## Exact public result and dependencies

The source claims bit saving `3886826921/10^14` and conditional final
`kappa=971668963/25000000000000=3.886675852e-5`. It retains
`9*[1]+[21,17,481]`, copied retained centers, all paid endpoint corrections,
the unchanged complex network, C1=1 and p^2000 row stock. It replaces the
**whole** h25 local profile by the exact original-envelope fixed profile;
the h23 factor remains generic and can retain its positive frames. The
source's scientific dependency is PR37/34 reversed geometry, PR36 copied
centers, PR32 fixed projectors and complete local profiling, and the retained
analytic/tape/assembly interfaces. Contributions and original licenses remain
attributed to those authors.

## Nonvanishing proof reviewed

At b=25 each source triple after I+J has primal coordinates 4 on the triple
and 3 elsewhere. Its normalized dual coordinates are `17/39` on the triple
and `-5/78` elsewhere. Their products are `68/39` and `-5/26`, with sum one.
Every primal/dual coordinate is nonzero.

For a=23, let `p_r=1`, `xi_r=(r+1)^2/4324`, where
`4324=sum_{s=1}^{23} s^2`; hence xi*p=1. For each actual first-axis source
projector, this rational rank-one idempotent is reachable by GL23
conjugation. Explicitly, two normalized pairs p,xi and p*,xi* determine
decompositions `<p> direct-sum ker(xi)` and `<p*> direct-sum ker(xi*)`.
A rational map sending p to p* and any rational kernel basis to a rational
kernel basis is invertible and conjugates the projectors. The witness may
depend on the first source: it establishes that each fixed-source condition
is a nonzero function, before the common-basis product argument.

The source C++ checker constructs the actual 47-square data-null corner
for **each** of the 2300 fixed second-axis triples. It verifies primality
of 1000003 and uses only rational denominators nonzero modulo that prime.
It checks every one of the 47 successive prescribed pivot values and
returns on the first zero. Thus the logic establishes every required
ordered-prefix determinant as nonzero, rather than inferring all prefixes
from one nonsingular final matrix. A nonzero rational value modulo an
admissible prime proves the corresponding rational function is not
identically zero; no CRT bound is needed for that one-sided implication.

The saved JSON contains one final determinant product per triple and total
pivot counts, rather than the individual pivot values. Its meaning depends
on the pinned checker and an honest completed replay. A bounded fresh replay
can confirm that provenance. This is a source/evidence boundary, not a new
mathematical gap in the written argument.

The required zero cuts are inherited universal PR34 identities and are
specialized independently. The checker also tests modular zeros, but its
zeros alone cannot prove identities over all GL23. PR39 explicitly separates
these roles. The source's common-basis proof uses the universal cuts for
the 21/17 runs and the incidence-tree restrictions for the full data corner.

## Why a changed first-factor DAG can fit

A nested pair of nondegenerate original/positive frames has commuting
orthogonal projectors P_U,P_V with `P_U P_V=P_V`; the residual
`P_U-P_V` is consequently an idempotent. Each new fixed first-factor
residual of rank r lies in the full rational GL23 conjugacy class of rank-r
idempotents. The ordinary generic corner-profile nonvanishing conditions
are therefore nonzero functions on the same GL23 family, regardless of
which valid DAG produced that residual. The copied-center complement is
another fixed rank-one idempotent and adds the same kind of condition.

There are finitely many changed occurrences. GL23 is irreducible, and
after clearing denominators its coordinate ring is a domain. The finite
product of the existing data/source/local nonzero conditions and the new
ordinary-residual conditions is nonzero. It therefore admits a rational
point. This argument permits different points to show each individual
condition is nonzero; it does not assign a different runtime basis per gate.

If the new DAG preserves source lines, ordered factors, controlled
permutations and endpoint maps, the data functions themselves are
unchanged. The 2300 fixed-middle triple certificate can then be reused
for those functions. New first-axis ordinary residuals merely enlarge
the finite product of open conditions.

This conclusion is conditional on the actual new labels being
nondegenerate and nested, the required residuals being idempotents, and
the ordinary generic-profile lemma applying. A changed source producer,
data geometry, controlled boundary or restricted first basis needs a new
argument. Fixing L23 to I+J removes the GL23 freedom, so the same product
argument cannot establish the second 17-block for a both-fixed candidate.

## Fixed-middle obligations survive the review

No generic argument certifies a changed **second** factor's fixed profile.
The new h25 DAG, original labels, original matching, all physical transition
matrices and exact CRT pivot profiles must be rebuilt. Positive matching
data cannot be inserted into the original-envelope projector formulas.
The paid rank24 copied transforms keep their actual fixed ordered profiles;
only the old 25 identity cleanup calls become 25 singleton complements.

The source's complement formulas are coherent. For U_i=ker(1^T-3e_i^T),
the normalized projector has
`p_i=e_i+1/8*1`, `xi_i=4/3*1^T-4e_i^T`.
After I+J the pair is
`p'_i=e_i+17/4*1`, `xi'_i=8/39*1^T-4e_i^T`.
Every coordinate is nonzero, the pairing is one, and the actual controlled
local contraction therefore permits one rank-one child. This does not
remove the preceding rank24 transform or the separate endpoint correction.

Finally, reconstruct the new complete child list and scalar/copy accounting,
prove the strict exact moment and refresh the semantic/bulk bridge and
assembly. The reviewed family appears suitable for a changed valid first
graph plus a freshly profiled original-envelope fixed middle. No accepted
new campaign saving follows from this compatibility review alone.
