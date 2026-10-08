# Review of the full characteristic and every matching cardinality

The extended exclusion is supported for the pinned positive continuation graph with its complete generic copied-center inner and exterior profiles. This supersedes the cardinality restriction of [the first review](continuation-review.md), without extending to fixed `I+J` profiles or other positive labels.

## Correct physical comparison

For one local axis of dimension `h`, a selected continuation contributes the original inner profile change

`-inner(h,h-ru) - inner(h,rv) - inner(h,rt-rv) + inner(h,rt-ru)`.

Its total inner rank change is `-h`. It also removes one auxiliary role. The pinned PR 36 `scripts/copied_centers_network.py::profile` shows that each such role has exterior children of widths `h` and `m-2h`, where `m=23*25=575`. The denominator `W*m^tau` loses one `m^tau` term per removed role. Therefore the correct additive characteristic change is

`inner_delta - [h] - [m-2h] + [m]`.

The plus sign on width `m` is essential: it represents subtracting the removed denominator contribution. The weighted mass is exactly zero: `-h-h-(m-2h)+m=0`. This is the quantity implemented by the coordinator's all-degree profile. Local invocation copy counts are positive fixed multipliers, so componentwise comparisons add correctly in the complete network. Data-profile and endpoint terms remain unchanged.

Comparing only the local unnormalized moment across cardinalities would not suffice, because the physical role volume `W` changes. No such comparison is used for this extended conclusion.

## Independent reconstruction

The scout's Cartesian-product implementation was extended independently with this physical characteristic. It enumerated all 8034 component matching states and reproduced 5872 distinct component profiles. All 3199 nonidentical alternatives are majorized by the incumbent; none remains unresolved. The unchanged maximum-cardinality receipt is retained separately.

| Local dimension | Component matching states | Distinct complete profiles | Nonidentical alternatives |
| --- | ---: | ---: | ---: |
| 23 | 3706 | 2694 | 1485 |
| 25 | 4328 | 3178 | 1714 |

Majorization and strict concavity imply that the incumbent characteristic is no greater for every `0 < tau < 1`. No alternative can satisfy the strict moment inequality at a saving for which the incumbent fails. This is a finite analytic exclusion for the exported graph, not global optimality of multiplication or verification of the upstream graph generator.

The 0.38-second independent run and input hashes are recorded in [all-cardinality-continuation-review.json](all-cardinality-continuation-review.json). Reproduce with the command in the first review, adding `--all-degrees` and writing to the separate receipt path.
