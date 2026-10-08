# Sparse cyclic Gaussian reference for local inverse controls

The [reference API](../code/cyclic_gaussian_reference.py) supplies a numerical
global inverse without a cubic dense solve. It is intended to discriminate
genuine packed regular Laurent cores against the complete physical periodic
operator. It does not replace the separately paid all-size free-axis window
schedule or claim its running-time exponent.

For integer source period s, target period t>s and integer alpha, set u=alpha².
The selector is q_j=floor(t*j/s+1/2) and beta_j=t*j/s-q_j. The retained lifted
coefficient from row i to column i+h is

`exp[-pi*u*(q_(i+h)-q_i)*(q_(i+h)-q_i+2*beta_(i+h))]`.

The API retains |h|<=w, folds those positions modulo s, and retains their
cyclic corner entries. Every other lifted coefficient, including all remote
periodic images and diagonal aliases, is omitted with an explicit row bound.
Since |beta_j|<=1/2 and t/s>=1, its exponent is at least |h|(|h|-1). Hence

`tail <= 2 exp[-pi*u*w*(w+1)] / (1-exp[-2*pi*u*(w+1)])`.

This bound concerns all omitted images together. The implementation does not
erase aliases while asserting the matrix was exact.

Partition the first w coordinates as a border. The remaining D block is
ordinary banded: wrap couplings now lead to the border. Factor D once,
compute D^-1C for its w border columns, solve the w×w Schur complement
`A-B*D^-1*C`, and reconstruct every interior solution. This uses O(s*w²)
numerical arithmetic and O(s*w) numerical storage for a reusable reference.
It is separate from fixed-tape acquisition and setup accounting.

The generated retained matrix must have a positive row-dominance gap. The
API conservatively halves its measured gap and subtracts the analytic tail.
Residuals independently regenerate all retained Gaussian coefficients at
32 extra bits, then add `tail*||solution||`. Dividing by the conservative
gap gives its numerical solution-error estimate. These are high-precision
numerical checks with an analytic tail, not directed interval certification.

The proposed finite case `(s,t,alpha,q)=(4093,4096,2,256)` has u*theta<1.
It is explicitly outside the campaign's all-size physical near-I hypothesis.
It can still be useful if the actual generated row gap and residual pass.
The sharper stationary Laurent weight in
[regular-laurent-interface.md](regular-laurent-interface.md) likewise permits
finite regular phases outside that near-I regime while rejecting phase edges.

## Interface and normalization

`CyclicGaussianReference(s,t,alpha,target_bits=256,half_bandwidth=None)`
constructs a reusable factorization. Its `solve(rhs)` accepts one real or
complex vector of length s and returns N^-1 rhs. Its
`residual_certificate(rhs,solution)` reports numerical residual, all-image
tail, row gap and error estimate. Its source map does NOT include the separate
`J'=N^-1/2` or source D' multiplier; callers must retain those factors.

Working precision is q+96+ceil(log2 s), with a conservative default band.
Mpmath1.3.0 is the campaign's pinned pure-Python dependency, recoverable by
`python3 -m pip install --no-deps --target <ignored-work>/deps mpmath==1.3.0`.
Expose that dependency and the API's directory in PYTHONPATH. The layout
branch owns the numerical integration caller and its run provenance.

## Completed independent callers

The layout branch retained eight independent random-vector callers in
[cyclic-inverse-reference-family.json](../../layout/results/cyclic-inverse-reference-family.json)
and
[cyclic-inverse-large-reference-family.json](../../layout/results/cyclic-inverse-large-reference-family.json).
Each passes its higher-precision residual plus the analytic bound on all
omitted lifted coefficients, including periodic aliases. The retained API
SHA256 is `21fa3749711da59b48059406a9db85f56a373405c1c8a51322dc3fe58600ad36`.

| Source / target periods | alpha | Target bits | Reported solution-error upper estimate |
|---|---|---|---|
|4093 /4096 |2 |256 |4.42e-108 |
|8191 /8192 |3 |320 |1.05e-127 |
|16381 /16384 |4 |384 |1.41e-146 |
|32749 /32768 |4 |384 |1.95e-147 |
|65521 /65536 |2 |512 |1.85e-185 |
|131071 /131072 |3 |640 |2.81e-223 |
|262139 /262144 |4 |768 |3.58e-262 |
|65521 /131072 |2 |512 |1.29e-188 |

The first seven near-equal-period cases lie outside u*theta>=1 and remain
labeled as such. The last case satisfies that inequality. The estimates are
below their requested targets; they are numerical residual estimates with
analytic tails, not interval-certified global inverses. They exercise the
retained cyclic-border interface independently of later packed Laurent
controls. Source hashes, seeds, working precision, bandwidths, exact result
strings and timings are in the linked receipts.
