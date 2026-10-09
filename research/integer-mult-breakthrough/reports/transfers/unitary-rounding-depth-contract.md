# Unitary endpoints, fixed-grid rounding and linear-depth precision

Status: **CONDITIONAL NUMERICAL LEMMA WITH EXACT FINITE CONTROLS**.
This is a new approximate-arithmetic interface. It does not replace the
published exact [endpoint-grid lemma](endpoint-aware-guards.md), supply
a faster native transform, or prove the outer integer-recovery hypotheses.
No multiplication exponent is asserted.

## Complete operator contract

Consider a well-founded recursive linear Gaussian word. Every child
decreases an integer width, so active depth is at most L. Each node has
a fixed number s of child calls and at most J norm-growing local scalar,
copy or buffer operations, with operator norm at most a fixed B>=1.
These constants are independent of selected width, column count and
record length. Other local operations may be norm-nonincreasing routes,
unit phases, zero embeddings or projections. All live fields, dirty
banks, copied streams and parked buffers belong to the normed state.

Require every COMPLETED child to be exactly its specified unitary
operator on that complete state; forward and inverse endpoints both
qualify. This condition holds for canonical all-field C endpoints. It
is stronger than a zero-scratch identity, a phase label, a projective
unit or a complete map on only the selected data bank. Address controls
are exact and independent of rounded payload values. Data-dependent
branch changes need a separate stability proof.

At any prefix, completed siblings have norm one. Only the unresolved
local words on the active ancestor stack can amplify. The same reasoning
applies to a suffix from one scalar injection to the final retained
output. Thus a uniform sufficient prefix/tail bound is

```text
Gamma = B^(J*(L+1)).
```

An arbitrary interval between two intermediate instants can meet two
unresolved stacks. The same decomposition gives norm at most Gamma^2.
For a square unitary total endpoint E this also follows from
`P_k P_j^-1=P_k E^-1 T_j`, where P and T are its exact prefix and tail.
With padded dimensions, use the two-stack decomposition directly:
embeddings and projections have norm at most one, rather than an
uncharged inverse of a rectangular prefix.

The endpoint family can be relaxed to a uniform forward/inverse norm
bound A0 independent of width. A fixed number of completed siblings
per ancestor then contributes only `A0^O(sL)`, which is absorbed into
Gamma. In particular, uniformly conditioned similarities
`G_e^-1 U_e G_e` with unitary U_e and `condition(G_e)<=A0` qualify if
their literal local words also meet the B,J contract. This includes
some nonunit boundary families. It does not assert that a particular
such frame has a cheap native compiler.

Signed-zeta and ordinary zeta endpoints have norm growing exponentially
with width and do not automatically meet this contract. Likewise, an
uncombined `(1+i)^f` gauge or width-dependent scaling is not a fixed
bounded local scalar gate. Its compensation and literal prefixes must
be proved before it can be absorbed into B or a completed endpoint.

## Rounding and magnitude bound

Use a common fractional grid q. Suppose every real scalar write differs
from its exact operation by at most `2^-q`; count all such injections,
including scalar temporaries rounded before further use, across N
writes. Copies and address routes must be exact or have their errors
counted. The full final error has the sufficient l2 bound

```text
||error_final||2 <= N*Gamma*2^-q.
```

For desired absolute precision `2^-t`, it suffices to take

```text
q >= t+ceil(log2 N)+ceil(log2 Gamma)+O(1).
```

This is an additive-error proof. No assumption of random error or
cancellation is used. It applies to the actual rounded trajectory,
because the ideal future linear tail transports each injection exactly.

For intermediate magnitude, a prefix bound alone is insufficient.
The interval bound gives

```text
||state_rounded||2
  <= Gamma*||input||2 + N*Gamma^2*2^-q.
```

If the final-error allowance is at most one, the second term is at most
Gamma. For M real/imaginary coordinates of magnitude at most 2^R,
a sufficient integer-part guard is therefore
`R+ceil(log2 M)/2+log2 Gamma+O(1)`. Literal local arithmetic numerators
and unreduced temporary grids need their additional fixed allowances.
This is a bound on every live coordinate, rather than only final data.

No polynomial node-count premise is required. With fixed branching and
depth L<=d, at most `(d+1)*max(1,s)^d` nodes occur. If each node has at most M_max
scalar coordinates and polynomial local work, then

```text
log N = O(log M_max+d+log p+log d).
```

The complete maximum live volume M_max, parking, padding and field count
are separate layout obligations. This loose injection count does not
claim a fast time bound. When `log M_max=O(p)`, `d=O(p)` and t=O(p),
the common precision and signed guards remain O(p). That permits a
constant-factor coefficient-width enlargement in principle. It does
not prove that an existing exact record layout has that spare capacity
or preserves the same physical volume without rebinding.

## Zero padding and conditional exact integer recovery

If an ideal completed endpoint returns a padded row to zero, its rounded
row may be nonzero. The final projection deleting that row has norm one;
its discarded residue is covered by the full error bound. Subsequent
error analysis uses the projected approximate state. The row cannot be
silently declared EXACT zero, and a correlated intermediate field may
not be erased merely because its input or eventual ideal output is zero.
The literal control below distinguishes these cases.

The numerical lemma alone does not recover an integer. One sufficient
outer contract can be stated explicitly. Suppose two approximate
polynomial operand arrays each have coefficient error at most eta<=1,
their ideal complex coefficients have magnitude at most M0>=1, and
each product has r negacyclic coefficients. The complete product error
per coefficient is at most

```text
r*(2*M0*eta+eta^2) <= 3*r*M0*eta.
```

An exact signed integer product of the approximate dyadic operands has
grid 2q; any rounding afterward must be counted. If the final linear
decoder has row-sum norm at most L_out and an exact clearing scale S,
then sufficient input precision satisfies

