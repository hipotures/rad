"""Candidate checkpoint swap without restarting the engine (Profile 3: repeated candidate evaluations).

    CUDA_VISIBLE_DEVICES=<uuid> python -m bench.weight_swap --models <gold dir>,<cand dir>,<gold dir> \
        --engine '{...}' --out <raw dir> --name <name>
    CUDA_VISIBLE_DEVICES=<uuid> python -m bench.weight_swap --models <cand dir> --out ... --name <fresh ref name>

Starts one engine on the first checkpoint, runs the Phase D editor cases (C_constrained_max256, C_free_max256), then
for each further checkpoint calls vLLM's in-place `reload_weights(weights_path=...)` on the worker, resets the prefix
cache and reruns the cases. Records reload wall time and the output-token hash of every pass, so a swapped engine can
be compared with a freshly started engine on the same checkpoint (same seeds and batch => outputs must match for the
swap to be a valid substitute for a restart). Writes <name>.swap.json.
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
from bench.vllm_bench import CTX, shutdown, workload_C  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True)
    ap.add_argument("--engine", default="{}")
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", required=True)
    a = ap.parse_args(argv)
    models = a.models.split(",")
    out = Path(a.out) / f"{a.name}.swap.json"
    assert not out.exists(), "never overwrite results"
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.sampling_params import StructuredOutputsParams
    cases = [c for c in workload_C(models[0], caps=(256,)) if c[0] in ("C_free_max256", "C_constrained_max256")]
    engine = dict(model=models[0], dtype="bfloat16", max_model_len=CTX, gpu_memory_utilization=0.85, seed=0)
    engine.update(json.loads(a.engine))
    t = time.perf_counter()
    llm = LLM(**engine)
    res = {"name": a.name, "engine": engine, "models": models, "startup_s": time.perf_counter() - t, "passes": []}

    def sp(d):
        d = dict(d)
        st = d.pop("structured", None)
        if st:
            d["structured_outputs"] = StructuredOutputsParams(**st)
        return SamplingParams(**d)

    for i, m in enumerate(models):
        p = {"model": m}
        if i > 0:
            t = time.perf_counter()
            llm.collective_rpc("reload_weights", kwargs={"weights_path": m})
            llm.reset_prefix_cache()
            p["reload_s"] = time.perf_counter() - t
        for name, prompts, sps, _ in cases:
            llm.reset_prefix_cache()
            t = time.perf_counter()
            outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x in prompts], [sp(s) for s in sps],
                                use_tqdm=False)
            w = time.perf_counter() - t
            h = hashlib.sha256()
            texts = []
            for o in outs:
                for c in o.outputs:
                    h.update(np.asarray(c.token_ids, np.int64).tobytes())
                    texts.append(c.text)
            p[name] = {"wall_s": w, "output_sha256": h.hexdigest()}
            (Path(a.out) / f"{a.name}.pass{i}.{name}.texts.json").write_text(json.dumps(texts))
        res["passes"].append(p)
        print(json.dumps(p), flush=True)
    out.write_text(json.dumps(res, indent=1))
    shutdown(llm)
    os._exit(0)


if __name__ == "__main__":
    main()
