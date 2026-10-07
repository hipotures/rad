# Primary literature and finite circuit comparators

Campaign `20261007T222521Z`, immutable interval 2026-10-07 22:25:21 UTC
to 2026-10-08 08:25:21 UTC. This report distinguishes source constructions,
implemented comparators, and leads still being investigated.

## A reproduced 2012 tree-projection comparator

Petteri Kaski, Mikko Koivisto, and Janne H. Korhonen,
*Fast Monotone Summation over Disjoint Sets*, arXiv:1208.0554v1,
submitted 2012-08-02 17:38:41 UTC,
[primary manuscript](https://arxiv.org/abs/1208.0554v1), give a binary-tree
projection method for monotone summation. Lemmas 1, 3, and 4 motivate the
authored comparator `review_tree_projection.py`.

The implementation projects input subsets to occupied nodes of a balanced
binary tree. It memoizes refined input patterns together with the active
query points and sums disjoint refinements. It supports disjointness and
exact prescribed intersection cardinality, omits padding leaves, interns
identical disjoint support sums, and checks every output against its exact
input support. This is one faithful construction with practical interning;
it is not asserted to be the best circuit obtainable from that paper.

For the local disjoint-pair problem, the following counts were obtained:

| Ground points | Tree additions | Paired baseline additions |
|---:|---:|---:|
| 7 | 101 | 90 |
| 15 | 1,063 | 723 |
| 25 | 4,230 | 2,313 |
| 49 | 21,900 | 9,813 |

For the whole `h=50`, three-subset, intersection-one problem, the tree
comparator uses 990,367 additions and 19,600 outputs. All 63,562,800
nonzero coefficients agree with the target map. Its source spans need a
separate rational-label eligibility audit; exact scalar coefficients alone
would not qualify it for the baseline transfer. Its operation count already
loses to the paired common-point construction, so that transfer was not
attempted. The run took 66.0 seconds.

These negative results reject this implemented comparator as an
improvement. They do not reject stronger versions of the source method.

## The stronger 2014 construction is a separate lead

Kaski, Koivisto, Korhonen, and Igor S. Sergeev, *Fast monotone summation
over disjoint sets*, Information Processing Letters 114(5), 264–267,
May 2014, DOI
[10.1016/j.ipl.2013.12.003](https://doi.org/10.1016/j.ipl.2013.12.003),
remove the logarithmic factor from the preliminary 2012 result. The
publisher's primary abstract exposes the bound

```text
C_(n,p,q) <= [p sum_(i<=p) binom(n,i) + q sum_(j<=q) binom(n,j)]
             * min(2^p,2^q).
```

Its endpoint-packing recurrence may yield a better finite constant than the
implemented tree method. The full recurrence has not yet been implemented
or used as evidence of a finite improvement. A truncated publisher snippet
is insufficient to reconstruct it safely.

The coauthor's repository `igorssergeev/igorssergeev.github.io`, pinned at
`0098a41336aa68227a89c3f4f87d62c07c300d85`, was accessed through `gh`.
It confirms the 2014 citation and distinguishes it from the author's
earlier arXiv:1209.1645 work. The author-hosted 2026 circuit-design book and
2026 unique-disjointness paper are additional primary construction leads.
No exhaustive novelty or priority claim is made.

## Reproduction and source recovery

The immutable arXiv PDF and source tar are external inputs under the
campaign's `inputs/review/`. The protocol records sizes and hashes. The
source tar contains the author's TeX and bibliography. The comparator uses
only Python's standard library. From the topic's `code` directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 review_tree_projection.py --sizes 7 15 25 49 --reference "$REF" --output "$OUT"
PYTHONDONTWRITEBYTECODE=1 python3 review_tree_projection.py --sizes 8 12 16 20 30 40 50 --p 3 --q 3 --intersection 1 --output "$OUT"
```

The first command imports only the pinned local baseline constructor for
comparison. Compact exact-support results are retained in
`runs/20261007T224230Z-review-baseline/results/`; the protocol identifies
each external original. The parent campaign owns shared manifests and
publication.