```text
eta <= 1/(32*|S|*L_out*r*M0),
```

with the combined propagated final error from all remaining operations
at most 1/16. The decoded
coefficient error is then below 1/4. If the exact ideal coefficients
are PROVED integers, exact nearest-integer recovery followed by exact
carry arithmetic returns them. Each of S,L_out,r,M0, the complete
operand lengths and the final integer property must be derived from
the actual assembly; they are not supplied by this note.

If their logarithms are O(p), this conditional recovery needs t=O(p),
and the numerical precision remains O(p). Modular centering, CRT
residue separation, resampling, rounding ties, prime hypotheses and
whole residual recovery can require further bounds. This report does
not assume them or change their campaign evidence status. It supplies
a sufficient sensitivity template, rather than an existing integer
multiplication theorem.

## Literal decreasing-depth experiment

The [standard-library source](../../code/transfers/unitary_rounding_depth.py)
uses two complete Gaussian banks. At each node it applies two fixed
bank shears of coefficient 1/2, calls its decreasing child word,
executes a selected elementary C and undoes those bank shears. The
canonical family has one child and exact endpoint C_e on BOTH banks.

A second family adds a controlled address permutation and the inverse
child before the final elementary C. Its exact endpoint is a separately
specified unitary nonlinear conjugate. The fixed bank shears commute
with the same completed address operator on both banks; every complete
node endpoint is unitary by induction. This family tests a broader
endpoint contract and is not relabeled canonical C.

Each local shear and its inverse has norm below two. Routes and selected
C gates are unitary. At most four shears per depth remain unresolved,
so the source uses `Gamma=2^(4e)` and counts exactly
`N=12*2^e*node_count` real rounding writes per forward word. Forward
and inverse are both charged. Every C or shear division rounds each
real component to nearest, ties to even, using integer arithmetic.

The word retains a constant q after every rounded write. Its literal
division numerators temporarily use grid q+1 and at most two extra
bits relative to the current scalar magnitude. The displayed signed
guard includes a four-bit local margin. Observed maxima in the receipt
are stored post-gate numerators; this fixed temporary margin is an
analytical charge, rather than a measurement of every Python register.

The exact reference computes dyadic operators and reports the minimal
common denominator after each gate. Its trailing-zero reduction is
MATHEMATICAL instrumentation, not a free physical output normalization.
All exact bank columns are compared to the operator with the commuting
bank shears removed; canonical cases additionally compare direct C
matrix coefficients. Exact Gaussian Gram matrices verify the unitary
endpoints, including the nonlinear family.

The repaired full four-worker run passes in 2.992 source seconds:

| e | Endpoint family | q | Exact prefix excess above q | Scalar writes per forward | Physical bank columns | Gram entries |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 3 | Canonical C | 90 | 7 | 288 | 16 | 64 |
| 4 | Canonical C | 159 | 9 | 768 | 32 | 256 |
| 5 | Nonlinear unitary conjugate | 167 | 14 | 11904 | 64 | 1024 |
| 6 | Nonlinear unitary conjugate | 301 | 17 | 48384 | 128 | 4096 |

All sixteen complete arbitrary Gaussian fields, their rounded true undo,
and eight charged final zero-bank projections satisfy the conservative
integer error bounds. Every padded-bank case has nonzero rounded residue;
the source retains its exact squared norm at grid q. The repaired early
projection control corrupts the RETAINED data bank at the mixed prefix.
This makes the projection distinction substantive.

The canonical examples have linear selected-width work, and the nonlinear
examples have exponentially many child calls. Neither is a proposed
faster supplier. The small examples provide numerical-contract evidence
without a workload or utilization objective.

## Exact-grid comparison, provenance and reproduction

The exact endpoint-grid contract requires exact dyadic equality on every
field and charges denominators from completed child widths. Its earlier
O(dL) allowance can become O(d^2) at linear depth. The new numerical
contract instead permits bounded rounding at a fixed grid and proves a
final error. Unitary completed endpoints control error amplification;
they do not prove small exact denominators.

The measured exact excess grids above are finite observations and happen
to be small. They are not an all-size grid theorem, an example requiring
Theta(d^2) denominators, or a counterexample to the exact-grid bound.
The useful new deduction is the conditional O(log N+d) rounding allowance,
which remains valid without an exact transient-denominator classification.

The [first attempt](../../runs/20261009T061122Z-transfer-unitary-rounding-depth/report.md)
passed the quantitative controls but its premature erasure control only
rejected the complete two-bank endpoint; the retained bank could remain
correct at that placement. The original source and all results remain
unchanged. The
[separate repair](../../runs/20261009T061517Z-transfer-unitary-rounding-projection-repair/report.md)
moves that control to the fully mixed prefix and requires retained-data
corruption. Its
[recovery patch](../../fixtures/transfers/unitary-rounding-projection-scope.patch)
reconstructs the exact original source; reverse application was exercised
in isolated ignored storage and verified by SHA256. This is a control
scope repair, rather than a failed positive arithmetic result.

The [bounded attempt](../../runs/20261009T061800Z-transfer-unitary-rounding-bounded/report.md)
passes the canonical e3 case. Source/configuration closure is the authored
source and [portable configuration](../../configs/transfers/unitary-rounding-depth.json);
there are no producer imports or external dependencies.

```sh
python3 research/integer-mult-breakthrough/code/transfers/unitary_rounding_depth.py --workers 1 --small
python3 research/integer-mult-breakthrough/code/transfers/unitary_rounding_depth.py --workers 4
```

Optional `--output` requires a fresh directory. Completed protocols record
actual UTC, seeds, source/configuration identities, commands, full compact
results and raw recovery paths. All current files are separate from the
frozen earlier exact-grid and row-lifecycle results.
