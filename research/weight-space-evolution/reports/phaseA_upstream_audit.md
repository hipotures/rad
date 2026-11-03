# Phase A — Upstream reference and reproducibility audit

Date: 2026-11-03. Upstream: <https://github.com/RikiyaT/lm_understand-logs> at
`4d09ba6d6a7e891dd8063974dfe81b3d78e3494f` (2026-10-29). Article:
<https://rikiyat.github.io/blog/weight-space-programming/> (not re-fetched; the upstream README and logs are the
primary evidence used here).

## 1. Licenses (from upstream `LICENSE`)

| Content | License | Consequence here |
|---|---|---|
| Logs, data, networks (incl. exp5 `hand.npz`, exp8 `edit/`) | CC BY 4.0 | May be used with attribution; we use exp5 Seaquest `hand.npz` as Gold and record its source. Not copied into Git. |
| Upstream scripts (`harness/`, `exp8_math/code/`, ...) | MIT | `mathqa.py` is executed from the pinned checkout; `harness/sandbox.py` was used as a reference (our sandbox is a re-implementation). |
| MinAtar source quoted in exp5 prompts | GPL-3.0 | Shown to the editor at runtime from external storage; not committed. |
| Benchmark content (MATH, GSM8K, ...) | Own licenses | Not committed; MATH-500 kept in external storage. |

Commercial-model terms: no paid model was called in this goal. The editor in Phase C was a Claude Code subagent
under the user's existing session; no distillation or redistribution of model outputs beyond these research logs.

## 2. Inventory (what the release contains)

| Folder | Relevant contents | Executable here? |
|---|---|---|
| `exp8_math/` | Qwen3.5-0.8B: 3 runs (p10c, p25c, p50c) with every turn's prompt/answer, `tool_calls.jsonl` (all Python runs and forward requests), `requests/` (forward-pass summaries), `edit/` exact diffs, `eval/` per-benchmark scores and per-problem results, `code/` (grader, evaluation, checkpoint and diff tools), `practice/` (the editor's practice sets), Gemma 3 270M follow-up | Edits and grader: yes. Forward-pass server / agent harness: **not released** |
| `exp4_fix_car/` | One-shot Kinetix repair, base and edited actor `.npz`, eval JSON | Needs Kinetix/JAX environment (not attempted) |
| `exp5_write_from_scratch/` | Hand-written MinAtar networks (Breakout/Seaquest/Asterix), prompts, eval JSON | **Yes** — used for Phase C (Gold + evaluator validation) |
| `exp6_go_from_scratch/` | 9x9 Go networks, pass logs, eval | Needs pgx + opponents (not attempted) |
| `harness/` | `sandbox.py` (bubblewrap runner), `codex_config.toml` (all Codex tools off), neutral instructions | Reference only |

Missing for exp8 (stated upstream): the agent loop, the persistent kernel, the forward-pass server (generation with
activations, teacher-forced reads), `weightenv` modules imported by `practice35.py`/`mathqa.py` (`mcqa`), the IFEval
and multiple-choice graders, the runs' work folders. Our harness reconstructs only the minimal pieces needed here.

## 3. How p50c was produced (from `runs/p50c/message.txt`, `notices/`, `state.json`, `final_answer.md`)

**Visible to the editor (gpt-6-astra, Codex CLI, effort `max`):**
- All Qwen3.5-0.8B weights read-only, a persistent CPU Python kernel (numpy/scipy/sklearn/torch-CPU, gradients
  disabled), up to 300 code runs (80 used), `save_edit` with refusals (final norm, embeddings/LM head, uniform scaling).
- Practice problems with answers: GSM8K train (7,469), MATH train (7,275), AIME 1983–2023 (714), decontaminated
  against all evaluation sets by 13-gram/normalized-text matching (`code/practice35.py`, `practice/stats.json`).
- **The full evaluation protocol** (chat template, thinking on, prompt suffix, sampling, 32,768-token limit), and the
  names of the target benchmarks (MATH-500, GSM8K) — but not their problems.
- 50 forward passes: generation (≤512 answers, eval sampling, optional paired original/edited, optional activations)
  or teacher-forced reads (≤1,024 texts). 69 requests were issued; failed requests did not count.
- Experimenter notices during the run (`notices/001`, `002`): pass size advice, tool corrections, and a changed
  submission rule ("submit the best edit ... even if not significant").

