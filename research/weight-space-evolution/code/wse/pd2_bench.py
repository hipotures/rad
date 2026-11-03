"""Phase D benchmark v2 ("phaseD-v2"): instance generation, splits, manifests, tier rendering, scoring, baselines.

    python -m wse.pd2_bench generate --split pilot [--workers 24]     (wse environment; writes work/benchmarks/phaseD-v2)
    python -m wse.pd2_bench manifest --split pilot --out <json>       (public splits: full manifest; secret: aggregate)
    python -m wse.pd2_bench verify --split dev --n 6                   (regenerate instances, compare hashes)

Families: F1-F3 MLP classifiers (wse.pd2_mlp), F4 MinAtar policies (wse.pd2_policy), F5 algorithmic transformers
(wse.pd2_algo, held-out transfer family). Every instance stores the clean (reference) and damaged weights, the probe
and test data, the oracle (exact inverse) edit, its per-instance non-agent baselines, and the pre-rendered editor
prompts for every tier, so the evaluator needs neither the generators nor the test data to run an editor.

Splits (frozen in configs/phaseD_v2/benchmark_v2.json):
  pilot     calibration only (all subtypes incl. held-out ones and F5); used before freezing, never shown to parents
  dev       core subtypes F1-F4; the only material visible to parent-guided editing (editor-evaluation passes)
  select    core subtypes F1-F4, independent seeds; candidate selection by the harness/operator, never parent feedback
  test      core subtypes F1-F4, held-out instances; final scoring only
  transfer  held-out subtypes of F1-F4 + the whole F5 family; final scoring only
Seeds: sha256("phaseD-v2/<split>/<family>/<subtype>/<index>/<attempt>/<salt>"). The salt is empty for pilot/dev/select
and a secret (work/benchmarks/phaseD-v2/secret_salt.txt, not in Git; sha256 commitment in the frozen config) for
test/transfer, so held-out instances cannot be reproduced or inspected from the repository before the reveal.

Tiers: T0 select (4 complete edits; each instance is presented in 4 rotations so that the correct option appears once
at every position), T1 parameterize (subtype named, oracle template with every number blanked), T2 free-form (DSL),
T2P free-form with one budgeted diagnostic probe pass (trial edit -> probe-set feedback -> final edit).
"""
import argparse
import hashlib
import json
import os
import re
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from . import edit_dsl as E
from . import work_root

VERSION = "phaseD-v2"
TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC / "configs" / "phaseD_v2" / "benchmark_v2.json"
TIERS = ("T0", "T1", "T2", "T2P")
PUBLIC_SPLITS = ("pilot", "dev", "select")
SECRET_SPLITS = ("test", "transfer")


def fam_module(fam):
    if fam in ("F1", "F2", "F3"):
        from . import pd2_mlp as M
    elif fam == "F4":
        from . import pd2_policy as M
    else:
        from . import pd2_algo as M
    return M


def subtypes(fam):
    return fam_module(fam).SUBTYPES[fam]


def bench_dir():
    """work/benchmarks/phaseD-v2 (override with WSE_BENCH_DIR, e.g. for smoke tests)."""
    return Path(os.environ["WSE_BENCH_DIR"]) if os.environ.get("WSE_BENCH_DIR") else work_root() / "benchmarks" / VERSION


def salt(split):
    if split in PUBLIC_SPLITS:
        return ""
    p = bench_dir() / "secret_salt.txt"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(os.urandom(32).hex())
        p.chmod(0o400)
    return p.read_text().strip()


def salt_commitment():
    return hashlib.sha256(salt("test").encode()).hexdigest()


def seed_of(split, fam, sub, index, attempt):
    h = hashlib.sha256(f"{VERSION}/{split}/{fam}/{sub}/{index}/{attempt}/{salt(split)}".encode()).digest()
    return int.from_bytes(h[:8], "little")


def plan(split):
    """[(family, subtype, index)] for a split, from the frozen benchmark config (subtypes balanced by construction)."""
    cfg = json.loads(CONFIG.read_text())["splits"][split]
    out = []
    for fam, spec in cfg.items():
        core, held = subtypes(fam)
        subs = {"core": core, "held_out": held, "all": core + held}[spec["subtypes"]]
        for sub in subs:
            out += [(fam, sub, i) for i in range(spec["per_subtype"])]
    return out


