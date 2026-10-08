# Keeping the packed chunk factor outside the recurrence sum

Campaign: immutable start 2026-10-07 22:25:21 UTC, deadline
2026-10-08 08:25:21 UTC. Pinned input:
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

The unchanged packed movement algorithm admits a slightly sharper
recurrence estimate. This is a changed estimate of the same executed
movement algorithm. The complete transfer and arithmetic rows passed
[independent review](review-packed-unrolling.md), including 960 complete
stopped recurrence controls and 26 strict conditions per selected row.
The phase-cell inverse used below has already passed
[independent review](review-phase-cell-inverse.md).

## Exact growing-geometric unroll

Write a=1-tau and b=1-sigma. The measured primitives satisfy
0<b<a, hence sigma>tau. At a node with e active chunks, the source
algorithm gives

```text
F(e)<=m^sigma F(e/m)+C*(K^tau e^tau+1),
K=Theta(d^c),
F(u)=O(u) at u<d^beta.
```

The hidden constants are fixed independently of p,d and payloads.
This follows from the pinned `upstream/build/sections/05-layers.tex`,
the packed selected-bit rectangle lemma, and the stated logical-volume
child factor. Its supplied proof replaces K by e^(c/beta) at every
internal node. Instead retain K^tau outside the unrolled sum.

For a piece with e>=d^beta, choose J minimal such that
u=e/m^J<d^beta. Its leaf size satisfies

```text
d^beta/m<=u<d^beta.
```

This lower bound is essential because tau-sigma<0. The internal
costs contributed by K^tau e^tau have sum

```text
C*K^tau e^tau * sum_(j=0)^(J-1) m^(j*(sigma-tau))
 < C*K^tau e^sigma u^(tau-sigma)/(m^(sigma-tau)-1)
 = O(K^tau e^sigma d^(beta*(tau-sigma))).
```

The geometric denominator is positive and fixed. It may be large;
it does not grow with the input. The separate constant-overhead sum
is O((e/u)^sigma), which is bounded by the displayed main sum since
K,u>=1. Leaves have combined normalized cost
O(e^sigma u^(1-sigma)), hence O(e^sigma d^(beta*(1-sigma))).

For e<=d, these exponents are

```text
internal = sigma+beta*(tau-sigma)+c*tau,
leaf     = sigma+beta*(1-sigma).
```

Pieces smaller than d^beta are executed individually; their O(e)
cost is bounded by O(d^leaf) because leaf>beta. The source partitions
the active chunks into O(log d) base-m pieces. Summing them costs
O(log d*(d^internal+d^leaf+1)), absorbed by any strict lambda_prime
above internal and leaf. No tape procedure, descriptor, padding,
exceptional repair, coefficient format or stopping test changes.
The same guard analysis applies to the same executed arithmetic graph.

Choose an auxiliary lambda strictly between max(sigma,internal) and
lambda_prime. Because sigma>tau and leaf>sigma, all formerly needed
lambda>max(tau,sigma) inequalities remain available. The old stronger
per-node comparison tau*(1+c/beta)<lambda is replaced by this unrolled
comparison; it is not assumed secretly in an intermediate step.

## Exact balance and scoped ceiling

Put x=1-beta and q=1-lambda_prime. The two savings constraints become

```text
q<b*x,
q<a*(1-x)+b*x-tau*c.
```

The movement saving is a*c. For a fixed x, balancing that saving with
the internal one gives

```text
c_star=a*(1-x)+b*x
```

because a+tau=1. Since a>b, the resulting a*c_star decreases with x;
the leaf cap b*x increases. Their intersection has the exact rational
solution

```text
x_star=a^2/(b*tau+a^2),
c_star=a*b/(b*tau+a^2),
q_star=b*x_star=a^2*b/(b*tau+a^2).
```

Within the reviewed phase guard family C1=1+4x+zeta, the two limiting
terms divided by 1+4x retain the same monotonicity. Letting fixed
zeta tend to zero and epsilon tend to 1/(1+4x), the scoped supremum is

```text
U=a^2*b/(b*tau+5*a^2).
```

This is increasing in each primitive saving. To check monotonicity in
a, write U=a^2/(1-a+5a^2/b); its numerator derivative after clearing
the positive squared denominator is 2a-a^2>0 for a<1. The b derivative
is positive as well. Therefore exact upper primitive log enclosures
give a valid upper ceiling in this restricted model. This is not an
upper bound for other movement algorithms, finite networks, guard
families or integer multiplication algorithms.

The actual top-level recurrence cost still contains d^tau K^tau.
For a positive saving, tau*(1+c)<1 is necessary for this estimate,
so c<a/tau and the movement margin is below a^2/tau. Thus the exact
unroll alone cannot remove the quadratic dependence on the bit
primitive. A genuinely different selected-bit movement estimate or a
stronger bit network would be needed to change that bottleneck.

## Strict witnesses and finite evidence

The [exact checker](../code/downstream_packed_unrolling.py) uses
rigorous primitive log intervals, the exact root above, c=(1-2^-32)c_star,
q=a*c and lambda_prime=1-q. Lambda is the midpoint between
lambda_prime and max(sigma,internal). It retains zeta=2^-30,
epsilon=(1-2^-20)/C1, r=(1-epsilon)/2 and delta=r/8. Every strict
slack is checked as a Python rational, with no floating-point threshold.
Kappa is a strict lower rational on the 10^-30 grid.

The [first exact run](../runs/20261008T001126Z-downstream-packed-unrolling/results/certificate.json)
supports these arithmetic candidates:

| Bit primitive | Kappa | Improvement over its old unroll |
|---|---|---|
| Unchanged h50 R509194 | 4394441151417/(5*10^29) | >1.000000002964654 |
| Envelope h50 R486200 | 4803028936777/(5*10^29) | >1.000000003099398 |
| Reviewed p52,q48,Rp549120,Rq426624 | 2404771744437/(25*10^28) | >1.000000003101437 |

All finite role counts are separately reviewed inputs. The complex
primitive remains the pinned h50 construction. The asymmetric counts
come from [the reviewed unequal motif](asymmetric-motifs.md), published
in RaD milestone `3a6f011fa00dd9b0082475fe51b8b4b8d34712ca`.
The new checker independently recomputes the same count formulas.
It also verifies 163 exact growing-geometric and balance identities,
all assembly slacks, guard/cell/scaling cutoffs, strict absorption and
the exact improvement over the old per-node proof.

The reviewed complete upstream multiplication theorem and unaffected
fixed-tape interfaces remain conditional inputs. This recurrence audit
does not formally verify that full algorithm. The relative gain is
about three parts per billion, not a practical runtime measurement.

```sh
python3 -B research/integer-multiplication-bounds/code/downstream_packed_unrolling.py \
  --upstream /path/to/pinned/integer-mult-bounds \
  --output /tmp/downstream-packed-unrolling.json
```

The next structural question is whether one can perform the selected-bit
change of basis using the number of selected bits rather than the full
guarded chunk width. The existing proof pays (eK)^tau because it moves
whole contiguous address chunks; merely renaming those selected positions
does not justify replacing that term by e^tau.
