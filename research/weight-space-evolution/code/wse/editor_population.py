"""Representative population of candidate-editor patches of E0 for persistent-evaluator tests and as editor-level
matched random controls (Phase D design baseline 3 at the editor level).

    python -m wse.editor_population --out <json>      (wse environment; deterministic, seeds in the output)

Members (all direct numerical edits of Gold tensors; no gradients):
  rand-dir-k   p50c-matched structure: remove a *random* unit direction from 64 random columns of two random
               mlp.down_proj tensors (p50c removes a measured "loop" direction from 64 columns in layers 15/19).
  rand-sparse-k  2,048 random entries of one random o_proj/out_proj/down_proj perturbed by N(0, 2% of tensor std).
  rand-fused   1,024 entries of an mlp.gate_proj tensor (runtime-fused in vLLM -> exercises the reload fallback).
  chain-p50c   child of p50c with a 256-entry random edit (exercises lineage with a parent).
Existing upstream imports p10c / p25c / p50c are listed alongside by patch id.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from . import patch, registry
from .tensors import bf16_bits_to_f32, f32_to_bf16_bits

GOLD = "qwen3.5-0.8B@2fc0636"
UPSTREAM = {"p50c": "p-4b2661ed6f35", "p25c": "p-b6000ab1175a", "p10c": "p-8cd661ba832c"}
L = "model.language_model.layers."


def policy(names):
    return {"allowed_tensors": sorted(names), "max_abs_value": 1e4, "max_changed_entries": 10 ** 7,
            "forbid_uniform_scale": True}


def rand_dir(rng, man):
    layers = sorted(rng.choice([i for i in range(24)], 2, replace=False).tolist())
    names = [f"{L}{i}.mlp.down_proj.weight" for i in layers]
    g = registry.load(GOLD, names)
    prop = {}
    u = rng.normal(size=1024)
    u /= np.linalg.norm(u)
    for n in names:
        w = bf16_bits_to_f32(g[n][1]).astype(np.float64)          # [1024, 3584]
        cols = rng.choice(w.shape[1], 64, replace=False)
        sub = w[:, cols]
        w[:, cols] = sub - np.outer(u, u @ sub)
        prop[n] = f32_to_bf16_bits(w.astype(np.float32))
    return prop, {"layers": layers}


def rand_sparse(rng, man, kind):
    pool = [n for n in man["tensors"] if n.startswith(L) and n.endswith(kind)]
    n = pool[int(rng.integers(len(pool)))]
    g = registry.load(GOLD, [n])[n][1]
    w = bf16_bits_to_f32(g).astype(np.float64).reshape(-1)
    k = 1024 if kind == "mlp.gate_proj.weight" else 2048
    idx = rng.choice(w.size, k, replace=False)
    w[idx] += rng.normal(0, 0.02 * w.std(), k)
    return {n: f32_to_bf16_bits(w.astype(np.float32)).reshape(g.shape)}, {"tensor": n, "entries": k}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20261103)
    a = ap.parse_args(argv)
    man = registry.manifest(GOLD)
    rng = np.random.default_rng(a.seed)
    members = [{"label": k, "patch_id": v, "kind": "upstream import"} for k, v in UPSTREAM.items()]
    specs = [("rand-dir-%d" % i, rand_dir, None) for i in range(4)]
    specs += [("rand-sparse-%d" % i, rand_sparse, kind) for i, kind in
              enumerate(["self_attn.o_proj.weight", "linear_attn.out_proj.weight", "mlp.down_proj.weight"])]
    specs += [("rand-fused", rand_sparse, "mlp.gate_proj.weight")]
    for label, fn, kind in specs:
        prop, info = fn(rng, man) if kind is None else fn(rng, man, kind)
        rec = patch.create(GOLD, prop, policy(prop), meta={"method": f"editor-population random control {label}",
                                                           "author": "wse.editor_population", "seed": a.seed, **info})
        members.append({"label": label, "patch_id": rec["patch_id"], "kind": "random control", **info,
                        "changed_entries": rec["changed_entries_total"]})
    # lineage member: child of p50c
    n = f"{L}15.mlp.down_proj.weight"
    base = patch.materialize(GOLD, UPSTREAM["p50c"], [n])[n][1]
    w = bf16_bits_to_f32(base).astype(np.float64).reshape(-1)
    idx = rng.choice(w.size, 256, replace=False)
    w[idx] += rng.normal(0, 0.02 * w.std(), 256)
    rec = patch.create(GOLD, {n: f32_to_bf16_bits(w.astype(np.float32)).reshape(base.shape)}, policy([n]),
                       meta={"method": "editor-population lineage control (child of p50c)", "author":
                             "wse.editor_population", "seed": a.seed}, parent_id=UPSTREAM["p50c"])
    members.append({"label": "chain-p50c", "patch_id": rec["patch_id"], "kind": "lineage control",
                    "parent": UPSTREAM["p50c"], "changed_entries": rec["changed_entries_total"]})
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps({"gold_id": GOLD, "seed": a.seed, "members": members}, indent=1))
    for m in members:
        print(m["label"], m["patch_id"])


if __name__ == "__main__":
    main()
