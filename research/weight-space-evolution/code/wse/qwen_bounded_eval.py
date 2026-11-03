"""Bounded behavioral check of a Qwen3.5-0.8B checkpoint (Gold or a reconstructed candidate) on a MATH-500 subset.

Follows the upstream exp8 'think35' protocol (vLLM, chat template with thinking on, prompt = problem + Qwen's boxed
instruction, temperature 0.6, top_p 0.95, top_k 20, presence penalty 1.5, max 32,768 new tokens, seed 0, last
\\boxed{} graded by math-verify 0.9.0) and reuses upstream exp8_math/code/mathqa.py for prompt/extraction/grading.

    python -m wse.qwen_bounded_eval --ckpt <dir> --math500 <test.jsonl> --upstream-code <exp8_math/code> \
        --stride 5 --samples 2 --out <results dir> --raw <raw dir>

This is a reduced-sample check (subset, fewer samples), not a reproduction of the full published evaluation.
"""
import argparse
import gzip
import importlib.util
import json
import os
import sys
import time
import types
from pathlib import Path


def load_mathqa(code_dir):
    stub = types.ModuleType("mcqa")          # mathqa imports an unreleased helper only for loop diagnostics
    stub.loop_signals = lambda *a, **k: {}
    sys.modules.setdefault("mcqa", stub)
    spec = importlib.util.spec_from_file_location("upstream_mathqa", os.path.join(code_dir, "mathqa.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--math500", required=True)
    ap.add_argument("--upstream-code", required=True)
    ap.add_argument("--stride", type=int, default=5)
    ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--max-tokens", type=int, default=32768)
    ap.add_argument("--gpu-mem", type=float, default=0.85)
    ap.add_argument("--shard", default=None, help="i/k: keep subset problems i, i+k, ... (balance work across GPUs)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw", required=True)
    a = ap.parse_args(argv)
    Q = load_mathqa(a.upstream_code)
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    import torch
    import vllm

    rows = [json.loads(l) for l in open(a.math500)][:: a.stride]
    if a.shard:
        i, k = map(int, a.shard.split("/"))
        rows = rows[i::k]
    tag = a.label + (f"_s{a.shard.replace('/', 'of')}" if a.shard else "")
    tok = AutoTokenizer.from_pretrained(a.ckpt)
    prompts = [tok.apply_chat_template([{"role": "user", "content": Q.build_prompt(r["problem"])}], tokenize=False,
                                       add_generation_prompt=True, enable_thinking=True) for r in rows]
    sampling = {"temperature": 0.6, "top_p": 0.95, "top_k": 20, "presence_penalty": 1.5, "max_tokens": a.max_tokens,
                "seed": 0}
    t0 = time.time()
    llm = LLM(model=a.ckpt, dtype="bfloat16", gpu_memory_utilization=a.gpu_mem, max_model_len=a.max_tokens + 2048,
              seed=0)
    t_load = time.time() - t0
    outs = llm.generate(prompts, SamplingParams(n=a.samples, **sampling))
    t_gen = time.time() - t0 - t_load
    per, ok, tot, cut, toks, noans = [], 0, 0, 0, 0, 0
    Path(a.raw).mkdir(parents=True, exist_ok=True)
    with gzip.open(Path(a.raw) / f"{tag}_generations.jsonl.gz", "wt") as raw:
        for r, o in zip(rows, outs):
            c = []
            for k, s in enumerate(o.outputs):
                pred, _ = Q.extract(s.text)
                good = Q.is_correct(pred, r["answer"])
                c.append(int(good))
                cut += s.finish_reason == "length"
                noans += pred is None and s.finish_reason != "length"
                toks += len(s.token_ids)
                raw.write(json.dumps({"id": r["unique_id"], "sample": k, "finish": s.finish_reason,
                                      "tokens": len(s.token_ids), "pred": pred, "answer": r["answer"],
                                      "correct": int(good), "text": s.text}) + "\n")
            per.append({"id": r["unique_id"], "correct": c, "cut": [int(s.finish_reason == "length") for s in o.outputs],
                        "tokens": [len(s.token_ids) for s in o.outputs]})
            ok += sum(c)
            tot += len(c)
    res = {"label": a.label, "shard": a.shard, "ckpt": a.ckpt, "protocol": "upstream think35 (reduced)", "sampling": sampling,
           "subset": f"MATH-500 test.jsonl rows[::{a.stride}]", "problems": len(rows), "samples": a.samples,
           "acc": ok / tot, "ok": ok, "total": tot, "cut_share": cut / tot, "mean_tokens": toks / tot,
           "no_answer_finished": noans, "load_s": round(t_load, 1), "generate_s": round(t_gen, 1),
           "gen_tokens_per_s": round(toks / t_gen, 1),
           "gpu_memory_note": "vLLM's engine runs in a separate process; see nvidia_smi.csv for device memory",
           "versions": {"vllm": vllm.__version__, "torch": torch.__version__},
           "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES")}
    Path(a.out).mkdir(parents=True, exist_ok=True)
    (Path(a.out) / f"{tag}_summary.json").write_text(json.dumps(res, indent=1))
    (Path(a.out) / f"{tag}_per_problem.json").write_text(json.dumps(per))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
