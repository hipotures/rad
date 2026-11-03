"""Scoring service for Phase D v2 editor outputs (wse environment; JSON lines on stdin/stdout).

The vLLM evaluator process never loads target networks or test data; it sends edit texts here. Requests:
  {"op": "score", "split": s, "which": "test"|"probe", "items": [{"key": k, "id": iid, "edit": text|null}]}
  {"op": "feedback", "split": s, "items": [{"key": k, "id": iid, "edit": text}]}     (T2P probe pass, probe set only)
  {"op": "ping"}
Every response is one line prefixed with '@@' (anything else on stdout is ignored by the client). Results are cached
by (split, id, which, sha256(edit)).
"""
import hashlib
import json
import sys
import time

from . import pd2_bench as B


def main():
    out = sys.stdout
    sys.stdout = sys.stderr          # keep library prints off the protocol channel
    insts, cache = {}, {}

    def inst(split, iid):
        if (split, iid) not in insts:
            insts[(split, iid)] = B.load(split, iid)
        return insts[(split, iid)]

    for line in sys.stdin:
        req = json.loads(line)
        t = time.perf_counter()
        res = {}
        if req["op"] == "ping":
            pass
        elif req["op"] == "score":
            for it in req["items"]:
                h = hashlib.sha256((it["edit"] or "\0").encode()).hexdigest()
                k = (req["split"], it["id"], req["which"], h)
                if k not in cache:
                    ins = inst(req["split"], it["id"])
                    opts = ins["tiers"]["T0"][0]["options"]
                    if req["which"] == "test" and it["edit"] in opts:   # T0 option: test score computed at generation
                        rec = ins["t0_option_recovery"][opts.index(it["edit"])]
                        r = B.apply_edit(ins, it["edit"])
                        base, ceil = ins["damaged_metric"], ins["ceiling"]
                        cache[k] = {"valid": True, "error": None, "n_changed": r["n_changed"],
                                    "metric": base + rec * (ceil - base), "delta": rec * (ceil - base),
                                    "recovery": rec, "regression": bool(rec < -B.regression_eps(ins)), "cached_t0": True}
                    else:
                        cache[k] = B.score_edit(ins, it["edit"], req["which"])
                res[it["key"]] = cache[k]
        elif req["op"] == "feedback":
            for it in req["items"]:
                fb, ok = B.probe_feedback(inst(req["split"], it["id"]), it["edit"])
                res[it["key"]] = {"feedback": fb, "valid": ok}
        out.write("@@" + json.dumps({"results": res, "seconds": time.perf_counter() - t}) + "\n")
        out.flush()


if __name__ == "__main__":
    main()
