"""Offline vLLM benchmark for Qwen3.5-0.8B (BF16) on one GPU: one engine configuration, a list of workloads, repeats.

    CUDA_VISIBLE_DEVICES=<uuid> python -m bench.vllm_bench --model <dir> --name <config name> \
        --engine '{"max_num_batched_tokens": 8192}' --workloads A,B,D,E --repeats 3 --out <raw dir>

Measures the workload the laboratory actually runs: the offline `vllm.LLM` class with `generate()` (no HTTP server).
Every workload is executed once as warm-up (discarded, `rep = -1`) and then `--repeats` times. Startup (engine
construction, including compilation and CUDA-graph capture) is timed separately and never included in token rates.

Prompts for A/B/D/E are fixed token IDs (seeded, drawn from ordinary vocabulary ids), so every configuration sees
identical inputs and exact context lengths. Decoding is greedy with `ignore_eos`, so output length is exactly the cap.
Workload C renders the real Phase D pilot prompts (wse.editor_tasks) with the pilot's chat template and sampling.

Per-request timings come from vLLM's RequestStateStats (engine-core monotonic timestamps):
  TTFT = first_token_ts - queued_ts (queueing + prefill), decode rate = (n_out - 1) / (last_token_ts - first_token_ts).
Prefix-cache hits and preemptions are deltas of the engine's Prometheus counters around each repeat.
GPU memory/utilisation/power/SM clock are sampled with NVML every 50 ms in a side thread.

Output: <out>/<name>.jsonl (one row per workload repeat) and <out>/<name>.meta.json (startup, versions, engine args).
"""
import argparse
import hashlib
import json
import os
import statistics
import sys
import threading
import time
from pathlib import Path

import numpy as np

CTX = 32768
VOCAB_LO, VOCAB_HI = 1000, 150000          # ordinary BPE ids of the Qwen3.5 vocabulary (no special tokens)


def ids(seed, n):
    return np.random.default_rng(seed).integers(VOCAB_LO, VOCAB_HI, n).tolist()


def wl_seed(*parts):
    return int.from_bytes(hashlib.sha256("/".join(map(str, parts)).encode()).digest()[:8], "little")


# ---------------------------------------------------------------- workloads
# Each workload returns a list of "cases"; a case is one generate() call: (case_name, prompts, sampling dicts, extra).

def workload_A():
    return [(f"A_in{n}_out128", [ids(wl_seed("A", n), n)], [dict(max_tokens=128)], {"in": n, "out": 128, "conc": 1})
            for n in (4096, 16384, 30720, 32640)]


def workload_B():
    return [(f"B_in{n}_out2048", [ids(wl_seed("B", n), n)], [dict(max_tokens=2048)], {"in": n, "out": 2048, "conc": 1})
            for n in (16384, 30720)]


def workload_D(levels=(1, 2, 4, 8, 16, 32), shapes=((30720, 1024), (4096, 512))):
    out = []
    for n_in, n_out in shapes:
        for c in levels:
            out.append((f"D_in{n_in}_out{n_out}_c{c}", [ids(wl_seed("D", n_in, i), n_in) for i in range(c)],
                        [dict(max_tokens=n_out)] * c, {"in": n_in, "out": n_out, "conc": c}))
    return out


def workload_E(n_req=16, total=16384, shared=12288, out_len=64):
    uniq = [ids(wl_seed("E-unique", i), total) for i in range(n_req)]
    same = [ids(wl_seed("E-same"), total)] * n_req
    pre = ids(wl_seed("E-prefix"), shared)
    part = [pre + ids(wl_seed("E-suffix", i), total - shared) for i in range(n_req)]
    sp = [dict(max_tokens=out_len)] * n_req
    return [(f"E_{k}_n{n_req}_in{total}", p, sp, {"in": total, "out": out_len, "conc": n_req, "shared": s})
            for k, p, s in (("unique", uniq, 0), ("identical", same, total), ("shared12k", part, shared))]


