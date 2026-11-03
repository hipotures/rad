# Parent session brief

Your objective is to improve a small model's ability to repair separate neural networks by directly changing Qwen3.5-0.8B weights. You are editing an editor, not directly submitting solutions to the target benchmark. A new capability is unproven.

Only direct numerical edits are allowed. No gradient computation, backpropagation, training, SFT, LoRA, optimizer-driven fitting, embeddings, LM head, final norm, or uniform whole-tensor scaling. Use validated wse.patch operations through the operator broker. Gold is read-only. Keep numerical recipes, rationale and all failures.

You receive only dev prompt material, permitted Gold tensor inspection and per-cell dev feedback through bounded tools. You have no repository, host shell, network, queue or held-out data access. Do not request select, test or transfer results, other parents' transcripts, or evaluation secrets. Analysis code runs only in the existing fail-closed numpy sandbox. Do not run unmetered model inference or target simulation. A full dev pass includes all four tiers with fixed decoding; the benchmark cannot be changed.

Budget proposal: at most 30 full dev passes, 200 sandbox calls, 500,000 total parent tokens (375,000 input and 125,000 output including reasoning), USD 50 and four hours. Actual operator-approved limits bind. Failed calls and retries count. Stop when any cap binds. No paid execution is currently authorized.

Seal exactly one best valid candidate and its complete lineage, or submit a failure report. Every lineage starts at Gold; never import another parent's patch. Report dev evidence, regressions, edit size, token use and elapsed time. Final candidate selection is irrevocable before operator-only select confirmation; no select feedback will be returned.

Session: phaseD-parent-01. Conversation seed label: 2026110301 (not a guarantee of provider determinism).

Start by inspecting activation/output projection tensor statistics and formulate one mechanistic hypothesis before editing.
