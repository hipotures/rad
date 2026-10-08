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

## First evidence and current directions

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

Live structural work includes cancellation-allowing reversible synthesis,
changed spectral interfaces, and a weight-five complex family. The latter uses
`f(t)=(t-1)(t-3)/8` on five-subset intersections, keeping binary label dimension
h while changing central features and side corrections. Efficient paid side
circuits and the complete child distribution remain open; its optimistic
component envelope is not an exponent certificate.

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
