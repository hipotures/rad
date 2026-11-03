"""Isolated execution of editor-submitted Python (bubblewrap), adapted from upstream harness/sandbox.py.

Inside the sandbox:  /gold  read-only Gold tensors (.npy) and description;  /work  read-write editor folder (kept
between runs);  /tmp  a disk-backed per-session directory (not tmpfs);  python = a numpy-only venv (no torch, no
autograd, no game simulator). No network (all namespaces unshared), clean environment, no host home, no Git, no
secrets. Per run: wall-clock timeout, address-space, CPU-time and file-size limits; own PID namespace
(killed with the parent); output truncated.

selftest() probes the isolation; callers must refuse to run editor code unless every check passes (fail closed).
"""
import json
import os
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path

PRELUDE = r'''
import json, os, numpy as np
np.set_printoptions(precision=4, suppress=True, linewidth=160)
GOLD, WORK = "/gold", "/work"
_D = json.load(open(GOLD + "/description.json"))
SHAPES = {k: tuple(v) for k, v in _D["shapes"].items()}
NAMES = list(SHAPES)
EDITABLE = _D["editable"]
def gold(name):
    """Read-only Gold tensor (float32)."""
    a = np.load(f"{GOLD}/{name}.npy"); a.setflags(write=False); return a
def load(name):
    """Current proposed tensor: /work/edit/<name>.npy if saved, else Gold."""
    p = f"{WORK}/edit/{name}.npy"
    return np.load(p) if os.path.exists(p) else gold(name).copy()
def save(name, a):
    assert name in EDITABLE, f"{name} is not editable; EDITABLE = {EDITABLE}"
    a = np.asarray(a, np.float32)
    assert a.shape == SHAPES[name], (name, a.shape, SHAPES[name])
    assert np.isfinite(a).all(), name
    os.makedirs(f"{WORK}/edit", exist_ok=True); np.save(f"{WORK}/edit/{name}.npy", a)
def reset(name=None):
    """Drop saved edits (one tensor or all)."""
    for n in ([name] if name else NAMES):
        p = f"{WORK}/edit/{n}.npy"
        if os.path.exists(p): os.remove(p)
def saved():
    d = f"{WORK}/edit"
    return sorted(f[:-4] for f in os.listdir(d)) if os.path.isdir(d) else []
'''


VENV_MOUNT = "/opt/venv"


class SandboxUnavailable(RuntimeError):
    pass


def _python_roots(venv: Path):
    """(host source, sandbox path) pairs: the venv and the base interpreter it links to, both under the literal
    symlink path and the resolved path (uv links through a versionless directory symlink)."""
    pairs = [(venv, Path(VENV_MOUNT))]   # neutral mount point: the host path may lie inside the repository
    link = venv / "bin" / "python"
    lit = Path(os.readlink(link)) if link.is_symlink() else link
    lit = lit if lit.is_absolute() else (link.parent / lit)
    for root in {lit.parents[1], Path(os.path.realpath(lit)).parents[1]}:
        pairs.append((Path(os.path.realpath(root)), root))
    return pairs


def _limits(mem, cpu, fsize, nproc):
    def f():
        resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
        resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
        resource.setrlimit(resource.RLIMIT_FSIZE, (fsize, fsize))
        if nproc:  # RLIMIT_NPROC counts every process of the host user, so it is off by default
            resource.setrlimit(resource.RLIMIT_NPROC, (nproc, nproc))
    return f


class Sandbox:
    def __init__(self, venv, gold_view, work_dir, tmp_dir, timeout=120, mem=4 << 30, max_out=20_000,
                 fsize=1 << 30, nproc=None, threads=4):
        self.venv = Path(venv)
        self.gold_view, self.work_dir, self.tmp_dir = Path(gold_view), Path(work_dir), Path(tmp_dir)
        for d in (self.work_dir, self.tmp_dir):
            d.mkdir(parents=True, exist_ok=True)
        self.timeout, self.mem, self.max_out, self.fsize, self.nproc, self.threads = timeout, mem, max_out, fsize, nproc, threads
        if not shutil.which("bwrap"):
            raise SandboxUnavailable("bubblewrap (bwrap) not found")

    def cmd(self, code):
        c = ["bwrap", "--unshare-all", "--die-with-parent", "--new-session", "--clearenv",
             "--ro-bind", "/usr", "/usr", "--symlink", "usr/lib", "/lib", "--symlink", "usr/lib64", "/lib64",
             "--symlink", "usr/bin", "/bin", "--proc", "/proc", "--dev", "/dev"]
        for src, dst in _python_roots(self.venv):
            c += ["--ro-bind", str(src), str(dst)]
        c += ["--ro-bind", str(self.gold_view), "/gold", "--bind", str(self.work_dir), "/work",
              "--bind", str(self.tmp_dir), "/tmp", "--chdir", "/work",
              "--setenv", "HOME", "/tmp", "--setenv", "TMPDIR", "/tmp", "--setenv", "PATH", "/usr/bin",
              "--setenv", "OMP_NUM_THREADS", str(self.threads), "--setenv", "OPENBLAS_NUM_THREADS", str(self.threads),
              "--setenv", "CUDA_VISIBLE_DEVICES", "",
              VENV_MOUNT + "/bin/python", "-I", "-c", PRELUDE + "\n" + code]
        return c

    def run(self, code):
        t0 = time.time()
        try:
            p = subprocess.run(self.cmd(code), capture_output=True, text=True, timeout=self.timeout,
                               preexec_fn=_limits(self.mem, self.timeout + 5, self.fsize, self.nproc))
            out = p.stdout + (("\n[stderr]\n" + p.stderr[-6000:]) if p.stderr.strip() else "")
            rc = p.returncode
        except subprocess.TimeoutExpired:
            out, rc = f"[timed out after {self.timeout} s]", None
        if len(out) > self.max_out:
            out = out[: self.max_out] + f"\n[output cut at {self.max_out:,} characters]"
        return {"returncode": rc, "seconds": round(time.time() - t0, 2), "output": out or "(no output)"}

    def selftest(self, forbidden_paths=()):
        """Probe isolation. Returns {check: bool}; all must be True. forbidden_paths: host paths that must be invisible
        (e.g. the repository, the session's private evaluation data, ~/.ssh)."""
        probe = "FORBIDDEN = " + json.dumps([str(p) for p in forbidden_paths]) + r'''
import os, socket, json
r = {}
try:
    s = socket.create_connection(("1.1.1.1", 53), timeout=2); s.close(); r["no_network"] = False
except OSError:
    r["no_network"] = True
r["forbidden_paths_invisible"] = not any(os.path.exists(p) for p in FORBIDDEN)
try:
    open("/gold/_w", "w"); r["gold_readonly"] = False
except OSError:
    r["gold_readonly"] = True
r["work_writable"] = (open("/work/.probe", "w").write("x") == 1)
os.remove("/work/.probe")
r["no_secrets_env"] = not any(k for k in os.environ if any(t in k.upper() for t in ("TOKEN", "KEY", "SECRET", "PASS")))
import importlib.util
r["no_torch"] = importlib.util.find_spec("torch") is None
r["no_minatar"] = importlib.util.find_spec("minatar") is None
print(json.dumps(r))
'''
        res = self.run(probe)
        try:
            checks = json.loads(res["output"].strip().splitlines()[-1])
        except Exception:  # noqa: BLE001
            return {"sandbox_runs": False, "output": res["output"][:500]}
        checks["sandbox_runs"] = res["returncode"] == 0
        return checks
