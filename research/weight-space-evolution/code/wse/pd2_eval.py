"""Phase D v2 editor evaluation on a persistent vLLM engine per GPU, with a file-based job queue.

    # register editors (Gold E0 + candidate patches) once:  configs/phaseD_v2/editors.json
    python -m wse.pd2_eval submit --queue <dir> --editors E0,p50c --split pilot [--tiers T0,T1,T2,T2P]
    CUDA_VISIBLE_DEVICES=<i> python -m wse.pd2_eval worker --queue <dir> --campaign <id> [--swap-mode direct]
        [--engine-json '{...}'] [--follow]            (vLLM environment; one worker per GPU)

A worker starts one engine on Gold (wse.swap_engine.PersistentEngine) and then repeatedly claims a job (atomic
rename pending/ -> running/), moves the engine to the job's editor state (validated transition, caches reset),
generates the editor's answers for every instance x tier of the split, hands them to a scoring thread (scoring and
result persistence overlap with the next job's generation), and finally returns to Gold and runs a full fingerprint
audit. Jobs can be submitted while workers run (`--follow` keeps polling until a STOP file appears), so future parent
sessions can enqueue candidates while earlier ones are being evaluated. Held-out splits (test, transfer) are refused
unless --allow-heldout is given (final scoring only).

Decoding (frozen protocol): non-thinking chat template, temperature 0.7, top-p 0.8, top-k 20, all tiers constrained:
T0 one of 'ANSWER: A'..'ANSWER: D' (4 rotations x 1 sample, seeds 0-3); T1 the instance's template regex; T2 the
instance's DSL regex (n = 4, seed 0); T2P trial (n = 4, seed 0, DSL regex) -> probe-set feedback -> final answer
(n = 1 per trial, seed 1, DSL regex). Invalid edits are scored as no-ops (recovery 0) and reported as invalid.
"""
import argparse
import hashlib
import json
import os
import queue as qmod
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wse import work_root  # noqa: E402

TOPIC = Path(__file__).resolve().parents[2]
EDITORS = TOPIC / "configs" / "phaseD_v2" / "editors.json"
VERSION = "phaseD-v2"
DECODE = {"temperature": 0.7, "top_p": 0.8, "top_k": 20}
MAX_TOKENS = {"T0": 8, "T1": 256, "T2": 384, "T2P": 384}
HELDOUT = ("test", "transfer")
ENGINE_PROFILES = {   # profile3 = validated Phase D profile (runs/20261103T-vllm-perf-32k); default = vLLM defaults
    "profile3": {"max_model_len": 32768, "gpu_memory_utilization": 0.85, "attention_backend": "FLASHINFER",
                 "max_num_seqs": 1024, "max_num_batched_tokens": 16384},
    "default": {"max_model_len": 32768, "gpu_memory_utilization": 0.85}}


def bench_dir():
    return Path(os.environ["WSE_BENCH_DIR"]) if os.environ.get("WSE_BENCH_DIR") else work_root() / "benchmarks" / VERSION


def editors():
    return {e["editor_id"]: e for e in json.loads(EDITORS.read_text())["editors"]}


