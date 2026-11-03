"""Correctness/stability tests of the persistent evaluator's candidate transitions (one GPU, vLLM environment).

    python -m wse.swap_test --mode direct  --sequence gold,p50c,gold,p25c,p50c,gold --out <dir> --name <name>
    python -m wse.swap_test --mode restart --sequence ... (each state on a freshly started engine = reference)
    python -m wse.swap_test --mode direct  --extended 60 --seed 1 ...  (random transitions, Gold audits, memory)

Workload per state (Phase D v1 pilot prompts, 144 prompts; identical batches in every state):
  greedy        temperature 0, n = 1, max 64 tokens          (deterministic case)
  sampled       temperature 0.7, top-p 0.8, n = 4, seed 0, max 256 tokens (controlled stochastic case)
  constrained   as sampled with the v1 structured-output constraints (T0 choice / DSL regex)
Records, for every state visit, a hash per request (token ids of all samples) and per case, the transition record
(timings, entries written, hash verification), GPU memory reported by the worker, and Gold full-fingerprint audits.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench.vllm_bench import workload_C  # noqa: E402
from wse import work_root  # noqa: E402
from wse.swap_engine import PersistentEngine  # noqa: E402


def population(path):
    m = json.loads(Path(path).read_text())["members"]
    return {"gold": None, **{x["label"]: x["patch_id"] for x in m}}


def build_cases(gold_dir, which):
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.sampling_params import StructuredOutputsParams
    cs = {c[0]: c for c in workload_C(gold_dir, caps=(256,))}
    free, cons = cs["C_free_max256"], cs["C_constrained_max256"]
    prompts = [TokensPrompt(prompt_token_ids=x) for x in free[1]]

    def sp(d):
        d = dict(d)
        st = d.pop("structured", None)
        if st:
            d["structured_outputs"] = StructuredOutputsParams(**st)
        return SamplingParams(**d)
    out = {"greedy": (prompts, [SamplingParams(temperature=0.0, max_tokens=64, n=1)] * len(prompts))}
    if which == "full":
        out["sampled"] = (prompts, [sp(s) for s in free[2]])
        out["constrained"] = (prompts, [sp(s) for s in cons[2]])
    return out


def run_cases(eng, cases, reset=True):
    """reset: cold prefix cache before every case (the evaluator's protocol); first campaign ran with reset=False."""
    res = {}
    for name, (prompts, params) in cases.items():
        t = time.perf_counter()
        outs = eng.generate(prompts, params, reset_cache=reset)
        w = time.perf_counter() - t
        per, tot, ntok = [], hashlib.sha256(), 0
        for o in outs:
            h = hashlib.sha256()
            for c in o.outputs:
                b = np.asarray(c.token_ids, np.int64).tobytes()
                h.update(b)
                tot.update(b)
                ntok += len(c.token_ids)
            per.append(h.hexdigest()[:16])
        res[name] = {"wall_s": w, "sha256": tot.hexdigest(), "per_request": per, "tokens": ntok}
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("direct", "reload", "restart"), required=True)
    ap.add_argument("--sequence", default="")
    ap.add_argument("--extended", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--ext-full", action="store_true", help="extended cycles with greedy + sampled + constrained cases")
    ap.add_argument("--population", default=str(Path(__file__).resolve().parents[2] / "configs/phaseD_v2/editor_population.json"))
    ap.add_argument("--gold-dir", default=str(work_root() / "derived/qwen3.5-0.8B-text-gold"))
    ap.add_argument("--engine-json", default='{"max_model_len": 32768, "gpu_memory_utilization": 0.85, '
                                             '"attention_backend": "FLASHINFER", "max_num_seqs": 1024, '
                                             '"max_num_batched_tokens": 16384}')
    ap.add_argument("--audit-every-gold", type=int, default=1)
    ap.add_argument("--no-reset-between-cases", action="store_true",
                    help="reproduce the first test round (prefix cache kept warm across cases within a visit)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out) / f"{a.name}.json"
    assert not out.exists(), "never overwrite results"
    out.parent.mkdir(parents=True, exist_ok=True)
    pop = population(a.population)
    if a.extended:
        rng = np.random.default_rng(a.seed)
        labels = [k for k in pop if k != "gold"]
        seq = ["gold"]
        for _ in range(a.extended):
            nxt = "gold" if rng.random() < 0.3 else labels[int(rng.integers(len(labels)))]
            if nxt != seq[-1]:
                seq.append(nxt)
        seq.append("gold")
        which = "full" if a.ext_full else "greedy"
    else:
        seq = a.sequence.split(",")
        which = "full"
    t0 = time.perf_counter()
    eng = PersistentEngine(a.gold_dir, json.loads(a.engine_json), mode=a.mode, name=a.name)
    res = {"name": a.name, "mode": a.mode, "reset_between_cases": not a.no_reset_between_cases, "sequence": seq, "engine": {k: v for k, v in eng.kw.items()},
           "identity": eng.identity, "startup_s": eng.startups[0], "init_total_s": time.perf_counter() - t0,
           "visits": [], "audits": []}
    cases = build_cases(a.gold_dir, which)
    res["memory_start"] = eng.memory()
    first_seen = {}
    for i, lab in enumerate(seq):
        tr = eng.transition(pop[lab], label=lab) if i else {"label": "gold", "initial": True}
        v = {"i": i, "label": lab, "patch_id": pop[lab], "transition": tr}
        if lab == "gold" and i and a.audit_every_gold:
            au = eng.audit()
            res["audits"].append({"i": i, **au})
            v["audit_ok"] = au["ok"]
        v["cases"] = run_cases(eng, cases, reset=not a.no_reset_between_cases)
        v["memory"] = eng.memory()
        if lab in first_seen:
            ref = first_seen[lab]
            v["same_as_first_visit"] = {c: v["cases"][c]["sha256"] == ref[c]["sha256"] for c in v["cases"]}
        else:
            first_seen[lab] = v["cases"]
        res["visits"].append(v)
        print(json.dumps({"i": i, "label": lab, "mode_used": tr.get("mode_used"), "total_s": tr.get("total_s"),
                          "verify_ok": tr.get("verify_ok"), "same": v.get("same_as_first_visit"),
                          "audit": v.get("audit_ok"), "alloc_mib": v["memory"]["allocated"] >> 20,
                          "gen_s": {c: round(x["wall_s"], 2) for c, x in v["cases"].items()}}), flush=True)
    res["startups_s"] = eng.startups
    res["wall_s"] = time.perf_counter() - t0
    out.write_text(json.dumps(res))
    eng.shutdown()
    os._exit(0)


if __name__ == "__main__":
    main()