# ------------------------------------------------------------------------------------------------ serialization
def _flat_data(data):
    arrays, meta = {}, {}
    for k, v in data.items():
        if isinstance(v, tuple):
            for i, a in enumerate(v):
                arrays[f"data.{k}.{i}"] = np.asarray(a)
        else:
            meta[k] = v
    return arrays, meta


def save(inst, d):
    arrays, meta = _flat_data(inst["data"])
    for k, v in inst["clean"].items():
        arrays[f"clean.{k}"] = v
    for k, v in inst["damaged"].items():
        arrays[f"damaged.{k}"] = v
    np.savez(d / f"{inst['id']}.npz", **arrays)
    rec = {k: v for k, v in inst.items() if k not in ("clean", "damaged", "data")}
    rec["data_meta"] = meta
    (d / f"{inst['id']}.json").write_text(json.dumps(rec, indent=1))


def load(split, iid):
    d = bench_dir() / split
    rec = json.loads((d / f"{iid}.json").read_text())
    with np.load(d / f"{iid}.npz", allow_pickle=False) as z:
        clean = {k[6:]: z[k] for k in z.files if k.startswith("clean.")}
        dmg = {k[8:]: z[k] for k in z.files if k.startswith("damaged.")}
        data = dict(rec["data_meta"])
        for k in z.files:
            if k.startswith("data."):
                _, name, i = k.split(".")
                data.setdefault(name, [None, None])
                data[name][int(i)] = z[k]
        data = {k: (tuple(v) if isinstance(v, list) and len(v) == 2 and isinstance(v[0], np.ndarray) else v)
                for k, v in data.items()}
    rec.update(clean=clean, damaged=dmg, data=data)
    return rec


def load_meta(split, iid):
    return json.loads((bench_dir() / split / f"{iid}.json").read_text())


# ------------------------------------------------------------------------------------------------ rendering
DSL_HELP = """EDIT LANGUAGE (one statement per line):
  NAME[i] = v | NAME[i] += v | NAME[i] -= v | NAME[i] *= v      (1-D tensors)
  NAME[i, j] = v (same operators; i or j may be ':' or 'a:b')     (2-D tensors)
  swap NAME[...] NAME[...]                                        (exchange two equal-shaped selections)
At most {ms} statements and {me} changed entries; |v| <= 100. Put the edit inside a ```edit fenced block."""
NUM_RX = r"-?\d{1,3}(\.\d{1,6})?"
IDX_RX = r"(\d{1,3}|:|\d{1,3}:\d{1,3})"


def head(inst, M):
    return ("You are repairing a small damaged neural network by editing its weights directly.\n\n"
            + M.probe_text(inst) + "\n\n")


def t2_regex(names, max_st=12):
    nm = "(" + "|".join(sorted(names, key=len, reverse=True)) + ")"
    sel = rf"{nm}\[{IDX_RX}(, {IDX_RX})?\]"
    st = rf"({sel} (=|\+=|-=|\*=) {NUM_RX}|swap {sel} {sel})"
    return rf"```edit\n({st}\n){{1,{max_st}}}```"


def t1_regex(tmpl):
    out, depth = [], 0
    for ch in tmpl:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        if ch == "?":
            out.append(r"\d{1,3}" if depth > 0 else NUM_RX)
        else:
            out.append(re.escape(ch))
    return "```edit\n" + "".join(out) + "\n```"


