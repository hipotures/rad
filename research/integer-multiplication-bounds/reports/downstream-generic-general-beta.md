# General rational stopping depth: complete generic-basis assembly

The fresh exact producer passes all eight conditional rows. Its strongest
candidate is

`kappa=400341739374364208307342473772447/10000000000000000000000000000000000000000`,

approximately `0.000000040034173937`,
and greater than `2^-25`. It is greater than
`482.339445029354467` times the newer upstream
`83/10^12` claim, and greater than
`2.377643171645184` times the
preceding independently accepted delayed-clone/joined witness.
**A complete independent final arithmetic review is still required.**
The previous headline remains unchanged until that review accepts this
new construction and parameter interface.

This combines the [constructive generic bit basis](downstream-generic-metric-characteristic.md)
with either the accepted original h28 R97586 complex circuit or its
independently accepted R92309 controller refinement. The new bit saving
exceeds both complex savings, so the stopping-depth choice has to change.
The exact semantic guard remains valid for every fixed rational beta;
no child truncation or representation rewrite is introduced.

## General-beta inequalities

Let `a` be the certified bit saving, `b` the complex saving,
`tau=1-a`, and `sigma=1-b`. The pinned compact-control layout supplies

`chi=tau+(1-beta)*max(sigma-tau,0)`,

`leaf=sigma+beta*(1-sigma)`, and `reserve=max(1-c,0)`.
These formulas retain the stopped growing geometric sum when
`tau<sigma`; they do not import the old root-dominated case.
The actual original lower bound on lambda is
`max(tau,sigma,chi)<lambda<lambda_prime`, not merely `chi<lambda`.
Take `q=1-lambda_prime` strictly below both `1-chi` and `1-leaf`,
and require `c>q`. Our lambda is the midpoint of the retained maximum
and lambda_prime. The certificate explicitly proves its positive gap
above all three lower exponents.

For `a>=b`, `1-chi=a*beta+b*(1-beta)` while
`1-leaf=b*(1-beta)`. Thus a small fixed positive beta allows `q` to
approach `b`. For `a<b`, `1-chi=a`; a sufficiently small positive beta
makes the leaf saving greater than `a`. In either order, the declared
family has supremum `theta=min(a,b)`. With completed balanced prefix
work the scoped cap is `theta/(1+theta)`; with the original incomplete
prefix work and `c>q`, it is `theta/(1+2theta)`. These are parameter
ceilings for the retained routing, resampling and precision family,
not lower bounds or universal algorithmic impossibility results.

The tight witnesses use `beta=2^-64` and fixed slack `h=2^-64`.
The conservative witnesses use `beta=h=2^-20`. Define
`q=b*(1-beta)*(1-2h)` in the present fast-bit case.
For balanced work take `c=q+h/4`, `epsilon=(1-h)/(1+q)`;
for original prefix work take `c=q*(1+h)`,
`epsilon=(1-h)/(1+c+q)`. Set `G=epsilon*q`,
`r=(G+1-epsilon)/2` and `delta=h/8`.
Every row verifies all seven original margin interfaces:

`g1=1-epsilon` (balanced) or `1-epsilon*(1+c)` (original),
`g2=a`, `g3=G`, `g4=a`,
`g5=min(1-epsilon-delta,r-delta)`,
`g6=1-epsilon-delta`, `g7=epsilon`.

The margin minimum is exactly `G`, and the compact reported kappa is
strictly below it. Gaussian cell/band, sublinear normalization,
prime interval, synthetic routing, exposure and artificial-boundary
conditions are saved separately. Tight negative controls show that the
old `beta=1/2` leaf cap and a tau-only lambda midpoint fail in this
primitive order. The source rederives all old four descendant rows and
also specializes the new formula to beta=1/2, reproducing their original
parameters, recurrence and margins exactly.

## Scalar guard and explicit leaf/row cutoffs

The accepted complex R92309 has actual grouped scalar gate count
`12567850311744`. The old `G_gates<6W` shortcut is false and is not used.
The exact literal depth bound is
`2*G_gates*W^2+4s+4W+4`, which is strictly below
`E=64(W+m+1)^3`. Set `B=s+E`, `C0=32mB^2`, `C1=1`.
The root-dominated child guard
`A(e)<=A(e/m)+s*e/m+E` bounds an active piece by `2Be`;
completed BASE-m pieces have total semantic size at most `d`.
Hence the entire layer is below `(2B+18)d<C0d`, independently of beta.
All values remain integers on the same fine grid until the complete
outer layer's original final truncation.

Let `d=floor(b_input^epsilon)`. The source explicitly requires
`d^beta>2max(m_bit,m_complex)` rather than assuming the stopping depth
is eventually suitable. Since `d>=b_input^epsilon/2` and `beta<1`,
it suffices that
`b_input^(epsilon*beta)>4max(m_bit,m_complex)`.
The conservative reciprocal ceiling and exact bit-length proof yield
six strict compressed certificates at the common cutoff and five
successive doublings. The strongest row's common numeric cutoff is

