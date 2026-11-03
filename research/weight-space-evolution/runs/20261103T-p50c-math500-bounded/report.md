# Bounded MATH-500 check, Gold vs p50c — report

**Outcome: not completed (interrupted).** No scores were produced.

- Protocol: upstream `think35` (vLLM 0.33.0, text-only export, thinking on, T 0.6 / top_p 0.95 / top_k 20 /
  presence 1.5, ≤ 32,768 tokens, seed 0), MATH-500 rows[::5] (100 problems) × 2 samples; Gold on GPU0, p50c on GPU1
  (`code/scripts/run_p50c_math500_bounded.sh`).
- First attempt failed immediately: vLLM loaded the full multimodal release and required image-processor files;
  fixed by evaluating the upstream-style text-only export (`wse.text_export`).
- Second attempt ran ~20 min (both GPUs at 100%, 21.8 GiB each; p50c had completed 58/200 generations at
  ≈ 1,000 tok/s aggregate, Gold 2/200 because almost all Gold samples run to the 32k limit) and was stopped by the
  operator before a host restart. Results are written only at the end, so nothing was saved.
- Observation only (not a result): p50c generations were completing steadily while Gold's were not, consistent with
  the published cut-off shares (Gold 93.0% vs p50c 33.1% cut at 32k tokens).
- Re-run: `code/scripts/run_p50c_math500_bounded.sh` (≈ 40–60 min on 2 GPUs); write partial results incrementally
  in a future version.
