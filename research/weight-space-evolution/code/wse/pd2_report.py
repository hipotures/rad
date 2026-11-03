"""Aggregate Phase D v2 editor evaluations: per-family/tier recovery with instance-bootstrap CIs, baselines, paired
comparisons with E0, resource-normalized rankings, candidate strengths/weaknesses, T0 position analysis.

    python -m wse.pd2_report --campaign <id> --split pilot --out <results dir> [--ref E0]   (wse environment)

Inputs: work/raw/<campaign>/<job>.jsonl (+ .summary.json) from wse.pd2_eval, and per-instance baselines stored with
the benchmark instances. Output: editor_results.json (compact) and acceptance.json (per family x tier cell).
"""
import argparse
import json
from pathlib import Path

import numpy as np

from . import pd2_bench as B
from . import work_root

TIERS = ("T0", "T1", "T2", "T2P")


def boot_ci(groups, n=2000, seed=0):
    """Mean over all values with a cluster bootstrap over instances (groups: list of per-instance value lists)."""
    rng = np.random.default_rng(seed)
    means = [np.mean(g) for g in groups]
    k = len(means)
    if k == 0:
        return None, None, None
    m = float(np.mean(means))
    bs = [np.mean(np.array(means)[rng.integers(0, k, k)]) for _ in range(n)]
    return m, float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))


def load_campaign(campaign, split):
    raw = work_root() / "raw" / campaign
    rows, recs = [], {}
    for f in sorted(raw.glob(f"*__{split}.summary.json")):
        rec = json.loads(f.read_text())
        if "error" in rec:
            recs[rec["editor_id"]] = rec
            continue
        recs[rec["editor_id"]] = rec
        rows += [json.loads(line) for line in open(raw / f"{rec['job_id']}.jsonl")]
    return rows, recs


def cell_stats(rs):
    by = {}
    for r in rs:
        by.setdefault(r["id"], []).append(r["recovery"])
    m, lo, hi = boot_ci(list(by.values()))
    return {"n": len(rs), "instances": len(by), "mean_recovery": m, "ci95": [lo, hi],
            "valid_rate": float(np.mean([r["valid"] for r in rs])),
            "effective_rate": float(np.mean([r["recovery"] >= 0.5 for r in rs])),
            "full_repair_rate": float(np.mean([r["recovery"] >= 0.9 for r in rs])),
            "regression_rate": float(np.mean([r["regression"] for r in rs])),
            "mean_recovery_valid_only": float(np.mean([r["recovery"] for r in rs if r["valid"]])) if any(r["valid"] for r in rs) else None,
            "gen_tokens": int(sum(r["gen_tokens"] for r in rs))}


