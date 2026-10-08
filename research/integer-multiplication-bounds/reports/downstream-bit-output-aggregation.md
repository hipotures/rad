# Final partial-output aggregation: exact spans, unchanged-flow negative

Campaign `20261007T222521Z`, immutable start/deadline
`2026-10-07T22:25:21Z` / `2026-10-08T08:25:21Z`.

The hypothesis was to combine each bit target's three common-point partial
sums into one output before injection. The first two-way sum can have an
indefinite rational source span while remaining nondegenerate; the final
sum can use the exact target kernel. This would remove two designated
partial outputs per target and introduce two additions. Baseline c+q
therefore stays unchanged, but perhaps the retained-controller compiler
could gain new chains.

For the unchanged compiler, it cannot create new multiuser controller
candidates. Every old designated partial sum has the same positive number
`binom(h-3,2)` of source summands. A cancellation-free addition strictly
increases that number. Distinct partial outputs therefore cannot feed one
another. After pruning the old graph each has exactly one user, its output
termination. Replacing that user by a combiner input preserves its one-user
status. The two new combiner nodes also have one user. All other user lists
are unchanged. The existing flow requires multiple uses of the same
controller node, so this change alone adds no eligible controller chain.
This is a structural negative for that compiler, not a lower bound for
broader compilers which reuse data/output pivots or change other labels.
The finite-circuit branch independently agreed with this conclusion.

The rational span formula is useful for any such future schedule. Fix a
target S of size three, let n=h-3 be its outside set size, and let U_k be
the sum of k of its common-point helper spans, k=1,2,3. In the retained
form `I-J/9` it consists of vectors with zero entries at the other 3-k
target coordinates and

```
sum(outside coordinates) = 2 sum(active target coordinates).
```

The dimension is n+k-1. Outside-coordinate differences form a positive
subspace of dimension n-1; active-target differences form a positive
subspace of dimension k-1. They are orthogonal to one another and to the
aggregate vector with every active target coordinate 1/k and every
outside coordinate 2/n. This aggregate vector has norm

```
g_k = 4/n + 1/k - 1.
```

In this explicit rational basis the Gram determinant is
`n*k*g_k=4k-n(k-1)`. Thus the two-helper intermediate is singular at h=11,
and the full target kernel at h=9 (where the ambient form is already
degenerate). At h=50 the two/three-helper determinants are -39 and -82;
their signatures are (47 positive,1 negative) and (48 positive,1 negative).
They are valid nondegenerate frames even though they are indefinite.

All basis vectors and helper generators are target-orthogonal by direct
rational comparison; triple generator norm remains two. The accompanying
exact checker constructs the full Gram matrix, computes its determinant,
and preserves the expected singular cases as negatives. Its finite tests
supplement the displayed algebraic proof; they do not establish a new
scalar/frame/rank transfer for a changed physical compiler.

Source: [downstream_bit_output_merge.py](../code/downstream_bit_output_merge.py).
Reproduction uses Python standard-library exact fractions:

```
python3 -B research/integer-multiplication-bounds/code/downstream_bit_output_merge.py \
  --upstream "$REFERENCE" --h 8 9 10 11 12 50 --output "$FRESH_RESULT"
```

REFERENCE is the campaign's immutable upstream at
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`; outputs must be fresh paths.
This branch does not justify an improved kappa. The next useful extension
would need a different physical reuse rule, not merely these final sums.
