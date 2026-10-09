# Independent review of compact actual-frame interfaces

The nine retained actual-frame interfaces in
[scalable-subspace-normal-forms.json](../../fixtures/complex/scalable-subspace-normal-forms.json)
are independently accepted as exact Gaussian operators. The review binds
all 166 conjugated X/Z generators, all 1,088 small matrix coefficients and
the actual global scalar in four dimension-16 cases. The large scalar checks
use independently constructed literal tensor blocks of at most three bits;
they do not reuse the producer's quadratic path-sum implementation. This is
finite algebraic and analytical review, not an independently implemented
all-size compiler, native routing proof or exponent certificate.

The fixture SHA256 is
`77fb258dcf779ae58e07a3839564114dd846694d0f49353dc3ec4439bc27cd42`.
It was generated from compiler
`cc8542fd0d177b33a8092285b18588ac4437432b3fc22ca3d95e1f6dab329afa`
and canonical source
`ddb0255a0668d43dd61c5183f3a0de56015f02b6acc462c4b8ad5b3f8173598b`.
The producer subsequently adds an after-run source-freeze assertion; its
retained recovery patch reconstructs the exact fixture-generating version.
The producer's full controls and all-size derivation are in
[scalable-actual-frame-interfaces.md](../complex/scalable-actual-frame-interfaces.md).
This reviewer does not claim to have independently rerun those full controls.

## Independent construction

[scalable_frame_review.py](../../code/transfers/scalable_frame_review.py)
imports only previously reviewed independent rational Gaussian arithmetic.
It reconstructs each canonical source and target word from its actual
specification, reverses the source literally, and checks that their concatenation
matches the fixture's relative word. It independently reconstructs the returned
affine routes, quadratic phases and selected-bit C child. Route inverses are
checked by binary elimination; every remaining coordinate is a complete
spectator.

For the convention `i^p X^x Z^z`, the reviewer implements the elementary
conjugations directly. A forward line C with label t changes an anticommuting
Pauli to `i^(p-1) X^(x+t) Z^z`; its inverse uses `p+1`. Literal SCS has the
Hadamard conjugation, including the sign from exchanging X and Z. Binary
routes act by A on X and `A^-transpose` on Z. For a quadratic diagonal q,
the phase change is `q(x)-q(0)` and the sign derivative is determined by
`q(x+e_j)-q(e_j)-q(x)+q(0)` modulo four. An output XOR retains its Pauli
sign. These rules bind all 2n Pauli generators for every fixture.

Both words are unitary. If two unitaries have identical conjugated X/Z
generators, their quotient commutes with all Z and is diagonal; commuting
with all X coordinate flips then forces that diagonal to be constant. A
single nonzero physical coefficient therefore fixes the complete scalar.
Checking generators alone would miss a global unit, so it is not the sole
acceptance test.

The fixture's dimension-16 subspaces split into independent blocks of at
most three physical bits. The reviewer constructs their actual local
Gaussian matrices by literal C and SCS gates and multiplies the selected
physical coefficient across blocks. The source and target routing columns
are explicitly checked to stay within these physical blocks. This derives
the complete dimension-16 coefficient independently of any general Gauss
sum evaluator. In particular a generic frame's rank-zero local spectators
equal `D^-2=Z`; applying the global identity override separately to those
spectators would be wrong. The reviewer retains those phases.

For dimensions three and four, every physical matrix coefficient is also
compared directly. For dimension 16, complete Pauli images plus the separately
computed nonzero scalar bind the whole operator algebraically, without
materializing an address matrix. The scope relies on the explicit block
structure of these four large fixtures; it is not an independent general
path-sum compiler for arbitrary large subspaces.

Every fixture rejects a corrupted input global fourth-root constant by its
actual coefficient, and rejects a corrupted output XOR by at least one
complete Pauli image. The quadratic constants are applied once per packed
column, so f repeated columns produce the fth power of a column-constant
phase. No phase is discarded through abstract frame identification.

## Analytical normal-form scope

The stated Grassmann width is correct for the canonical subspaces
`L_E=(Eperp,0)+(E,E)`. In their intersection, x lies in `E intersect F` and
the residual z+x lies in `(E+F)perp`. Hence

```text
dim(L_E intersect L_F)
  = n-dim(E)-dim(F)+2dim(E intersect F).
```

The mixing rank of the actual relative Clifford is the codimension of this
intersection. It equals
`dim(E)+dim(F)-2dim(E intersect F)`, including degenerate and nonnested
subspaces. The independent source verifies that rank for every fixture by
separate binary elimination. This accepts the algebraic width, not a free
address permutation or a native recurrence.

There is also an independent ring argument for the fourth-root normalization.
Every literal canonical coefficient lies in `Z[i,1/2]`. A Clifford block
of rank r has uniform coefficient norm squared `2^-r`; dividing a nonzero
coefficient by `alpha^r`, with `alpha=(1+i)/2`, leaves an element of
`Z[i,1/2]` of norm one. Write it as `(a+ib)/2^P` for integers a,b. The
identity `a^2+b^2=2^(2P)` forces both a,b even when P>0, because squares
modulo four are zero or one. Repeated descent leaves only
`(a,b)=(1,0),(-1,0),(0,1),(0,-1)`. The unit is therefore exactly one of
`1,-1,i,-i`. This accepts the normalization without granting an unpaid
square-root or eighth-root scalar.

The two Gauss-elimination identities stated by the producer are also valid:
for odd a, summing `i^(a*x+2*x*L)` gives
`(1+i^a)*i^(-a*L)`; the even coupled-pair sum gives
`2*(-1)^((a+L)*(b+M))`. Binary affine substitution must retain the modulo-four
quadratic corrections of parity expressions. The producer's proof explains
that requirement. The present literal-block review fixes the selected large
global phases independently; it does not exhaustively reimplement every
Gauss-elimination branch.

## Native and recursive boundaries

An exact one-child normal form specifies a monomial/quadratic wrapper and
a C oracle. It does not implement those wrappers on a fixed tape set or
prove their complete payload cost. Arbitrary binary routes, affine flips,
address chirps, source/sink ordering, guard buffers, copied streams and
every inverse must be included in a later native ledger.

The general Grassmann rank can equal n. In a one-axis master this could be
a same-width recursive child. Calling it a single child does not itself
establish termination; a separate decreasing row/depth budget and complete
stock contract would be needed. In a wider tensor master the same algebraic
rank may instead be strictly below the ambient width. The selected width r
with f packed columns also differs from its physical `r*f` tensor factors.
These cases cannot inherit the campaign's old controller merely from a
matching rank label.

The compiler and these checks improve the mathematical interface portfolio.
They do not close canonical signed-swap chronology, precision, all-size row
allocation, paid native routing or a multiplication exponent.

## Reproduction

From the new worktree:

```sh
python3 research/integer-mult-breakthrough/code/transfers/scalable_frame_review.py --workers 4
```

Bounded CI uses the same complete nine-fixture check with `--workers 1`.
The runtime closure is this source, its
[config](../../configs/transfers/scalable-frame-review.json), the retained A
fixture and independent `conditioned_frame_review.py`. No producer imports,
downloaded checkout, random seed or third-party package is needed.

The actual-time four-worker
[run](../../runs/20261009T022651Z-transfer-scalable-frame-review/report.md)
passes in 0.0628 seconds. Protocol and compact summary retain exact closure
hashes. The finite literal checks and the analytical deductions above are
distinguished from the producer's broader completed controls and from an
unproved native transfer.
