# A weighted Neumann estimate for Gaussian resampling

Campaign `20261007T222521Z`, immutable start 2026-10-07 22:25:21 UTC,
deadline 2026-10-08 08:25:21 UTC. This branch changes a downstream analytic
estimate and the Gaussian width; it does not change the upstream paired bit
graph or the fixed finite-alphabet, fixed-tape computational model.

The starting checkout is CrocSwap/integer-mult-bounds at
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`. The advertised conditional saving
is `2^-59`; the actual certified margin is
`272158569/156250000000000000000000000`.

## Proposed improvement and current verification boundary

The weighted estimate below supports a Neumann cutoff
`k = ceil(1/theta) + ceil(p/alpha^2)` instead of
`ceil(p/(alpha^2*theta))`. Choosing
`alpha = ceil((32*b)^(1/4))`, `p=6*b`, and `epsilon<1/4` gives the same
ordered Gaussian line cost `O(t*p^(3/2+delta)*alpha)`, but removes `d`
from the width. The normalized tensor Gaussian cost exponent changes from
`3/4+delta+5*epsilon/4` to `3/4+delta+epsilon`.

This is a changed estimate and parameter construction. Merely choosing a
different kappa below the starting certificate's existing margin would not
produce this dimension increase. Exact finite identities and assembly
inequalities are checked by
[downstream_gaussian.py](../code/downstream_gaussian.py). The following is
a mathematical proof, conditional on the same Gaussian identity,
scalar numerical routines, finite-network transfer, and multiplication
interfaces already assumed by the starting paper. Full upstream theorem
formalization is outside the certificate's scope.

## Weighted power bound

Write `rho=t/s=1+theta`, and extend all integer indices periodically with
`q_j=floor(rho*j+1/2)` and `beta_j=rho*j-q_j`. Then
`-1/2<=beta_j<1/2`, `q_(j+s)=q_j+t`, and `beta_(j+s)=beta_j`.
For `u=alpha^2`, the matrix `E=N-I` acts by the periodic sum

```text
(E z)_j = sum over delta in Z\{0}
          exp(-pi*u*phi(j,delta)) z_(j+delta),
phi(j,delta) = (rho*delta+beta_j)^2-beta_(j+delta)^2.
```

This includes aliases with `delta` a nonzero multiple of `s`. They contribute
to the diagonal of `E` and must not be omitted.

Put `g=q_(j+delta)-q_j-delta`, an integer. Expansion gives the exact identity

```text
phi(j,delta) - (beta_(j+delta)^2-beta_j^2)/theta
 = rho * [delta^2 + g*(g+2*beta_(j+delta))/theta]
 >= rho*delta^2.
```

The inequality follows because `g*(g+2*beta)>=0` for every integer `g`
and every `beta` in the rounding interval. For `g>=1` both factors are
nonnegative; for `g<=-1` both are nonpositive; `g=0` gives zero.

Define a positive periodic diagonal matrix
`W_j=exp(pi*u*beta_j^2/theta)`. The orientation is `W^-1 E W`:
its individual summands have exponents
`-pi*u*[phi-(beta_(j+delta)^2-beta_j^2)/theta]`. Thus its maximum-row-sum
norm is at most

```text
r_alpha = 2 * sum(delta>=1) exp(-pi*u*rho*delta^2) < exp(-u),  u>=4.
```

For a simple rigorous constant bound, use `rho>1`, `pi>3`, and
`delta^2>=delta` to obtain
`r_alpha < 2*exp(-3u)/(1-exp(-3u)) < exp(-u)`.
The last comparison is equivalent to
`2*exp(-2u)+exp(-3u)<1`, and follows for `u>=4` from
`exp(1)>2` and `2/2^8+1/2^12<1`.

No weights are computed or stored by the algorithm. They are used only in
the estimate. Their condition-number bound is
`max(W)/min(W)<=exp(pi*u/(4*theta))<exp(u/theta)` using `pi<4`.
Consequently

```text
||E^k|| <= max(W)/min(W) * ||W^-1 E W||^k
         < exp(u/theta-k*u).
```

The integer cutoff `k=ceil(1/theta)+ceil(p/u)` therefore gives
`||E^k||<exp(-p)<2^-p`. This controls the actual unweighted error; no
weighted norm is substituted for the multiplication interface's norm.

## Retaining contraction, numerical accuracy, and tape costs

The retained Gaussian inverse argument only needs `u*theta>1` to establish
`||E||<0.42` and `||J'||<7/8`, where `J'=N^-1/2`. The stronger old
condition `alpha^4*theta>p` was used to turn the old Neumann cutoff into
`k<=alpha^2+1`. The contraction and Gaussian identity survive with
`u*theta>1`; this must be stated as a replacement interface, not a silent
change to the old verifier.

Keep `theta>1/(4d)` from the same prime intervals. Set
`alpha=ceil((32b)^(1/4))`, `p=6b`, and `d=floor(b^epsilon)` with
`epsilon<=1/4`. Then `u>=sqrt(32b)` and `d<=b^(1/4)`, so
`u*theta>sqrt(32b)/(4b^(1/4))>1`. The function
`f(u)=u^2-4du-6b` is increasing for `u>=sqrt(32b)>2d`, and

```text
f(sqrt(32b)) = 26b-4d*sqrt(32b)
             >= 26b-4sqrt(32)*b^(3/4)
             > 26b-24b >= 2b > 0.