def render(inst, rng):
    """Prompts and structured-output constraints for every tier (stored with the instance)."""
    M = fam_module(inst["family"])
    hd = head(inst, M)
    lim = M.LIMITS
    help_ = DSL_HELP.format(ms=lim["max_statements"], me=lim["max_entries"])
    names = sorted(inst["damaged"])
    dis = M.distractors(inst, rng)
    assert len(dis) == 3 and inst["oracle"] not in dis, (inst["id"], dis)
    t0 = []
    for r in range(4):                       # rotation r: oracle at position r, distractors rotated as well
        opts = [dis[(r + k) % 3] for k in range(3)]
        opts.insert(r, inst["oracle"])
        body = "Which ONE of these edits repairs the defect(s)?\n\n" + "\n\n".join(
            f"Option {'ABCD'[i]}:\n{o}" for i, o in enumerate(opts))
        body += "\n\nAnswer with the option letter only, on the last line as: ANSWER: <letter>"
        t0.append({"prompt": hd + body, "options": opts, "correct": r})
    tmpl = M.template(inst)
    t1 = (hd + f"The defect type is: {M.SUBTYPE_TEXT[inst['subtype']]}.\nFill in the numbers (?) of this edit "
          f"template and output the completed edit in a ```edit fenced block:\n{tmpl}\n\n{help_}")
    t2 = hd + "The network has one or more defects in its weights. Find them and write an edit that repairs them.\n\n" + help_
    t2p = (hd + "The network has one or more defects in its weights. You may first submit ONE trial edit; the harness "
           "will apply it to a copy of the network and report its effect on the probe inputs only. Then you will "
           "submit your final edit.\n\n" + help_ + "\n\nSubmit your TRIAL edit now.")
    return {"T0": t0, "T1": {"prompt": t1, "regex": t1_regex(tmpl), "template": tmpl},
            "T2": {"prompt": t2, "regex": t2_regex(names)},
            "T2P": {"prompt": t2p, "regex": t2_regex(names),
                    "followup": "TRIAL RESULT: {feedback}\nNow submit your FINAL edit in a ```edit fenced block."}}


# ------------------------------------------------------------------------------------------------ scoring
def apply_edit(inst, text):
    M = fam_module(inst["family"])
    return E.run(inst["damaged"], text, **M.LIMITS)


def regression_eps(inst):
    return 0.02 if inst["family"] != "F4" else 0.05


def score_edit(inst, text, which="test"):
    """valid flag, metric, delta, recovery; invalid -> no-op (recovery 0). regression: recovery < -eps."""
    M = fam_module(inst["family"])
    r = apply_edit(inst, text) if text is not None else {"valid": False, "error": "no answer", "n_changed": 0}
    base = inst["damaged_metric"] if which == "test" else inst["damaged_probe_metric"]
    ceil = inst["ceiling"] if which == "test" else inst["ceiling_probe"]
    if not r["valid"]:
        return {"valid": False, "error": r["error"], "n_changed": 0, "metric": base, "delta": 0.0, "recovery": 0.0,
                "regression": False}
    m = M.metric(inst, r["edited"], which)
    rec = (m - base) / (ceil - base)
    return {"valid": True, "error": None, "n_changed": r["n_changed"], "metric": m, "delta": m - base,
            "recovery": rec, "regression": bool(rec < -regression_eps(inst))}


def probe_feedback(inst, text):
    M = fam_module(inst["family"])
    r = apply_edit(inst, text)
    if not r["valid"]:
        return f"the trial edit was invalid ({r['error']}); nothing was applied", False
    return M.probe_feedback(inst, r["edited"]), True


# ------------------------------------------------------------------------------------------------ baselines
def _best_on_probe(inst, edits):
    """Choose the edit with the best probe metric (non-agent selection; counts probe evaluations)."""
    M = fam_module(inst["family"])
    best, best_m, n = None, inst["damaged_probe_metric"], 0
    for e in edits:
        r = apply_edit(inst, e)
        if not r["valid"]:
            continue
        n += 1
        m = M.metric(inst, r["edited"], "probe")
        if m > best_m + 1e-9:
            best, best_m = e, m
    return best, n


def retarget(inst, text, rng):
    """Same statements with explicit indices moved to random valid targets, consistently: an index value that occurs
    several times on axes of the same length (e.g. W2[:, j] and b2[j]) maps to the same new index (matched random edit
    and T0 distractors keep the oracle's internal structure)."""
    w = inst["damaged"]
    mp = {}

    def r(tok, n):
        if tok == ":":
            return tok
        if ":" in tok:
            a, b = (int(x) for x in tok.split(":"))
            k = b - a
            key = (n, tok)
            if key not in mp:
                s = int(rng.integers(0, n - k + 1))
                mp[key] = f"{s}:{s + k}"
            return mp[key]
        key = (n, tok)
        if key not in mp:
            mp[key] = str(int(rng.integers(0, n)))
        return mp[key]

    def rep(m):
        name, i, j = m.group(1), m.group(2), m.group(3)
        sh = w[name].shape
        return f"{name}[{r(i, sh[0])}" + (f", {r(j, sh[1])}]" if j is not None else "]")
    return re.sub(r"(\w+)\[\s*([\d:]+)\s*(?:,\s*([\d:]+)\s*)?\]", rep, text)


