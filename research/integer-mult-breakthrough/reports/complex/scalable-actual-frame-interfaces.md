# Compact actual-frame compiler with one Grassmann-width child

The new [compiler](../../code/complex/scalable_subspace_interfaces.py) produces
an actual Gaussian-dyadic interface `F_F * F_E^-1` without enumerating its
address matrix. It returns affine binary address routes, two fourth-root
quadratic phases and exactly one selected-coordinate `C^tensor(rank)` block.
The rank is the Grassmann distance

```text
rank = dim(E) + dim(F) - 2 dim(E intersect F).
```

Increasing or decreasing nested pairs therefore pay the absolute dimension
difference. Nonnested pairs pay their larger distance. The compiler never
identifies different actual phase gauges at a scalar mixer. It uses the
previously defined canonical `F_E` representatives, including identity,
odd-line `C_T`, full `C_h`, odd-kernel `C_h*C_T^-1` and degenerate generic
subspaces. The canonical source is pinned by SHA256
`ddb0255a0668d43dd61c5183f3a0de56015f02b6acc462c4b8ad5b3f8173598b`.

This closes an algebraic compiler requirement left open by the finite
[canonical-frame controls](canonical-subspace-actual-frames.md). It does not
close native tape routing, a complete stock ledger, a canonical signed-swap
chronology, or the multiplication exponent.

## Literal normal form and interface

`compile_interface(E,F,n)` accepts arbitrary binary subspaces, supplied as
integer bitmasks. Its returned routes and quadratics describe the temporal
word

```text
input route inverse
input fourth-root quadratic
one C child on the selected rank coordinates
output fourth-root quadratic
output linear route
output XOR offset
```

All remaining coordinates are spectators of the child. There are no input
or output arrays of length `2^n`. Quadratics have a constant, n linear
coefficients modulo four and square-free cross coefficients equal to two.
Their constants, the final affine offset and all routing columns are retained.
For f packed columns the selected recurrence width is rank, with f columns;
the literal tensor has rank times f two-by-two factors. A column-constant
phase must be applied in every column, producing its f-th power.

`compiled_word(normal)` expands this specification into elementary monomial
wrappers and selected-bit `C` factors for algebraic verification. This is a
word of exact address operators, not a unit-cost claim about payload movement.

## Algebraic derivation

Use the Pauli convention `i^p X^x Z^z`. Products obey

```text
(x,z,p) * (X,Z,P) = (x XOR X, z XOR Z, p+P+2 dot(z,X) mod 4).
```

The literal canonical word is expanded into `D=diag(i^weight)`, invertible
binary routes, dyadic Hadamard factors and forward or inverse line `C` factors.
Conjugating the 2n Pauli generators uses binary linear algebra and exact
phase exponents. The input-zero column is fixed by the n conjugated Z
generators. Their X-label span S has dimension rank. Combinations with zero
X-label impose even-character equations on an offset o; their nullspace is
S. Thus the column support is exactly `o+S`.

For a stabilizer `i^p X^s Z^z`, its eigenvalue-one condition gives

```text
psi(o+s) / psi(o) = i^(p+2 dot(z,o)).
```

Chosen stabilizers lifting a basis of S therefore determine all relative
column phases. Conjugated X generators determine every other input column:
if `U X^y U^-1 = i^p X^s Z^z`, then

```text
U[x,y] = i^(p+2 dot(z,x XOR s)) * U[x XOR s,0].
```

The input directions that leave the output support coset unchanged form a
rank-dimensional kernel. Choose a basis for this kernel and a spectator
complement. The mixed second phase differences between active output and
input directions are binary and nonsingular: a null active direction would
make two distinct columns proportional, contradicting unitarity. Invert that
coupling to match the standard `C` bilinear term. Output spectator columns are
the corresponding conjugated input translations. The two remaining phase
functions are Z4 quadratics, so their values at zero, basis vectors and pairs
give complete compact coefficients.

The chosen canonical Lagrangians are
`L_E=(E^perp,0)+(E,E)`. Their intersection has dimension
`n-dim(E)-dim(F)+2dim(E intersect F)`. For the actual relative Clifford,
the computational mixing rank is the codimension of this intersection.
This proves the paid Grassmann width independently of a matrix scan.

## Actual global phase

Pauli images alone leave a global scalar undetermined. The compiler separately
evaluates the physical coefficient `(output=o,input=0)` from the literal word.
Every dyadic Hadamard or `C` factor introduces one binary path variable and
an `alpha=(1+i)/2` factor. Address bits remain linear path expressions; the
phase is a Z4 quadratic. Fixing the output gives an affine linear system.
Substitution into the phase reduces the coefficient to an exact quadratic
Gauss sum on O(n) variables.

The eliminator uses two elementary identities. For odd a, summing a variable
with phase `a*x+2*x*L` produces `(1+i^a)*i^(-a*L)`. When all linear
coefficients are even, a coupled pair with phase
`2*x*y+2*x*(a+L)+2*y*(b+M)` produces
`2*(-1)^((a+L)*(b+M))`. Remaining uncoupled even characters either cancel
or contribute a power of two. Every step is exact integer Gaussian
arithmetic; there is no floating-point phase choice.

