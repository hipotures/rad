"""Compact analysis of wse.swap_test results (any environment with numpy).

    python -m wse.swap_analyze --raw <raw dir> --out <results/swap_tests.json>

For every state label and case: per-request agreement of the persistent-engine visits (direct / reload modes) with
the fresh-engine visits (restart mode) of the same state, and the agreement among fresh-engine visits themselves
(the engine's own run-to-run variation, which bounds what any swap mechanism can achieve for sampled outputs).
"""
import argparse
import itertools
import json
from pathlib import Path

import numpy as np


def agree(a, b):
    return float(np.mean([x == y for x, y in zip(a, b)]))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prefix", default="", help="round prefix, e.g. r2_ (cold prefix cache before every case)")
    a = ap.parse_args(argv)
    R = {n: json.loads((Path(a.raw) / f"{a.prefix}{n}.json").read_text())
         for n in ("seq_direct", "seq_reload", "seq_restart", "ext_direct")}
    out = {"prefix": a.prefix, "reset_between_cases": R["seq_direct"].get("reset_between_cases", False),
           "modes": {}, "transitions": {}, "extended": {}}
    fresh = {}
    for v in R["seq_restart"]["visits"]:
        fresh.setdefault(v["label"], []).append(v["cases"])
    for mode in ("seq_direct", "seq_reload", "seq_restart"):
        rows = []
        for v in R[mode]["visits"]:
            for case, c in v["cases"].items():
                refs = [f[case]["per_request"] for f in fresh[v["label"]] if f[case] is not c]
                if mode == "seq_restart":
                    refs = [f[case]["per_request"] for f in fresh[v["label"]] if f[case]["per_request"] is not c["per_request"]]
                if not refs:
                    continue
                rows.append({"i": v["i"], "label": v["label"], "case": case,
                             "agree_with_fresh_mean": float(np.mean([agree(c["per_request"], r) for r in refs])),
                             "identical_to_some_fresh": any(c["sha256"] == f[case]["sha256"] for f in fresh[v["label"]]
                                                            if f[case]["per_request"] is not c["per_request"])})
        out["modes"][mode] = {"rows": rows, "by_case": {case: {
            "mean_agreement": float(np.mean([r["agree_with_fresh_mean"] for r in rows if r["case"] == case])),
            "min_agreement": float(np.min([r["agree_with_fresh_mean"] for r in rows if r["case"] == case])),
            "visits_bit_identical_to_a_fresh_visit": int(sum(r["identical_to_some_fresh"] for r in rows if r["case"] == case)),
            "visits": int(sum(1 for r in rows if r["case"] == case))} for case in ("greedy", "sampled", "constrained")}}
    # fresh vs fresh (run-to-run variation of freshly started engines on the same weights)
    ff = {}
    for lab, vs in fresh.items():
        for x, y in itertools.combinations(vs, 2):
            for case in x:
                ff.setdefault(case, []).append(agree(x[case]["per_request"], y[case]["per_request"]))
    out["fresh_vs_fresh"] = {c: {"pairs": len(v), "mean_agreement": float(np.mean(v)), "min": float(np.min(v))} for c, v in ff.items()}
    # cross-state: do different candidates actually change outputs? (greedy, first visits)
    first = {}
    for v in R["seq_restart"]["visits"]:
        first.setdefault(v["label"], v["cases"]["greedy"]["per_request"])
    out["greedy_agreement_with_gold_fresh"] = {k: agree(v, first["gold"]) for k, v in first.items()}
    for mode in ("seq_direct", "seq_reload", "seq_restart", "ext_direct"):
        trs = [v["transition"] for v in R[mode]["visits"][1:]]
        mem = [v["memory"]["allocated"] for v in R[mode]["visits"]]
        out["transitions"][mode] = {
            "n": len(trs), "modes_used": {m: sum(t.get("mode_used") == m for t in trs) for m in ("direct", "reload", "restart")},
            "verify_ok": all(t.get("verify_ok") for t in trs), "reset_ok": all(t.get("reset_prefix_cache_ok") for t in trs),
            "audits": len(R[mode]["audits"]), "audits_ok": all(x["ok"] for x in R[mode]["audits"]),
            "audit_s_median": float(np.median([x["seconds"] for x in R[mode]["audits"]])) if R[mode]["audits"] else None,
            "total_s": {m: {"median": float(np.median([t["total_s"] for t in trs if t.get("mode_used") == m])),
                            "max": float(np.max([t["total_s"] for t in trs if t.get("mode_used") == m])),
                            "n": sum(t.get("mode_used") == m for t in trs)}
                        for m in ("direct", "reload", "restart") if any(t.get("mode_used") == m for t in trs)},
            "per_transition": [{k: (round(t[k], 4) if isinstance(t.get(k), float) else t.get(k)) for k in
                                ("label", "mode_used", "entries", "tensors", "prepare_s", "export_s", "apply_s", "reset_s",
                                 "verify_s", "total_s", "verified_tensors", "unverifiable_runtime_tensors")} for t in trs],
            "memory_allocated_mib": {"first": mem[0] >> 20, "last": mem[-1] >> 20, "max": max(mem) >> 20, "min": min(mem) >> 20},
            "startup_s": R[mode]["startups_s"]}
    ext = R["ext_direct"]
    revis = [v for v in ext["visits"] if "same_as_first_visit" in v]
    cases_ext = sorted(ext["visits"][0]["cases"])
    out["extended"] = {"cases": cases_ext, "per_case_revisits_identical": {c: sum(v["same_as_first_visit"][c] for v in
                                                                             [x for x in ext["visits"] if "same_as_first_visit" in x])
                                                                         for c in cases_ext},
                       "transitions": len(ext["visits"]) - 1, "distinct_states": len({v["label"] for v in ext["visits"]}),
                       "revisits": len(revis), "revisits_greedy_identical": sum(v["same_as_first_visit"]["greedy"] for v in revis),
                       "gold_audits": len(ext["audits"]), "gold_audits_ok": sum(x["ok"] for x in ext["audits"]),
                       "wall_s": ext["wall_s"]}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("fresh_vs_fresh", "extended", "greedy_agreement_with_gold_fresh")}, indent=1))
    for m, x in out["modes"].items():
        print(m, json.dumps(x["by_case"]))
    for m, x in out["transitions"].items():
        print(m, {k: x[k] for k in ("n", "modes_used", "verify_ok", "audits_ok", "total_s", "memory_allocated_mib")})


if __name__ == "__main__":
    main()
