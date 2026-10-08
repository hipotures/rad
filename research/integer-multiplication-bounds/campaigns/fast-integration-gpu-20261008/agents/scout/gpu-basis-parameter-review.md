# Basis-parameter discovery: mathematical gates and execution scope

The coordinator assigned both GPUs and two CPU host slots at15:04 UTC.
The [initial implementation](code/gpu_basis_parameter_discovery.py) preserves
the inherited controlled-permutation CUDA kernel and indexes each block's
actual x/y weight arrays separately. It independently matches CPU modular
elimination on both initial source fixtures. Each8192-block batch varies
the actual rational basis pair, rather than replaying one fixed family.
The [initial completed evidence](gpu-parameter-results/initial-20261008T1518/manifest.json)
retains protocols, source hashes, seeds, full sampled candidates and outcomes.

For `L_h=I-beta_h J`, with beta not1/h, direct rank-one inversion gives

```
p_T=1_T-3*beta*1,
xi_T=(1_T+gamma*1)^T/2,
gamma=(9*beta-1)/[3(1-h*beta)].
```

Their coordinate products are `(1-3beta)(1+gamma)/2` inside T and
`-3beta*gamma/2` outside, with total one. Thus source nonzero coordinates
require beta outside `{0,1/3,1/9,1/h,2/[3(h-3)]}`. This exactly reproduces
the negative basis beta4/[3(h+3)] and I+J at beta=-1.

Copied-center coordinates add two more gates. Direct conjugation gives

```
p_i=e_i+[2-3*beta*(h-3)]/(h-9)*1,
xi_i(outside)=(h-9)*(1-3beta)/[12(1-hbeta)],
xi_i(center)=(h-9)*[-2+3beta*(h-1)]/[12(1-hbeta)].
```

All-center nonzero transfer also excludes beta `(h-7)/[3(h-3)]` and
`2/[3(h-1)]`. These extra conditions were derived independently and sent
to the coordinator immediately. The first discovery catalogue did not
filter those two points, so its outputs cannot be promoted without checking
them. No claim that every sampled first-run basis is a valid complete
copied-center transfer is made.

The [vectorized continuation](code/gpu_basis_parameter_vectorized.py) excludes
all seven values. It places precomputed inverse-weight tables on the actual
device and gathers parameter/source rows there. Each batch executes two
independent modular fields, retaining only matching complete pivot profiles.
An improvement is then checked against exact Fraction elimination on that
actual sampled matrix. Source inputs, parameter fractions, permutation,
pivots, modular arrays and sampled Q result are all retained. Its canonical
lambda denominators29/31/37/41 yield parameter pairs disjoint from the first
denominator<=24 catalogue; seeds and output paths are fresh. Initial observed
GPU utilization rose from approximately10–15% to90%/88% after vectorization.

Both fixtures use T23=(0,1,22), with S25=(0,2,24) and S25=(0,1,22).
The objective `sum run*log(run)` is a sample entropy heuristic, not the
assembled multiplication objective. Attempts can repeat parameter/permutation
pairs and must not be counted as unique mathematical candidates.

Even an exact Q sample is DISCOVERY ONLY. Promotion requires all actual
source pairs, universal ordered zero cuts or complete exact rank tables,
the actual changed-basis local-frame CRT profiles, copied centers, bridge
and restriction basis conditions, scalar/timeline/physical costs, eventual
address-prime exclusions and the full conditional assembly. Internal
changes cannot borrow a prior fixed-basis nonvanishing certificate after
altering these coefficients. No new kappa is claimed by this search.

## Completed mathematical discrimination

The first reported device0 candidate at beta25=1/57 is an exact rational
sample improvement of2log2 at its one-mutation permutation. The first
device1 candidate is a bad-prime artifact and was rejected after independent
Q and second-field checks; the original candidate remains intact. See
[the independent review](gpu-parameter-results/initial-candidate-rational-review.json).
The original regular negative data profile is21+17 with nine singletons.
The stronger21+19 discovery fixture is exceptional, not the regular profile.

Complete source-family discrimination separates basis and permutation.
The sample one-mutation permutation fragments most second blocks, with
width15 dominant. [Three independent exact Q representatives](gpu-parameter-results/bad-permutation-Q-representatives-20261008T1653.json)
confirm this failure. A sample entropy gain cannot be applied to all sources.
At the inherited permutation, beta25=1/57 instead removes fragmentation:
every actual pair has the same nine singletons, width21 and width17.

Three different source-weight families are now completely certified over Q:

| beta23 | beta25 | Integer scale | Entry bound | Primes | Bound bits | Product bits |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2/39 | 1/57 | 99 | 7542 | 24 | 740 | 744 |
| 1/51 | 1/57 | 36 | 5148 | 23 | 713 | 713 |
| 5/3 | 1/57 | 315 | 24633 | 27 | 819 | 837 |

Each family includes all1771 times2300=4,073,300 source pairs at the actual
inherited physical order. One complete expected modular profile attains
every lower NE-corner rank for each pair; the unlucky-field sets are
disjoint. Every larger corner minor vanishes in every proven31bit prime.
The exact product, compared as an integer, exceeds47^24 times the entry
bound to power47. Thus all larger integer minors are zero. The713-bit
product in the second row is strictly greater than its713-bit bound;
bit length equality alone was not used.

