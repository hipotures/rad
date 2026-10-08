# Gaussian parity audit: scope and integration conditions

Observed 2026-10-08 14:45 UTC; source reviewed 14:50 UTC.
[CrocSwap PR45](https://github.com/CrocSwap/integer-mult-bounds/pull/45)
by Alejandro Zarzuelo Urdiales, with substantial OpenAI Codex assistance,
uses `alejandrozu/integer-mult-bounds` at
`5e219f7b3513b092d3ee919a303db0f55a3a0a0e`. Ten selected source/provenance
files are pinned read-only in the [input manifest](input-manifest.json),
with exact hashes and GitHub CLI recovery. No Lean compilation or Python
arithmetic suite was executed by the scout.

The author reports 69 Lean theorem declarations, a fresh Lean 4.31.0 kernel
build and complete foundational-axiom audit, plus exact finite controls and
188 destination unit tests. Full integration `make verify` was explicitly
not run. These are source-author receipts; this review does not attribute
a fresh kernel check or external human acceptance to the campaign.

## Independently checked written arithmetic

Put `pi=1+i`, `rho(a+bi)=(a+b) mod2`, and `C=(iI+X)/pi`.
Solving multiplication by pi gives
`(a+bi)/pi=(a+b)/2 + (b-a)i/2`, exact in Z[i] precisely when
rho vanishes. Both C numerators have residue `rho(u)+rho(v)`;
the guard therefore requires one Gaussian parity bit per input, rather
than separate equality of real and imaginary parities. The pair `(1,i)`
passes and maps to `(1+i,0)`.

For an admissible pair, the output parity sums are `a+d` and `b+c`.
Their difference is even under the incoming condition, so that SAME pair's
admissibility is preserved. It cannot be propagated to arbitrary re-pairing:
the initially admissible pairs in `(1,1,1,i)` give outputs `(1,1,1+i,0)`;
the next pair `(1,1+i)` fails. Also `(iI+X)^2=2iX=pi^2 X`, hence C squared
is swap where exactness is preserved. These identities agree with the
pinned theorem statements.

For the completed tensor `C_D=C tensor ... tensor C`, its coefficient
numerators are Gaussian units over `pi^D`. Since
`pi^(2q)=2^q i^q`, the binary enclosure needs exactly `ceil(D/2)` additional
bits. At odd D the converted numerator has equal real/imaginary parity.
An impulse gives a primitive numerator at the claimed grid, proving
sharpness. The final normalized tensor H0 has entries `+/-2^-D`, so its
universal bound is D bits, as its own impulse witnesses. The C-return bound
cannot replace final normalization. These are depth-D tensor statements;
D is not an arbitrary local residual width such as 23 or 25.

## Safe use in this campaign

The local guard and total denominator-tag fallback are useful reference
assertions for semantic child returns. The claimed formal lattice results
concern arbitrary Gaussian numerators, while the explicit tensor coefficient
formula and its connection to a concrete recursive schedule are written
mathematics and finite controls. The whole network is not formalized.

A changed producer, controlled call or arbitrary-matrix transfer must still
establish its own completed-child semantic contract before importing the
tensor return lattice. Unfinished coefficients, dirty scratch and temporary
XOR records require the existing recursive magnitude and guard argument.
Per-pair denominator tags are not automatically a common grid for later
addition; exponent alignment, scans, copied defect bits and normalization
must remain in the physical cost. No source/basis transformation with other
denominator factors is certified merely by this Gaussian lemma.

The original selected finite network, recurrence exponent, paid endpoint
corrections and multiplication saving are unchanged by this audit component.
This is an optional arithmetic oracle and sharper bounded return statement,
not a new exponent-saving mechanism. Full tensor-network execution, tape
costs, analytic hypotheses and the multiplication theorem remain outside
the claimed formal scope.
