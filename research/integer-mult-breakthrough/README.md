# Structural routes to faster integer multiplication

**Status: active parallel structural research, started 2026-10-08 21:01 UTC.**

The verified isolated worktree is `/home/user/DEV/rad-breakthrough`, starting
from `cb2ae8734a58eae09432b307409b5553a19d79db`. The coordinator and three
autonomous agents are investigating four independent tracks. Their first
discriminators have run; there is no new claim of kappa >= 1e-4.

The goal is a structural route to a conditional integer-multiplication exponent **kappa >= 1e-4**, with larger improvements as the continuing objective. This is not another campaign to optimize the last digits of the current public record.

## Start here

- [GOAL.md](GOAL.md): scientific objective, bottleneck analysis, and initial independent research tracks.
- [AGENTS.md](AGENTS.md): scoped agent behavior, parallel execution, evidence, and checkpoint policy.
- [input-manifest.json](input-manifest.json): initial source pins and their limitations.
- [Hypothesis portfolio](reports/hypothesis-portfolio.md): bottlenecks, leverage,
  changed assumptions and continuation criteria for the live tracks.
- [Reproduction](reproduce.md) and [artifact recovery](artifact-manifest.json).

## Evidence and current directions

The inherited assembly's exact arithmetic ceiling and the complete frozen
moments both rule out reaching 1e-4 through parameter polishing or positive
relabeling of unchanged children. The complex track reported a rigorous root
bracket `71744621/10^12 < b < 71744622/10^12`, only about 0.062% above its
published saving. The transfer checker independently replays that bracket.
These facts constrain their stated fixed models, not other algorithms.

- [Positive type mixing](reports/transfers/positive-type-mixing.md): complete
  row moments exceed one at saving 1e-4; unequal positive potentials and
  varying complete levels cannot repair that certificate.
- [Deferred normalization](reports/transfers/deferred-normalization.md): exact
  carry and padding counterexamples, plus a finite positive redundant-format
  identity. A bilinear multilevel spectral interface remains a hypothesis.
- [Gaussian-dyadic unitary restrictions and escapes](reports/obstructions/unitary-dyadic-and-escapes.md):
  two-coordinate unitary rows are monomial or balanced; an exact paid
  three-coordinate macro escapes that angle restriction. This auxiliary model
  does not bound the original nonunitary bulk network.
- [Weight-five mixed pair centers](reports/complex/five-subset-mixed-pair.md)
  and [general odd-weight kernels](reports/obstructions/odd-weight-kernel-family.md):
  exact scalar components change the label/feature geometry. At h20 the
  optimistic necessary side-role budget is about 31.42 roles per source.
  A [joint weighted tree](reports/complex/weighted-tree-and-frame-obstruction.md)
  instead uses about 103.33 and has nested-frame obstructions. This redirects
  the search toward different circuits and chronology.
- [Independent component review](reports/transfers/five-subset-component-review.md):
  paid complete-stream copied reads survive; the new scatter needs an
  eight-bit denominator allowance and updated endpoint phases. The old guard
  and a full native compiler require separate verification.
- [Literal auxiliary dirty scalar words](reports/synthesis/global-incidence-first-discriminators.md),
  [frozen native ceiling](reports/synthesis/frozen-native-ledger-ceiling.md)
  and [stationary joint-frame obstruction](reports/synthesis/static-joint-frame-obstruction.md):
  scalar cancellations are exact, but stationary compressed address frames
  cannot realize the proposed target intertwiners. SMT timeouts are UNKNOWN.
- [Shared dynamic scatter factors](reports/synthesis/shared-twist-factorization.md):
  a literal arbitrary-dirty auxiliary word pays 2(h+v) rank-one permutations
  against 6v rank-two permutations in a specified unshared implementation.
  Endpoint absorption and a complete native cost ledger are the next tests.
- [Same-width row/depth budgets](reports/transfers/same-width-row-budget.md):
  an exact toy recurrence demonstrates terminating same-width children under
  complete contracting moments. A real native phase program and its changed
  precision/layout obligations remain open.

Live structural work includes cancellation-allowing reversible synthesis,
changed spectral interfaces, and a weight-five complex family. The latter uses
`f(t)=(t-1)(t-3)/8` on five-subset intersections, keeping binary label dimension
h while changing central features and side corrections. Efficient paid side
circuits and the complete child distribution remain open; its optimistic
component envelope is not an exponent certificate. Arbitrary symmetric
quadratic phase frames are a new hypothesis for broadening eligible edge
changes. The old library already contains alternating projector phases;
their identity alone is not a new discovery or a larger saving.

Registered CI checks replay only their stated finite arithmetic and semantic
controls. There is no formal proof package or external human review.

Repository: `hipotures/rad`.
Branch: `research/integer-mult-breakthrough-20261008`.
Working directory within the checkout: `research/integer-mult-breakthrough/`.

The branch is based on CPU checkpoint `def95e9c12f62a41fc7a50af13d5dcc87ce13d79` so previous code, certificates, and negative results remain available without merging live work. Old results are read-only references. This setup does not stop running processes, alter the previous campaign, or modify the other machine.

Expected host: approximately 12 CPU slots and 62 GiB RAM, no GPU. Confirm actual resources at execution time. Experiments normally receive about four CPU workers; four or more independent jobs may overlap. There is no utilization quota. Memory safety, genuine scientific diversity, and measurable evidence matter more than full CPU occupancy.

## Launch instruction for an agent

From this branch and this directory:

> Read AGENTS.md and GOAL.md, then execute this new exploratory campaign. Start independent research tracks and their first discriminating experiments. Use the previous CPU work only as read-only evidence, preserve its open proof boundaries, and continue until explicitly stopped.

Do not switch a checkout still being written by the old coordinator. Stop that session safely or use a separate worktree. A new branch is not a command to terminate another process.

All authored artifacts are in English. Public publication requires separate authorization; scientific commits and pushes to this research branch are authorized.
