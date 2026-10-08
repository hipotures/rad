# Payload and address fields in the two-center construction

This supplements the frozen [two-center derivation](downstream-two-disjoint-centers.md)
without changing its executed source or certificates.

The incidence, central basis and gather/scatter coefficients act on the
**bit payload F2**. The native coordinate frames and projectors are
defined over Q, then reduced into the original fixed admissible
**odd-prime address field Fq**. These fields have separate roles.

For the row `1-e0`, the coefficient of a triple T is
`3-[0 in T]`. In the payload field this equals `1-[0 in T]`, exactly
the complement of the first row's support. There is no factor1/3 and
no weighted payload addition. The literal native checker applies XOR
to payload records and fixed-q address permutations to their locations.

Over Q or an odd payload field, those two coefficient rows would not
have disjoint supports. The protected-frame claim does not cover that
different scalar program. The identity `R'G'=Inc^T Inc` is formal under
an invertible T, but the low-frame containment proof additionally uses
the F2 support pattern. A formal rational matrix product alone is not
the native implementation asserted here.

The new native address table must avoid the finite exceptional
denominators and profile factors for all changed Q-projectors, including
the nonzero factors9-h and10-h. Those are fixed setup constraints on q;
they do not change payload arithmetic. The address alphabet is not
inflated to encode the center-basis coefficients.