class Scorer:
    """Client of wse.pd2_scorer running in the wse environment (separate interpreter)."""

    def __init__(self):
        py = str(work_root() / "envs" / "wse" / "bin" / "python")
        env = dict(os.environ, PYTHONPATH=str(TOPIC / "code"), OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
        env.pop("CUDA_VISIBLE_DEVICES", None)
        self.p = subprocess.Popen([py, "-m", "wse.pd2_scorer"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  text=True, env=env, cwd=str(TOPIC / "code"))
        self.lock = threading.Lock()
        self.call({"op": "ping"})

    def call(self, req):
        with self.lock:
            self.p.stdin.write(json.dumps(req) + "\n")
            self.p.stdin.flush()
            while True:
                line = self.p.stdout.readline()
                if not line:
                    raise RuntimeError("scorer exited")
                if line.startswith("@@"):
                    return json.loads(line[2:])

    def close(self):
        """EOF on stdin; a scorer still tearing down its episode pool after 30 s is killed (results are already
        persisted at this point; seen once in the restart-mode throughput run)."""
        self.p.stdin.close()
        try:
            self.p.wait(timeout=30)
        except subprocess.TimeoutExpired:
            self.p.kill()
            self.p.wait()


def load_split(split, ids=None):
    d = bench_dir() / split
    out = []
    for f in sorted(d.glob("*.json")):
        m = json.loads(f.read_text())
        if ids is None or m["id"] in ids:
            out.append(m)
    return out


def chat(tok, msgs):
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)


def sp(n, seed, max_tokens, regex=None, choice=None):
    from vllm import SamplingParams
    from vllm.sampling_params import StructuredOutputsParams
    so = StructuredOutputsParams(choice=choice) if choice else StructuredOutputsParams(regex=regex)
    return SamplingParams(n=n, seed=seed, max_tokens=max_tokens, structured_outputs=so, **DECODE)


def extract_edit(text):
    import re
    m = re.search(r"```(?:edit)?\s*\n(.*?)```", text, re.S)
    return m.group(1).strip() if m else text


def generate_editor(eng, tok, insts, tiers, scorer_fb, split):
    """Generate all answers of the engine's current editor. Returns (rows without scores, stats)."""
    reqs, meta = [], []
    for inst in insts:
        T = inst["tiers"]
        if "T0" in tiers:
            for r, rot in enumerate(T["T0"]):
                reqs.append((chat(tok, [{"role": "user", "content": rot["prompt"]}]),
                             sp(1, r, MAX_TOKENS["T0"], choice=[f"ANSWER: {c}" for c in "ABCD"])))
                meta.append(("T0", inst, {"rotation": r}))
        if "T1" in tiers:
            reqs.append((chat(tok, [{"role": "user", "content": T["T1"]["prompt"]}]), sp(4, 0, MAX_TOKENS["T1"], T["T1"]["regex"])))
            meta.append(("T1", inst, {}))
        for tier in ("T2", "T2P"):
            if tier in tiers:
                reqs.append((chat(tok, [{"role": "user", "content": T[tier]["prompt"]}]),
                             sp(4, 0, MAX_TOKENS[tier], T[tier]["regex"])))
                meta.append((tier, inst, {}))
    t = time.perf_counter()
    outs = eng.generate([r[0] for r in reqs], [r[1] for r in reqs])
    gen1 = time.perf_counter() - t
    rows, stats = [], {"prompt_tokens": 0, "gen_tokens": 0, "requests": len(reqs), "generate_s": gen1,
                       "probe_passes": 0, "feedback_s": 0.0, "round2_s": 0.0}
    t2p = []
    for (tier, inst, extra), o in zip(meta, outs):
        stats["prompt_tokens"] += len(o.prompt_token_ids) * len(o.outputs)
        for k, c in enumerate(o.outputs):
            stats["gen_tokens"] += len(c.token_ids)
            row = {"id": inst["id"], "family": inst["family"], "subtype": inst["subtype"], "tier": tier,
                   "sample": extra.get("rotation", k), "text": c.text, "gen_tokens": len(c.token_ids),
                   "finish": c.finish_reason}
            if tier == "T0":
                rot = inst["tiers"]["T0"][extra["rotation"]]
                ans = c.text.strip()[-1:] if c.text.strip()[-1:] in "ABCD" and c.text.strip() else None
                row.update(answer=ans, correct="ABCD"[rot["correct"]],
                           edit=rot["options"]["ABCD".index(ans)] if ans else None)
            elif tier == "T2P":
                row["trial_edit"] = extract_edit(c.text)
                t2p.append((row, inst, o.prompt))
            else:
                row["edit"] = extract_edit(c.text)
            rows.append(row)
    if t2p:   # one budgeted probe pass per T2P sample, then the final answer
        t = time.perf_counter()
        fb = scorer_fb.call({"op": "feedback", "split": split, "items": [
            {"key": str(i), "id": inst["id"], "edit": row["trial_edit"]} for i, (row, inst, _) in enumerate(t2p)]})
        stats["feedback_s"] = time.perf_counter() - t
        stats["probe_passes"] = len(t2p)
        reqs2 = []
        for i, (row, inst, _) in enumerate(t2p):
            f = fb["results"][str(i)]
            row["trial_valid"], row["feedback"] = f["valid"], f["feedback"]
            msgs = [{"role": "user", "content": inst["tiers"]["T2P"]["prompt"]},
                    {"role": "assistant", "content": row["text"]},
                    {"role": "user", "content": inst["tiers"]["T2P"]["followup"].format(feedback=f["feedback"])}]
            reqs2.append((chat(tok, msgs), sp(1, 1, MAX_TOKENS["T2P"], inst["tiers"]["T2P"]["regex"])))
        t = time.perf_counter()
        outs2 = eng.generate([r[0] for r in reqs2], [r[1] for r in reqs2])
        stats["round2_s"] = time.perf_counter() - t
        for (row, _, _), o in zip(t2p, outs2):
            c = o.outputs[0]
            stats["prompt_tokens"] += len(o.prompt_token_ids)
            stats["gen_tokens"] += len(c.token_ids)
            row["gen_tokens"] += len(c.token_ids)
            row["final_text"] = c.text
            row["edit"] = extract_edit(c.text)
    return rows, stats


def score_rows(scorer, split, rows):
    t = time.perf_counter()
    items = [{"key": str(i), "id": r["id"], "edit": r.get("edit")} for i, r in enumerate(rows)]
    res = scorer.call({"op": "score", "split": split, "which": "test", "items": items})["results"]
    for i, r in enumerate(rows):
        r.update(res[str(i)])
    return time.perf_counter() - t


def summarize(rows):
    out = {}
    for key in sorted({(r["family"], r["tier"]) for r in rows}):
        rs = [r for r in rows if (r["family"], r["tier"]) == key]
        v = np.array([r["recovery"] for r in rs], float)
        out["/".join(key)] = {"n": len(rs), "mean_recovery": float(v.mean()),
                              "valid_rate": float(np.mean([r["valid"] for r in rs])),
                              "effective_rate": float(np.mean(v >= 0.5)), "full_repair_rate": float(np.mean(v >= 0.9)),
                              "regression_rate": float(np.mean([r["regression"] for r in rs])),
                              "gen_tokens": int(sum(r["gen_tokens"] for r in rs))}
    return out


def claim(qdir, tag):
    for f in sorted((qdir / "pending").glob("*.json")):
        dst = qdir / "running" / f"{f.stem}.{tag}.json"
        try:
            os.rename(f, dst)
            return dst
        except FileNotFoundError:
            continue
    return None


def worker(a):
    from transformers import AutoTokenizer
    from wse.swap_engine import PersistentEngine
    qdir = Path(a.queue)
    for s in ("pending", "running", "done", "failed"):
        (qdir / s).mkdir(parents=True, exist_ok=True)
    raw = work_root() / "raw" / a.campaign
    raw.mkdir(parents=True, exist_ok=True)
    tag = f"gpu{os.environ.get('CUDA_VISIBLE_DEVICES', '0')}"
    gold_dir = str(work_root() / "derived" / "qwen3.5-0.8B-text-gold")
    t0 = time.perf_counter()
    eng = PersistentEngine(gold_dir, {**ENGINE_PROFILES[a.engine_profile], **json.loads(a.engine_json)}, mode=a.swap_mode,
                           name=f"pd2-{tag}")
    tok = AutoTokenizer.from_pretrained(gold_dir)
    scorer, scorer_fb = Scorer(), Scorer()
    log = {"worker": tag, "swap_mode": a.swap_mode, "engine_profile": a.engine_profile, "engine": {k: v for k, v in eng.kw.items()}, "identity": eng.identity,
           "startup_s": eng.startups[0], "init_s": time.perf_counter() - t0, "jobs": []}
    ed = editors()
    jobs_q = qmod.Queue()
    split_cache = {}

    def scoring_thread():
        while True:
            item = jobs_q.get()
            if item is None:
                return
            job, rows, rec, jf = item
            try:
                rec["score_s"] = score_rows(scorer, job["split"], rows)
                t = time.perf_counter()
                with open(raw / f"{job['job_id']}.jsonl", "w") as f:
                    for r in rows:
                        f.write(json.dumps(r) + "\n")
                rec["summary"] = summarize(rows)
                (raw / f"{job['job_id']}.summary.json").write_text(json.dumps(rec, indent=1))
                rec["persist_s"] = time.perf_counter() - t
                os.rename(jf, qdir / "done" / jf.name)
            except Exception as ex:   # noqa: BLE001
                rec["error"] = repr(ex)
                os.rename(jf, qdir / "failed" / jf.name)
            rec["completed_at"] = time.time()

    th = threading.Thread(target=scoring_thread, daemon=True)
    th.start()
    idle_since = None
    while True:
        jf = claim(qdir, tag)
        if jf is None:
            if not a.follow or (qdir / "STOP").exists():
                break
            idle_since = idle_since or time.time()
            time.sleep(1.0)
            continue
        idle_since = None
        job = json.loads(jf.read_text())
        rec = {"job_id": job["job_id"], "editor_id": job["editor_id"], "split": job["split"], "tiers": job["tiers"],
               "worker": tag, "claimed_at": time.time()}
        try:
            if job["split"] in HELDOUT and not a.allow_heldout:
                raise PermissionError("held-out split refused (final scoring only; use --allow-heldout)")
            e = ed[job["editor_id"]]
            tr = eng.transition(e.get("patch_id"), label=job["editor_id"])
            rec["transition"] = {k: v for k, v in tr.items() if not isinstance(v, list)}
            rec["editor"] = e
            rec["engine_state"] = dict(eng.state)
            if job["split"] not in split_cache:
                split_cache[job["split"]] = load_split(job["split"])
            insts = split_cache[job["split"]]
            if job.get("ids"):
                insts = [i for i in insts if i["id"] in set(job["ids"])]
            rec["instances"] = len(insts)
            rows, stats = generate_editor(eng, tok, insts, job["tiers"], scorer_fb, job["split"])
            for r in rows:
                r["editor_id"] = job["editor_id"]
            rec["gen"] = stats
            rec["generated_at"] = time.time()
            rec["benchmark"] = {"version": VERSION, "split": job["split"], "decode": DECODE, "max_tokens": MAX_TOKENS}
            jobs_q.put((job, rows, rec, jf))
        except Exception as ex:   # noqa: BLE001
            rec["error"] = repr(ex)
            os.rename(jf, qdir / "failed" / jf.name)
            (raw / f"{job['job_id']}.summary.json").write_text(json.dumps(rec, indent=1))
        log["jobs"].append(rec)
    jobs_q.put(None)
    th.join()
    t = time.perf_counter()
    log["final_transition"] = eng.transition(None, label="gold")
    log["final_audit"] = eng.audit()
    log["final_memory"] = eng.memory()
    log["transitions"] = eng.log
    log["wall_s"] = time.perf_counter() - t0
    (raw / f"worker-{tag}-{int(t0)}.json").write_text(json.dumps(log, indent=1, default=str))
    scorer.close()
    scorer_fb.close()
    eng.shutdown()
    print(json.dumps({"worker": tag, "jobs": len(log["jobs"]), "audit": log["final_audit"]["ok"], "wall_s": log["wall_s"]}))
    os._exit(0)


def submit(a):
    qdir = Path(a.queue)
    (qdir / "pending").mkdir(parents=True, exist_ok=True)
    ed = editors()
    for eid in a.editors.split(","):
        assert eid in ed, f"unknown editor {eid}"
        jid = f"{a.prefix}{eid}__{a.split}"
        job = {"job_id": jid, "editor_id": eid, "split": a.split, "tiers": a.tiers.split(","),
               "ids": a.ids.split(",") if a.ids else None, "submitted_at": time.time()}
        tmp = qdir / "pending" / f".{jid}.tmp"
        tmp.write_text(json.dumps(job))
        os.rename(tmp, qdir / "pending" / f"{a.order:04d}-{jid}.json")
        a.order += 1
        print("submitted", jid)


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp_ = ap.add_subparsers(dest="cmd", required=True)
    s = sp_.add_parser("submit")
    s.add_argument("--queue", required=True)
    s.add_argument("--editors", required=True)
    s.add_argument("--split", required=True)
    s.add_argument("--tiers", default="T0,T1,T2,T2P")
    s.add_argument("--ids", default="")
    s.add_argument("--prefix", default="")
    s.add_argument("--order", type=int, default=0)
    w = sp_.add_parser("worker")
    w.add_argument("--queue", required=True)
    w.add_argument("--campaign", required=True)
    w.add_argument("--swap-mode", default="direct", choices=("direct", "reload", "restart"))
    w.add_argument("--engine-profile", default="profile3", choices=sorted(ENGINE_PROFILES))
    w.add_argument("--engine-json", default="{}", help="extra LLM kwargs on top of the profile")
    w.add_argument("--follow", action="store_true")
    w.add_argument("--allow-heldout", action="store_true")
    a = ap.parse_args(argv)
    submit(a) if a.cmd == "submit" else worker(a)


if __name__ == "__main__":
    main()
