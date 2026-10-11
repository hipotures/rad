# Upstream frontier inventory, 2026-10-11

## Question

Where is the CrocSwap/integer-mult-bounds frontier now? This report separates
the reviewed selection on upstream `main` from the open pull-request claims
and records how much evidence each claim has. It is step 2 of the
re-baselining plan. Step 1 pinned input `upstream-frontier-12a4934d`.

## Method

- Upstream `main` was pinned at `12a4934d15006e8c10f9b2264f13f8f341be802b`
  (committed 2026-10-10 14:13 UTC). The selected witness was read from its
  `README.md` and `docs/research/community-pr279-review.md`.
- All 481 pull requests, with bodies, were fetched with `gh` at
  2026-10-11 19:18 UTC, along with every issue comment (125).
- `code/upstream_frontier_inventory.py` parses the first kappa value in each
  title. It falls back to the body only when the title has no value and no
  "no new κ"-style marker.
- GitHub check runs were fetched for 259 PR heads with
  `code/fetch_upstream_check_runs.py`. These are all PRs claiming at least
  0.95 x the main selection, plus every merged PR.
- Each PR was checked for mentions in upstream review documents (`README.md`,
  `CONTRIBUTORS.md`, `docs/**/*.md`) on the pinned main.

Exact settings and commands are in [protocol.json](protocol.json). Full
per-PR rows are in [results/pull-inventory.csv](results/pull-inventory.csv),
and the tables in [results/frontier-tables.md](results/frontier-tables.md).
The raw snapshots are published as gzip copies under
[evidence/20261011T1916Z-upstream-frontier-inventory](../../evidence/20261011T1916Z-upstream-frontier-inventory/).

## Measured results

| Quantity | Value |
|---|---|
| Pull requests | 481 (408 open, 36 merged, 37 closed unmerged) |
| PRs with a parsed kappa claim | 412 |
| Open title-stated claims above main | 173 |
| Upstream main selected kappa | `90446448750933/125000000000000000` = 7.23571590007464e-4 (PR276 + PR279, reviewed 2026-10-10) |
| Highest merged claim | 7.22869827347495e-4 (#276) |
| Highest open claim | 1.372550159367980e-3 (#480, higherbeing), 1.897 x main |
| CI on the 173 open claims above main | 78 success, 49 failure, 37 no runs, 9 pending |
| Upstream review mentions of those 173 | 0 on the pinned main |
| PR claims created per day | 10-08: 97, 10-09: 108, 10-10: 91, 10-11: 115 |

The top of the open frontier (title-stated, self-reported):

| PR | Author | Claimed kappa | x main | CI | Builds on |
|---|---|---|---|---|---|
| #480 | higherbeing | 1.372550e-3 | 1.897 | none | #472, #469 |
| #469 | ahrazzle | 1.350581e-3 | 1.867 | none | #450 |
| #464 | ahrazzle | 1.347745e-3 | 1.863 | none | #450 |
| #450 | DreamingOfClouds | 1.347745e-3 | 1.863 | failure | #448 |
| #448 | higherbeing | 1.330734e-3 | 1.839 | none | #447 |
| #473 | rohanarun | 1.295630e-3 | 1.791 | pending | - |
| #478 | Dugongue | 1.295509e-3 | 1.790 | none | #473 |
| #472 | chafreaky | 1.292100e-3 | 1.786 | pending | #458, #463 |
| #456 | rohanarun | 1.266565e-3 | 1.750 | success | - |
| #454 | chafreaky | 1.266536e-3 | 1.750 | success | - |

The two leading lineages, from the first back-reference in each title:

- #480 <- #472 <- #458 <- #454 (chafreaky's R715/R740 shared-kernel line,
  with cross-copy hosting added by higherbeing)
- #469 <- #450 <- #448 <- #447 <- #445 (eleven-stage cross-copy hosting)

The highest open claim with a fully successful CI run is #456 (1.266565e-3,
1.750 x main).

Our own upstream PRs are:
- #51, merged: 4.171211781e-5
- #41, open: 4.034168124e-5
- #20, open draft: the source-framed h53 witness above 2^-20

The best result of our 2026-10-08 fast-integration campaign is about
5.14e-5, roughly 14 times below the current main selection.

## Interpretation

- **Fact:** the reviewed upstream frontier is 7.2357e-4. Every larger number
  is an unreviewed open claim. No upstream review document on the pinned main
  mentions any of the 173 open claims above it. Their reviews, if any, came
  after 2026-10-10.
- **Measured:** CI results are mixed. A green CI only means the upstream
  workflows passed on that head. Those workflows replay main's selected
  packages and the generic artifact checks. A PR's own claim is replayed only
  if the PR adds its own workflow.
- **Inference:** the open frontier moves several times a day and is dominated
  by a few authors (rohanarun, chafreaky, eumemic, Dugongue, DreamingOfClouds).
  Most late claims are small increments (+0.01% to +2%) stacked on each
  other's heads. A specific claim can be invalidated when an earlier link in
  its chain fails review.
- **Inference:** our techniques (interval joint compilation, positive frames,
  matrix-weighted allocation, skip-prefix strips) belong to the PR51-PR62 era.
  They are 1-2 orders of magnitude below the current constructions. Those
  constructions use five- to eleven-stage words, E8 units, completed banks and
  cross-copy hosting. Whether any of our mechanisms still adds value on top of
  them is untested.

## Confidence and limitations

- Claim parsing reads the title, or the body when the title has none. I
  manually checked every title that mentions kappa without yielding a value:
  each is a ceiling, tooling, audit or negative-result PR. 23 claims come from
  PR bodies and are less reliable. The frontier tables use title claims only.
- Closed outliers such as #159 (kappa = 0.127865, closed unmerged) are kept in
  the CSV but are not part of the open frontier.
- Kappa values were not replayed or checked here.
- The snapshot is a single moment. New PRs were still arriving when it was
  taken.

## Next step

Step 3 of the plan: compare our mechanisms with the techniques of the leading
lineages (#454-#480, #445-#469) and with the reviewed PR276/PR279 package.
The goal is to decide whether to port a mechanism or to change the target, for
example to independent replay of the leading open claims.
