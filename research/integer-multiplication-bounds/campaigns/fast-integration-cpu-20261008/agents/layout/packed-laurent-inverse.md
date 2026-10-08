# Genuine packed Laurent inverse and global cyclic reference

## Scope and source

The numerical discriminator now computes a real signed Kronecker tensor
inverse cell, instead of comparing two inverses of the same retained local
matrix. Its independent reference solves the complete physical cyclic
Gaussian `N`, including the cyclic border and an analytic tail for every
omitted lifted alias. The reference API and infinite-Neumann kernel API are
authored by the inverse agent and pinned in every receipt.

This stage applies bare `N^-1`. The source compression's `J'=N^-1/2` and
`D'` are separate factors. A one-cell validation does not assert the joint
fixed-tape gathering, sparse exception repair or all-size theorem.

## Actual computation

For a centered regular interval with `q(j*+i)=q(j*)+i`, define

`beta*=t*j*/s-q(j*)`, `rho=t/s`, `theta=rho-1`,
`W_i=exp(pi*u*theta*i^2)` and
`M_h=exp(-pi*u*(rho*h^2+2*beta* h))`.

The physical local identity is `N=W M W^-1`. The kernel API generates a
finite infinite-Laurent Neumann series, retaining all intermediate support
before cropping. It separately charges the omitted original Gaussian band,
Neumann remainder and Laurent inverse tail. If `b_h` acts from input column
`i+h`, the polynomial convolution uses `b_-h`.

The checker builds every input record of a two-dimensional retained cell,
applies the contracting `W^-1`, forms the tensor kernel with a rounding after
each setup prefix, and executes four exact signed integer products. Its mixed
radix is `B=input_side+2R`, so the sum of input and kernel coordinate degrees
is strictly below `B`; polynomial carries do not cross tensor coordinates.
Each output receives its expanding `W` factor.

The earliest controls apply the outer diagonals with high-precision numerical
arithmetic after the exact packed products. Current source instead freezes
P-bit diagonal words and applies input/output factors using integer dyadic
products. Their distinct source versions are recoverable by the retained
patches; the numerical kernel accuracy and fixed-tape theorem remain separate.

The complete input is the sum of two separable signed tensors. Four global
one-dimensional inverse solves independently give its full cyclic tensor
reference. That separability only reduces reference work; the packed producer
still creates and multiplies the entire tensor cell. Every output in the core
is checked, with higher-precision global residual and alias certificates
retained alongside the comparison.

The reserve uses the maximum retained input distance, including both halos,
and sums over both axes. It is not the output-core-only reserve. Independent
source review also caught the slight operator norm above one for bare Laurent
inverse factors. The tensor tail now includes the product of conservative
exact/approximate inverse row norms. Earlier immutable raw receipts preserve
the original bound; derived receipts explicitly record this correction. It
does not change any numerical output or positive conclusion.

## Completed controls

| Source / target | Core | Radius | Target bits | Full retained reserve | Maximum global comparison error |
| --- | --- | --- | --- | --- | --- |
| `(4093,4091)` / `4096^2`, seed202610103101 | `64^2` | 28 | 256 | 128 | `4.700e-126` |
| `(8189,8191)` / `8192^2`, internal anchors2730/1023 | `96^2` | 42 | 384 | 72 | `3.723e-161` |
| `(4093,4091)` / `4096^2`, seed202610103103 | `64^2` | 8 | 256 | 57 | `2.923e-48`, fails |
| Same matched source/input | `64^2` | 28 | 256 | 128 | `6.192e-126`, passes |

The radius-negative and positive use the same independently generated input.
The negative is retained rather than masked by a successful local matrix
solve. Omitting the output chirp also produces a large discrepancy in every
row. A first automatic anchor `round(s/(t-s))` equals the source period when
`t-s=1`; that unwrapped retained cell touches the period cut. The checker now
rejects it explicitly and the repaired fixture uses an internal anchor.
This correction does not assume covariance across an untreated cyclic cut.

The first positive takes 10.92 seconds; the internal-anchor positive takes
36.93 seconds; the matched radius-negative/positive take 7.80/10.74 seconds.
These are numerical execution costs, not tape complexity bounds.

Changed source65,521/65,519 at target65,536 also completes full `128^2`
packed cores at target512 and768 bits, with radii40/58. Their globally
compared errors and all source/kernel hashes are retained in
`results/packed-laurent-large-period-precision.json`; the two cases take
219.69 and323.87 seconds. Their tensor norm correction is explicit in the
derived receipt. Higher-precision cells with completely dyadic outer factors
continue independently.

## Global cyclic reference family

Eight full global reference cases span source periods 4,093 to 262,139,
target precisions256--768 bits and alpha2--4. Every case passes the separately
recomputed high-precision residual plus analytic all-alias tail. Seven
near-equal-period cases are outside the campaign's `u*theta>=1` condition;
their measured conservative row gap, not the all-size near-identity constants,
supports the numerical comparison. The eighth case, source65,521/target131,072
at alpha2, is inside that condition. All flags are explicit in the receipts.

Four additional global references at `(4093,8192)`, `(32749,65536)`,
`(65521,131072)` with alpha1 and `(131071,262144)` with alpha2 all satisfy
`u*theta>=1`. All higher-precision residual and all-alias checks pass in
300.41 seconds total. Their retained receipt is
`results/cyclic-inverse-strict-theta-reference-family.json`.

The bordered cyclic reference factors an ordinary banded interior and solves
a small cyclic Schur complement. It avoids a cubic global dense inverse.
Its coefficients and residuals use ordinary arbitrary precision, not directed
interval arithmetic. The local kernel analytic tail alone does not prove
replacement of the global phase-boundary operator; the independent global
numerical comparison tests that interface for these configurations.

Source, exact configurations and receipts are indexed by
`code/check_packed_laurent_inverse.py`, `configs/packed-laurent-*.json`,
`results/packed-laurent-*.json` and `results/cyclic-inverse-*.json`.
Reproduction commands are in [the pipeline guide](reproduce-gaussian-pipeline.md).
