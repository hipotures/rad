# Two-family bit batching with the retained complete multiplication estimates

The fresh producer gives the strict conditional tight balanced witness

\[
\kappa=\frac{2646714117957216181019532004157}{5\cdot10^{38}}
       =\frac{52934282359144323620390640083140}{10^{40}}.
\]

The arithmetic has passed. The independent full primitive transfer is
positive; independent final assembly arithmetic for this finer witness is
pending when this report is written. The theorem is conditional on the
retained chunk and multiplication interfaces and the reviewed routing,
semantic guard and bulk resampling proofs. It is not an unconditional
bound, a practical finite-size guarantee, or a novelty claim.

## Changed primitive and explicit proof input

The accepted h51 R502265 scalar circuit, rational frames and exact roles
are unchanged. The new movement implementation groups contiguous diagonal
Bruhat pivots of two disjoint auxiliary endpoint families into wider child
interchanges. It is a changed recursive implementation, rather than
rounding unused margin in the old uniform-shrink estimate.

The explicit bit input is

`a=1058685652786963/(2*10^23)`, `tau=1-a`.

It comes from the
[two-family Taylor certificate](../runs/20261008T043510Z-downstream-diagonal-join-bound/results/certificate.json),
not from `log(s/W)/log(m)`. The exact source rechecks that certificate, its
finite counts and its positive Taylor gap. For child rank counts n_r,

`W*m*exp(-a*log(m)) - sum(n_r*r*exp(-a*log(r)))`

is bounded below by

`D - a*(W*m*log(m)_upper - sum(n_r*r*log(r)_lower))
   - (a*a/2)*s*(log(m)_upper)^2`.

The elementary negative-exponential inequalities are valid for all
nonnegative arguments and require no geometric remainder denominator.
The first moment uses the exact middle endpoint histogram plus the
joined lower bound `(R+h)*v²*(m-4h)*log((m-4h)/(4h+1))`. Every other pivot
remains individual and the rank sum stays s.

The [independent primitive transfer](review-contiguous-pivot-transfer.md)
checks the universal low-rank rank profile, componentwise carry reset,
arbitrary integer widths/tails, original canonical factors and odd prime,
and row padding. Its
[kernel-hole review](../runs/20261008T0443Z-review-pivot-forbidden/results/certificate.json)
proves that joined kernel columns spaced h² apart cannot be rightmost
pivots. Consequently the uncapped joined runs have length at most h²-1,
so every child has width strictly less than e/h. This retains the larger
uncapped log-sum bound with the same simple depth bound as the earlier
capped alternative. The finite graph is not replayed or changed.

The independent primitive review initially certifies the slightly coarser
`a=5293423/10^15`. The present producer's finer Taylor input remains
explicit, permitting a separate exact longer-log check before promotion.

## Retained analytic assembly and checks

The fresh
[source](../code/downstream_batched_semantic_bulk_assembly.py) has executed
SHA256 `69e8d68b468526bde62b22a88a235c6d5b225e36fd06e11cb55f544761c4bbb7`.
It copies the frozen semantic/bulk witness algebra while replacing only
the bit certificate and the declared-exponent parameter cap. It verifies
the hashes of all retained dependencies and exactly reproduces every
uniform h51 conservative/tight and original/balanced row before composing
the new bit input.

The complex primitive stays accepted h28 R97586. Thus b_complex>a and
b_complex/2>a, beta=1/2 is valid, and the compact internal exponent is
tau. Arbitrary routing and bulk resampling give movement/exposure margins
a. The exact semantic guard remains C1=1 and C0=32m_complex(s_complex+E)².
The original-prefix and balanced-prefix alternatives retain the earlier
Gaussian, gamma, phase-cell, reservoir and interval inequalities.

All four new rows have positive rational slacks: 40 in the original
prefix and 41 in the balanced prefix. The tight original-prefix witness
is `2117371283157620008634707069231/(4*10^38)`, with common numeric
log2(input b) cutoff 2284051653235653185. The tight balanced row above
has cutoff 258254417031933722624. These cutoffs cover the listed numeric
inequalities; additional fixed-table/setup, prime-existence and strict
absorption thresholds remain explicit eventual assumptions.

The scoped parameter cap a/(1+a), or a/(1+2a) for the original prefix,
uses the **declared certified primitive exponent a**. It is not an upper
bound on all possible batched circuit improvements. The output names this
`declared_exponent_parameter_upper` to distinguish it from the earlier
uniform primitive enclosure.

## Quantitative row padding

The accepted invocation layout gives e<=C p for a fixed constant C; after
p>=C, e<=p². The kernel-hole bound gives depth at most ceil(log_h e),
and W<2^49. For log2(p)>=25,

`W^depth < 2^[49*(2*log2(p)+1)] < p^100`.

The producer separately checks the stronger field inequality

`b_input^(1-epsilon)>400*(log2(b_input)+8)`

at the common cutoff and five successive doublings. It uses integer
bit-length certificates, so no astronomical power is allocated. Since
p=6b_input, log2(p)<log2(b_input)+3; and the short axis has
ell>=b_input^(1-epsilon)/2. This implies ell>100log2(p), providing room
for the row span. Real-log monotonicity extends the first checked endpoint
to larger inputs. The existing fixed C threshold is kept separate; the
producer never asserts e<=2p or replaces C by a convenient small number.

## Run and reproduction

The completed run is
[20261008T045209Z-downstream-batched-semantic-bulk](../runs/20261008T045209Z-downstream-batched-semantic-bulk/protocol.json).
Its compact
[certificate](../runs/20261008T045209Z-downstream-batched-semantic-bulk/results/certificate.json)
contains all exact parameters, margins, primitive proof inputs, row power
checks, dependency hashes and cutoff certificates. The protocol retains
the complete command and input hashes, one-worker admission, and external
stdout path. Reproduce the saved command with a fresh output filename.

The source and result are stable for final independent review and parent
publication. The optional third data-edge family is excluded from this
baseline and has its own prospective arithmetic. The original campaign
start 2026-10-07 22:25:21 UTC, original deadline 2026-10-08 08:25:21 UTC,
and authorized extended deadline 2026-10-08 10:00:00 UTC are retained.
