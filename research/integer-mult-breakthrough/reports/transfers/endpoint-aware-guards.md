# Proposed endpoint-aware guard for exact recursive phase programs

Status: **PROPOSED CONDITIONAL ANALYTICAL LEMMA**, with separately described
**EXACT FINITE PRECISION CONTROLS**. This is a replacement guard argument to
review and integrate, not a certified native circuit or multiplication bound.

The usual sum of recursive elementary depths can be unnecessarily large.
Several serial same-width children can make that depth ledger grow like
`q_m^L`. A completed exact child nevertheless has a simple target operator
with its own endpoint grid and magnitude bound. Its internal excursion need
not be carried forward as the next sibling's input bound. Only one child is
active on the fixed depth-first stack at a time.

## Endpoint certificate

Suppose every component of every current Gaussian value lies in `2^-P Z`,
and its real and imaginary components have absolute value at most M. For
the exact target `C^tensor(t)`, all coefficients are Gaussian integers divided
by `2^t`. A conservative component-infinity row bound is `2^t`. Consequently
the complete returned stream lies in grid `2^-(P+t) Z`, with component bound
`2^t M`. The inverse C target has the same bounds.

These statements hold on arbitrary current dirty values, every field, and
the full selected address cube. Unit fourth-root phases and affine complete
address permutations add no grid or magnitude charge. Knowing only a Pauli
label, projective Clifford class, a zero-scratch test, or a finite basis sample
does not supply the required exact all-size endpoint contract.

## Integration contract

Use recursive state `(e,L)`. Each child receives a complete stream and has
selected width `e_j<=e` and remaining budget `L-1`; strict width decrease is
not required for this guard lemma. An exact bounded-width or budget-zero leaf
implements the target by ordinary C kernels. Its internal guard satisfies
`G_D,leaf(e)<=c_D*e+c_0` and `G_M,leaf(e)<=c_M*e+c_0`.

For each internal node supply a literal finite local word, including all
scalar gates, wrapper phases, field copies/erase/restoration, routing and
reassembly. Its total completed-child width satisfies
`sum_j e_j<=q*e+q_0`, with fixed constants. Let D_s and M_s be uniform bounds
on its nonrecursive scalar grid and component-magnitude charges. These bounds
must cover every temporary register and prefix of the actual implementation,
not just its final matrix. Copying and complete address routing preserve these
numeric bounds; their full time, storage and legality obligations remain.

A fixed dyadic coefficient alpha contributes its actual denominator exponent.
For a scalar shear `y<-y+alpha*x`, one endpoint magnitude bound uses
`1+|Re(alpha)|+|Im(alpha)|`. The compiled multiply/add word can have larger
temporary values and must be included in M_s. A subtraction, inverse scalar
word or reused dirty helper is a real operation with its own prefix charge.
Any field allocation, precision format or scratch restoration used by the
local word must be proved separately.

## Simultaneous induction

Prove two statements together by induction on L:

1. The complete child returns its exact target operator on all permitted dirty
   inputs, with the endpoint bounds above.
2. Its entire active execution stays within the stated internal grid and
   magnitude allowances.

The leaf is the explicit elementary algorithm. At an internal node, consider
the point just before child j. Every earlier child has completed, so statement
one charges its **endpoint width**, not its internal guard. Together with
the actual scalar prefixes, the current stream has grid exponent at most
`P+q*e+q_0+D_s` and component bound at most
`M*2^(q*e+q_0+M_s)`. Inactive streams, complete copies and dirty auxiliaries
are bounded in the same way.

During child j, use statement two at its smaller budget and the current input
bound. After it returns, statement one again supplies its exact endpoint
bound for the next local operation. Thus sufficient recurrences are

```text
G_D(e,L) <= q*e+q_0+D_s + max_j G_D(e_j,L-1),
G_M(e,L) <= q*e+q_0+M_s + max_j G_M(e_j,L-1).
```

The maximum accounts for one active child's excursion. The preceding-child
sum remains in the local coefficient q; no sibling, copy or scalar charge
has disappeared. Since `e_j<=e`, iteration gives

```text
G_D(e,L) <= c_D*e+c_0 + (q*e+q_0+D_s)*L,
G_M(e,L) <= c_M*e+c_0 + (q*e+q_0+M_s)*L.
```

For `L=O(log(e))`, both bounds are `O(e*log(e))`, even when a scalar dependency
path contains several same-width children. If all children have a uniform
strict ratio below one, the child-width contribution is geometric and the
same argument yields `O(e)` after bounded-width stopping. This conclusion
uses exact endpoint semantics and does not follow from a width-only recursive
oracle or from the elementary-depth sum alone.

The implementation may keep one fixed global grid throughout. Returned
child values have zero trailing grid bits by their exact operator identity;
no numerical truncation, unproved cancellation or free normalization is
performed. If the machine changes formats instead, those scans and their
correctness must be charged. The induction must establish sufficient actual
buffers before executing arithmetic; it cannot invoke an overflowing child
and appeal afterwards to an ideal exact result.

