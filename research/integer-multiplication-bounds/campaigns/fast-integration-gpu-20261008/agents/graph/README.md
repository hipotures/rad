# Graph, controller and copied-center search

This branch of the GPU campaign tests new computation DAGs and retained
controller assignments against the actual mixed-width two-stage moment.
The initial historical h53 lead was superseded before execution by public
PR36 and PR37. Their copied-center schedules and source attribution are
retained as inputs, not claimed as discoveries here.

Allocated compute: eight single-thread CPU workers. GPU use requires the
coordinator's separate allocation. This agent performs no Git publication.

- [Hypotheses and progress](hypotheses.md)
- [Input provenance](input-manifest.json)
- [Execution and recovery](reproduce.md)

Status: small exact producer/controller discriminators, followed by
parallel graph rewrite and moment-sensitive matching searches.
