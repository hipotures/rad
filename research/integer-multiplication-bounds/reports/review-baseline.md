# Independent review of the paired baseline and rational labels

This is an independent review branch of campaign `20261007T222521Z`.
The immutable campaign interval is 2026-10-07 22:25:21 UTC to
2026-10-08 08:25:21 UTC. The reference is
`CrocSwap/integer-mult-bounds` at
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`; its OpenAI manuscript is
at `adc7f1241b42e322a6451854ab7e4b4c146bf78a`.

## Findings and scope

No counterexample to the actual paired baseline was found in the interfaces
reviewed below. This does not establish its full upstream theorem. Its
conditional transfer assumptions remain conditional. In particular, scalar
execution over characteristic two and rational label geometry are separate
parts of the construction; identifying their fields would be an invalid
transfer, but the paired proof does not make that identification.

An independent expansion confirms the campaign's aligned point-order graph
at `h=50`: 435,450 additions, 58,800 partial outputs, and 494,250 roles.
Every addition has disjoint input support and a common point. All 63,562,800
nonzero partial-output coefficients agree with the required incidence map.
This check reconstructs supports directly from graph arguments and physical
input triples. It does not call the builder's provenance or support verifier.
Its SHA-256 graph/support digest is
`90da04d2dac53553c1967a5346b9238bb7a36405d40dde8f4430c74cb0781ed0`.
The expansion took 23.0 seconds and used about 1.34 GiB peak resident memory.
The reference natural order has 450,394 additions and 509,194 roles; the
local `n=49` circuit still has 9,813 additions. This is a global sharing
improvement, with a separately retained finite-agent certificate.

The review also gives a concrete obstruction to some broader mixed-span
labels, and an exact criterion that permits others. It should guide new
circuit searches rather than be treated as a general circuit lower bound.

## Rational nondegeneracy beyond a common point

Let the label form on `Q^h` be `B(x,y)=x·y-(sum x)(sum y)/9`, and let
`U` be a rational subspace. With respect to the Euclidean inner product,
write `v=Proj_U(1)`. The restriction is

```text
B|_U = I_U - v v^T / 9.
```

It is nondegenerate exactly when `||v||^2 != 9`. Its radical has dimension
at most one. It is positive definite when the value is below nine and has
one negative direction when the value exceeds nine. This follows directly
from the rank-one determinant formula, or by separating the line spanned
by `v` from its Euclidean orthogonal complement. All quantities are rational
when computed in a rational basis.

For triple indicators sharing point `i`, every vector in their span satisfies
`sum x=3x_i`, so `B(x,x)=sum_(j!=i) x_j^2`. This is the baseline's valid
sufficient condition. It is not a necessary condition.

Here is an exact degenerate family of three valid neighbors of target
`T=(0,1,2)`:

```text
S1=(0,3,4), S2=(1,5,6), S3=(2,7,8).
```

Their Gram matrix is `3I_3-J_3`, of rank two. The sum `r` of their three
indicators, equal to the indicator of points zero through eight, lies in
the radical. All 2,800 pairwise-disjoint three-triple families at `h=10`
tested by the exact checker have this same degeneracy.

A stronger obstruction uses all 27 targets choosing one point from each
`S_i`. Their span has dimension seven and contains `r`. Every source is
orthogonal to every such target. Any candidate label containing the source
span and contained in all those targets' orthogonal complements must
contain `r` and be perpendicular to `r`. Its restriction is therefore
degenerate. Enlarging the source span alone cannot repair this example
while retaining all those output constraints.

For the single target `T`, however, add `S4=(0,3,9)`. The resulting
four-dimensional source span is nondegenerate and indefinite, with
`||Proj_U(1)||^2=48/5`. A balanced binary grouping of `S1,S2` and `S3,S4`
also avoids the degenerate three-source intermediate. Thus some mixed spans
are eligible. Both intermediate labels and all target constraints must be
checked, rather than rejecting every mixed span or checking only a final
span.

## Interfaces reviewed

The scalar dirty-register schedule `L,J,Li,R,V,G,R,L,J,Li,G,V` restores
its work registers over characteristic two. For rational frames, forward
labels use cancellation-free input supports and the common-point property.
Reverse labels use complements of those source spans, whose nesting has
the opposite orientation. They do not require positive definiteness of an
arbitrary target span. The early `L,J,Li,R` controls carry the broad `D0`
frame, rather than an unjustified common-point line frame.

At endpoint sources, the additional negative rational summand corrects the
rank so that all-role endpoint incidence is `I`. The triple matching is a
bijection, and the repeated source/target role share is justified by the
stated containment. The saving of `m` per removed role must use the actual
role count, including outputs. A scalar XOR simplification alone supplies
neither a rational frame nor a rank saving.

The enormous width in the certificate is finite and input-independent.
The manuscript specifies finite tapes and uniform sweeps; its stated bound
may absorb that fixed width. This review found no necessity for an
unbounded alphabet or a tape count growing with the integer input length.

The stopped complex guard uses `s<m^5`, stops when `e<d^beta`, and bounds
the recursion depth by `(1-beta) log_m d+1`. Unrolling yields the claimed
`d^(5-4 beta)` term, from which the stated quadratic guard follows in its
parameter range. Pure encoding permutations add no arithmetic guard depth.
The original Gaussian restriction `alpha^4 theta>p` is stronger than
contractivity; replacing it requires an explicit new tail estimate and
numerical interface proof. That replacement is reviewed separately.

These checks concern the actual paired construction and manuscript
interfaces. They are not a new proof of the general lower-bound transfer,
the retained multiplication theorem, or its analytic imported facts.

## Reproduction and retained evidence

Run from the topic's `code` directory, using the immutable reference path
as `REF` and an external output path as `OUT`:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 review_aligned_graph.py --reference "$REF" --h 50 --output "$OUT"
PYTHONDONTWRITEBYTECODE=1 python3 review_rational_frames.py --census-h 10 --output "$OUT"
```

The first command also imports the campaign's `finite_block_search.py` to
construct the candidate. The protocol pins hashes of both the constructor
and independent checker. The second checker uses Python standard-library
`Fraction` arithmetic throughout. Compact results and input identities are
retained in `runs/20261007T224230Z-review-baseline/`. Original inputs were
read, not edited; no reviewed source's `__main__` was run.

Next steps are explicit rational eligibility checks for new shared spans,
independent endpoint/rank review for a reduced-register schedule, and the
separate blocked Gaussian convolution precision audit.