```

Since `ceil(1/theta)<=4d`, and `p/u<u-4d` with the right side integral,
`ceil(p/u)<=u-4d`. The replacement cutoff obeys `k<=u=alpha^2`.
For `b>16`, the bound `alpha<=2*(32b)^(1/4)` also gives
`u<24*sqrt(b)<6b=p`, hence `alpha<sqrt(p)` and `k<p`.

Audit of the published constructive proofs of Harvey and van der Hoeven's
Gaussian scalar maps shows that their `S'`, `D'`, and one-step `E` algorithms
use `alpha>=2`, `alpha<sqrt(p)`, and `u*theta>1`, but not
`alpha^4*theta>p` elsewhere. Their Gaussian tails, grid rounding, and
window sizes remain the same. The one-step approximation has scaled error
less than `p/3` and returns disk-grid values. Contractivity gives scaled
error at most `2p/3` for every approximate Neumann iterate. Summing `k`
iterates exactly, and using the new unweighted remainder, bounds the
scaled `J'` error by `(2/3)*k*p+1 < 3p^2/4` when `p>100` and `k<=p`.
The contraction `||J'||<7/8` then preserves the disk output margin exactly
as in the retained argument. Completed iterates alone are reused as inputs;
partial signed sums use `O(p+log k)=O(p)` bits and need not be contractions.

Each `E` call scans radius `ceil(sqrt(p)/(2alpha))` windows and costs
`O(t*p^(3/2+delta)/alpha)`; `k<=alpha^2` gives total
`O(t*p^(3/2+delta)*alpha)`. The forward `S'` map retains the same bound.
All record conversions, cyclic boundary traversals, exact accumulation,
ordered coordinate output, cleanup, and fixed tape counts are retained.
The algorithm never stores `W` or evaluates its exponential entries.

## Propagation through the assembly

The new width has exponent `1/4` in `p`, instead of `(1+epsilon)/4`.
Therefore `gamma=2d*alpha^2<46d*sqrt(b)` has exponent
`1/2+epsilon`, below one for `epsilon<1/2`. The unchanged cutoff
`b>=2^40` suffices to give `gamma<=b/4` for every `epsilon<=1/4`, since
`184^4<2^40`. The source-scale error amplification and final rounding
bounds therefore remain valid. Prime-interval growth uses
`1-2*epsilon>0`; product capacity, coprimality, source degree, and all
other source-scaling and disk margins are unchanged.

The stopped complex guard continues with `C1=2`, `beta>=9/10`, and
`2*epsilon<1`. The bit circuit performs exact permutations of encodings,
so the analytic change adds no coefficient-depth term to that guard.
The new Gaussian cost margin is `g5=1/4-delta-epsilon`; the remaining
six assembly margins are unchanged. For the unchanged paired graph,
take the retained `a_bit=296/10^11`, `a_complex=1/10^11`, and

```text
epsilon=249/1000, beta=999/1000, delta=1/10000,
c=beta*a_bit,
lambda=1-(1+beta)*a_bit^2/2,
lambda_prime=1-beta*a_bit^2.
```

The strict minimum margin is `epsilon*beta*a_bit^2` and exceeds
`kappa=5/2^61`, exactly `5/4` times the advertised starting kappa.
The original finite counts and all retained rank/frame assumptions are
unchanged in this witness. A separate composition with a campaign circuit
must carry that circuit's independent coefficient, restoration, frame, and
rank certificate.

## Sources, evidence, and novelty status

Primary analytic source: David Harvey and Joris van der Hoeven,
*Integer multiplication in time O(n log n)*, Annals of Mathematics
193(2), 563–617 (2021), DOI `10.4007/annals.2021.193.2.4`;
[45-page author manuscript](https://www.texmacs.org/joris/nlogn/nlogn.pdf),
Sections 4.1–4.3, checked 2026-10-07. This report derives its similarity
identity independently from the Gaussian matrix definition. No priority or
exhaustive literature novelty claim is made.

Pinned starting implementation/proof references: `notes/paired-note.tex`,
`notes/stopped-guard.tex`, and manuscript `07-resampling.tex` and
`08-assembly.tex` inside the pinned upstream checkout. The exact checker
records their hashes. Parent campaign integration owns the acquisition
manifest, shared README, hypothesis ledger, and Git publication.

Next: independent adversarial review of this replacement scalar interface,
exact regeneration of the witness, and exploration of sharper Gaussian
evaluation costs beyond this Neumann estimate.

The complete arithmetic milestone, including an independently computed
logarithm enclosure, is in
[the exact certificate](../runs/20261007T224116Z-downstream-weighted-gaussian-log-audit/results/certificate.json).
The subsequent [blocked Gaussian extension](downstream-blocked-gaussian.md)
reduces the per-iteration arithmetic cost and permits a larger dimension.

The first combined-role arithmetic trial used `a_bit=306/10^11` with
`R=494250`; this failed the exact finite-saving requirement.
The supported ratio is `eta_b/(11737/1000)=23/7539555375`, strictly
between `305/10^11` and `306/10^11`. The repaired composition uses
`305/10^11`; the original-graph witness is unaffected. This was a
screening rejection, not a change to a verifier threshold.