**Held out:** MATH-500, GSM8K test, AMC23, Minerva, OlympiadBench, MMLU-Pro, GPQA, IFEval problems and all final
scores. Evaluation ran after the session (vLLM, 4 samples on MATH-500).

**What the edit is:** layers 15 and 19 `mlp.down_proj.weight` (1024×3584 each), 64 columns per tensor (the MLP
neurons that write a measured "loop/repetition" direction most), with that direction subtracted. Our independent
rebuild finds the per-tensor delta to be rank-1 (≥99.999% of its energy in one singular direction), consistent with
the description. 131,072 touched weights; 130,188 differ after bfloat16 rounding.

**Astra's own development evidence (practice problems, not benchmarks):** paired gain +49.8 pp (SE 1.5) on 1,152
held-out practice items; 579 rescues vs 5 losses; **576 of 579 rescues were originally truncated answers, and
accuracy on originally finished answers was unchanged (93.9% → 93.9%)** (`state.json` final output). Astra's notes
also mention dose-response, layer isolation and a norm-matched random control.

## 4. Reconstruction (this repository, run `runs/20261103T-p50c-reconstruction/`)

| Check | Result |
|---|---|
| Gold file sha256 = HF LFS sha256 (`04b1c301…`) | pass |
| Upstream manifest base hashes of edited tensors | pass (p10c 30 tensors, p25c 1, p50c 2) |
| Rebuilt edited-tensor hashes = evaluated-checkpoint hashes | pass (all three runs) — with our independent rebuild **and** upstream `apply_edit.py` |
| p50c changed entries / columns / rows | 65,260 / 64 / 1,024 and 64,928 / 64 / 1,023 = manifest (total 130,188) |
| Round trip through WSE patch format (`p-4b2661ed6f35`) | pass |
| Full candidate checkpoint: edited tensors match, sampled untouched tensors identical | pass |
| Gold registry still read-only and hash-valid after all operations | pass |

Minor discrepancy: our float64 `relative_change` differs from the manifest's in the 6th significant digit
(0.106362 vs 0.106360) — attributable to accumulation precision; the bit-level hashes match.

**This is a patch reconstruction, not a benchmark reproduction.** See section 5 for the bounded behavioural check.

## 5. Bounded behavioural check (run `runs/20261103T-p50c-math500-bounded-r2/`)

Upstream `think35` protocol on the text-only exports, MATH-500 rows[::5] (100 problems) × 2 samples, Gold and p50c on
separate RTX 4090s, upstream `mathqa.py` grading (math-verify 0.9.0):

| Model | Ours | Upstream, same 100 problems | Upstream, full 500 | Ours cut / upstream cut |
|---|---|---|---|---|
| Gold | 6.5% (CI 2.5–11.0) | 6.2% | 7.9% | 95.0% / 93.0% |
| p50c | 47.5% (CI 39.0–56.0) | 45.0% | 48.1% | 33.5% / 33.1% |
| p50c − Gold (paired) | +41.0 pp (CI 33.0–49.0) | +38.75 pp | +40.2 pp | |

**Partial reproduction confirmed:** the reconstructed edit reproduces the published MATH-500 behaviour change within
sampling error on this subset (other benchmarks not re-run). An earlier attempt was interrupted by a host restart
(`runs/20261103T-p50c-math500-bounded/`).

## 6. Interpretation and caveats

- **Edit vs capability.** The upstream evidence (Astra's own strata) indicates that p50c mainly suppresses a
  degenerate repetition loop that prevented the 0.8B model from finishing: when the unedited model finishes, it is
  already right about as often as the edited one. This is best classified as *editing a model that already has the
  capability* (unblocking it), not as *creating new capability*.
- **Single runs, selection.** Each budget has one run in the post. The results table also lists other prompt
  versions/budgets with no edit or smaller gains (e.g. v3 5 passes: no edit; v4 10 passes: no edit; v4 25 passes:
  same as p25c). The 50-pass outcome is n = 1 and should not be treated as a reliable success rate.
- **Protocol knowledge.** The editor knew the exact evaluation protocol and target benchmarks (not their items); an
  edit targeted at the 32k-token truncation behaviour of that protocol is legitimate but protocol-specific.
- **Unreleased components.** Without the forward-pass server and kernel, the editing session itself cannot be
  re-run; only its output (the edit) and its records can be checked.
