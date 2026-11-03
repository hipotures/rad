"""Compare the bounded MATH-500 check with upstream per-problem results on the same problems.

    python -m wse.compare_math500 --ours <run results dir> --upstream-eval <exp8_math/eval> --out <json>

Upstream per-problem files: eval/<unedited|p50c>/parts/math500_s*/math500_per_problem.json (4 samples per problem).
Reports, on the problems of our subset: upstream accuracy (4 samples) and ours (our samples), per model, and the
problem-level paired difference p50c - Gold with a bootstrap 95% interval (resampling problems).
"""
import argparse
import glob
import json
import os
from pathlib import Path

import numpy as np


def upstream(eval_dir, run):
    out = {}
    for f in glob.glob(os.path.join(eval_dir, run, "parts", "math500_s*", "math500_per_problem.json")):
        for r in json.load(open(f)):
            out[r["id"]] = r["correct"]
    return out


def boot(d, n=5000, seed=0):
    rng = np.random.default_rng(seed)
    b = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)])
    return [float(np.quantile(b, 0.025)), float(np.quantile(b, 0.975))]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ours", required=True)
    ap.add_argument("--upstream-eval", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    ours = {}
    for lab in ("gold", "p50c"):   # unsharded file or problem shards (<lab>_s<i>of<k>_per_problem.json)
        files = sorted(Path(a.ours).glob(f"{lab}_per_problem.json")) or sorted(Path(a.ours).glob(f"{lab}_s*_per_problem.json"))
        ours[lab] = {r["id"]: r for f in files for r in json.load(open(f))}
    up = {"gold": upstream(a.upstream_eval, "unedited"), "p50c": upstream(a.upstream_eval, "p50c")}
    ids = sorted(set(ours["gold"]) & set(ours["p50c"]))
    assert all(i in up["gold"] and i in up["p50c"] for i in ids), "subset ids missing upstream"
    res = {"problems": len(ids), "models": {}}
    pa = {}
    for lab in ("gold", "p50c"):
        o = np.array([np.mean(ours[lab][i]["correct"]) for i in ids])
        u = np.array([np.mean(up[lab][i]) for i in ids])
        oc = np.array([np.mean(ours[lab][i]["cut"]) for i in ids])
        pa[lab] = o
        res["models"][lab] = {"ours_acc": float(o.mean()), "ours_acc_ci95": boot(o), "ours_cut_share": float(oc.mean()),
                              "ours_mean_tokens": float(np.mean([t for i in ids for t in ours[lab][i]["tokens"]])), "upstream_acc_same_problems": float(u.mean()),
                              "upstream_acc_ci95": boot(u), "ours_minus_upstream": float(o.mean() - u.mean()),
                              "problem_level_corr_ours_upstream": float(np.corrcoef(o, u)[0, 1]) if o.std() and u.std() else None,
                              "upstream_full_500": None}
    d = pa["p50c"] - pa["gold"]
    ud = np.array([np.mean(up["p50c"][i]) - np.mean(up["gold"][i]) for i in ids])
    res["paired_p50c_minus_gold"] = {"ours": float(d.mean()), "ours_ci95": boot(d), "upstream_same_problems": float(ud.mean()),
                                     "upstream_ci95": boot(ud)}
    for lab, run in (("gold", "unedited"), ("p50c", "p50c")):
        m = json.load(open(os.path.join(a.upstream_eval, run, "merged.json")))["math500"]
        res["models"][lab]["upstream_full_500"] = {"acc": m["acc"], "cut_share": m["cut_share"], "mean_tokens": m["mean_tokens"]}
    Path(a.out).write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