def workload_C(model, per_family=16, caps=(64, 256, 1024), cons_cap=256, prefix="C"):
    """Phase D pilot prompts (exact rendering/sampling of wse.editor_pilot), non-thinking, 4 samples, seed 0.
    prefix "P" with caps=(4096,), cons_cap=4096 is the exact pilot setting (outputs comparable to the saved pilot
    generations of runs 20261103T-phaseD-pilot-e0 / -constrained)."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from wse import editor_tasks as K
    from wse import targets as T
    from wse.editor_pilot import DSL_REGEX, TIERS
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model)
    jobs = []
    for f in T.FAMILIES:
        for i in range(per_family):
            inst = T.build(f, "pilot", i)
            for tier in TIERS:
                rng = np.random.default_rng([inst["seed"] % (2 ** 32), TIERS.index(tier)])
                jobs.append((tier, K.render(inst, tier, rng)[0]))
    texts = [tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True,
                                     enable_thinking=False) for _, p in jobs]
    pids = [tok(t, add_special_tokens=False)["input_ids"] for t in texts]
    base = dict(n=4, seed=0, temperature=0.7, top_p=0.8, top_k=20)
    cases = []
    for cap in caps:
        cases.append((f"{prefix}_free_max{cap}", pids, [dict(base, max_tokens=cap)] * len(pids),
                      {"conc": len(pids), "samples": 4, "constrained": False, "max_tokens": cap}))
    cons = [dict(base, max_tokens=cons_cap, structured={"choice": [f"ANSWER: {c}" for c in "ABCD"]} if t == "T0"
                 else {"regex": DSL_REGEX}) for t, _ in jobs]
    cases.append((f"{prefix}_constrained_max{cons_cap}", pids, cons, {"conc": len(pids), "samples": 4,
                                                                    "constrained": True, "max_tokens": cons_cap}))
    return cases


# ---------------------------------------------------------------- telemetry
class NvmlSampler(threading.Thread):
    def __init__(self, period=0.05):
        super().__init__(daemon=True)
        import pynvml
        self.nv = pynvml
        pynvml.nvmlInit()
        uuid = os.environ.get("CUDA_VISIBLE_DEVICES", "").split(",")[0]   # TP runs: first GPU only
        self.h = (pynvml.nvmlDeviceGetHandleByUUID(uuid) if uuid.startswith("GPU-")
                  else pynvml.nvmlDeviceGetHandleByIndex(int(uuid or 0)))
        self.period, self.samples, self.on, self.stop_ = period, [], False, False

    def run(self):
        nv = self.nv
        while not self.stop_:
            if self.on:
                m = nv.nvmlDeviceGetMemoryInfo(self.h)
                u = nv.nvmlDeviceGetUtilizationRates(self.h)
                self.samples.append((m.used / 2 ** 20, u.gpu, nv.nvmlDeviceGetPowerUsage(self.h) / 1000,
                                     nv.nvmlDeviceGetClockInfo(self.h, nv.NVML_CLOCK_SM)))
            time.sleep(self.period)

    def window(self):
        self.samples, self.on = [], True

    def close(self):
        self.on = False
        s = self.samples
        if not s:
            return {}
        a = np.array(s)
        return {"vram_peak_mib": float(a[:, 0].max()), "util_mean": float(a[:, 1].mean()),
                "power_mean_w": float(a[:, 2].mean()), "sm_clock_mean_mhz": float(a[:, 3].mean()), "nvml_n": len(s)}


def counters(llm):
    want = {"vllm:prefix_cache_queries", "vllm:prefix_cache_hits", "vllm:num_preemptions",
            "vllm:prompt_tokens", "vllm:generation_tokens", "vllm:spec_decode_num_draft_tokens",
            "vllm:spec_decode_num_accepted_tokens", "vllm:prompt_tokens_by_source"}
    out = {}
    try:
        for m in llm.get_metrics():
            if m.name in want and hasattr(m, "value"):
                key = m.name + ("" if not getattr(m, "labels", None) else
                                "{" + ",".join(f"{k}={v}" for k, v in sorted(m.labels.items()) if k not in
                                               ("engine", "model_name")) + "}")
                out[key] = out.get(key, 0) + m.value
    except Exception as ex:   # noqa: BLE001
        out["error"] = repr(ex)
    return out


def shutdown(llm):
    """Stop the engine-core process explicitly (os._exit alone would orphan it with its GPU memory)."""
    try:
        llm.llm_engine.engine_core.shutdown()
    except Exception as ex:   # noqa: BLE001
        print("engine shutdown:", repr(ex), file=sys.stderr)


def pct(v, q):
    return float(np.percentile(v, q)) if len(v) else None


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--engine", default="{}", help="JSON dict of vllm.LLM keyword arguments (overrides defaults)")
    ap.add_argument("--workloads", default="A,B,D,E")
    ap.add_argument("--d-levels", default="1,2,4,8,16,32")
    ap.add_argument("--d-shapes", default="30720x1024,4096x512")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--out", required=True)
    ap.add_argument("--save-texts", type=int, default=1, help="store output token ids hash (+C texts) for equivalence")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows_p, meta_p = out / f"{a.name}.jsonl", out / f"{a.name}.meta.json"
    assert not rows_p.exists() and not meta_p.exists(), f"never overwrite results: {rows_p}"

    import torch
    import vllm
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.sampling_params import StructuredOutputsParams

    engine = dict(model=a.model, dtype="bfloat16", max_model_len=CTX, gpu_memory_utilization=0.85, seed=0,
                  disable_log_stats=False)
    engine.update(json.loads(a.engine))
    smp = NvmlSampler()
    smp.start()
    smp.window()
    t0 = time.perf_counter()
    meta = {"name": a.name, "engine_kwargs": engine, "argv": sys.argv, "cuda_visible_devices":
            os.environ.get("CUDA_VISIBLE_DEVICES"), "env": {k: v for k, v in os.environ.items()
                                                             if k.startswith("VLLM_")},
            "versions": {"vllm": vllm.__version__, "torch": torch.__version__, "cuda": torch.version.cuda},
            "start_unix": time.time()}
    try:
        llm = LLM(**engine)
    except Exception as ex:   # noqa: BLE001
        meta.update(status="startup_failed", error=f"{type(ex).__name__}: {ex}"[:4000],
                    startup_s=time.perf_counter() - t0)
        meta_p.write_text(json.dumps(meta, indent=1))
        print(json.dumps({"name": a.name, "status": "startup_failed", "error": meta["error"][:500]}))
        sys.exit(3)
    meta["startup_s"] = time.perf_counter() - t0
    meta["startup_telemetry"] = smp.close()
    try:
        cc = llm.llm_engine.vllm_config
        meta["resolved"] = {
            "max_num_batched_tokens": cc.scheduler_config.max_num_batched_tokens,
            "max_num_seqs": cc.scheduler_config.max_num_seqs,
            "chunked_prefill": cc.scheduler_config.enable_chunked_prefill,
            "async_scheduling": cc.scheduler_config.async_scheduling,
            "prefix_caching": cc.cache_config.enable_prefix_caching,
            "mamba_cache_mode": cc.cache_config.mamba_cache_mode,
            "block_size": cc.cache_config.block_size,
            "num_gpu_blocks": cc.cache_config.num_gpu_blocks,
            "cudagraph_mode": str(cc.compilation_config.cudagraph_mode),
            "compile_mode": str(cc.compilation_config.mode),
            "max_cudagraph_capture_size": cc.compilation_config.max_cudagraph_capture_size,
            "optimization_level": str(getattr(cc, "optimization_level", None)),
            "performance_mode": str(getattr(cc, "performance_mode", None)),
            "attention_backend": str(getattr(cc.attention_config, "backend", None)),
            "mamba_backend": str(getattr(cc.mamba_config, "backend", None)),
            "kv_cache_dtype": cc.cache_config.cache_dtype,
            "speculative": str(cc.speculative_config) if cc.speculative_config else None}
    except Exception as ex:   # noqa: BLE001
        meta["resolved"] = {"error": repr(ex)}
    meta_p.write_text(json.dumps(meta, indent=1))

    def sp(d):
        d = dict(d)
        st = d.pop("structured", None)
        base = dict(temperature=0.0, ignore_eos=True, seed=0) if "temperature" not in d else {}
        base.update(d)
        if st:
            base["structured_outputs"] = StructuredOutputsParams(**st)
        return SamplingParams(**base)

    cases = []
    for w in a.workloads.split(","):
        if w == "A":
            cases += workload_A()
        elif w == "B":
            cases += workload_B()
        elif w == "D":
            cases += workload_D(tuple(int(x) for x in a.d_levels.split(",")),
                                tuple(tuple(int(y) for y in s.split("x")) for s in a.d_shapes.split(",")))
        elif w == "E":
            cases += workload_E()
        elif w == "C":
            cases += workload_C(a.model)
        elif w == "P":
            cases += workload_C(a.model, caps=(4096,), cons_cap=4096, prefix="P")
        else:
            raise SystemExit(f"unknown workload {w}")

    with open(rows_p, "w") as fo:
        for name, prompts, sps, info in cases:
            mml = engine.get("max_model_len", CTX)
            if any(len(p) + s.get("max_tokens", 0) > mml for p, s in zip(prompts, sps)):
                print(f"skip {name}: exceeds max_model_len {mml}")
                continue
            tp = [TokensPrompt(prompt_token_ids=p) for p in prompts]
            spo = [sp(s) for s in sps]
            for rep in range(-1, a.repeats):
                # every repeat starts from an empty prefix cache: repeats are independent (no cross-repeat hits);
                # workload E measures sharing *within* one batch only
                llm.reset_prefix_cache()
                c0 = counters(llm)
                smp.window()
                t = time.perf_counter()
                try:
                    res = llm.generate(tp, spo, use_tqdm=False)
                    err = None
                except Exception as ex:   # noqa: BLE001
                    res, err = [], f"{type(ex).__name__}: {ex}"[:2000]
                wall = time.perf_counter() - t
                tel = smp.close()
                c1 = counters(llm)
                ttft, dec, e2e, n_out, n_in, pre = [], [], [], 0, 0, 0
                h = hashlib.sha256()
                texts = []
                for r in res:
                    n_in += len(r.prompt_token_ids)
                    m = r.metrics
                    for o in r.outputs:
                        n_out += len(o.token_ids)
                        h.update(np.asarray(o.token_ids, np.int64).tobytes())
                        if name[:2] in ("C_", "P_"):
                            texts.append(o.text)
                    if m is not None and m.first_token_ts:
                        ttft.append(m.first_token_ts - m.queued_ts)
                        e2e.append(m.last_token_ts - m.queued_ts)
                        k = len(r.outputs[0].token_ids)
                        if k > 1 and m.last_token_ts > m.first_token_ts:
                            dec.append((k - 1) / (m.last_token_ts - m.first_token_ts))
                        pre += m.num_preemptions
                row = {"config": a.name, "case": name, "rep": rep, **info, "wall_s": wall, "error": err,
                       "n_prompts": len(prompts), "prompt_tokens": n_in, "output_tokens": n_out,
                       "output_tok_s": n_out / wall if wall else None,
                       "total_tok_s": (n_in + n_out) / wall if wall else None,
                       "ttft_s": {"p50": pct(ttft, 50), "p90": pct(ttft, 90), "max": pct(ttft, 100),
                                  "mean": float(np.mean(ttft)) if ttft else None},
                       "e2e_s": {"p50": pct(e2e, 50), "p90": pct(e2e, 90), "max": pct(e2e, 100)},
                       "decode_tok_s_per_req": {"p50": pct(dec, 50), "min": pct(dec, 0)},
                       "req_preemptions": pre,
                       "counters_delta": {k: c1.get(k, 0) - c0.get(k, 0) for k in c1 if k != "error"},
                       "output_sha256": h.hexdigest(), **tel}
                if info.get("conc") == 1 and ttft:
                    row["prefill_tok_s"] = info["in"] / ttft[0]
                if texts and a.save_texts and rep == 0:
                    (out / f"{a.name}.{name}.texts.json").write_text(json.dumps(texts))
                fo.write(json.dumps(row) + "\n")
                fo.flush()
                print(f"{name} rep{rep}: wall {wall:.3f}s out_tok/s {row['output_tok_s']:.0f} "
                      f"ttft50 {row['ttft_s']['p50']} vram {tel.get('vram_peak_mib')} err {err}", flush=True)
    meta["end_unix"] = time.time()
    meta["status"] = "ok"
    meta_p.write_text(json.dumps(meta, indent=1))
    smp.stop_ = True
    shutdown(llm)
    os._exit(0)


if __name__ == "__main__":
    main()
