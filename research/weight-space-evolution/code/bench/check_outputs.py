"""Behavioural equivalence of benchmark outputs (workloads C/P) against a reference.

    python -m bench.check_outputs --campaign <id> --ref <config> --cand <config> [<config> ...] --out <json>
    python -m bench.check_outputs --campaign <id> --pilot <pilot generations.jsonl> --cand <config> --case P_free_max4096

For every case both sides ran, reports: identical-text share, first-divergence statistics and the Phase D score
(mean recovery and validity, strict, scored with wse.editor_tasks exactly as wse.pilot_rescore) of each side, so a
numerical/scheduling difference can be told apart from a change in experimental outcome. The pilot mode compares a
config's P_* texts with the saved generations of the original pilot run (same job and sample order).
"""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

TOPIC = Path(__file__).resolve().parents[2]
W = Path(os.environ.get("WSE_WORK_ROOT", TOPIC / "work"))
sys.path.insert(0, str(TOPIC / "code"))


def jobs():
    from wse import editor_tasks as K
    from wse import targets as T
    from wse.editor_pilot import TIERS
    out = []
    for f in T.FAMILIES:
        for i in range(16):
            inst = T.build(f, "pilot", i)
            for tier in TIERS:
                rng = np.random.default_rng([inst["seed"] % (2 ** 32), TIERS.index(tier)])
                out.append((inst, tier, K.render(inst, tier, rng)[1]))
    return out


def score(texts, J):
    from wse import editor_tasks as K
    rec, val = [], []
    for j, (inst, tier, meta) in enumerate(J):
        for k in range(4):
            e = K.evaluate_answer(inst, tier, texts[4 * j + k], meta)
            rec.append(float(e["recovery"]))
            val.append(bool(e["valid"]))
    return np.array(rec), np.array(val)


def compare(a, b, J):
    same = [x == y for x, y in zip(a, b)]
    div = []
    for x, y in zip(a, b):
        if x != y:
            n = next((i for i, (p, q) in enumerate(zip(x, y)) if p != q), min(len(x), len(y)))
            div.append(n)
    ra, va = score(a, J)
    rb, vb = score(b, J)
    d = rb - ra
    rng = np.random.default_rng(12345)
    bs = d[rng.integers(0, len(d), (2000, len(d)))].mean(1)
    return {"n": len(a), "identical_share": float(np.mean(same)),
            "first_divergence_char_median": float(np.median(div)) if div else None,
            "ref_mean_recovery": float(ra.mean()), "cand_mean_recovery": float(rb.mean()),
            "ref_valid": float(va.mean()), "cand_valid": float(vb.mean()),
            "recovery_diff": float(d.mean()), "recovery_diff_ci95": [float(np.percentile(bs, 2.5)),
                                                                   float(np.percentile(bs, 97.5))]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", required=True)
    ap.add_argument("--ref")
    ap.add_argument("--pilot")
    ap.add_argument("--case")
    ap.add_argument("--cand", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    raw = W / "raw" / a.campaign
    J = jobs()
    res = {}
    for c in a.cand:
        if a.pilot:
            ref = [json.loads(l)["output"] for l in open(a.pilot)]
            cand = json.loads((raw / f"{c}.{a.case}.texts.json").read_text())
            res[f"{c}/{a.case} vs pilot"] = compare(ref, cand, J)
            continue
        for tf in sorted(raw.glob(f"{a.ref}.*.texts.json")):
            case = tf.name[len(a.ref) + 1: -len(".texts.json")]
            cf = raw / f"{c}.{case}.texts.json"
            if cf.exists():
                res[f"{c}/{case} vs {a.ref}"] = compare(json.loads(tf.read_text()), json.loads(cf.read_text()), J)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    old = json.loads(Path(a.out).read_text()) if Path(a.out).exists() else {}
    old.update(res)
    Path(a.out).write_text(json.dumps(old, indent=1))
    for k, v in res.items():
        print(k, {x: (round(y, 4) if isinstance(y, float) else y) for x, y in v.items()})


if __name__ == "__main__":
    main()
