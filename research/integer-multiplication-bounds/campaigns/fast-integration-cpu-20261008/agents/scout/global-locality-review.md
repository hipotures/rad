# Independent criticism of physical Gaussian inverse locality

Reviewed the inverse agent's `reports/global-gaussian-locality.md` at the 13:20 UTC checkpoint. The lifted-kernel, phase cancellation, tail and principal-window arguments are supported under the stated Gaussian interface. This is mathematical criticism, not a rerun of its large finite checks or a formal proof assistant result.

## Attribution boundary

Selectively read `reports/downstream-weighted-gaussian.md` from completed RaD commit `6b32837aee0561af85e4efaca21af07b9f2749d2`. It already proves the exact Gaussian conjugation `W^-1 E W`, explicitly retains nonzero period-multiple aliases, and bounds powers by a diagonal condition number. It does not state the spatially weighted inverse-kernel or principal-window tail estimates reviewed here. The new statement must credit that identity and does not establish worldwide novelty of inverse decay.

## Checks of the changed argument

Let `W_j=exp(pi*u*beta_j^2/theta)` and `rho=1+theta`. With a signed integer displacement h and wrap count `w=beta_j+theta*h-beta_(j+h)`, the exponent after conjugation is exactly

`rho*h^2 + (rho/theta)*w*(2*(beta_j+theta*h)-w)`.

Centered rounding makes the second term nonnegative for both signs of w. Hence every lifted `F_(j,h)` is bounded by `exp(-pi*u*rho*h^2)`. The weighted row norm on periodic-coefficient kernels is submultiplicative by the triangle inequality for displacements; it does not require translation invariance.

With `a=pi*u*rho-ln4`, its norm is below `2/3`, so the inverse Neumann series has weighted row norm below three. Absolute convergence permits periodic folding and matrix composition to commute. Periodicity of W is essential and is satisfied. Aliases on the diagonal remain included.

For `0<=v=theta*|h|<=1`, the centered phase-square difference is at most `v*(1-v)`. For positive h, the no-wrap and one-wrap expressions are respectively `-2*beta_j*v-v^2` and `(1-v)*(2*beta_j+v-1)`. The reverse expressions give the same upper bound for negative h. Combining this phase gain with the lifted inverse decay yields the physical Gaussian bound. At larger displacements, the global gain `1/4` and linear lifted decay suffice. The proposed constants 24 and 32 for row tails and local error are conservative geometric-series bounds when `u*theta>=1` and `R<=1/(2theta)`.

Projecting onto a physical subset I and all its periodic images preserves the weighted bound, because it removes permitted paths. The principal inverse has norm below three and its product with the cross-boundary F block has norm below two. Every outside destination of a core row has lifted displacement greater than R when its circular distance is greater than R. Therefore the same unweighting and alias-inclusive tail estimate applies to this boundary product. The resolvent identity has the stated negative sign; multiplying by the inherited `||N^-1||<2` gives the proposed local error.

The regular-phase estimate also checks: within `|h|<=delta/theta`, the stronger phase gain is `(1-2delta)*theta*|h|-(theta*h)^2`. Split the farther tail at `floor(delta/theta)>=delta/(2theta)` to obtain the additional Gaussian remainder. No hidden use of the forward Gaussian window is needed.

## Remaining solver interface

This proves locality of the **actual cyclic principal matrix**. A finite wrap-free Toeplitz block is not exactly that matrix: remote period aliases still contribute tiny entries. A structured local solver must charge their perturbation and bound its own factor/rounding error before applying the locality lemma. Smallness of an alias is not equality to zero. The inverse agent was notified of this requirement.

The result also does not establish a cheap physical gather of all halo boxes, sparse exception access or the full multiplication recurrence. Those remain separate machine and precision obligations. Subject to these stated limits, this is a reusable written locality lemma and supports the regular/exception window analysis.
