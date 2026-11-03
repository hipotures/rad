"""Rescore saved Phase D pilot generations offline (strict and lenient parsing) and compare editors pairwise.

    python -m wse.pilot_rescore --gens <raw dir> --out <results json> LABEL_thinkX [LABEL_thinkX ...]

Rules applied uniformly to every generations file:
- thinking outputs without a closing </think> are "no answer" (truncated reasoning; no answer is taken from inside it);
- T0 answers are matched case-insensitively ("ANSWER: b", "Answer: (B)");
- strict: the edit block must parse completely; lenient: unparseable lines are skipped (format repair, reported apart);
- invalid / missing answers count as no-op (recovery 0).
T0 chance = mean recovery of the four options of each instance (uniform random choice).
Pairing for editor comparisons: instance x tier x sample index (identical prompts and vLLM seed).
"""
import argparse
import json
from pathlib import Path

import numpy as np

from . import editor_tasks as K
from . import targets as T
from .editor_pilot import TIERS


def boot_ci(d, n=2000, seed=12345):
    rng = np.random.default_rng(seed)
    d = np.asarray(d, float)
    m = d[rng.integers(0, len(d), (n, len(d)))].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("tags", nargs="+")
    a = ap.parse_args(argv)
    cache, metas = {}, {}
    res, scored = {"tags": a.tags, "rules": __doc__}, {}
    for tag in a.tags:
        thinking = tag.endswith("think1")
        rows = []
        for line in open(Path(a.gens) / f"{tag}_generations.jsonl"):
            g = json.loads(line)
            if g["id"] not in cache:
                fam, split, idx = g["id"].split("-")
                cache[g["id"]] = T.build(fam, split, int(idx))
            inst = cache[g["id"]]
            key = (g["id"], g["tier"])
            if key not in metas:
                rng = np.random.default_rng([inst["seed"] % (2 ** 32), TIERS.index(g["tier"])])
                metas[key] = K.render(inst, g["tier"], rng)[1]
            out = g["output"]
            ans = (out.split("</think>")[-1] if "</think>" in out else None) if thinking else out
            r = {}
            for mode in ("strict", "lenient"):
                e = (K.evaluate_answer(inst, g["tier"], ans, metas[key], lenient=(mode == "lenient")) if ans is not None
                     else {"valid": False, "recovery": 0.0})
                r[mode] = {"valid": e["valid"], "recovery": float(e["recovery"])}
            rows.append({"id": g["id"], "family": inst["family"], "tier": g["tier"], "sample": g["sample"],
                         "answered": ans is not None, **r})
        scored[tag] = rows
        summ = {}
        for fam in T.FAMILIES:
            for tier in TIERS:
                s = [x for x in rows if x["family"] == fam and x["tier"] == tier]
                d = {"n": len(s), "answered_rate": float(np.mean([x["answered"] for x in s]))}
                for mode in ("strict", "lenient"):
                    v = np.array([x[mode]["recovery"] for x in s])
                    d[mode] = {"mean_recovery": float(v.mean()), "ci95": boot_ci(v),
                               "valid_rate": float(np.mean([x[mode]["valid"] for x in s])),
                               "full_repair_rate": float(np.mean(v >= 0.9))}
                summ[f"{fam}/{tier}"] = d
        res[tag] = summ
    chance = {}
    for fam in T.FAMILIES:
        v = []
        for (iid, tier), meta in metas.items():
            if tier == "T0" and iid.startswith(fam):
                v.append(np.mean([K.evaluate_answer(cache[iid], "T2", o, {})["recovery"] for o in meta["options"]]))
        chance[fam] = float(np.mean(v))
    res["t0_chance_recovery"] = chance
    if len(a.tags) > 1:
        pairs = {}
        for i, x in enumerate(a.tags):
            for y in a.tags[i + 1:]:
                ky = {(r["id"], r["tier"], r["sample"]): r for r in scored[y]}
                for mode in ("strict", "lenient"):
                    for tier in TIERS:
                        d = [ky[(r["id"], r["tier"], r["sample"])][mode]["recovery"] - r[mode]["recovery"]
                             for r in scored[x] if r["tier"] == tier and (r["id"], r["tier"], r["sample"]) in ky]
                        pairs[f"{y} - {x} / {tier} / {mode}"] = {"n": len(d), "mean_diff": float(np.mean(d)),
                                                                  "ci95": boot_ci(d)}
        res["pairwise"] = pairs
    Path(a.out).write_text(json.dumps(res, indent=1))
    for tag in a.tags:
        print(tag)
        for k, d in res[tag].items():
            print(f"  {k}: answered {d['answered_rate']:.2f} | strict rec {d['strict']['mean_recovery']:+.3f} "
                  f"valid {d['strict']['valid_rate']:.2f} | lenient rec {d['lenient']['mean_recovery']:+.3f} "
                  f"valid {d['lenient']['valid_rate']:.2f}")
    print("T0 chance", {k: round(v, 3) for k, v in chance.items()})
    for k, v in res.get("pairwise", {}).items():
        print(k, f"{v['mean_diff']:+.3f}", [round(c, 3) for c in v["ci95"]])


if __name__ == "__main__":
    main()
