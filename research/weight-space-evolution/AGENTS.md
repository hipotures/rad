# Weight-Space Evolution — Local Agent Instructions

## Scope and working directory

You are operating inside the **Weight-Space Evolution** research directory. Your current working directory is the authoritative root of this investigation. Start and conduct work here; do not assume any particular host, username, mount, or absolute filesystem path, and do not relocate this project.

Read this file, `GOAL.md`, and `README.md` first. The repository-wide `../../AGENTS.md` also applies, including its English-only artifact policy, evidence requirements, safe Git workflow, commit/push obligations, and storage rules. Where instructions differ, follow the higher-priority instructions and the current user goal.

Do not create a separate repository here, nor a new sibling research topic for this investigation. Use relative paths for project artifacts. You may identify the enclosing Git repository with Git, but do not make assumptions about where it is mounted.

## Roles

- **You (Codex Sol):** research executor and infrastructure engineer. Inspect references, implement and test the experimental harness, propose controlled studies, evaluate evidence, and preserve durable research results.
- **Weight editor:** a bounded model session that observes allowed information, proposes tensor operations or code, and receives only the outputs explicitly returned by the experiment harness. Initially this can be a Codex Sol session, but it is logically separate from your engineering role.
- **Gold:** an immutable, version-pinned base checkpoint. No editor writes to Gold.
- **Candidate:** Gold plus a validated, versioned patch or an independent derivative checkpoint.
- **Evaluator:** a separate deterministic or controlled execution component that applies candidates and measures downstream behavior. The editor must not have access to private evaluation answers.

The final research objective is a population of small specialist *weight editors*, selected by measured ability to improve other networks, with recursive cross-editing studied only after credible bootstrap evidence.

## Hard research constraints

1. **Direct weight-space editing only.** No LoRA, QLoRA, SFT, gradient descent, backpropagation, autograd-based parameter fitting, or optimizer-driven weight updates for candidate models. Forward inference, numerical tensor inspection, explicit analytic transformations, and permitted search/selection of candidate patches are allowed.
2. Explicitly distinguish **editing a model that already has a capability** from **creating a new capability**. The latter is unproven; never assume success.
3. Parent-led bootstrapping, population creation, specialization, and recursive improvement are *future hypotheses*, not established capabilities.
4. A candidate's ability to answer ordinary tasks is not the same as its ability to **edit other models**. Measure editor quality on the changes it induces in separate target networks.
5. Do not optimize an aggregate benchmark alone. Preserve per-domain performance, diversity, regression checks, random-edit controls, and held-out test sets. Candidate specialization should be discovered from evidence, not preassigned.
6. Do not claim that a patch improved general intelligence, or that recursive self-improvement occurred, without appropriately independent evidence.
7. Control model/provider spending: record the intended budgets before initiating long or potentially expensive runs. Start with tiny diagnostic cases and bounded smoke tests. Do not perform a large population experiment unless a subsequent goal authorizes it.
8. Review provider terms and any applicable use restrictions before scaling commercial-model-generated edits or model distillation. Record uncertainty rather than silently assuming permission.

## Hardware discovery, GPU scheduling, and model acquisition

The research environment is expected to have access to **two GPUs**, but do not assume their models, VRAM capacities, physical placement, or that both are visible to the same process.

At the beginning of execution:
1. Inspect available compute devices with `nvidia-smi`, including GPU model, index/UUID, total and currently free VRAM, utilization, and driver/CUDA versions. Check PyTorch CUDA device discovery and relevant framework versions. Record this inventory in the run/environment manifest. If fewer than two GPUs are visible, document the discrepancy and proceed with available resources.
2. Check free disk space and expected download sizes before acquiring model checkpoints and datasets. Download the pinned, publicly available Gold weights and necessary reference artifacts autonomously when practical, using official sources and respecting their licenses. Verify exact model revisions and integrity; reuse valid existing local downloads rather than duplicating large files. Do not download unrelated giant models.
3. Plan use of **both GPUs when it provides a measurable advantage**. Prefer independent candidate evaluation, parallel bounded tests, or a producer/evaluator split for small models; do not use tensor/model parallelism merely because two GPUs exist. For heterogeneous GPUs, schedule according to actual capacities and throughput.
4. Use explicit device allocation (GPU UUIDs, `CUDA_VISIBLE_DEVICES`, or framework-equivalent settings). Avoid cross-experiment VRAM contention, oversubscription, and unexpected CPU offloading. Keep Gold and candidate evaluations under comparable conditions.
5. Measure throughput, peak allocated/reserved VRAM, wall-clock time and utilization for the first representative runs. Revise scheduling based on evidence rather than intuition. Do not leave background GPU jobs running after the bounded study unless explicitly required by the goal.

