# Independent analytical review of routed signed exchange

The all-size operator identity and stated single-child support boundary in
the coordinator's `routed_swap_alignment.py` are accepted by independent
algebra and read-only source inspection. The reviewed SHA256 is
`215a9d1b84df93c01ac1cd2b09c4475d3b2f388616fa9bfd0f85cbeab3285af5`.
This reviewer does not import or execute that producer, does not independently
rerun its 208 physical pair columns, and does not claim a native circuit lower
bound.

Let `A_U=C_U`, `A_T=C_T`, `F=C^tensorh`, and let P permute coordinates with
`P*U=T`. Then `P*A_U^-1=A_T^-1*P`, because permutation conjugation sends
the translation X_U to X_T. The literal two-by-two coefficients give
`A_T^2=X_T`, so `A_T^-2=X_T`. Consequently

```text
F*A_T^-1*P*A_U^-1 = F*A_T^-2*P = F*X_T*P.
```

This first identity holds for any invertible binary router sending U to T.
The canonical pair repair additionally uses `P^-1*F*P=F`, which follows for
coordinate permutations because every tensor factor of F is the same.
A general binary linear router need not commute with F; that generalization
would instead leave `P^-1*F*P` and requires another paid interface.

For input phase frames `diag(A_U,I)` and virtual signed exchange
`[[0,P^-1],[-P,0]]`, output frames `diag(F,F*A_T^-1)` give physical outputs

```text
x_out = F*P^-1*y_raw
y_out = -F*A_T^-1*P*A_U^-1*x_raw = -F*X_T*P*x_raw.
```

The monomial corrections `x_final=-P^-1*X_T*y_out` and
`y_final=P*x_out` produce `F*x_raw,F*y_raw` for coordinate P. The bank minus
sign is a scalar applied once to the whole payload. At f packed columns,
the line, translation and router operators are repeated tensors, retaining
their column phases; this does not turn the bank sign into `(-1)^f`.

The rank loss in the unrouted interface is also independently reconstructed.
For odd orthogonal U,T and coefficient kernel
`F(delta)=alpha^h*(-i)^weight(delta)`, put
`ell_L=(weight(L)-1)/2 mod2`. The ratio

```text
F(delta XOR L)/F(delta)
  = -i*(-1)^(ell_L+dot(delta,L))
```

holds for an odd L. Orthogonality makes the ratio for U+T factor into the
product of the two individual ratios. Expanding the two inverse line gates
therefore leaves nonzero coefficients precisely when
`dot(delta,U)=ell_U` and `dot(delta,T)=ell_T`. The two independent equations
give support `2^(h-2)`, including the affine offsets of odd weights other than
one. In f repeated columns the support is `2^((h-2)*f)`.

Routing aligns the two line gates, replacing their two independent equations
by a translation. `F*X_T*P` has support `2^(h*f)` in every complete column.
Invertible monomial and nonzero diagonal wrappers preserve column support.
A single `C_(h-2)` child with f columns has support only
`2^((h-2)*f)`; those wrappers cannot represent this routed full-support
operator. This accepts the scoped one-child exclusion.

Additional children, scalar mixers, copied streams, shared data/auxiliary
chronology, nonunitary factorizations and changed primitives are outside this
support argument. It does not show that every canonical signed exchange
costs full rank, nor that arbitrary routing is free. The coordinator's exact
finite controls and actual timing/namespace correction remain in its own
run receipt; this analytical review adds no measured execution claim.
