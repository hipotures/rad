# IQ3_S expert-residency laboratory

Primary reference: frozen Strata 6f32ec070f23ced9f50e704d854d775da52591ab, layer split K=25, PCIe fraction 0.28. Only 32768 and 131072 total-context profiles are in scope. Existing weights and campaigns remain read-only.

Read GOAL.md, deadline.json and STATUS.json before continuing. Experiment protocols, attempts, negatives and runnable variants are retained separately. No automatic deployment, push or PR.

The main report is [report.md](report.md); clean results with raw links are [summary.json](summary.json) and [summary.csv](summary.csv). The experiment journal is [experiments.jsonl](experiments.jsonl), with bounded family dispositions in [candidate-ledger.json](candidate-ledger.json). [launch-index.md](launch-index.md) maps every preserved runtime variant to its exact executable, source, configuration and replay commands.

Primary recommendation: `PROMISING_NEEDS_MORE_WORK`. The existing `STRATA_POOL_SPIN_US=100` setting is the strongest scoped follow-up on the unchanged layer-split control binary. It produced 178.5/154.0 tok/s with 4,096 output tokens at 32,768/131,072 total capacity and sharply reduced spinning CPU. Separate serial batches and increased CPU-positive wakeup costs limit the performance conclusion. No live residency predictor or portable policy speedup was established, and no normal user launcher was switched.

Saved prompts have 28,378–28,381/126,715–126,719 effective input tokens. They leave room for 4,096 output tokens and the recorded speculative reserve inside the actual context limits. Historical larger prompts/runtimes are not fresh A/B controls.

Example manual launch of the preserved experimental option, one server at a time:

```bash
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/pool-wait-v1/start-32k.sh --port 18132
# Use the 128K command instead of the 32K command, never both concurrently.
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/pool-wait-v1/start-128k.sh --port 18132
/srv/ai/research/iq3s-residency-20261004T230051Z/variants/pool-wait-v1/stop.sh
```

These commands print frozen configs, verify source/binary hashes and serve privately on 127.0.0.1. They never update/rebuild or download the model. Diagnostic/unsafe variants are explicitly labeled in the index. For later measured reproduction after the recorded deadline, use a new experiment directory plus `--reproduction`; original attempts refuse overwrite.

Build/compiler/CUDA/driver/topology and pinned dependencies are in `git/`. [git/final-provenance.json](git/final-provenance.json) verifies retained binaries/patches and model metadata. [git/artifact-inventory.jsonl](git/artifact-inventory.jsonl) includes large Git-ignored raw/traces/checkpoints remaining on disk. [analysis/final-audit.json](analysis/final-audit.json) records the checks and explicit limits, including four original fixture/VM test failures. No all-tests-pass or zero-instrumentation-overhead claim is made.
