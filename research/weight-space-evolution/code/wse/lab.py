"""Editor-facing laboratory interface for one bounded weight-editing session (MinAtar policy target).

The editor may use ONLY these commands (every call is logged to <session>/log.jsonl with its result):

  python -m wse.lab --session S brief                 task text, rules, budgets, network description
  python -m wse.lab --session S status                budgets used / left, candidates, submission
  python -m wse.lab --session S stats NAME            summary statistics of a Gold tensor
  python -m wse.lab --session S show NAME 'SLICE'     values of a Gold tensor slice (numpy syntax, <= 4096 entries)
  python -m wse.lab --session S py FILE.py            run editor Python in the sandbox (1 python run)
  python -m wse.lab --session S propose --rationale T validate /work/edit/*.npy against Gold -> candidate patch id
  python -m wse.lab --session S devpass ID [--episodes N] [--trace K]
                                                     paired Gold-vs-candidate rollouts on fresh development seeds
                                                     (1 pass; ID = patch id or 'gold'); results in /work/pass_<k>/
  python -m wse.lab --session S submit ID             freeze the final candidate (no further passes/edits)

Admin only (never given to the editor):  init  (create a session from a config).

Held-out verification is a separate program (wse.heldout) run after submission on seeds drawn at that time.
"""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np

from . import minatar_eval as M
from . import patch, registry, work_root
from .sandbox import Sandbox

TOPIC = Path(__file__).resolve().parents[2]


def sdir(sid) -> Path:
    return work_root() / "sessions" / sid


