# Independent review of the sharper packed recurrence estimate

Campaign clock: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.
Pinned original: `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

The revised unrolling is valid for the branch `0 < b < a`, where
`a = 1 - tau`, `b = 1 - sigma`, and therefore `sigma > tau`. It changes
the estimate of the existing algorithm. It neither changes selected-bit
movement nor removes its quadratic dependence on the bit primitive saving.
This conclusion is conditional on the separately reviewed finite networks,
phase-cell inverse, and unaffected interfaces of the original complete
multiplication proof. It is not a formal verification of that entire proof.

## Source contract and all-size bound

The pinned `upstream/build/sections/05-layers.tex`, paragraphs “Where the
rows come from” and “Unrolling the recurrence”, supplies normalized time

```text
F(e) <= (s/W) F(e/m) + O(K^tau e^tau + 1),
F(e) = O(e) below e < d^beta,
s/W <= m^sigma, K <= d^c, e <= d.
```

The factor `s/W` follows from the exact `V/W` volume of each child stream.
The same global chunk width `K` remains in every call. The overhead bound
includes address permutations, exceptional-address repairs, descriptors,
parked streams, resets, scalar scans, and bank reassembly. The manuscript
uses `K <= e^(c/beta)` only to simplify the recurrence estimate. Retaining
`K^tau` outside the sum is compatible with its actual fixed-tape schedule.

Let `J` be the first stopped depth and `u = e/m^J`. For an initially internal
piece, `d^beta/m <= u < d^beta`. Since `sigma > tau`, the exact growing sum is

```text
K^tau e^tau sum_(j<J) m^(j(sigma-tau))
 < K^tau e^sigma u^(tau-sigma)/(m^(sigma-tau)-1)
 = O(K^tau e^sigma d^(beta(tau-sigma))).
```

The lower bound on `u` is necessary: an upper bound alone has the wrong
orientation for the negative exponent `tau-sigma`. The extra factor
`m^(sigma-tau)` and the geometric denominator are fixed constants, however
large they are. The independent controls exhibit the endpoint factor
explicitly. Constant per-node overhead is bounded by this sum because
`K,u >= 1` eventually. The leaf cost is
`O(e^sigma d^(beta(1-sigma)))`. Hence the two relevant powers of `d` are

```text
internal = sigma + beta(tau-sigma) + c tau,
leaf     = sigma + beta(1-sigma).
```

Pieces already below the stop are executed individually. Their cost is
covered because `leaf > beta`. The original base-`m` partition and prefix
preprocessing add `O(log d)` factors, absorbed by a strict `lambda_prime`
above both exponents. One may still choose `lambda` strictly above `sigma`,
`tau`, and `internal`, and strictly below `lambda_prime`.

The old condition `tau(1+c/beta) < lambda` is used only for the replaced
time estimate. The stopped-depth arithmetic guard depends on `beta` and
the executed network, not on that comparison. The phase, padding, residual
dimensions, inverse wrappers, arbitrary scratch contract, and tape counts
therefore retain their already reviewed proofs. Every new certified row
actually violates the old per-node comparison with `lambda_prime`; this is
explicitly a changed proof, rather than reuse of its obsolete hypothesis.

## Balance, scope, and independent arithmetic

With `x=1-beta` and `q=1-lambda_prime`, the two time savings require

```text
q < b x,
q < a(1-x) + b x - tau c.
```

At fixed `x`, the movement saving `a c` balances the second expression at
`c=a(1-x)+bx`, using `a+tau=1`. That balanced saving decreases with `x`,
whereas the leaf cap increases. Their intersection is

```text
x = a^2/(b tau + a^2),
c = a b/(b tau + a^2),
q = a^2 b/(b tau + a^2).
```

For the retained phase guard family `C1=1+4x+zeta`, its scoped limiting
ceiling is `a^2 b/(b tau+5a^2)`. It is increasing in both primitive
savings: the cleared numerator of the derivative in `a` is `2a-a^2 > 0`,
and the derivative in `b` is positive. Upper logarithm enclosures may thus
bound this family. This is not a ceiling for different movement or guard
algorithms. The actual top-level overhead remains `d^tau K^tau`, so
positive saving still requires `c < a/tau` and movement saving below
`a^2/tau` in this model.

The [independent checker](../code/review_packed_unrolling.py) recomputes
finite counts, uses longer independent exact logarithm enclosures, checks
all 26 strict conditions per row, reconstructs the exact balance and
unchanged guard/cell/scaling cutoffs, checks strict grid absorption, and
compares against independently validated old balance-root intervals.
The [completed run](../runs/20261008T001728Z-review-packed-unrolling/results/packed-unrolling-independent.json)
supports:

| Reviewed finite input | New kappa |
|---|---|
| Original h50, R509194 | 4394441151417/(5·10^29) |
| Envelope h50, R486200 | 4803028936777/(5·10^29) |
| Asymmetric p52,q48, Rp549120,Rq426624 | 2404771744437/(25·10^28) |

The relative improvements over the corresponding previous estimates are
about three parts per billion. They are exponent calculations, not measured
runtime improvements. The last row retains a common explicit cutoff
`log2(b_input) >= 6149507232401`, plus the retained prime and source
thresholds. New finite circuits outside these input rows require fresh
composition.

The same checker also executes 960 complete stopped recurrences with
`m=64`, `tau=1/2`, `sigma=2/3`, `beta=1/3`, `c=1/6`, integer global
`K`, genuine stopped leaves, and branching factors 12 and 16. It compares
bottom-up recurrence evaluation with the independently expanded sum and
the predicted powers `25/36` and `7/9`, including individual small pieces.
The first audit attempt stopped on a metadata lookup for derived `vp/vq`
fields absent from the producer row. Its source and explanation are
preserved under the run's `failed-v1/`; the corrected common-field check
passed without changing any arithmetic formula.

```sh
python3 -B research/integer-multiplication-bounds/code/review_packed_unrolling.py \
  --certificate research/integer-multiplication-bounds/runs/20261008T001126Z-downstream-packed-unrolling/results/certificate.json \
  --output /tmp/packed-unrolling-independent.json
```

The run protocol records Python 3.14.4, source and input hashes, the pinned
original section hash, commands, scope, and failed-attempt provenance.