def paired(rows_a, rows_b):
    key = lambda r: (r["id"], r["tier"], r["sample"])   # noqa: E731
    b = {key(r): r["recovery"] for r in rows_b}
    by = {}
    for r in rows_a:
        if key(r) in b:
            by.setdefault(r["id"], []).append(r["recovery"] - b[key(r)])
    m, lo, hi = boot_ci(list(by.values()))
    return {"pairs": int(sum(len(v) for v in by.values())), "mean_diff": m, "ci95": [lo, hi],
            "significant": bool(lo is not None and (lo > 0 or hi < 0))}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", required=True)
    ap.add_argument("--split", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref", default="E0")
    a = ap.parse_args(argv)
    rows, recs = load_campaign(a.campaign, a.split)
    metas = {m["id"]: m for m in (json.loads(f.read_text()) for f in sorted((B.bench_dir() / a.split).glob("*.json")))}
    fams = sorted({m["family"] for m in metas.values()})
    eds = sorted({r["editor_id"] for r in rows})
    out = {"campaign": a.campaign, "split": a.split, "editors": {}, "baselines": {}, "paired_vs_ref": {}, "t0_position": {},
           "resources": {}, "ranking": [], "strengths": {}}
    # baselines per family (and subtype) -- per instance, tier independent; T0 chance per family
    for fam in fams + ["ALL"]:
        ms = [m for m in metas.values() if fam == "ALL" or m["family"] == fam]
        bl = {}
        for b in ("random_matched_mean", "heuristic_simple", "heuristic_improved", "oracle"):
            bl[b] = boot_ci([[m["baselines"][b]] for m in ms])[0]
        bl["t0_chance"] = float(np.mean([np.mean(m["t0_option_recovery"]) for m in ms]))
        bl["heuristic_improved_probe_evals"] = float(np.mean([m["baselines"]["heuristic_improved_probe_evals"] for m in ms]))
        bl["n_instances"] = len(ms)
        out["baselines"][fam] = bl
    for sub in sorted({(m["family"], m["subtype"]) for m in metas.values()}):
        ms = [m for m in metas.values() if (m["family"], m["subtype"]) == sub]
        out["baselines"]["/".join(sub)] = {b: float(np.mean([m["baselines"][b] for m in ms])) for b in
                                           ("random_matched_mean", "heuristic_simple", "heuristic_improved", "oracle")}
        out["baselines"]["/".join(sub)]["t0_chance"] = float(np.mean([np.mean(m["t0_option_recovery"]) for m in ms]))
    for e in eds:
        er = [r for r in rows if r["editor_id"] == e]
        cells = {}
        for fam in fams:
            for t in TIERS:
                rs = [r for r in er if r["family"] == fam and r["tier"] == t]
                if rs:
                    cells[f"{fam}/{t}"] = cell_stats(rs)
        for t in TIERS:
            rs = [r for r in er if r["tier"] == t]
            if rs:
                cells[f"ALL/{t}"] = cell_stats(rs)
        cells["ALL/ALL"] = cell_stats(er)
        sub = {}
        for key in sorted({(r["family"], r["subtype"], r["tier"]) for r in er}):
            rs = [r for r in er if (r["family"], r["subtype"], r["tier"]) == key]
            sub["/".join(key)] = {"n": len(rs), "mean_recovery": float(np.mean([r["recovery"] for r in rs])),
                                  "valid_rate": float(np.mean([r["valid"] for r in rs]))}
        out["editors"][e] = {"cells": cells, "subtypes": sub}
        rec = recs.get(e, {})
        g = rec.get("gen", {})
        tr = rec.get("transition", {})
        out["resources"][e] = {"gen_tokens": g.get("gen_tokens"), "prompt_tokens": g.get("prompt_tokens"),
                               "generate_s": g.get("generate_s"), "round2_s": g.get("round2_s"),
                               "feedback_s": g.get("feedback_s"), "probe_passes": g.get("probe_passes"),
                               "score_s": rec.get("score_s"), "transition_s": tr.get("total_s"),
                               "gpu_seconds": (g.get("generate_s") or 0) + (g.get("round2_s") or 0) + (tr.get("total_s") or 0)}
        if a.ref in eds and e != a.ref:
            refr = [r for r in rows if r["editor_id"] == a.ref]
            pc = {}
            for fam in fams + ["ALL"]:
                for t in TIERS + ("ALL",):
                    ra = [r for r in er if (fam == "ALL" or r["family"] == fam) and (t == "ALL" or r["tier"] == t)]
                    rb = [r for r in refr if (fam == "ALL" or r["family"] == fam) and (t == "ALL" or r["tier"] == t)]
                    if ra and rb:
                        pc[f"{fam}/{t}"] = paired(ra, rb)
            out["paired_vs_ref"][e] = pc
            out["strengths"][e] = {"better_than_ref": [k for k, v in pc.items() if v["significant"] and v["mean_diff"] > 0 and "ALL" not in k],
                                   "worse_than_ref": [k for k, v in pc.items() if v["significant"] and v["mean_diff"] < 0 and "ALL" not in k]}
        t0 = [r for r in er if r["tier"] == "T0"]
        if t0:
            ans = [r.get("answer") for r in t0]
            out["t0_position"][e] = {"answer_counts": {c: ans.count(c) for c in "ABCD"},
                                     "accuracy_by_correct_position": {c: float(np.mean([r.get("answer") == c for r in t0 if r["correct"] == c]))
                                                                      for c in "ABCD"},
                                     "accuracy": float(np.mean([r.get("answer") == r["correct"] for r in t0]))}
    for e in eds:
        c = out["editors"][e]["cells"]["ALL/ALL"]
        res = out["resources"][e]
        out["ranking"].append({"editor": e, "mean_recovery": c["mean_recovery"], "ci95": c["ci95"],
                               "valid_rate": c["valid_rate"], "regression_rate": c["regression_rate"],
                               "recovery_per_1k_tokens": c["mean_recovery"] * 1000 / max(res["gen_tokens"] or 1, 1) * c["n"],
                               "recovery_per_gpu_second": c["mean_recovery"] * c["n"] / max(res["gpu_seconds"] or 1e-9, 1e-9)})
    out["ranking"].sort(key=lambda x: -x["mean_recovery"])
    o = Path(a.out)
    o.mkdir(parents=True, exist_ok=True)
    (o / f"editor_results_{a.split}.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["ranking"], indent=1))


if __name__ == "__main__":
    main()
