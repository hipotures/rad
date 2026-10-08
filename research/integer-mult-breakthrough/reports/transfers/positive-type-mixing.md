# Positive type mixing preserves the complete moment barrier

Status: **EXACT CERTIFICATE** for the supplied finite moment arithmetic and
**REFUTED WITHIN STATED SCOPE** for exponent amplification by child relabeling.
This is an obstruction to a particular recurrence certificate. It is not a
lower bound for integer multiplication, arbitrary circuit synthesis, or a
different conversion algorithm.

## Question and mathematical leverage

Can mutually recursive binary and complex primitives gain more than either
retained primitive merely by changing children's types, alternating stages,
using unequal type potentials, or composing complete levels?

Such a mechanism would be attractive because a successful amplification could
avoid constructing a much stronger complex circuit. The frozen complex
characteristic is only slightly above its saved saving: its full root is in
`(71744621/10^12, 71744622/10^12)`. The old final binary root is in
`(476829673/10^13, 476829675/10^13)`. Both are below `1e-4`.
The experiment uses all child multiplicities, including complete exterior
payloads; equal ranks or maximum-child proxies are insufficient.

## Recurrence and scope

For type `i`, retain the complete normalized recurrence

```text
F_i(e) <= (1/W_i) sum_(t,j) n_(i,t,j) F_j(t floor(e/m_i)) + K_i,
sum_j n_(i,t,j) = n_(i,t),
0 < t < m_i, n_(i,t,j) >= 0.
```

The changed hypothesis is only the type assigned to a complete child. Every
native child ratio, multiplicity, normalization, complete payload and fixed
overhead remains paid. An exact type conversion would need an independently
justified implementation; this note optimistically lets it cost nothing.
Additional nonnegative conversion work cannot repair the obstruction below.
This optimism does not certify any conversion.

For a saving `s` and positive constants `c_j`, the candidate potential is
`F_j(e) <= c_j e^(1-s)`. Its complete moment matrix is

```text
M_ij(s) = (1/W_i) sum_t n_(i,t,j) (t/m_i)^(1-s).
sum_j M_ij(s) = H_i(s)
                = sum_t n_(i,t) t/(m_i W_i) exp(s log(m_i/t)).
```

Every `H_i` is strictly increasing because every retained child has positive
mass and contracts. The supplied profiles have `H_i(0)<1`, so the individual
root is unique where bracketed. A strict common polynomial supersolution
requires `M(s)c<c` componentwise. Floors only decrease the positive power and
do not supply a new constant relative saving at all sufficiently large sizes.

## Lemma: no positive potential above every retained root

Let `M` be a finite nonnegative square matrix with every row sum at least one.
For any strictly positive vector `c`, choose an index `i` minimizing `c_i`.
Then

```text
(M c)_i = sum_j M_ij c_j >= c_i sum_j M_ij >= c_i.
```

Thus `M c<c` is impossible. This directly proves the required comparison
without assuming irreducibility, a positive eigenvector, or nonzero entries.
Equivalently the Perron spectral radius is at least one, by the standard
nonnegative-matrix comparison. The elementary argument is the proof used
here; numerical eigenvalues are not certificates.

If every complete level matrix `M_l` satisfies `M_l 1>=1`, their product does
too: nonnegativity gives `M_1 M_2 1>=M_1 1>=1`, and induction extends this to
any finite product. Level alternation therefore leaves this barrier intact.
The proof also applies to a closed set of reachable types; unreachable types
may be omitted only when no retained child exits the remaining set.

Rows of sum exactly one exclude strict contraction, even if reducible. A row
of sum below one removes this particular obstruction, but does not establish
that the whole matrix contracts. Zero type potentials and signed work charges
are outside the cost model. Algebraic cancellation inside a circuit is lawful
when its actual executed gates and child calls are paid; that is a change to
the circuit or child distribution, rather than negative elapsed time.

The conclusion is that positive reassignment with unchanged complete moments
cannot certify a saving above the largest retained primitive root. It can
improve a coupling that unnecessarily uses the poorer root. It cannot cross
`1e-4` for these two frozen profiles.

## Exact discriminator and negative controls

The independently authored [checker](../../code/transfers/coupled_moments.py)
uses rational atanh-series logarithm enclosures, rational exponential
remainder bounds, and outward dyadic rounding. It does not import an old
producer or trust a saved PASS field.

At `s=1/10000`, the verified lower excesses over one are approximately

| Full profile | Lower moment excess |
|---|---:|
| Final old binary | `2.3490202812e-5` |
| Frozen PR36 complex | `5.3997976237e-6` |

The four-worker run checked 384 assigned recurrence matrices and 1,584
varying-level products. Complete integer child counts were split among types
with four distinct fixed seeds. Diagonal reducible matrices, directed cycles,
random assignments, unequal potentials and exact unit-row boundaries were
included. The analytical lemma covers all such assignments; the experiment
checks the implemented arithmetic and retained ledger, rather than replacing
that proof by sampling.

Two substantive negative controls distinguish tempting shortcuts:

1. Deleting all high-rank complete children changes both target moments from
   above one to below one. This produces a fictitious `1e-4` certificate while
   omitting actual recursive payload work.
2. With the final old binary saving, `epsilon=999999/1000000`,
   `q=epsilon*a` and `kappa=99999*a/100000`, the old nonlinear triangular CRT
   exponent is `epsilon`, exceeding `1-kappa`. Substituting the known-bit
   router exponent `1-a` makes that necessary row pass. The substitution is
   unsupported: the CRT map is nonlinear and its complete payload movement
   needs the separate guarded-reflection construction and integration proof.

Invalid signed costs, zero potentials and subunit row hypotheses are rejected
with nonzero failure on unexpected acceptance. The checker also replays both
root brackets directly from all supplied multiplicities.

## Sources and attribution

The compact [input fixture](../../fixtures/transfers/frozen-full-moments.json)
records original source paths and hashes. The binary distribution is extracted
read-only from `hipotures/rad` at
`0aea633524d6e54e21c077fb6af0bbc6aaa37a81`, the final accepted old campaign.
Its physical and all-size claims retain the limitations of that campaign.
The complex distribution was independently reconstructed by the new complex
track from CrocSwap/integer-mult-bounds PR36 at
`11817ccacb564bb7f98789c20dc11d3fece207e3`. The prior Rohan Arun, Zhihao Chen,
James Chang, Rohan Gupta, eumemic, Chafik Boukhalfa and RaD contributions retain
their original source notices. This new recurrence lemma and checker were
written with AI assistance during the breakthrough campaign. Worldwide
novelty, external peer review and formal verification are not claimed.

## Continuation

The next useful candidate must change actual row moments or create a different
size/cost relation: a new phase primitive, a paid conversion with a stronger
child contraction, a genuinely shared global circuit, or another transform
architecture. Sweeping mixing fractions or asymmetric stopping parameters
under these frozen moments is abandoned as a route to `1e-4`.

The old guarded CRT/packed Gaussian transfer is an independent integration
obligation. It can recover lost savings toward the binary primitive; it cannot
amplify that primitive past its own frozen root merely by improving the outer
cost ledger.
