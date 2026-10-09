# Independent analytical review of the naive product-side exclusion

I accept the stated all-h exclusion for one dirty helper per nonzero
product-side edge with closed full-width center releases. This is a
conditional architecture obstruction, not a lower bound on general
reversible circuits or on the product fitting matrix itself. I inspected
the source and reconstructed the inequalities; I did not rerun its interval
controls or instantiate the product graph.

The reviewed [source](../../code/synthesis/tensor_center_side_preflight.py)
has SHA256
`115fe038048e8ed73e4639ca9118d791333c77662f0324efb8e87d2f836a3ace`.
It uses exact scalar counts and interval arithmetic without allocating the
large graph. The complete native product-center ledger is a premise here,
rather than an independently established physical implementation.

For the weight-five scalar center, put `v=choose(h,5)`, `q=choose(h,2)`.
Its polynomial is nonzero at intersections0,2,4,5. The nonzero row count is

```text
c(h)=choose(h-5,5)+10*choose(h-5,3)+5*(h-5)+1.
```

The product center K tensor K has N=v^2 sources and ambient dimension
m=h^2. Its diagonal entry is one. Hence the nonzero entries of its side
I-K tensor K number `c(h)^2-1` per source, and the model allocates
`M=N*(c(h)^2-1)` separate helpers. With the product center's three bank
families, the complete paid stock is `W=3N+M`.

Every side helper has an obligatory width-one entrance. Concentrating
all remaining rank m-1 into one child is optimistic: for0<s<1,
`sum_i t_i^s >= (sum_i t_i)^s`. Thus the proposed histogram
`n1=N+M`, `n_(m-1)=3N+M`, `n_m=2q^2` is a lower moment bound for this
model, not a claimed legal full circuit. Its first rank sum is exactly

```text
Wh^2-2N+2q^2*h^2.
```

At `b=1/10000`, the M obligatory width-one terms alone, using
`exp(z)>=1+z`, give

```text
Phi(1-b) >= 1+[b*M*ln(m)-2N+2q^2*m]/(W*m).
```

For h>=13, c(h) is nondecreasing and c(13)=657, while m>=169 and
ln(m)>1. Therefore, after discarding the nonnegative feature term, the
numerator divided by N is at least

```text
(657^2-1)/10000-2 = 25728/625 > 0.
```

This proves strict failure of the reference complex saving10^-4 in every
such size without a sweep. For h7 through h12, `v<=qh`, so even the
central deficit is nonpositive. A positive proper width-one term makes
`Phi(1-b)>Phi(1)>=1`; h12 equality does not escape the bound.

The proof needs the allocated M distinct side helpers, their full paid
payload/endpoints, the entrance calls, and the closed2q^2*m center fees.
Sharing/factorizing side channels, changing the central release, using a
joint signed exchange, or changing the primitive/transfer invalidates named
premises and requires a new argument. The conclusion already rejects the
optimistic framed profile; canonical input encodings would add costs.
No integer-multiplication kappa follows from a different profile merely
because this one is excluded.
