"""Phase D pilot: measure an editor LM (default E0 = Qwen3.5-0.8B text export) and non-agent baselines on F1-F3 tiers.

    python -m wse.editor_pilot --model <dir> --out <run dir> --raw-dir <dir> [--per-family 16] [--samples 4]
        [--thinking 0|1] [--max-tokens 4096] [--gpu-mem 0.85]

Run with the vLLM environment (it needs only numpy besides vLLM). Instances come from the deterministic 'pilot' split
(never used for dev/test of a gate run). Every sample is scored independently (no best-of-k). Invalid or missing edits
count as no-ops (recovery 0) and are reported separately as validity.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np

from . import editor_tasks as K
from . import targets as T

TIERS = ("T0", "T1", "T2")
_I = r"(\d{1,2}|:|\d{1,2}:\d{1,2})"
_N = r"-?\d{1,3}(\.\d{1,4})?"
_OP = r" (=|\+=|-=|\*=) "
_ST = (rf"(b[123]\[\d{{1,2}}\]{_OP}{_N}|W[123]\[{_I}, {_I}\]{_OP}{_N}|"
       rf"swap b[123]\[{_I}\] b[123]\[{_I}\]|swap W[123]\[{_I}, {_I}\] W[123]\[{_I}, {_I}\])")
DSL_REGEX = rf"```edit\n({_ST}\n){{1,8}}```"


def baselines(insts, rng):
    rows = []
    for inst in insts:
        h = K.heuristic_best(inst)
        r_h = K.evaluate_answer(inst, "T2", h, {}) if h else {"valid": False, "recovery": 0.0, "delta": 0.0}
        r_o = K.evaluate_answer(inst, "T2", K.oracle_edit(inst), {})
        rnd = [K.evaluate_answer(inst, "T2", K.random_edit(inst, rng, 4, 0.5), {})["recovery"] for _ in range(4)]
        rows.append({"id": inst["id"], "family": inst["family"], "heuristic": r_h["recovery"], "oracle": r_o["recovery"],
                     "random_mean": float(np.mean(rnd))})
    return rows


def summarize(rows, key="recovery"):
    out = {}
    for fam in sorted({r["family"] for r in rows}):
        for tier in sorted({r["tier"] for r in rows}):
            s = [r for r in rows if r["family"] == fam and r["tier"] == tier]
            if s:
                v = np.array([r[key] for r in s], float)
                out[f"{fam}/{tier}"] = {"n": len(s), "mean_recovery": float(v.mean()),
                                        "se": float(v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else None,
                                        "valid_rate": float(np.mean([r["valid"] for r in s])),
                                        "full_repair_rate": float(np.mean(v >= 0.9))}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--label", default="E0")
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw-dir", required=True)
    ap.add_argument("--per-family", type=int, default=16)
    ap.add_argument("--samples", type=int, default=4)
    ap.add_argument("--thinking", type=int, default=0)
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--gpu-mem", type=float, default=0.85)
    ap.add_argument("--constrained", type=int, default=0,
                    help="1: grammar-constrained output (T0: one of 'ANSWER: A..D'; T1/T2: a ```edit block of 1-8 DSL "
                         "statements); non-thinking mode only (design baseline 5, 'format-fixed' editor)")
    ap.add_argument("--engine-json", default="{}",
                    help="extra vllm.LLM keyword arguments (JSON), e.g. a profile from configs/vllm_perf/profiles/; "
                         "default {} keeps the original pilot engine settings. Not bit-identical to the default "
                         "engine when scheduling/kernels change (see runs/20261103T-vllm-perf-32k/report.md)")
    a = ap.parse_args(argv)
    out, raw = Path(a.out), Path(a.raw_dir)
    (out / "results").mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)
    assert not (a.constrained and a.thinking), "constrained decoding is defined for non-thinking mode only"
    tag = f"{a.label}_think{a.thinking}" + ("_constrained" if a.constrained else "")
    assert not (out / "results" / f"{tag}_summary.json").exists(), "never overwritten"
    t0 = time.time()
    insts = [T.build(f, "pilot", i) for f in T.FAMILIES for i in range(a.per_family)]
    jobs = []
    for inst in insts:
        for tier in TIERS:
            rng = np.random.default_rng([inst["seed"] % (2 ** 32), TIERS.index(tier)])
            prompt, meta = K.render(inst, tier, rng)
            jobs.append((inst, tier, prompt, meta))
    build_s = time.time() - t0

    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    tok = AutoTokenizer.from_pretrained(a.model)
    texts = [tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True,
                                     enable_thinking=bool(a.thinking)) for _, _, p, _ in jobs]
    sp = (dict(temperature=0.6, top_p=0.95, top_k=20) if a.thinking else dict(temperature=0.7, top_p=0.8, top_k=20))
    sps = [SamplingParams(n=a.samples, max_tokens=a.max_tokens, seed=0, **sp)] * len(jobs)
    if a.constrained:
        from vllm.sampling_params import StructuredOutputsParams
        sps = [SamplingParams(n=a.samples, max_tokens=a.max_tokens, seed=0, **sp,
                              structured_outputs=StructuredOutputsParams(
                                  choice=[f"ANSWER: {c}" for c in "ABCD"]) if tier == "T0" else
                              StructuredOutputsParams(regex=DSL_REGEX)) for _, tier, _, _ in jobs]
    engine = dict(model=a.model, dtype="bfloat16", gpu_memory_utilization=a.gpu_mem,
                  max_model_len=a.max_tokens + 3072, seed=0)
    engine.update(json.loads(a.engine_json))
    llm = LLM(**engine)
    t1 = time.time()
    outs = llm.generate(texts, sps)
    gen_s = time.time() - t1

    rows, raw_rows = [], []
    for (inst, tier, prompt, meta), o in zip(jobs, outs):
        for k, c in enumerate(o.outputs):
            txt = c.text
            ans = txt.split("</think>")[-1] if a.thinking else txt
            r = K.evaluate_answer(inst, tier, ans, meta)
            rows.append({"id": inst["id"], "family": inst["family"], "tier": tier, "sample": k,
                         "gen_tokens": len(c.token_ids), "truncated": c.finish_reason == "length", **r})
            raw_rows.append({"id": inst["id"], "tier": tier, "sample": k, "prompt": prompt if k == 0 else None,
                             "output": txt, **{x: r[x] for x in ("valid", "error", "recovery")}})
    base = baselines(insts, np.random.default_rng(12345))
    summ = {"label": a.label, "model": a.model, "engine_overrides": json.loads(a.engine_json), "thinking": a.thinking, "samples": a.samples,
            "per_family": a.per_family, "max_tokens": a.max_tokens, "sampling": sp,
            "build_s": round(build_s, 1), "generation_s": round(gen_s, 1),
            "gen_tokens_total": int(sum(r["gen_tokens"] for r in rows)),
            "truncated_rate": float(np.mean([r["truncated"] for r in rows])),
            "editor": summarize(rows),
            "baselines": {f: {k: float(np.mean([b[k] for b in base if b["family"] == f]))
                              for k in ("heuristic", "oracle", "random_mean")} for f in T.FAMILIES},
            "t0_chance_recovery_note": "T0 chance = 1/4 of the oracle recovery plus 3/4 of the distractors' recovery"}
    (out / "results" / f"{tag}_summary.json").write_text(json.dumps(summ, indent=1))
    (raw / f"{tag}_per_sample.json").write_text(json.dumps(rows))   # row-level: raw dir (packed as evidence)
    (out / "results" / "baselines_per_instance.json").write_text(json.dumps(base))
    with open(raw / f"{tag}_generations.jsonl", "w") as f:
        for r in raw_rows:
            f.write(json.dumps(r) + "\n")
    print(json.dumps({k: summ[k] for k in ("generation_s", "gen_tokens_total", "truncated_rate", "editor", "baselines")},
                     indent=1))


if __name__ == "__main__":
    main()
