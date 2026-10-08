# Structural routes to faster integer multiplication

**Status: research brief prepared; no experiments have been launched by this setup commit.**

The goal is a structural route to a conditional integer-multiplication exponent **kappa >= 1e-4**, with larger improvements as the continuing objective. This is not another campaign to optimize the last digits of the current public record.

## Start here

- [GOAL.md](GOAL.md): scientific objective, bottleneck analysis, and initial independent research tracks.
- [AGENTS.md](AGENTS.md): scoped agent behavior, parallel execution, evidence, and checkpoint policy.
- [input-manifest.json](input-manifest.json): initial source pins and their limitations.

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