## Relation to time, rows and long-digit capacity

The guard lemma supplies no time contraction. The independent
[row-budget transfer](same-width-row-budget.md) still requires the complete
volume moment
`n_m/W+sum_(t<m)(n_t/W)*(t/m)^(1-s)<1`, a real preceding stock of `W^L`
complete rows, a paid elementary fallback and all binary routing costs.
Every child, row and payload must exist. The semantic induction and the row
allocation must refer to the same literal program and stopping state.

A root with e at most `p^epsilon` and L logarithmic in e has guard
`O(p^epsilon log(p))`, so this part fits `o(p)` for every fixed epsilon below
one. Equivalently it can be bounded by `O(e^(1+zeta))` for each fixed positive
zeta. Other CRT, Fourier, prime, precision, routing and final transfer margins
remain unchanged until separately rebuilt. This guard cannot make the frozen
child moments cross kappa `1e-4`.

## Scalar and leaf temporary charges

For the finite stress word below, the local shear uses
`alpha=(3+i)/4`. Its output adds two grid bits and at most one magnitude bit.
A literal implementation builds `3a`, `3b`, `3a-b` and `a+3b`, then divides
by four and adds the old y. The largest numerator is at most four times the
incoming component bound. A safe internal magnitude charge per shear is two
bits. Its inverse has the same charges. Thus the two scalar operations give
`D_s=4`, `M_s=4` when their registers are included.

A literal C kernel uses four signed input components for each numerator,
then divides by two. Each partial numerator is bounded by four times the
current maximum; after a completed direction the bound is twice that maximum.
An e-direction leaf therefore needs at most e extra grid bits and `e+1`
magnitude bits including its last numerator. This is a direct elementary
leaf proof, rather than a bound inferred only from its final matrix.

## Exact controls and their limits

The deliberately inefficient stress word has three serial same-width
children at every internal node. It applies a Z sign, a dirty scalar shear,
the three children, the inverse scalar shear and a final Z/unit correction.
The shears commute with the column C operator. Since `C^3=C^-1` and
`C=i Z C^-1 Z`, the word returns exactly C on every field. Budget L decreases,
so it terminates. It has no volume contraction and is not a proposed fast
algorithm.

Two distinct executions are preserved. The first
[atomic scalar-state control](../../code/transfers/endpoint_guard.py) monitors
stored payload states after compound scalar operations. It uses their
endpoint magnitude charge one; it does not observe their temporary numerator
registers. Four workers finish that limited model in 0.381 seconds.

The subsequent [literal register control](../../code/transfers/endpoint_guard_literal.py)
observes every partial scalar and C numerator, division, output and dirty
field. It uses the full charges just derived. Four workers check widths one
through four and budgets zero through four in 0.555 seconds. Every completed
recursive call is independently compared with the elementary exact C target.
At budget four there are 121 calls and up to 324 serialized leaf direction
layers, yet the endpoint-aware grid and magnitude bounds hold. This verifies
the finite stress word, not an arbitrary native motif or formal proof.

For this word the literal sufficient guards are

```text
G_D <= e+(3e+4)L,
G_M <= e+1+(3e+4)L.
```

The [complex-track independent critique](../complex/endpoint-guard-independent-critique.md)
and [coordinator's independent review](../obstructions/endpoint-guard-review.md)
accept this induction under the stated integration contract. The latter also
preserves independent paired-scale controls: even the same exact C endpoint
can hide arbitrarily large internal grid or magnitude excursions. Those
controls are not counterexamples to the charged induction. They explain why
exact endpoints alone do not replace the uniform literal prefix and recursive
implementation hypotheses. Neither review certifies native integration.

The atomic model's smaller scalar magnitude ledger is not promoted to a
literal arithmetic claim. The unit-wrapper omission is rejected. More
generally a child proportional to `2^(-N)*C^tensor(t)` can have the same
projective Clifford label while adding N grid bits; applying the exact C
endpoint bound to that child would be invalid. Exact normalization and
complete source/sink semantics are part of the hypothesis.

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/endpoint_guard_literal.py \
  --workers 1 --small
```

The bounded literal closure is both authored source files, standard-library
Python only. The [atomic run](../../runs/20261008T223823Z-transfer-endpoint-guard/)
and [literal run](../../runs/20261008T224439Z-transfer-endpoint-guard-literal/)
pin each source version, seeds, command, UTC interval and complete compact
results. The latter explicitly pins the imported local atomic reference.

This proposed induction, finite word and separate register review were
authored with OpenAI Codex. No external novelty, formal verification, complete
native guard or improved exponent is claimed. The next integration step is an
independent review of the induction and a literal native program satisfying
every stated interface, row, scalar and capacity assumption.