The [hybrid](gpu-parameter-results/hybrid-half-uniform-data-certificate.json),
[both-half](gpu-parameter-results/both-half-uniform-data-certificate.json) and
[five-thirds](gpu-parameter-results/five-thirds-half-uniform-data-certificate.json)
certificates retain exact histograms and identities. The
[independent byte-binding audit](gpu-parameter-results/complete-data-input-audit-20261008T1655.json)
rehashes all six full-family pivot arrays, checks exact dtype and lexical
coverage, source/dependency/CUDA/checker hashes, every prime receipt and
strict minor bounds. Its input-table hashes are independently regenerated
deterministic inputs, explicitly not GPU readbacks. The
[readable proof and interface](hybrid-half-data-proof.md) derives the
actual normalized matrix and separates the remaining assembly obligations.

The first31bit attempt failed before any prime replay was accepted:
`(v%p+p)%p` overflowed signed32. Original failure source, logs and receipt
are preserved. Fresh immutable derivatives use signed64 initialization,
branch normalization, canonical subtraction in(-p,p), and signed64 products
below p squared. Each successful prime run independently controls the full
pivot profile against CPU modular elimination, including negative and
near-prime entries. The full checker compares every NE rank; it does not
union permutation IDs or merely test full rank.

[Exact conjugacy](basis-conjugacy-review.md) gives beta-star=-gamma/3.
Conjugate roots share all source coordinate products and DATA matrices;
their source, center and signed-frame projectors transpose. Consequently
their local NE profiles require separate checks. In particular,1/57 and1/6
share data;5/3 and1/24 share data. Searching these as different DATA families
would duplicate mathematical work.

The [initial six complete runs](gpu-parameter-results/completed-20261008T1553/manifest.json)
and [fifteen subsequent complete/failed/stopped runs](gpu-parameter-results/completed-20261008T1657/manifest.json)
have readable protocols, outcomes, seeds, input identities and complete
unsplit text gzip archives. All archives passed original-file hash and
framing verification. Large binary pivot tables remain external; their
hashes, byte sizes and deterministic recovery are recorded in the summaries.
Two new deduplicated class continuations are separately live or subsequently
completed; the thirty-second status is an observation, not a proof receipt.


## Exhaustive field loci and changed source controls

The baseline joint-field experiment exhausts all1,073,086,564 admissible
canonical F65521 source-weight class pairs, split once across the devices,
with two actual source fixtures. Bounded rational reconstruction requires
numerator/denominator absolute bounds180, with2*180^2<65521, and an exact
square discriminant before a rational beta is accepted. Thus a field
singularity is not automatically a rational locus. The complete
[joint receipts](gpu-parameter-results/completed-20261008T1741/manifest.json)
retain both finite partitions and the new rational-pair whole-family test.

Besides the known negative class, baseline discovery found
beta23=-5/11, beta25=-4/9 with an exact21+19 rare sample.
Full source-family discrimination has3,880,336 agreeing ordinary21+17
profiles, only564 width19 calls, and372 field disagreements; substantial
fragmentation remains. Its [complete frequency receipt](gpu-parameter-results/new-joint-pair-20261008T1723/combined.json)
is discovery, not a uniform21+19 claim. Local cost also changed, so no full
CRT run or new multiplication saving was inferred.

The exact authorized [PR54 DATA identity](pr54-data-basis-compatibility.md)
closes full-data reuse for both I+J/conjugate choices on each axis. Its
current public head later moved; the original authorized84eb snapshot is
retained. The [mixed I+J23/negative25 proof](mixed-fixed-negative-data-proof.md)
separately closes that family using fresh retained mixed nonvanishing,
all-weight rational incidence bounds and22 independent Q controls.
These do not reuse the169 negative×negative exception classes.

Two exhaustive changed boundary-order catalogues were tested on the rare
fixtures. Exact +2log2 samples at the one-mutation order and beta25=1/6
occur across many left parameters, but new full-N tests with beta23=-1 and
1/13 still fragment, dominated by width15. This closes those sample-only
leads without further CRT. The later joint catalogue changes the actual
sources to contiguous(0,1,2)/(0,1,2) and spaced(3,9,15)/(5,11,17).
It exhausts the same finite parameter space on new matrices. Only two
bounded-lift Q samples improve the contiguous fixture, at(1/4,5/9) and
(5/17,5/13); neither improves the spaced fixture. Their complete full-N
checks have8,820 and8,818 agreeing +2log2 profiles respectively, with314
and384 field disagreements and an otherwise ordinary profile. These are
small nonuniform reserves; local/rational closure is pending. The user has
prioritized joint interval assembly over tiny parameter refinement.

The finite single-swap search changes only actual physical boundary order,
not a fixed family's repeated discovery fixture. Its945 endpoint signatures
are deduplicated exactly. A coefficient-free restriction-tree gate identifies
542 viable signatures and403 universally invalid ones. Earlier complete
negative receipts showed zero full-rank pairs for every invalid signature;
the successor prefilters these and excludes all completed prior questions.
Both actual source families are now discriminated over two fields for each
untouched valid order. No per-pair binary pivot arrays are kept for this
stage; complete frequency tables, controls and deterministic recovery are
recorded. A promising order would need a fresh retained-pivot rational
certificate and the complete scalar/physical/bridge gates.
