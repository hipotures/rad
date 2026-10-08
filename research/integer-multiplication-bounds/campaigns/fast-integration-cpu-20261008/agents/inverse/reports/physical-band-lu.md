# Physical banded LU for rare principal-window repair

Status: direct bounded-precision lemma for real banded matrices close to the
identity. This avoids large phase similarities in exceptional inverse patches.
The global/local Gaussian tail is supplied by the separate locality report.
Sparse input-patch acquisition and the complete composition remain separate.

## Matrix assumptions and exact no-pivot factors

Let `A` be an `m` by `m` real matrix of half-bandwidth `w>=1`, with positive
diagonal and `||A-I||_infinity<=1/16`. Thus every row has diagonal-dominance
gap at least `15/16`, row norm at most `17/16`, and `||A^-1||<=16/15<2`.

For one leading pivot `k`, write
`S_ij=A_ij-A_ik*A_kj/A_kk`. For any remaining row `i`,

```
S_ii-sum_(j!=i,k)|S_ij|
 >= [A_ii-sum_(j!=i)|A_ij|]
    +|A_ik|*[1-sum_(j!=k)|A_kj|/A_kk].
```

The diagonal stays positive, the gap does not decrease, and the analogous
upper triangle inequality gives

```
sum_(j!=k)|S_ij|
 <=sum_j|A_ij|-|A_ik|*[1-sum_(j!=k)|A_kj|/A_kk]
 <=sum_j|A_ij|.
```

Induction proves nonzero positive pivots without pivoting. Half-bandwidth `w`
is preserved: a pivot only joins rows/columns already within its `w`-frontier.
Exact factors obey `U_ii>=15/16`, `||U||<=17/16`, and `|L_ij|<2`.
Consequently `||L||<=1+2w`; using `LU=A` also gives
`||L^-1||=||U A^-1||<2` and `||U^-1||<2(1+2w)`.

## Fixed-grid factorization has a local backward error

Use the common fractional grid `eta=2^-P`. At pivot `k`, round each multiplier
`S_ik/U_kk` down to this grid and then round each completed Schur update
`S_ij-L_ik*U_kj` to this grid. Values may be signed; downward rounding still
has absolute error less than `eta`.

Assume inductively `U_kk<=2`. The reconstructed pivot-column error is below
`2eta`, and each updated trailing entry has error below `eta`. In the
original matrix, these local errors need no norm amplification from previously
eliminated columns: the accumulated lower prefix factor has identity on the
remaining trailing block, and each new error is supported in that block.
Each original row participates in at most `w` pivot steps; each step changes
at most `w` trailing entries plus its pivot column. Hence the final exact
residual of the stored factors satisfies

```
A+Delta= L_hat U_hat,
||Delta|| < w*(w+2)*eta.
```

This same estimate applies at every partial stage. If
`w*(w+2)*eta<=1/16`, the corresponding perturbed original matrix has gap at
least `7/8` and row norm at most `9/8`. Exact Schur preservation therefore
closes the induction: every computed pivot lies between `7/8` and `9/8`,
every multiplier has modulus below two, and the stored factors satisfy
`||U_hat||<2`, `||L_hat||<=1+2w`, `||L_hat^-1||<2`.
There is no exponential-in-`m` elimination estimate or growing rational
denominator requirement.

All intermediate products use at most twice `P` fractional bits, plus the
`O(log w)` accumulation guard, and are rounded back to the common grid.
The temporary double precision is still `O(P)`.

## Rounded reciprocals and online residuals

Store the reciprocal of each `U_hat_ii` rounded to the same grid. Each exact
reciprocal lies between `1/2` and two. For `eta<=1/4`, replacing the diagonal
by the exact reciprocal of the stored value changes it by less than `8eta`.
Call the resulting triangular factor `U_eff` and `A_eff=L_hat U_eff`.

Combining factorization and reciprocal errors gives conservatively

```
||A_eff-A|| <32*(w+1)^2*eta.
```

Take `eta<=1/[512(w+1)^2]`; then `A_eff` retains a fixed row gap and
`||A_eff^-1||<2`. A forward substitution rounds each completed row dot
once. Back substitution rounds its completed off-diagonal dot and reciprocal
product once each. Their exact triangular residuals have row norm at most
`eta` and `6eta`, respectively. Therefore the returned `x_hat` has

```
||A_eff x_hat-b|| <=16*(w+1)*eta,
||x_hat|| <=4*max(1,||b||),
||x_hat-A^-1 b|| <2^12*(w+1)^2*eta*max(1,||b||).
```

A sufficient common precision for target error `2^-Q` and bounded input is

```
P=Q+ceil(log2[2^14*(w+1)^2])+ceil(log2 B)
 =Q+O(log w+log B), B=max(1,||b||).
```

This bound concerns the rounded matrix `A`. Its Gaussian-entry and remote
alias/truncation perturbation must be added through the inverse resolvent.
Because both inverse norms remain below two, an input-matrix row perturbation
`epsilon_A` contributes at most `4epsilon_A*||b||`. Choosing its row error
below `2^-Q/16` leaves an explicit share of the final error budget.

## Fixed-tape setup and application

