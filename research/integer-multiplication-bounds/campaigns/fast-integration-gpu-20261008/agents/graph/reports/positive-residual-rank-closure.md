# Residual rank closure for the actual positive-frame compiler

The negative-basis composition uses the existing backward-positive spaces,
not newly assigned original-envelope spaces. The fresh literal compiler
receipt is [positive-negative-refined-compiler-1515.json](../results/positive-negative-refined-compiler-1515.json).
It independently checked both selected immutable DAGs and selected use maps:
h23 has 36,311 physical roles and 80,280 frame transitions; h25 has 47,979
roles and 106,163 transitions. The scalar outputs, retained-center terminal
chronology, exact rational containment, physical carrier allocation and
forward/reverse rank timelines passed. These are finite witness checks.

For a nondegenerate symmetric form, let V be a nondegenerate subspace of a
nondegenerate subspace U. Their orthogonal projectors satisfy

```
P_U P_V = P_V P_U = P_V,
(P_U - P_V)^2 = P_U - P_V,
im(P_U - P_V) = U intersect V-perp,
rank(P_U - P_V) = dim(U) - dim(V).
```

The first identities follow because P_U acts as the identity on V, and
orthogonal projection onto V kills U-perp. The decomposition
U = V direct-sum (U intersect V-perp) gives the rank equality. With the
rational Euclidean form, every subspace is nondegenerate. The compiler
reconstructs literal integer bases of each signed positive-frame class and
checks every physical nesting incidence exactly; it does not infer
containment merely from recorded ranks. Thus its recorded transition rank
is exactly the rank of the residual projector. Full and complementary
cleanup projectors have ranks dim(U) and h-dim(U), respectively.

Conjugating every projector by the same invertible address-basis matrix B
preserves multiplication, idempotence and rank. Consequently
B-inverse (P_U-P_V) B retains rank dim(U)-dim(V), including under the
negative basis. Transposition for the reverse-complement construction also
preserves rank. These identities justify ignoring minors larger than the
corresponding rank when certifying each actual child block. They do not
give the ranks of smaller child blocks or a bound on integer minors.

The geometry certificates separately check the rational matrix formulas,
denominators, modular profiles, minor bounds and CRT conditions. A reduction
to a finite characteristic requires the relevant Gram determinants and
basis denominators to remain nonzero. This note does not certify those
conditions for untested primes or replace the geometry certificates.

The scalar support audit uses exact integer coefficients. The packed dirty
JLV word checks use F2. Rational address-space projector identities are a
separate geometric statement. The all-size construction and eventual
machine/field transfer remain the conditional dependencies stated in the
coordinator report.
