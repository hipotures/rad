# Independent criticism of the generic continuation exclusion

Reviewed `code/continuation_frontier.py`, `code/moment_matching.cpp`, and the completed `work/matching-20261008T125010Z/exhaustive.json`. The finite exclusion is supported within its stated exported-graph and generic inner-profile scope.

## Independent check

`check_continuations.py` does not import either implementation. It reconstructs connected components, enumerates each donor's unmatched or adjacent-use choices by a Cartesian product, filters repeated uses, reconstructs explicit generic child lists, and checks exact majorization against the incumbent. Its 0.31-second bounded run reproduced:

| Local dimension | Edges | Components | Maximum cardinality | Sum of component maximum-matching counts | Nonidentical profiles excluded |
| --- | ---: | ---: | ---: | ---: | ---: |
| 23 | 1738 | 1209 | 1324 | 1646 | 46 |
| 25 | 2039 | 1464 | 1589 | 1939 | 25 |

Every incumbent component matching has maximum cardinality. Every alternate maximum-cardinality profile is either identical or majorized by the incumbent. The largest component has four donors. [The compact receipt](continuation-review.json) includes the exported edge hashes.

The maximum-matching counts above are sums of component counts, not counts of global matchings. Global choices form a Cartesian product. Independence of components is sufficient because both matching cardinality and child moments add across components; componentwise maximum cardinality is necessary for global maximum cardinality.

## Majorization direction

Write `D = incumbent_profile - alternative_profile`. The positive entries of `D` form a width list A and its negative entries form B, with zero padding to equal lengths. The implementation verifies that A majorizes B: all descending partial sums of A are at least those of B, and totals agree. For every `0 < a < 1`, `w^(1-a)` is strictly concave on nonnegative widths. Therefore `sum_A w^(1-a) <= sum_B w^(1-a)`, so the incumbent has no larger native moment than the alternative. This is the correct direction for excluding improvements. Scaling all widths by the unchanged other arity preserves the comparison.

The rational log enclosure uses range reduction to `[1,2]` followed by a positive atanh series and an outward tail. The cubic lower and quartic upper bounds for `exp(-x)` are valid for the asserted `0 <= x < 1`. These arithmetic bounds are not needed for the universal Schur exclusions observed here.

## Limits and minor implementation observations

- The checker consumes exported edges. This independent run does not prove that the C++ eligibility predicate generates every mathematically possible continuation, or that upstream positive labels and physical compilation are correct.
- The C++ heuristic changes traversal order while its augmenting-path routine preserves maximum cardinality. The independent exhaustive run confirms maximum cardinality for its exported incumbent.
- The exhaustive checker stores `improved_candidate` in per-profile verdicts but does not include an improvement count in its top-level totals. A summary should inspect those verdicts explicitly. The actual evidence contains only `identical` and `baseline_schur_optimal`, so this omission does not alter this result.
- This excludes only maximum-cardinality continuations of the pinned graph under the generic inner profile. It does not exclude lower-cardinality choices, other positive labels or producers, relabelings, PR 38 fixed-basis profiles, or a new physical compiler.
- This is an independent implementation and agent review, not external mathematical peer review or formal verification.

## Reproduction

From the repository root, after regenerating the coordinator's two exported edge fixtures:

```bash
python3 research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/scout/code/check_continuations.py \
  research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/matching-20261008T125010Z/h23-edges.csv \
  research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/matching-20261008T125010Z/h25-edges.csv \
  --output research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/scout/continuation-review.json
```
