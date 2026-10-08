# Scope review of the finite composition adapters

Campaign: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.
Pinned original: `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

The thin `finite_phase_composition.py` and `finite_packed_composition.py`
adapters correctly substitute promoted finite role counts into the previously
reviewed count and parameter formulas. Their conclusion is confined to the
supplied finite grid and retained proof families. They do not establish a
general optimum or independently prove the inherited multiplication theorem.

The phase loader retains immutable certificate hashes, requires terminal
full scalar/frame/target/matching evidence and bounded dirty controls,
recomputes the uniform count identities, and regresses every numerical
parameter and common cutoff of all eight earlier phase rows. It substitutes
a smaller verified role count only. The loader's truth checks are evidence
gates, not substitutes for the separately reviewed mathematical proof.
The h50 gap23 boundary is supplied by [the independent dense review](review-singleton-witness.md).

The packed adapter changes only the reviewed recurrence estimate. Its
reviewer independently recomputes every competing finite count and uses
longer rational logarithm enclosures. It requires `0 < b < a`, the branch
for which the growing-geometric derivation is valid, and proves the complete
supplied Cartesian grid is represented exactly once. For that branch the
retained guard-family ceiling is

```text
U(a,b) = a^2 b/[b(1-a)+5a^2].
```

Its derivative numerators after clearing the positive squared denominator
are `b^2(2a-a^2)` in `a` and `5a^4` in `b`, both positive. Independent upper
primitive enclosures therefore supply valid upper ceilings. Comparing each
ceiling against the selected actual strict kappa is stronger than trusting
the producer's sorted candidate scores. This monotonicity does not authorize
using the same formula when a new complex primitive changes the order of
the two savings.

Fresh independent replays select uniform h50 with 485,360 side roles:

| Retained estimate | Strict kappa |
|---|---|
| Original per-node phase estimate | 9638040483941/10^30 |
| Reviewed exact packed unrolling | 4819020256931/(5·10^29) |

Both replays check 120 other candidates using independent family ceilings;
the closest competitor is `(50,52)`. The packed replay also checks all
960 complete stopped recurrences. Its common parameter cutoff is
`log2(b_input) >= 6132477715457`, with additional retained prime, recurrence
absorption, and source-interface thresholds. It is not a fully explicit
threshold for the complete multiplication machine.

The [completed run](../runs/20261008T003843Z-review-composition-adapters/)
records source/input hashes, Python 3.14.4, exact
commands, and compact replay outputs. No arithmetic or parameter formula
was changed by this scope review.