The resulting coefficient is compared exactly with
`alpha^rank*i^p`, for all four possible p. The matching p is retained.
This handles alternating forms, radical characters and affine offsets.
The coefficient is Gaussian dyadic and has modulus `2^(-rank/2)`.
After clearing its power-of-two denominator, its two integer components
have square sum a power of two. Repeated division by two leaves either
an axis pair of norm one or a signed balanced pair of norm two. Hence the
coefficient lies in the fourth-root orbit of `alpha^rank`; an unpaid
eighth-root normalization is unnecessary.

Binary elimination, phase fitting and quadratic substitution use polynomial
metadata work in n. The implementation uses O(n^4) loops over bitmask or
integer operations in its current straightforward form; no claim of an
optimal metadata exponent is needed. Gaussian integer bit lengths remain
O(n). The output description has O(n^2) coefficients.

## Verification and limitations

The first two attempts tested all 579 increasing nested pairs in dimensions
3 and 4, with 135,552 full matrix coefficients, plus exact quadratic sums
and seeded dimensions 16,32,64. The second attempt checked all 2n Pauli
generator images of each larger compiled word and its exact global
coefficient. Those completed originals remain separate attempts. The final
attempt extends the compiler and checks to arbitrary ordered subspace pairs;
its [run receipt](../../runs/20261009T021521Z-complex-grassmann-interface-full/report.md)
supplies the definitive counts: all256 ordered pairs among the16 dimension-3
subspaces and all4,489 ordered pairs among the67 dimension-4 subspaces.
All1,165,568 matrix entries pass. Eighteen seeded dimension16,32,64 interfaces
pass all1,344 conjugated Pauli generator images and their exact global
coefficient; each has40 additional phase-relation checks. The four-worker
attempt completed in129.624 seconds. It includes increasing, decreasing and
nonnested pairs, with rank15/31/63 nonnested controls in the larger spaces.

The final [bounded CI run](../../runs/20261009T022022Z-complex-scalable-interface-ci/report.md)
passes all256 dimension-3 pairs and64 exact randomly selected quadratic sums
in0.246 seconds using one worker. Both compiler and imported canonical
source are checked unchanged before and after execution. The full attempt's
post-run freeze receipt separately checks both source hashes against its
protocol before the later CLI-only freeze assertion was added.

The [compact literal fixture](../../fixtures/complex/scalable-subspace-normal-forms.json)
contains nine interfaces in dimensions3,4,16. It includes actual canonical
specifications and relative words, along with complete routes, quadratics
and units. Its producer source is recoverable at exactly its original hash;
[this generator](../../code/complex/make_scalable_interface_fixture.py)
regenerates the mathematical cases without importing a native implementation.

Every earlier source remains recoverable exactly through the three patches
listed in the [recovery config](../../configs/complex/scalable-interface-recovery.json).
Each patch was applied in an isolated directory and the resulting bytes
matched the immutable run snapshot. The earliest protocol/certificate,
later complete-generator extension and final all-pair receipts were never
overwritten. The fixture used the all-pair source before the final
imported-source end assertion, with identical scientific compiler code.

For unitary words, equality of every conjugated X/Z generator implies equality
up to scalar: their quotient commutes with the full Pauli algebra. A single
nonzero coefficient fixes that scalar. Consequently the large-dimensional
controls compare complete operators algebraically, without claiming a full
address-matrix enumeration. Random coefficient relations are additional
stress controls, not the reason for that complete algebraic comparison.

Negative controls corrupt the global fourth-root constant and the final XOR
offset. Each changes the actual physical operator and is rejected. Exact
quadratic Gauss sums are also compared against exhaustive small sums.

All wrappers preserve the dyadic grid and component magnitude, apart from
the paid child's own precision/magnitude charge. Their execution time is
not free. In particular an arbitrary binary route need not fit a
predecessor-only XOR router. The native proof must retain complete payloads,
the bank and coordinate ordering, affine flips, quadratic address controls,
guard buffers and every stream pass. Neither efficient classical metadata
compilation nor a Clifford word by itself proves that fixed-tape bound.

The underlying linear/quadratic stabilizer representation is established
background, not a new general Clifford theorem. See Jeroen Dehaene and Bart
De Moor, [The Clifford group, stabilizer states, and linear and quadratic
operations over GF(2)](https://arxiv.org/abs/quant-ph/0304125), arXiv
quant-ph/0304125v1, 18 April 2003; Phys. Rev. A68,042318,20 October 2003,
DOI10.1103/PhysRevA.68.042318. The exact Gaussian-dyadic normalization,
pinned canonical endpoints and executable one-child compiler above were
derived and checked in this campaign with OpenAI Codex assistance.

Reproduce the bounded finite controls with standard Python:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/scalable_subspace_interfaces.py --workers 1 --bounded
```

For discovery, omit `--bounded`, use four workers and an optional fresh
`--output` directory. Independent literal review of the compact fixtures
is requested before using this compiler to support a larger native claim.
