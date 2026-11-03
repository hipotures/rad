"""Read-only Gold registry.

register() copies a source container into <work>/gold/<gold_id>/, writes a manifest (source identity, file sha256,
per-tensor shape/dtype/sha256) and removes write permission. The public API returns read-only arrays only; there is
no function that writes into a registered Gold directory, and verify() re-checks every hash.
"""
import json
import os
import shutil
import stat
from pathlib import Path

import numpy as np

from . import work_root
from .tensors import load_any, sha256_array, sha256_file

MANIFEST = "gold_manifest.json"


def gold_dir(gold_id: str) -> Path:
    return work_root() / "gold" / gold_id


def _readonly(path: Path):
    for p in [path, *path.rglob("*")]:
        mode = p.stat().st_mode
        p.chmod(mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def register(gold_id: str, source_file, source_identity: dict, names=None, link=False) -> dict:
    """Register Gold once. link=True hard-links a large immutable input instead of copying it."""
    d = gold_dir(gold_id)
    if (d / MANIFEST).exists():
        man = json.loads((d / MANIFEST).read_text())
        assert man["file_sha256"] == sha256_file(source_file), f"{gold_id} already registered with different bytes"
        return man
    d.mkdir(parents=True)
    src = Path(source_file)
    dst = d / ("weights" + "".join(src.suffixes[-1:]))
    if link:
        os.link(src, dst)
    else:
        shutil.copyfile(src, dst)
    tensors = load_any(dst, names)
    man = {
        "gold_id": gold_id,
        "source": source_identity,
        "file": dst.name,
        "file_sha256": sha256_file(dst),
        "tensors": {k: {"dtype": dt, "shape": list(a.shape), "sha256": sha256_array(a)} for k, (dt, a) in
                    sorted(tensors.items())},
    }
    (d / MANIFEST).write_text(json.dumps(man, indent=1))
    _readonly(d)
    return man


def manifest(gold_id: str) -> dict:
    return json.loads((gold_dir(gold_id) / MANIFEST).read_text())


def load(gold_id: str, names=None) -> dict:
    """{name: (dtype, read-only array)}, each tensor hash-checked against the manifest."""
    man = manifest(gold_id)
    out = load_any(gold_dir(gold_id) / man["file"], names)
    for k, (dt, a) in out.items():
        assert sha256_array(a) == man["tensors"][k]["sha256"], f"Gold tensor {k} changed on disk"
        a = np.array(a, copy=True)
        a.setflags(write=False)
        out[k] = (dt, a)
    return out


def verify(gold_id: str) -> bool:
    man = manifest(gold_id)
    d = gold_dir(gold_id)
    ok = sha256_file(d / man["file"]) == man["file_sha256"]
    ok &= not any(p.stat().st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH) for p in d.rglob("*"))
    return bool(ok)


def is_inside_gold(path) -> bool:
    g = (work_root() / "gold").resolve()
    try:
        Path(path).resolve().relative_to(g)
        return True
    except ValueError:
        return False
