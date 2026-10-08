# Rational-beta actual positive-frame profiles

This extends the credited `I+tJ` basis family to arbitrary rational beta with `L=I-beta J`. It changes the common basis used by every actual positive frame, rather than assigning independent bases to calls. The scalar producer, source triples, nested spaces, paid banks and compiler chronology stay explicit in each witness. A changed source-weight family requires its own complete data certificate.

Let `H=I-J/9`, `f=|F|` in `{1,2}`, `s=3-f`. The disjoint signed class vectors are `a_c`, with squared norm `k_c` and sum `sigma_c`. Actual basis columns are `s a_c+sigma_c 1_F`; their Gram matrix is `s² diag(k_c)+(f-1)sigma sigma^T`. Set

`D=sum a_c a_c^T/k_c`, `u=sum sigma_c a_c/k_c`, `v=sum sigma_c²/k_c`, `d=s²+(f-1)v`.

Sherman–Morrison followed by the single common conjugation gives

`P = D + [s u z^T+s w u^T+v w z^T-(f-1)u u^T]/d`,

where `w=1_F-3 beta 1` and `z=1_F+gamma 1`, with `gamma=(9 beta-1)/(3(1-h beta))`. The rank-one source projector is `(1_T-3 beta 1)(1_T+gamma 1)^T/2`; its intrinsic `H` norm is two. The Gram projectors are nondegenerate: these frames lie in common-point hyperplanes, where the `H` quadratic form is positive. The surrounding space and the new common basis need not be positive definite.

Write reduced `3 beta=wN/wD`, `gamma=gN/gD` with positive denominators; let `K=lcm(k_c)`, `U=K u`, `V=K v`, `dnum=K d`. An integer denominator is `wD*gD*K*dnum`. The correction numerator is

`s*wD*K*U_i*zN_j+s*gD*K*wN_i*U_j+K*V*wN_i*zN_j-wD*gD*(f-1)*U_i*U_j`,

where the local coordinate numerators are `wN_i=wD*1_F[i]-wN` and `zN_j=gD*1_F[j]+gN`. Add the diagonal-class numerator for `D`, then reduce the common gcd. Source denominators are `2*wD*gD`. The native generic implementation uses arbitrary-precision integers throughout this formula, the denominator lcm, and the minor bound.

The independent literal positive-frame compiler supplies actual inclusion and ranks. For nested nondegenerate spaces `A⊆B`, the two projectors commute with product `P_A`; hence `P_B-P_A` is an idempotent of rank `dim B-dim A`. This supplies the a priori upper bound for every NE corner. If `Z` bounds the cleared integer entries and the residual rank is `r`, every possible nonzero minor has size at most `r` and is bounded by `r^ceil(r/2)*Z^r`. Distinct prime product strictly exceeding that bound makes the maximum modular NE rank exact over Q. Mixed differences of these ranks give the actual rook pivots and contiguous recursive widths. Merely taking a union of modular pivot lists is invalid. Chosen primes must avoid the actual frame denominators; the present finite parameter runs assert this condition.

For a copied center, a normalized primal and dual pair is

`p_i=e_i+[(2-3 beta(h-3))/(h-9)]1`,

`nu_i=[(h-9)(1-3 beta)/(12(1-h beta))]1-[(h-9)/4]e_i`.

Every source and center coordinate is nonzero when beta avoids `0`, `1/h`, `1/3`, `1/9`, `2/[3(h-3)]`, `(h-7)/[3(h-3)]`, and `2/[3(h-1)]`. [The direct rational check](results/parameter-source-center-review.json) derives these pairs from `H`, `H^-1`, `L` and `L^-1`, without importing the native formula. Normalization products equal one.

The conjugate parameter `beta*=-gamma/3` exchanges `w` and `z`, so every actual projector is transposed and each source coordinate product is identical. The complete source-pair data certificate therefore transfers to the conjugate family. Ordered local NE ranks must still be freshly computed. [Independent direct Gram controls](results/parameter-gram-20261008T1632.json) check twelve selected physical transitions for each h25 parameter `1/57` and `1/6`, including exact denominators, minor bounds and rational pivot lists.

Variable-cardinality continuation matching uses local profile benefits plus the exterior charge `Phi(h)+Phi(575-2h)` for each saved bank role. Discovery field costs and floating min-cost-flow choices do not establish a global optimum. Accepted selected maps receive complete rational CRT profiles, literal compiler checks, and source-only recovery. Full recurrence moments, precision, tapes, Gaussian inverses, stock and strict eventual absorption belong to the coordinator's separate assembly.