`log2(b_input)>=368934896244194840180`.

This is the explicit stopped-leaf threshold. The same row separately
checks the new generic reservoir
`b_input^(1-epsilon)>264000(log2(b_input)+8)`, giving enough `p^66000`
row stock after `e<=C*p`, `p>=C` and `log2 p>=25`. It does not reuse the
old `p^2600` depth. The exact sufficient phase-cell, gamma, scalar guard,
compact-control, K-geometry, microbox period and reservoir thresholds
are all present in the certificate.

A numeric common cutoff is not a bound on the uncomputed giant generic
isometry/table/prime, new fixed alphabet/layout constant C, or the
strict recurrence/polylog absorption constants. The latter include the
very small lambda and leaf gaps at beta=2^-64. These remain additional
explicitly scoped eventual thresholds, along with BHP existence,
setup amortization and the original conditional theorem interfaces.
The fixed rational stopping test is `e^v<d^u` for beta=u/v;
its large but fixed arithmetic/descriptor constants are also eventual.

## Eight exact witnesses

| Complex input | Slack | Prefix | Strict kappa | Common log2 b |
| --- | --- | --- | --- | ---: |
| original97586 | conservative | original | `189700405764318163719266770798721/5000000000000000000000000000000000000000` | 44461349193960001 |
| original97586 | conservative | balanced | `379400825923161907779286798455613/10000000000000000000000000000000000000000` | 837982072326401 |
| original97586 | tight | original | `379402258831601704590775927248419/10000000000000000000000000000000000000000` | 368934909469138635240 |
| original97586 | tight | balanced | `189701136613104825688811147134241/5000000000000000000000000000000000000000` | 368934895471664833800 |
| controller92309 | conservative | original | `200170098083216810395528749549729/5000000000000000000000000000000000000000` | 39931971348980737 |
| controller92309 | conservative | balanced | `400340212193692098624885121543603/10000000000000000000000000000000000000000` | 825426230773825 |
| controller92309 | tight | original | `200170861673507010709965930725339/5000000000000000000000000000000000000000` | 368934911014198648020 |
| controller92309 | tight | balanced | `400341739374364208307342473772447/10000000000000000000000000000000000000000` | 368934896244194840180 |

The [complete certificate](../runs/20261008T065403Z-downstream-generic-general-beta-repair/results/certificate.json)
has SHA256 `b69782fa9aea361cc23f34d6847692350ade755f2e104828d17010fc124986f8`. The exact child completed in 0.221s,
with 24,740KiB peak RSS and one thread, and released its own reservation.
The [protocol](../runs/20261008T065403Z-downstream-generic-general-beta-repair/protocol.json)
pins all sources, finite identities and independent input proofs.
No accepted large graph was recomputed.

## Reproduction, provenance and preserved negative

The reusable [general-beta arithmetic](../code/downstream_general_beta_semantic_bulk.py)
and [pinned full adapter](../code/downstream_generic_metric_semantic_bulk.py)
are frozen. The input proof chain includes the actual changed R485680
finite certificate, independent constructive generic theorem, root's
longer-log/actual-tensor-data review, accepted full predecessor review,
and complete R92309 complex scalar/frame/matching/dirty/G/E audit.

From this topic directory with one numerical thread and
`PYTHONINTMAXSTRDIGITS=0`, use a fresh output:

```bash
python3 code/downstream_generic_metric_semantic_bulk.py \
  --previous-descendant-assembly runs/20261008T062330Z-downstream-descendant-joined-assembly-repair/results/certificate.json \
  --previous-final-review runs/20261008T063322Z-review-descendant-joined-assembly-repair/results/certificate.json \
  --generic-characteristic runs/20261008T063741Z-downstream-generic-metric-characteristic/results/certificate.json \
  --root-generic-inputs runs/20261008T064015Z-review-generic-composition-inputs/results/certificate.json \
  --complex-controller-review runs/20261008T0415Z-review-complex-controller/results/certificate.json \
  --output /path/to/fresh-certificate.json
```

The first [attempt](../runs/20261008T065303Z-downstream-generic-general-beta/protocol.json)
failed before any mathematical result: the root review has one named
source SHA rather than a source-name dictionary. Its exact executed
[adapter snapshot](../code/downstream_generic_metric_semantic_bulk_v1.py)
and external traceback are preserved. The repair explicitly pins that
single source and resolves absolute review input paths; it does not
weaken any inequality or modify any immutable input. Historical result
bytes and source snapshots remain unchanged.

The campaign still started 2026-10-07 22:25:21 UTC. The original deadline
was 2026-10-08 08:25:21 UTC; the user authorized extension to 10:00 UTC.
This checkpoint is progress within that same campaign. New complex
clones and nonuniform complex boundary calls are separate hypotheses;
they are not included in this exact witness.
