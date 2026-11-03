"""Persistent vLLM evaluator with explicit model identity and validated candidate transitions.

One `PersistentEngine` owns one vLLM `LLM` (one GPU, TP = 1) that is started once on the immutable Gold text export.
Candidates are WSE patches (wse.patch, lineage relative to the same Gold). A transition current -> target is done by
one of three modes:

  direct      sparse in-place write of the changed BF16 entries into the runtime parameters (wse.vllm_ext), with
              before/after hash checks of every touched runtime tensor; falls back to `reload` (recorded) when a
              touched tensor is not byte-identical at runtime (fused/repacked parameters).
  reload      vLLM `reload_weights(weights_path=<full candidate checkpoint>)` (checkpoint exported on demand, cached).
  restart     shut the engine down and start a fresh one on the candidate checkpoint (reference/baseline mode).

After every transition: assert no unfinished requests, reset the prefix cache (KV blocks and the Mamba/GDN state
blocks cached with them; GDN per-request state is not persistent across requests), and verify the hashes of all
touched runtime tensors against the target state. `audit()` hashes every runtime parameter and compares it to the
Gold reference fingerprint taken at start (valid when the engine is at Gold) to detect cross-candidate contamination.

Usage (vLLM environment, PYTHONPATH=code):
    eng = PersistentEngine(gold_dir, engine_kwargs, mode="direct")
    eng.transition("p-4b2661ed6f35"); outs = eng.generate(prompts, params); eng.transition(None)  # back to Gold
"""
import json
import os
import shutil
import time
from pathlib import Path

import numpy as np

from . import patch, registry, work_root
from .tensors import sha256_array, sha256_file, st_header, st_save
from .vllm_ext import runtime_name

GOLD_ID = "qwen3.5-0.8B@2fc0636"
EXT = "wse.vllm_ext.WSEWorkerExtension"


def touched(pid):
    """Tensor names edited anywhere in a patch lineage (None = Gold -> empty)."""
    if pid is None:
        return set()
    return {t["name"] for p in patch.lineage(pid) for t in patch.load_patch(p)["tensors"]}


class StateCache:
    """Materialized touched tensors per state (Gold tensors loaded once, read-only)."""

    def __init__(self, gold_id):
        self.gold_id = gold_id
        self._gold, self._state = {}, {}

    def gold(self, names):
        miss = [n for n in names if n not in self._gold]
        if miss:
            self._gold.update(registry.load(self.gold_id, miss))
        return {n: self._gold[n] for n in names}

    def state(self, pid, names):
        """{name: uint16/raw array} for state pid (None = Gold) restricted to names."""
        out = {n: a for n, (dt, a) in self.gold(names).items()}
        if pid is not None:
            if pid not in self._state:
                if len(self._state) >= 4:      # small LRU: bounded host memory for large patches (p10c ~ 330 MB)
                    self._state.pop(next(iter(self._state)))
                self._state[pid] = patch.materialize(self.gold_id, pid, sorted(touched(pid)))
            else:
                self._state[pid] = self._state.pop(pid)
            for n in names:
                if n in self._state[pid]:
                    out[n] = self._state[pid][n][1]
        return out


def write_spec(path, cur, tgt, man):
    """Sparse transition spec (JSON + uncompressed npz) from current to target tensor states; returns summary."""
    arrays, tensors, entries = {}, [], 0
    for i, n in enumerate(sorted(tgt)):
        c, t = cur[n], tgt[n]
        assert c.shape == t.shape and c.dtype == t.dtype == np.uint16, f"{n}: only BF16 tensors are patchable"
        idx = np.flatnonzero(c.reshape(-1) != t.reshape(-1))
        if idx.size == 0:
            continue
        arrays[f"t{i}_idx"] = idx.astype(np.int64)
        arrays[f"t{i}_val"] = t.reshape(-1)[idx]
        tensors.append({"key": f"t{i}", "ckpt_name": n, "runtime_name": runtime_name(n), "shape": list(t.shape),
                        "before_sha256": sha256_array(c), "after_sha256": sha256_array(t),
                        "gold_sha256": man["tensors"][n]["sha256"], "entries": int(idx.size)})
        entries += int(idx.size)
    np.savez(str(path) + ".npz", **arrays)
    Path(str(path) + ".json").write_text(json.dumps({"npz": str(path) + ".npz", "tensors": tensors}))
    return {"tensors": len(tensors), "entries": entries}