@contextlib.contextmanager
def locked(sid):
    with open(sdir(sid) / ".lock", "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def jload(p):
    return json.loads(Path(p).read_text())


def jsave(p, obj):
    tmp = Path(str(p) + ".part")
    tmp.write_text(json.dumps(obj, indent=1))
    os.replace(tmp, p)


def log(sid, rec):
    rec = {"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **rec}
    with open(sdir(sid) / "log.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")


def sandbox_for(sid, cfg):
    d = sdir(sid)
    b = cfg["budgets"]
    return Sandbox(cfg["sandbox_venv"], d / "gold_view", d / "editor", d / "tmp", timeout=b["sandbox_timeout_s"],
                   mem=int(b["sandbox_mem_gib"] * (1 << 30)))


def forbidden_paths(sid):
    return [str(TOPIC.parents[1]), str(Path.home() / ".ssh"), str(work_root() / "sessions"),
            str(work_root() / "patches"), str(work_root() / "gold"), str(work_root() / "inputs")]


# ----------------------------------------------------------------------------------------------- admin
def init(sid, config_path):
    cfg = jload(config_path)
    d = sdir(sid)
    if d.exists():
        raise SystemExit(f"session {sid} exists; sessions are never overwritten")
    for sub in ("editor", "tmp", "gold_view"):
        (d / sub).mkdir(parents=True)
    cfg["sandbox_venv"] = str(Path(os.environ.get("WSE_SANDBOX_VENV", work_root() / "envs" / "sandbox")))
    cfg["config_file"] = str(Path(config_path).resolve())
    gold = registry.load(cfg["gold_id"])
    for k, (_, a) in gold.items():
        np.save(d / "gold_view" / f"{k}.npy", a)
    (d / "gold_view" / "description.json").write_text(json.dumps(
        {"shapes": {k: list(a.shape) for k, (_, a) in gold.items()}, "editable": cfg["policy"]["allowed_tensors"],
         "network": cfg["network_text"]}))
    for p in (d / "gold_view").iterdir():
        p.chmod(0o444)
    (d / "gold_view").chmod(0o555)
    jsave(d / "config.json", cfg)
    st = {"session": sid, "passes_used": 0, "python_runs_used": 0, "candidates": [], "submitted": None,
          "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    jsave(d / "state.json", st)
    checks = sandbox_for(sid, cfg).selftest(forbidden_paths(sid))
    st["sandbox_selftest"] = checks
    st["sandbox_ok"] = all(v is True for k, v in checks.items() if k != "output")
    jsave(d / "state.json", st)
    log(sid, {"cmd": "init", "config": cfg["config_file"], "sandbox_selftest": checks})
    print(json.dumps({"session": sid, "sandbox_ok": st["sandbox_ok"], "checks": checks}, indent=1))


# ----------------------------------------------------------------------------------------------- editor commands
def cmd_brief(sid, cfg, st, a):
    b = cfg["budgets"]
    txt = Path(TOPIC / cfg["brief_file"]).read_text()
    txt = txt.replace("{BUDGETS}", json.dumps(b, indent=1)).replace("{POLICY}", json.dumps(cfg["policy"], indent=1))
    if a.game_source:
        txt += "\n\n=== " + cfg.get("game_source_header",
                                "GAME SOURCE AND INPUT DESCRIPTION (upstream exp5 prompt, MinAtar 1.0.15, GPL-3.0)") + " ===\n"
        gs = (work_root() / cfg["game_source_file"]).read_bytes()
        if cfg.get("game_source_sha256") and hashlib.sha256(gs).hexdigest() != cfg["game_source_sha256"]:
            raise ValueError("game context file does not match the configured sha256")
        txt += gs.decode()
    return txt


def cmd_status(sid, cfg, st, a):
    b = cfg["budgets"]
    return json.dumps({"passes_used": st["passes_used"], "passes_left": b["dev_passes"] - st["passes_used"],
                       "python_runs_used": st["python_runs_used"],
                       "python_runs_left": b["python_runs"] - st["python_runs_used"],
                       "candidates": st["candidates"], "submitted": st["submitted"]}, indent=1)


def cmd_stats(sid, cfg, st, a):
    _, x = registry.load(cfg["gold_id"], [a.name])[a.name]
    x = x.astype(np.float64)
    return json.dumps({"name": a.name, "shape": list(x.shape), "mean": x.mean(), "std": x.std(), "min": x.min(),
                       "max": x.max(), "nonzero": int((x != 0).sum()), "abs_quantiles_50_90_99":
                       [float(np.quantile(np.abs(x), q)) for q in (0.5, 0.9, 0.99)]}, indent=1)


def parse_slice(text):
    """'3', '0:10', '::60, 5', '-1' -> tuple of int/slice (no evaluation of arbitrary code)."""
    parts = []
    for p in text.split(","):
        p = p.strip()
        if ":" in p:
            f = [int(x) if x.strip() else None for x in p.split(":")]
            if len(f) > 3:
                raise ValueError(f"bad slice {p!r}")
            parts.append(slice(*f))
        else:
            parts.append(int(p))
    return tuple(parts)


def cmd_show(sid, cfg, st, a):
    _, x = registry.load(cfg["gold_id"], [a.name])[a.name]
    sl = parse_slice(a.slice)
    v = x[sl]
    if np.size(v) > 4096:
        raise ValueError(f"slice has {np.size(v)} entries > 4096")
    with np.printoptions(precision=4, suppress=True, linewidth=160, threshold=5000):
        return f"{a.name}[{a.slice}] shape={np.shape(v)}\n{v}"


def cmd_py(sid, cfg, st, a):
    if st["submitted"]:
        raise ValueError("already submitted")
    if not st.get("sandbox_ok"):
        raise ValueError("sandbox self-test failed; editor code is not run (fail closed)")
    if st["python_runs_used"] >= cfg["budgets"]["python_runs"]:
        raise ValueError("python run budget exhausted")
    code = Path(a.file).read_text()
    st["python_runs_used"] += 1
    res = sandbox_for(sid, cfg).run(code)
    log(sid, {"cmd": "py", "run": st["python_runs_used"], "code": code, "result": res})
    return f"[python run {st['python_runs_used']} of {cfg['budgets']['python_runs']}, {res['seconds']} s, rc={res['returncode']}]\n{res['output']}"


def _proposed_from_editor(sid):
    d = sdir(sid) / "editor" / "edit"
    out = {}
    for f in sorted(d.glob("*.npy")) if d.is_dir() else []:
        out[f.stem] = np.load(f, allow_pickle=False).astype(np.float32)
    return out


def cmd_propose(sid, cfg, st, a):
    if st["submitted"]:
        raise ValueError("already submitted")
    proposed = _proposed_from_editor(sid)
    gold = registry.load(cfg["gold_id"])
    proposed = {k: v for k, v in proposed.items() if k not in gold or not np.array_equal(v, gold[k][1])}
    try:
        rec = patch.create(cfg["gold_id"], proposed, cfg["policy"],
                           meta={"method": "editor direct edit", "rationale": a.rationale, "session": sid,
                                 "editor": cfg.get("editor_identity")})
    except patch.PatchRefused as e:
        log(sid, {"cmd": "propose", "refused": str(e)})
        return f"REFUSED: {e}"
    if rec["patch_id"] not in st["candidates"]:
        st["candidates"].append(rec["patch_id"])
    pd = patch.patches_dir() / rec["patch_id"]
    shutil.copyfile(pd / "patch.json", sdir(sid) / "editor" / f"{rec['patch_id']}.json")
    log(sid, {"cmd": "propose", "patch_id": rec["patch_id"], "changed": rec["changed_entries_total"],
              "rationale": a.rationale})
    return json.dumps({"patch_id": rec["patch_id"], "changed_entries_total": rec["changed_entries_total"],
                       "delta_l2_total": rec["delta_l2_total"],
                       "tensors": {t["name"]: t["changed_entries"] for t in rec["tensors"]}}, indent=1)


def weights_of(cfg, pid):
    t = patch.materialize(cfg["gold_id"], None if pid == "gold" else pid)
    return {k: v for k, (_, v) in t.items()}


def cmd_devpass(sid, cfg, st, a):
    b = cfg["budgets"]
    if st["submitted"]:
        raise ValueError("already submitted")
    if st["passes_used"] >= b["dev_passes"]:
        raise ValueError("pass budget exhausted")
    if a.id != "gold" and a.id not in st["candidates"]:
        raise ValueError(f"unknown candidate {a.id}; propose first")
    n = min(a.episodes or b["episodes_per_pass_max"], b["episodes_per_pass_max"])
    k = st["passes_used"] + 1
    seeds = list(range(cfg["dev_seed_base"] + 10_000 * k, cfg["dev_seed_base"] + 10_000 * k + n))
    trace = seeds[: min(a.trace, b["trace_episodes_max"])]
    wk = cfg.get("eval_workers", 6)
    gs, ge = M.evaluate(cfg["game"], weights_of(cfg, "gold"), seeds, trace_seeds=trace, workers=wk)
    out = {"pass": k, "candidate": a.id, "episodes": n, "gold": gs}
    if a.id != "gold":
        cs, ce = M.evaluate(cfg["game"], weights_of(cfg, a.id), seeds, trace_seeds=trace, workers=wk)
        out.update(candidate_summary=cs, paired=M.paired(ge, ce))
    else:
        ce = None
    st["passes_used"] = k
    pdir = sdir(sid) / "editor" / f"pass_{k}"
    pdir.mkdir()
    (pdir / "summary.json").write_text(json.dumps(out, indent=1))
    (pdir / "gold_episodes.json").write_text(json.dumps(ge))
    if ce is not None:
        (pdir / "candidate_episodes.json").write_text(json.dumps(ce))
    log(sid, {"cmd": "devpass", "pass": k, "candidate": a.id, "seeds": [seeds[0], seeds[-1]], "summary": out})
    return f"[pass {k} of {b['dev_passes']}; per-episode files and traces in /work/pass_{k}/]\n" + json.dumps(out, indent=1)


def cmd_submit(sid, cfg, st, a):
    if st["submitted"]:
        raise ValueError("already submitted")
    if a.id not in st["candidates"]:
        raise ValueError(f"unknown candidate {a.id}")
    st["submitted"] = a.id
    st["submitted_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log(sid, {"cmd": "submit", "patch_id": a.id})
    return f"SUBMITTED {a.id}. The session is closed."


CMDS = {"brief": cmd_brief, "status": cmd_status, "stats": cmd_stats, "show": cmd_show, "py": cmd_py,
        "propose": cmd_propose, "devpass": cmd_devpass, "submit": cmd_submit}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="wse.lab")
    ap.add_argument("--session", required=True)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init")
    p.add_argument("config")
    p = sp.add_parser("brief")
    p.add_argument("--game-source", action="store_true")
    sp.add_parser("status")
    p = sp.add_parser("stats")
    p.add_argument("name")
    p = sp.add_parser("show")
    p.add_argument("name")
    p.add_argument("slice")
    p = sp.add_parser("py")
    p.add_argument("file")
    p = sp.add_parser("propose")
    p.add_argument("--rationale", required=True)
    p = sp.add_parser("devpass")
    p.add_argument("id")
    p.add_argument("--episodes", type=int)
    p.add_argument("--trace", type=int, default=0)
    p = sp.add_parser("submit")
    p.add_argument("id")
    a = ap.parse_args(argv)
    if a.cmd == "init":
        return init(a.session, a.config)
    if not (sdir(a.session) / "state.json").exists():
        raise SystemExit(f"no session {a.session}")
    with locked(a.session):
        cfg = jload(sdir(a.session) / "config.json")
        st = jload(sdir(a.session) / "state.json")
        try:
            out = CMDS[a.cmd](a.session, cfg, st, a)
            ok = True
        except (ValueError, KeyError, IndexError, FileNotFoundError, AssertionError) as e:
            out, ok = f"ERROR: {type(e).__name__}: {e}", False
        jsave(sdir(a.session) / "state.json", st)
        if a.cmd in ("brief", "status", "stats", "show") or not ok:
            log(a.session, {"cmd": a.cmd, "args": {k: v for k, v in vars(a).items() if k not in ("cmd", "session")},
                            "ok": ok, "output_chars": len(out), "error": None if ok else out})
    print(out)


if __name__ == "__main__":
    main()
