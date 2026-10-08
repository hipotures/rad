# Payload field and signed rational addresses in joint reclamation

Reviewed 2026-10-08 19:22 UTC against the immutable public PR62 head
`ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`. The scoped review concerns
the inherited bit construction and the new signed rational address frames.
It does not transfer the binary scalar word to the complex construction.
The exact source identities are recorded in
[the source-bound receipt](gpu-parameter-results/joint-reclaim-payload-field-scope-20261008T1922.json).

The book separates two domains. Section03 lines50–55 puts the bit scalar
payload in F2. Its rational labels construct operators on the address
indices, not scalar coefficients in that payload ring. Lines149–182 prove
the common-frame identity for any scalar ring R: all incidences of a
pointwise gate use the same invertible R-linear array operator, so the
gate commutes with that operator. With bit payload, R remains F2.

Section03 lines479–486 defines the rational-address frame Phi_M by moving
an entry from `(H,D)` to `(H+M D,D)`. Addition is modulo the common address
range, using a radix coprime to all fixed denominators. This is a permutation
of entries and hence an F2-linear array operator even if M contains signed
rational coefficients or the integer coefficient2. Section04 lines69–76
chooses an odd address prime avoiding every denominator and every nonzero
pivot numerator in the finite rational factorization table. Such a prime
exists because the table is finite. This field choice concerns address
coordinates; the payload is still one bit.

Consequently a paid GF2 reclamation relation between retired scalar values
and anchors is sufficient for its scalar XOR semantics. It need not be the
same span relation over Q. For example, the relation between binary rows
110, 011 and 101 is valid in F2 and fails as that same dependence over Q;
this is not an obstruction to the stated bit interface. Invertibility of a
binary support matrix and rational support dependence are distinct issues.

The signed address construction still requires its separate exact Q
obligations: every physical gate incidence must use its actual common
frame; all source and copied-center labels must be preserved; every claimed
nested transition must have proved containment and nondegeneracy; and the
paid residual profiles must be those of the executed word. The finite
dirty-basis scalar replay alone proves none of those Q properties. The
graph's complete address audit and geometry's fresh exact profiles are
therefore necessary dependencies, not interchangeable certificates.

Under those gates, signed rational coefficients introduce no new payload
field conversion. General finite-alphabet tape implementation and the
conditional rank recurrence retain their inherited proof obligations.
No unconditional field-lifting theorem or new multiplication bound is
claimed by this review.
