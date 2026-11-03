"""Summarize a benchmark campaign: per configuration startup breakdown and per case medians over steady-state repeats.

    python -m bench.summarize --campaign <id> --out <runs/<id>/results>

Reads work/raw/<id>/<config>.{jsonl,meta.json} and work/logs/<id>/<config>.log. Warm-up repeats (rep = -1) are
excluded. Writes summary.json (all configs), cases.csv (one row per config x case) and startup.csv.
"""
import argparse
import csv
import json
import os
import re
import statistics as st
from pathlib import Path

TOPIC = Path(__file__).resolve().parents[2]
W = Path(os.environ.get("WSE_WORK_ROOT", TOPIC / "work"))

LOG_PATTERNS = {
    "model_load_s": r"Model loading took [\d.]+ GiB memory and ([\d.]+) seconds",
    "model_load_gib": r"Model loading took ([\d.]+) GiB memory",
    "dynamo_s": r"Dynamo bytecode transform time: ([\d.]+) s",
    "torch_compile_s": r"torch.compile took ([\d.]+) s in total",
    "graph_capture_s": r"Graph capturing finished in ([\d.]+) secs",
    "graph_capture_gib": r"Graph capturing finished in [\d.]+ secs, took ([\d.]+) GiB",
    "init_engine_s": r"init engine \(profile, create kv cache, warmup model\) took ([\d.]+) s",
    "kv_cache_gib": r"Available KV cache memory: ([\d.]+) GiB",
    "kv_cache_tokens": r"GPU KV cache size: ([\d,]+) tokens",
    "max_concurrency_32k": r"Maximum concurrency for [\d,]+ tokens per request: ([\d.]+)x",
    "attention_backend": r"Using (\w+) attention backend",
    "peak_activation_gib": r"([\d.]+) GiB for peak activation",
}


def parse_log(p):
    out = {}
    if not p.exists():
        return out
    txt = p.read_text(errors="replace")
    for k, pat in LOG_PATTERNS.items():
        m = re.findall(pat, txt)
        if m:
            v = m[-1].replace(",", "")
            try:
                out[k] = float(v)
            except ValueError:
                out[k] = v
    out["graph_capture_events"] = len(re.findall(LOG_PATTERNS["graph_capture_s"], txt))
    out["errors"] = len(re.findall(r"\bERROR\b", txt))
    return out


def med(v):
    v = [x for x in v if x is not None]
    return st.median(v) if v else None


def cv(v):
    v = [x for x in v if x is not None]
    return st.stdev(v) / st.mean(v) if len(v) > 1 and st.mean(v) else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    raw, logs, out = W / "raw" / a.campaign, W / "logs" / a.campaign, Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    summ, case_rows, start_rows = {}, [], []
    for mp in sorted(raw.glob("*.meta.json")):
        name = mp.name[: -len(".meta.json")]
        meta = json.loads(mp.read_text())
        lg = parse_log(logs / f"{name}.log")
        cfg = {"status": meta.get("status"), "error": meta.get("error"), "engine_kwargs": meta.get("engine_kwargs"),
               "env": meta.get("env"), "gpu": meta.get("cuda_visible_devices"), "resolved": meta.get("resolved"),
               "startup_s": meta.get("startup_s"), "startup_log": lg, "cases": {}}
        start_rows.append({"config": name, "status": meta.get("status"), "gpu": (meta.get("cuda_visible_devices") or "")[:12],
                           "startup_s": round(meta.get("startup_s") or 0, 2), **{k: lg.get(k) for k in LOG_PATTERNS}})
        rows = [json.loads(l) for l in open(raw / f"{name}.jsonl")] if (raw / f"{name}.jsonl").exists() else []
        by = {}
        for r in rows:
            by.setdefault(r["case"], []).append(r)
        for case, rs in by.items():
            ss = [r for r in rs if r["rep"] >= 0]
            if not ss:
                continue
            g = lambda f: [f(r) for r in ss]   # noqa: E731
            d = {"n": len(ss), "in": ss[0].get("in"), "out": ss[0].get("out"), "conc": ss[0].get("conc"),
                 "errors": sum(r["error"] is not None for r in ss),
                 "wall_s": med(g(lambda r: r["wall_s"])), "wall_cv": cv(g(lambda r: r["wall_s"])),
                 "wall_min": min(r["wall_s"] for r in ss), "wall_max": max(r["wall_s"] for r in ss),
                 "output_tok_s": med(g(lambda r: r["output_tok_s"])),
                 "total_tok_s": med(g(lambda r: r["total_tok_s"])),
                 "ttft_p50_s": med(g(lambda r: r["ttft_s"]["p50"])), "ttft_p90_s": med(g(lambda r: r["ttft_s"]["p90"])),
                 "ttft_max_s": med(g(lambda r: r["ttft_s"]["max"])),
                 "e2e_p50_s": med(g(lambda r: r["e2e_s"]["p50"])), "e2e_p90_s": med(g(lambda r: r["e2e_s"]["p90"])),
                 "e2e_max_s": med(g(lambda r: r["e2e_s"]["max"])),
                 "decode_tok_s_req_p50": med(g(lambda r: r["decode_tok_s_per_req"]["p50"])),
                 "prefill_tok_s": med(g(lambda r: r.get("prefill_tok_s"))),
                 "vram_peak_mib": max((r.get("vram_peak_mib") or 0) for r in ss),
                 "util_mean": med(g(lambda r: r.get("util_mean"))), "power_mean_w": med(g(lambda r: r.get("power_mean_w"))),
                 "sm_clock_mhz": med(g(lambda r: r.get("sm_clock_mean_mhz"))),
                 "preemptions": sum(r["counters_delta"].get("vllm:num_preemptions{}", 0) for r in ss),
                 "prefix_hit_rate": med(g(lambda r: (r["counters_delta"].get("vllm:prefix_cache_hits{}", 0) /
                                                     r["counters_delta"]["vllm:prefix_cache_queries{}"])
                                          if r["counters_delta"].get("vllm:prefix_cache_queries{}") else None)),
                 "computed_prompt_tokens": med(g(lambda r: r["counters_delta"].get(
                     "vllm:prompt_tokens_by_source{source=local_compute}"))),
                 "spec_accept_rate": med(g(lambda r: (r["counters_delta"].get("vllm:spec_decode_num_accepted_tokens{}", 0)
                                                      / r["counters_delta"]["vllm:spec_decode_num_draft_tokens{}"])
                                           if r["counters_delta"].get("vllm:spec_decode_num_draft_tokens{}") else None)),
                 "output_tokens": ss[0]["output_tokens"],
                 "output_sha256": sorted({r["output_sha256"] for r in rs}),
                 "deterministic_across_reps": len({r["output_sha256"] for r in rs}) == 1}
            cfg["cases"][case] = d
            case_rows.append({"config": name, "case": case, **{k: (round(v, 4) if isinstance(v, float) else v)
                                                              for k, v in d.items() if k != "output_sha256"},
                              "output_sha12": d["output_sha256"][0][:12]})
        summ[name] = cfg
    (out / "summary.json").write_text(json.dumps(summ, indent=1))
    for fn, rows in (("cases.csv", case_rows), ("startup.csv", start_rows)):
        if rows:
            keys = list(dict.fromkeys(k for r in rows for k in r))
            with open(out / fn, "w", newline="") as f:
                w = csv.DictWriter(f, keys)
                w.writeheader()
                w.writerows(rows)
    print(f"{len(summ)} configs, {len(case_rows)} case rows -> {out}")


if __name__ == "__main__":
    main()