class PersistentEngine:
    def __init__(self, gold_dir, engine_kwargs=None, mode="direct", gold_id=GOLD_ID, name="eng", verify=True):
        assert mode in ("direct", "reload", "restart")
        self.gold_dir, self.mode, self.gold_id, self.name, self.verify = str(gold_dir), mode, gold_id, name, verify
        self.kw = dict(model=self.gold_dir, dtype="bfloat16", seed=0, worker_extension_cls=EXT)
        self.kw.update(engine_kwargs or {})
        self.man = registry.manifest(gold_id)
        self.cache = StateCache(gold_id)
        self.scratch = work_root() / "swap" / f"{name}-{os.getpid()}"
        self.scratch.mkdir(parents=True, exist_ok=True)
        self.patchable = None
        self.log = []
        self.state = {"patch_id": None, "label": "gold"}
        self.startups = []
        self._start(self.gold_dir)
        self.gold_fingerprint = self.fingerprint()
        self._check_gold_identity()

    # ---------------------------------------------------------------- engine lifecycle
    def _start(self, model_dir):
        from vllm import LLM
        t = time.perf_counter()
        kw = dict(self.kw, model=str(model_dir))
        self.llm = LLM(**kw)
        self.startups.append(time.perf_counter() - t)
        if self.patchable is None:
            info = self.llm.collective_rpc("wse_param_info")[0]
            self.runtime_info = {n: s for n, s, *_ in info}

    def shutdown(self):
        try:
            self.llm.llm_engine.engine_core.shutdown()
        except Exception:  # noqa: BLE001
            pass
        shutil.rmtree(self.scratch, ignore_errors=True)

    def fingerprint(self, names=None):
        return self.llm.collective_rpc("wse_fingerprint", kwargs={"names": names})[0]["hashes"]

    def memory(self):
        return self.llm.collective_rpc("wse_memory")[0]

    def _check_gold_identity(self):
        """Classify every Gold language-model tensor as directly patchable (runtime bytes == checkpoint bytes)."""
        self.patchable = set()
        for n, rec in self.man["tensors"].items():
            r = runtime_name(n)
            if r in self.gold_fingerprint and self.gold_fingerprint[r] == rec["sha256"]:
                self.patchable.add(n)
        self.identity = {"runtime_params": len(self.gold_fingerprint), "byte_identical_to_gold": len(self.patchable)}

    # ---------------------------------------------------------------- candidates
    def _compatible(self, pid):
        if pid is None:
            return
        for p in patch.lineage(pid):
            rec = patch.load_patch(p)
            if rec["gold_id"] != self.gold_id:
                raise ValueError(f"{p}: patch is relative to {rec['gold_id']}, engine Gold is {self.gold_id}")
            for t in rec["tensors"]:
                if t["name"] not in self.man["tensors"] or list(self.man["tensors"][t["name"]]["shape"]) != t["shape"]:
                    raise ValueError(f"{p}: tensor {t['name']} {t['shape']} incompatible with Gold")

    def checkpoint_dir(self, pid):
        """Full text-only candidate checkpoint for reload/restart modes (exported once, cached under work/)."""
        if pid is None:
            return Path(self.gold_dir), 0.0
        d = work_root() / "derived" / "candidates" / pid
        if (d / "wse_export.json").exists():
            return d, 0.0
        t = time.perf_counter()
        tmp = d.with_name(pid + ".partial")
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        head, _ = st_header(registry.gold_dir(self.gold_id) / self.man["file"])
        names = sorted(k for k in head if k.startswith("model.language_model."))
        tensors = patch.materialize(self.gold_id, pid, names)
        st_save(tmp / "model.safetensors", tensors, {"format": "pt"})
        for f in os.listdir(self.gold_dir):
            if f != "model.safetensors" and (Path(self.gold_dir) / f).is_file() and f != "wse_export.json":
                shutil.copyfile(Path(self.gold_dir) / f, tmp / f)
        (tmp / "wse_export.json").write_text(json.dumps({"gold_id": self.gold_id, "patch_id": pid,
                                                         "model_sha256": sha256_file(tmp / "model.safetensors")}))
        tmp.rename(d)
        return d, time.perf_counter() - t

    def transition(self, pid, label=None):
        """Move the engine from its current state to candidate pid (None = Gold). Returns the timing record."""
        cur = self.state["patch_id"]
        rec = {"from": cur, "to": pid, "label": label or (pid or "gold"), "mode": self.mode}
        if pid == cur:
            rec.update(noop=True)
            self.log.append(rec)
            return rec
        self._compatible(pid)
        assert not self.llm.llm_engine.has_unfinished_requests(), "requests in flight during a transition"
        t0 = time.perf_counter()
        names = sorted(touched(cur) | touched(pid))
        mode = self.mode
        if mode == "direct" and not set(names) <= self.patchable:
            mode = "reload"
            rec["fallback"] = sorted(set(names) - self.patchable)[:8]
        rec["mode_used"] = mode
        if mode == "direct":
            cs, ts = self.cache.state(cur, names), self.cache.state(pid, names)
            spec = self.scratch / f"t{len(self.log):05d}"
            rec.update(write_spec(spec, cs, ts, self.man))
            rec["prepare_s"] = time.perf_counter() - t0
            r = self.llm.collective_rpc("wse_apply", kwargs={"spec_path": str(spec) + ".json", "verify": self.verify})[0]
            rec["apply_s"] = r["apply_s"]
            for ext in (".json", ".npz"):
                os.unlink(str(spec) + ext)
            expected = {runtime_name(n): sha256_array(ts[n]) for n in names}
        else:
            d, export_s = self.checkpoint_dir(pid)
            rec["prepare_s"] = time.perf_counter() - t0
            rec["export_s"] = export_s
            t1 = time.perf_counter()
            if mode == "reload":
                self.llm.collective_rpc("reload_weights", kwargs={"weights_path": str(d)})
            else:
                self.llm.llm_engine.engine_core.shutdown()
                del self.llm
                self._start(d)
            rec["apply_s"] = time.perf_counter() - t1
            ts = self.cache.state(pid, names)
            expected = {runtime_name(n): sha256_array(ts[n]) for n in names if n in self.patchable}
            # fused/repacked runtime tensors cannot be compared byte-wise; their identity rests on the checkpoint hash
            rec["unverifiable_runtime_tensors"] = len([n for n in names if n not in self.patchable])
        t2 = time.perf_counter()
        ok = self.llm.reset_prefix_cache()
        rec["reset_prefix_cache_ok"] = bool(ok)
        assert ok, "prefix cache reset refused (requests still running?)"
        rec["reset_s"] = time.perf_counter() - t2
        t3 = time.perf_counter()
        got = self.fingerprint(sorted(expected)) if expected else {}
        rec["verify_s"] = time.perf_counter() - t3
        bad = [n for n in expected if got.get(n) != expected[n]]
        rec["verified_tensors"] = len(expected)
        rec["verify_ok"] = not bad
        rec["total_s"] = time.perf_counter() - t0
        self.log.append(rec)
        if bad:
            raise RuntimeError(f"transition to {pid}: runtime tensors differ from the target state: {bad[:4]}")
        self.state = {"patch_id": pid, "label": rec["label"]}
        return rec

    def audit(self):
        """Full runtime fingerprint vs the Gold reference; only meaningful at Gold. Returns (ok, n_diff, seconds)."""
        assert self.state["patch_id"] is None, "audit compares against Gold; restore Gold first"
        t = time.perf_counter()
        fp = self.fingerprint()
        diff = [n for n in self.gold_fingerprint if fp.get(n) != self.gold_fingerprint[n]]
        return {"ok": not diff, "diff": diff[:8], "seconds": time.perf_counter() - t}

    def generate(self, prompts, params, reset_cache=True, **kw):
        """Generate with the current weights. reset_cache (default): reset the prefix cache first. Measured in
        runs/20261103T-persistent-swap-evaluator: with a cold prefix cache, sampled outputs are bit-reproducible
        run to run; after unrelated requests have populated the cache, prefix hits change chunking/batching and
        sampled texts differ (GDN layers do not support VLLM_BATCH_INVARIANT in vLLM 0.33)."""
        assert not self.llm.llm_engine.has_unfinished_requests()
        if reset_cache:
            assert self.llm.reset_prefix_cache(), "prefix cache reset refused"
        return self.llm.generate(prompts, params, use_tqdm=False, **kw)
