# Independent source review of the sequential Boolean Jordan basis bill

This receipt records analytical and source-only review of the coordinator's
classical linear BTK basis implementation. Its producer was not imported,
executed or rerun. Its measured n1..6 columns are producer evidence, not
measurements by this reviewer. The source/report identities are pinned in the
accompanying protocol. The literature attribution belongs to the coordinator's
primary-source record; this receipt does not claim discovery of the basis.

At dimension j, the basis has C(j,floor(j/2)) chains whose total lengths sum
to 2^j. Extending a chain of length ell creates ell-1 interior two-input
blocks. Each displayed block mixes the old base and shifted coordinates
with two additions and separately retained scalar multiplications. Therefore
there are 2^j-C(j,floor(j/2)) interior blocks. Two recursive copies of the old
basis give the exact optimistic addition recurrence

```
T(0)=0,
T(n)=2 T(n-1)+2(2^(n-1)-C(n-1,floor((n-1)/2))).
```

Dividing by 2^n telescopes exactly:

```
T(n)/2^n = sum_{j=0}^{n-1}(1-C(j,floor(j/2))/2^j).
```

Central binomial probabilities are Theta(1/sqrt(j+1)), so their sum is
Theta(sqrt(n)); thus this sequential realization costs
T(n)=2^n(n-Theta(sqrt(n))). Both basis directions alone have Theta(n2^n)
optimistic additions. Scalars, address permutations and chain work only
increase its bill. This does not accelerate direct zeta in this realization.
It does not exclude a balanced coupling algorithm or a different basis.

The interior 2x2 matrix has columns (1,a) and (-1,b), with a+b=ell, hence
determinant ell. Its inverse exposes odd division once ell=3. The program's
actual inverse is the orthogonal column transpose divided by its squared
norm, and checks every complete column pair rather than presuming a free
normalization. The upward-chain and exp(U) identities bind the intended
conjugated zeta operator exactly. Any later rational-to-dyadic approximation
or finite-ring good-prime route must pay its own coefficients, denominator
exclusions, guards and precision; none is supplied by the current code.

The source's addition ledger matches the stated recurrence, and its omitted
normalization/corrupted-chain negatives discriminate the identified domains.
Acceptance here is an analytical/source review, not formal verification,
independent finite replay, a native tape supplier or an exponent result.