def baselines(inst, rng):
    M = fam_module(inst["family"])
    sc = lambda e: score_edit(inst, e)["recovery"] if e else 0.0   # noqa: E731
    rnd = [sc(retarget(inst, inst["oracle"], rng)) for _ in range(8)]
    hs, ns = _best_on_probe(inst, M.simple_heuristic_edits(inst))
    hi, ni = _best_on_probe(inst, M.improved_heuristic_edits(inst))
    return {"noop": 0.0, "random_matched_mean": float(np.mean(rnd)), "random_matched": rnd,
            "heuristic_simple": sc(hs), "heuristic_simple_edit": hs, "heuristic_simple_probe_evals": ns,
            "heuristic_improved": sc(hi), "heuristic_improved_edit": hi, "heuristic_improved_probe_evals": ni,
            "oracle": inst["oracle_recovery"]}


# ------------------------------------------------------------------------------------------------ generation
def build_one(split, fam, sub, index):
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[k] = "1"
    os.environ["CUDA_VISIBLE_DEVICES"] = ""      # targets are CPU-only (F5 torch training must not touch the GPUs)
    M = fam_module(fam)
    t = time.time()
    errs = []
    for attempt in range(8):
        seed = seed_of(split, fam, sub, index, attempt)
        try:
            inst = M.build(fam, sub, seed)
            break
        except RuntimeError as ex:
            errs.append(str(ex))
    else:
        raise RuntimeError(f"{split}/{fam}/{sub}/{index}: no accepted instance: {errs}")
    iid = f"{fam}-{sub}-{split}-{index:03d}"
    inst.update(id=iid, family=fam, subtype=sub, split=split, index=index, attempt=attempt, rejected_attempts=errs,
                version=VERSION, held_out_subtype=sub in subtypes(fam)[1])
    inst["ceiling_probe"] = M.metric(inst, inst["clean"], "probe")
    inst["damaged_probe_metric"] = M.metric(inst, inst["damaged"], "probe")
    rng = np.random.default_rng([seed % 2 ** 32, 7])
    inst["tiers"] = render(inst, rng)
    inst["baselines"] = baselines(inst, rng)
    inst["t0_option_recovery"] = [score_edit(inst, o)["recovery"] for o in inst["tiers"]["T0"][0]["options"]]
    inst["gen_seconds"] = time.time() - t
    d = bench_dir() / split
    d.mkdir(parents=True, exist_ok=True)
    save(inst, d)
    return summary_row(inst, d)


def summary_row(inst, d):
    from .tensors import sha256_file
    return {"id": inst["id"], "family": inst["family"], "subtype": inst["subtype"], "index": inst["index"],
            "attempt": inst["attempt"], "held_out_subtype": inst["held_out_subtype"], "ceiling": inst["ceiling"],
            "damaged": inst["damaged_metric"], "oracle_recovery": inst["oracle_recovery"],
            "baselines": {k: v for k, v in inst["baselines"].items() if not isinstance(v, (list, str)) and v is not None},
            "t0_chance": float(np.mean(inst["t0_option_recovery"])), "gen_seconds": round(inst["gen_seconds"], 2),
            "npz_sha256": sha256_file(d / f"{inst['id']}.npz"), "json_sha256": sha256_file(d / f"{inst['id']}.json")}


def _job(args):
    try:
        return build_one(*args)
    except Exception as ex:   # noqa: BLE001
        return {"error": repr(ex), "job": list(args)}


def generate(split, workers):
    jobs = [(split, f, s, i) for f, s, i in plan(split)]
    d = bench_dir() / split
    todo = [j for j in jobs if not (d / f"{j[1]}-{j[2]}-{split}-{j[3]:03d}.json").exists()]
    t = time.time()
    par = [j for j in todo if j[1] != "F4"]
    with ProcessPoolExecutor(workers) as ex:      # F1-F3, F5: one instance per process (single-threaded BLAS)
        rows = list(ex.map(_job, par, chunksize=1))
    rows += [_job(j) for j in todo if j[1] == "F4"]   # F4 uses its own 16-process episode pool
    bad = [r for r in rows if "error" in r]
    print(f"{split}: {len(rows) - len(bad)} built, {len(bad)} failed, {len(jobs) - len(todo)} existing, {time.time() - t:.0f}s")
    for b in bad:
        print("FAILED", b)
    return rows


