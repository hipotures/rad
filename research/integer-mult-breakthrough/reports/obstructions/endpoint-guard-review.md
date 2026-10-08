# Independent review of the endpoint-aware precision induction

Status: **INDEPENDENT CONDITIONAL ANALYTICAL REVIEW**, with **EXACT FINITE
SCOPE COUNTEREXAMPLES**. The stated induction is valid under its explicit
interfaces. It is not formal verification or acceptance of a native compiler.

The transfer track proposes an [endpoint-aware guard](../transfers/endpoint-aware-guards.md)
for recursive exact Gaussian phase programs. This review reads its derivation
and separately reconstructs a family of counterexamples without importing the
producer. The purpose is to distinguish the useful induction from an invalid
endpoint-only bound.

## The contract that supports the bound

The returned child must be exactly C on every selected axis, on the entire
current stream and every arbitrary dirty field. Its coefficient denominator
divides `2^t` and its component-infinity row bound is at most `2^t` for
selected width t. Thus a completed child increases the current logical grid
and component-magnitude allowances by at most t bits each. Inverse C and
fourth-root wrappers have the stated analogous bounds.

The child must also have an independently inductive bound for every internal
Gaussian register. A literal local schedule must bound each scalar prefix and
temporary register, and its total completed-child width by `q*e+q_0`. The
constants and local scalar charges must be uniform in remaining budget L and
selected width e. Fixed arity can make those constants extremely large; that
does not make them free in a finite implementation.

At a point inside one active child, preceding siblings have returned. Their
inputs for later siblings therefore use the returned target's endpoint
bounds, while the active child's internal bound is added only once. With
local charge E_D for grids and E_M for magnitude, sufficient recurrences are

```text
G_D(e,L) <= q*e+q_0+E_D + max_j G_D(e_j,L-1),
G_M(e,L) <= q*e+q_0+E_M + max_j G_M(e_j,L-1).
```

This is justified by simultaneous semantic and guard induction on L: the
known explicit leaf establishes both statements; each internal child has
smaller budget even if its width is unchanged. The argument does not execute
an overflowing child and infer correctness afterwards. For e_j<=e it gives
`O(e*L)` plus the stated leaf/local constants. With L logarithmic this is
`O(e*log(e))`. Uniform strict-width contraction and bounded-width stopping
give a geometric width sum and `O(e)` overall.

Only Gaussian payload buffers and their homogeneous scalar temporaries are
covered by these numeric inequalities. Address counters, row allocation,
descriptor storage, packet movement, exception repair and arithmetic time
retain their separate bounds. An affine scalar constant or nonhomogeneous
temporary needs a bound beyond multiplication of the current payload maximum.

One globally fixed grid is compatible with the proof. The exact returned
operator implies that its low grid bits are zero; the representation need
not be shortened or reencoded. A Fraction denominator reducing in a finite
oracle is evidence of that algebraic property, not a paid-machine normalization
procedure. An implementation that changes formats must account for it.

The literal producer controls correctly distinguish atomic stored-state
bounds from numerator-register bounds. The scalar `(3+i)/4` uses partial
numerators as large as four times the incoming component maximum. Its two
appearances need the larger local magnitude charge four. An elementary C
direction also has a four-term numerator before division by two; an e-axis
leaf needs the additional constant magnitude allowance in that implementation.

## Why the exact endpoint alone is insufficient

Fix any selected width t and an arbitrary positive integer N. The two words

```text
2^N I ; C^tensor(t) ; 2^(-N) I,
2^(-N) I ; C^tensor(t) ; 2^N I
```

both return exactly C, since constant scalings commute with it. In the first
word an input component one becomes `2^N` before C. In the second an integral
basis input first needs N denominator bits. Their endpoint semantics therefore
do not bound internal magnitude or grid independently of N. The local scalar
prefix or active-child bound must include that charge. A projective Clifford
label is weaker still: omitting the restoring scale changes the actual endpoint.

The [independent exact source](../../code/obstructions/endpoint_guard_counterexamples.py)
checks all these assertions at t=1,2,3 and N=10,20. All six four-worker cases
pass in 0.046 seconds. Both paired-scale words agree entrywise with the exact
unit-basis C result, while their internal bounds exceed the endpoint-only
allowances. The unrestored scale is rejected. The source imports none of the
transfer implementation and uses only standard-library rational arithmetic.

These examples are not counterexamples to the proposed charged induction:
they have large local scalar charges, exactly as that induction requires.
They prevent promoting a tested endpoint matrix into an unproved guard for
an opaque implementation.

## Result and integration boundary

The proposed conditional induction survives this independent review. Its
endpoint property, active-stack argument, fixed-grid interpretation and
explicit temporary charges are consistent. A full all-size native program
must still prove that every callback, local word and stopping state meets
those hypotheses, with enough physical numeric capacity in its complete rows.
The induction supplies no contracting time moment, row stock or improvement
of the frozen complex characteristic. It does not certify kappa >= 1e-4.

The exact counterexample [run](../../runs/20261008T225540Z-endpoint-scope-review/)
records source identity, settings, original evidence and a corrected output
namespace typo. Original bytes remain unchanged. From the repository root:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/endpoint_guard_counterexamples.py \
  --workers 4 --output research/integer-mult-breakthrough/work/obstructions/NEW-RUN/results.json
python3 -B research/integer-mult-breakthrough/code/transfers/endpoint_guard_literal.py --workers 1 --small
```

This review and its independent counterexample implementation were authored
with OpenAI Codex. The induction is attributed to the transfer track. No
external novelty claim or external human review is implied.
