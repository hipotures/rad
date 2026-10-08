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