def manifest(split):
    d = bench_dir() / split
    from .tensors import sha256_file
    rows = []
    for f, s, i in plan(split):
        iid = f"{f}-{s}-{split}-{i:03d}"
        rec = json.loads((d / f"{iid}.json").read_text())
        rec.update(clean={}, damaged={})
        rows.append({"id": iid, "family": f, "subtype": s, "index": i, "attempt": rec["attempt"],
                     "held_out_subtype": rec["held_out_subtype"], "ceiling": rec["ceiling"],
                     "damaged": rec["damaged_metric"], "oracle_recovery": rec["oracle_recovery"],
                     "baselines": {k: v for k, v in rec["baselines"].items() if isinstance(v, (int, float)) and not isinstance(v, bool)},
                     "t0_chance": float(np.mean(rec["t0_option_recovery"])),
                     "npz_sha256": sha256_file(d / f"{iid}.npz"), "json_sha256": sha256_file(d / f"{iid}.json")})
    return rows


def aggregate(rows):
    out = {}
    for key in sorted({(r["family"], r["subtype"]) for r in rows}):
        rs = [r for r in rows if (r["family"], r["subtype"]) == key]
        out["/".join(key)] = {"n": len(rs), "ceiling": float(np.mean([r["ceiling"] for r in rs])),
                              "damaged": float(np.mean([r["damaged"] for r in rs])),
                              "oracle": float(np.mean([r["oracle_recovery"] for r in rs])),
                              **{b: float(np.mean([r["baselines"][b] for r in rs]))
                                 for b in ("random_matched_mean", "heuristic_simple", "heuristic_improved")},
                              "t0_chance": float(np.mean([r["t0_chance"] for r in rs]))}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    g = sp.add_parser("generate")
    g.add_argument("--split", required=True)
    g.add_argument("--workers", type=int, default=24)
    m = sp.add_parser("manifest")
    m.add_argument("--split", required=True)
    m.add_argument("--out", required=True)
    v = sp.add_parser("verify")
    v.add_argument("--split", required=True)
    v.add_argument("--n", type=int, default=6)
    a = ap.parse_args(argv)
    if a.cmd == "generate":
        generate(a.split, a.workers)
    elif a.cmd == "manifest":
        rows = manifest(a.split)
        body = {"version": VERSION, "split": a.split, "n": len(rows), "aggregate": aggregate(rows)}
        if a.split in PUBLIC_SPLITS:
            body["instances"] = rows
        else:   # held-out: only aggregate statistics and a hash of the full (secret) manifest
            full = json.dumps(rows, sort_keys=True).encode()
            (bench_dir() / f"manifest-{a.split}.json").write_bytes(full)
            body["manifest_sha256"] = hashlib.sha256(full).hexdigest()
            body["salt_sha256"] = salt_commitment()
        Path(a.out).write_text(json.dumps(body, indent=1))
        print(json.dumps(body["aggregate"], indent=1))
    elif a.cmd == "verify":
        rows = {r["id"]: r for r in manifest(a.split)}
        rng = np.random.default_rng(0)
        ids = rng.choice(sorted(rows), min(a.n, len(rows)), replace=False)
        ok = 0
        for iid in ids:
            meta = load_meta(a.split, iid)
            M = fam_module(meta["family"])
            inst = M.build(meta["family"], meta["subtype"], seed_of(a.split, meta["family"], meta["subtype"],
                                                                      meta["index"], meta["attempt"]))
            stored = load(a.split, iid)
            same = all(np.array_equal(inst["damaged"][k], stored["damaged"][k]) for k in inst["damaged"]) and \
                inst["oracle"] == stored["oracle"]
            ok += same
            print(iid, "identical" if same else "DIFFERENT")
        print(f"{ok}/{len(ids)} regenerated identically")


if __name__ == "__main__":
    main()