The factorization stores one moving frontier of `O(w)` rows, each with
`O(w)` matrix/factor entries. For each pivot, scan its `w`-entry upper row
against each of at most `w` trailing rows. Rewinding the pivot row, advancing
through a complete trailing row, and compacting the frontier all cost
`O(w^2 P)` head steps per pivot. Completed lower/upper rows are emitted in
row order when a frontier row becomes the next pivot. No random matrix
addressing is used. The fixed set of frontier tapes is reused across patches.

Online substitution keeps the previous or following `w` solution values as
an ordered buffer. Each row is one factor scan plus a buffer scan/return;
shifting the buffer is `O(wP)` per row. The reverse sweep reads fixed-width
factor rows in reverse order. A constant number of tapes handles both real
and imaginary components.

Setup therefore costs `O(m*w^2*M(P))`, and online application costs
`O(m*w*M(P))`, where the established scalar multiplier may be bounded by
`M(P)=O(P^(1+zeta))` for any fixed `zeta>0`. Setup need not be cached to
obtain the rare-repair estimate. The line's actual data and output movement
are included in these bounds; global sparse sorting/acquisition is separate.

## Gaussian applicability and rare-volume accounting

For the physical Gaussian matrix, nearest off-diagonal exponents satisfy
`X>=2theta`, while distances `|h|>=2` satisfy `X>=|h|(|h|-1)`.
Thus at `u*theta>=1`, `u>=4`, `theta<=1/4`,

```
||N-I||
 <=2exp(-2pi*u*theta)+2sum_(h>=2)exp[-pi*u*h*(h-1)]
 <1/16.
```

One simple rational bound uses `pi>3`, `exp(1)>2`: the nearest sum is below
`1/32`; the farther sum is below `2*2^-24/(1-2^-12)<1/32`.
All nonzero period aliases are part of this inequality. Truncating and
rounding down positive off-diagonal Gaussian coefficients preserves the
near-identity bound; dropping diagonal aliases is a separately charged
perturbation.

A local lifted window shorter than half the period has no uncharged cyclic
border. Its omitted remote images are bounded by their original Gaussian
exponents. The global locality lemma connects its principal inverse to the
desired core output, including windows crossing a physical period cut.

In the candidate parameters `Q=Theta(d^18)`, `u=Theta(Q/d)`, the required
direct Gaussian half-bandwidth has `w^2=O(Q/u)=O(d)` after a constant larger
accuracy budget is assigned to its coefficient tail. If rare gathered input
patches occupy fraction `rho=O(d^-3)` of the full `TQ=Theta(n)` bit volume,
factoring/applying up to `d` axes costs

```
O(rho*n*d*w^2*Q^zeta)=O(n*d^-1*Q^zeta).
```

For sufficiently small fixed `zeta`, this is absorbed. The hypothesis is the
**actual gathered patch volume**, not merely a count of rare output rows.
Sorting its payloads up to `d` times costs separately
`O(rho*n*d*log T)=O(n*b/d^2)` with `b=log n`, which is linear or smaller
when `d=Theta(b^epsilon)` and `epsilon>1/2`. `Q` is already inside `n=TQ`
and must not be multiplied into that volume a second time.

## Independent fixed-integer controls

`../code/fixed_grid_band_lu.py` stores every factor, reciprocal and returned
component as an integer on one common grid. The original matrix-factor and
matrix-solution residuals are computed with exact integers. Four generic
signed near-identity band systems of dimensions 32, 48, 64 and 96 and
half-bandwidths 2, 4, 6 and 8 passed 48 independent basis/arbitrary-grid
right-hand sides at 24, 40, 64 and 96 fractional bits. Deliberately lowering
precision to three bits failed the residual target in every case.

These controls exercise the changed precision implementation; the general
lemma is the written backward-error argument. Cyclic-to-local approximation,
actual Gaussian exponent rounding and sparse volume remain explicit external
interfaces, not facts implied by a PASS label.

The separate `../code/gaussian_band_lu_controls.py` probes the same fixed-grid
algorithm against independently evaluated physical Gaussian matrices at 200
decimal digits. Three principal windows, including a lifted physical-period
crossing and exact phase-edge starts, passed 36 basis/arbitrary-grid inputs at
64-, 192- and 256-bit target accuracy. Gaussian coefficient truncation,
rounding and retained cyclic-image perturbations are included in the actual
original-matrix residual. Omitted images have an explicit exponentially small
row bound. A diagonal-only negative control fails in every case.
The complete result is retained under
`../runs/20261008T1344Z-gaussian-band-lu/results/certificate.json`.

The campaign scout independently criticized the Schur preservation, local
backward-error embedding, reciprocal replacement and triangular residual
argument and reported no blocking flaw. This is internal mathematical review,
not external human peer review or formal verification.

Reproduce the generic exact controls and Gaussian numerical controls from the
repository root:

```sh
python3 -B research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/inverse/code/fixed_grid_band_lu.py \
  --output /tmp/fixed-grid-band-lu.json
python3 -B research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/inverse/code/gaussian_band_lu_controls.py \
  --output /tmp/gaussian-band-lu.json
```