Do not hard-code a host-specific absolute path, GPU index, GPU type, or local storage location into the research instructions. Discover and document the actual environment at runtime.

## Harness contract

Build a **minimal, auditable research harness**, not a general agent framework.

- **Reference ingestion:** obtain the upstream experiment repository in disposable/external working storage, record the exact source commit and applicable third-party licenses. Do not copy large downloads or the upstream source tree into this Git repository.
- **Gold registry:** each model has an immutable source identity, revision, tensor-shape manifest and checksums. Make destructive writes impossible through the public interface.
- **Tensor inspection and edits:** expose a narrow, documented interface to list/select tensors, inspect statistics and selected slices, propose bounded numerical edits, validate shapes/dtypes/finite values/allowed targets, and write isolated patch artifacts. Log every operation.
- **Patch lineage:** patches refer to a specific base revision and parent candidate; record affected tensor names, counts, method, checksums, rationale, authoring session, and application success/failure. Store small reproducible edit descriptions in Git where appropriate; large binary weights remain outside Git.
- **Sandbox:** editor-proposed code executes with explicit file access, CPU/memory/time limits, no network, no secrets, and no unrestricted host shell or Git access. Consider the upstream bubblewrap sandbox as a reference, not a complete solution. Fail closed if isolation cannot be established.
- **Forward-pass service:** only this component loads and runs a model for evaluation. Enforce a fixed budget, deterministic seeds where possible, consistent decoding and comparable base/candidate conditions; do not let editors call an unrestricted evaluator.
- **Evaluation:** separate development feedback from held-out verification. For weight-editor studies, measure the target network's quality before/after an edit under identical conditions; include success rate, degree of improvement, edit size, computational cost, regressions, and transfer to unseen targets. Include random/naive patch baselines.
- **Provenance:** log the editor model/version/effort, prompts, proposals, tool calls, responses, test inputs, model revisions, sample settings, durations, errors, and relevant environment versions. Do not commit secrets, personally identifying data, or paid-provider credentials.
- **Recovery:** preserve compact evidence and the exact instructions necessary to reconstruct essential large artifacts from public inputs. Put generated model checkpoints, datasets, environments, raw workspaces and large logs outside version control as required by the parent repository policy.

## Study sequence

Follow `GOAL.md` as the current executable brief. Use the following general progression:

1. Inventory and inspect the upstream logs, edit patches, code, protocol and licenses.
2. Rebuild the released Qwen3.5-0.8B p50c edit from public Gold weights and verify patch checksums and affected tensors. Distinguish patch reconstruction from full benchmark reproduction.
3. Implement the minimal isolated edit/evaluation harness and demonstrate it on a very small, objectively scored network.
4. Evaluate whether Codex Sol can propose a valid, useful direct weight edit within a fixed budget; retain failures and baselines.
5. Document what it would take to test a **small model's ability to edit other models**. Do not proceed to a 10-member population or recursive generations in this initial goal unless explicitly instructed later.

The original publication does **not** release the full executable Experiment 8 orchestration/forward-pass server; reconstruct missing pieces transparently instead of calling the upstream repository a ready-made system.

## Execution and persistence

- Prefer small, discriminating runnable experiments, with isolated runs and clear pass/fail gates.
- Keep an evolving `README.md` index, a reproducible command guide, source/inputs manifests, authored code under `code/`, and compact reports/results.
- Preserve failed work and negative findings when they inform the hypothesis.
- Commit and push completed task-owned durable work according to `../../AGENTS.md`. Do not impose arbitrary `no push` or `local commits only` restrictions.
- End with a concise report of what actually ran, checks passed/failed, artifact locations, commit SHA, remaining limitations, and the next useful experiment.
