"""Versioned, validated weight patches and candidate lineage.

A patch is relative to one Gold (gold_id + per-tensor base sha256) and optionally a parent patch. It is stored as
<work>/patches/<patch_id>/{patch.json, delta.npz}: for each edited tensor the flat indices of changed entries and the
new values in the tensor's own dtype. patch_id is derived from the content, so identical edits share an id and
a stored patch is never overwritten.

Validation policy (explicit, per experiment config):
  allowed_tensors      names that may be edited (others are refused)
  max_abs_value        bound on any edited value (finite only)
  max_changed_entries  bound on changed entries per patch
  forbid_uniform_scale refuse an edit that only multiplies a whole tensor by one constant
"""
import json
import time
from pathlib import Path

import numpy as np

from . import registry, work_root
from .tensors import bf16_bits_to_f32, sha256_array, sha256_bytes

PATCH_VERSION = 1


class PatchRefused(ValueError):
    pass


def patches_dir() -> Path:
    d = work_root() / "patches"
    d.mkdir(parents=True, exist_ok=True)
    return d


def values(dt, a):
    """Numeric values of a stored tensor (BF16 is kept as uint16 bit patterns)."""
    return bf16_bits_to_f32(a).astype(np.float64) if dt == "BF16" else np.asarray(a, dtype=np.float64)


def _is_uniform_scale(base, new):
    b = base.astype(np.float64).ravel()
    n = new.astype(np.float64).ravel()
    nz = b != 0
    if not nz.any() or (n[~nz] != 0).any():
        return False
    r = n[nz] / b[nz]
    return bool(np.allclose(r, r[0], rtol=1e-6, atol=0) and r[0] != 1.0)


def validate(gold_id, proposed: dict, policy: dict, parent_id=None) -> list:
    """Return a list of human-readable refusal reasons ([] = valid). proposed: {name: array (target dtype)}."""
    man = registry.manifest(gold_id)
    base = materialize(gold_id, parent_id, names=[n for n in proposed if n in man["tensors"]])
    reasons, total = [], 0
    for name, arr in proposed.items():
        arr = np.asarray(arr)
        if name not in man["tensors"]:
            reasons.append(f"{name}: not a Gold tensor")
            continue
        if name not in policy["allowed_tensors"]:
            reasons.append(f"{name}: not an editable tensor")
            continue
        dt, b = base[name]
        if list(arr.shape) != list(b.shape):
            reasons.append(f"{name}: shape {list(arr.shape)} != {list(b.shape)}")
            continue
        if arr.dtype != b.dtype:
            reasons.append(f"{name}: dtype {arr.dtype} != {b.dtype}")
            continue
        vals = values(dt, arr)
        if not np.isfinite(vals).all():
            reasons.append(f"{name}: non-finite values")
            continue
        if np.abs(vals).max() > policy["max_abs_value"]:
            reasons.append(f"{name}: |value| {np.abs(vals).max():.4g} > {policy['max_abs_value']}")
        if policy.get("forbid_uniform_scale", True) and _is_uniform_scale(values(dt, b), vals):
            reasons.append(f"{name}: whole-tensor constant scaling is refused")
        total += int((arr != b).sum())
    if total == 0 and not reasons:
        reasons.append("patch changes nothing")
    if total > policy["max_changed_entries"]:
        reasons.append(f"{total} changed entries > {policy['max_changed_entries']}")
    return reasons


def create(gold_id, proposed: dict, policy: dict, meta: dict, parent_id=None) -> dict:
    """Validate and store a patch. meta: method, rationale, author/session. Raises PatchRefused."""
    reasons = validate(gold_id, proposed, policy, parent_id)
    if reasons:
        raise PatchRefused("; ".join(reasons))
    man = registry.manifest(gold_id)
    base = materialize(gold_id, parent_id, names=list(proposed))
    arrays, tensors = {}, []
    for i, name in enumerate(sorted(proposed)):
        new = np.ascontiguousarray(proposed[name])
        dt, b = base[name]
        idx = np.flatnonzero(new != b)
        if idx.size == 0:
            continue
        arrays[f"t{i}_idx"] = idx.astype(np.int64)
        arrays[f"t{i}_val"] = new.reshape(-1)[idx]
        d = values(dt, new) - values(dt, b)
        tensors.append({"key": f"t{i}", "name": name, "shape": list(b.shape), "dtype": dt,
                        "gold_sha256": man["tensors"][name]["sha256"], "base_sha256": sha256_array(b),
                        "edited_sha256": sha256_array(new), "changed_entries": int(idx.size),
                        "delta_l2": float(np.linalg.norm(d)),
                        "relative_change": float(np.linalg.norm(d) / max(np.linalg.norm(values(dt, b)), 1e-30))})
    content = json.dumps({"gold": gold_id, "parent": parent_id, "tensors": [(t["name"], t["edited_sha256"]) for t in tensors]},
                         sort_keys=True).encode()
    pid = "p-" + sha256_bytes(content)[:12]
    d = patches_dir() / pid
    rec = {"patch_version": PATCH_VERSION, "patch_id": pid, "gold_id": gold_id, "parent_id": parent_id,
           "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "policy": policy,
           "changed_entries_total": sum(t["changed_entries"] for t in tensors),
           "delta_l2_total": float(np.sqrt(sum(t["delta_l2"] ** 2 for t in tensors))),
           "tensors": tensors, **{"meta": meta}}
    if d.exists():
        old = json.loads((d / "patch.json").read_text())
        return old
    d.mkdir()
    np.savez_compressed(d / "delta.npz", **arrays)
    rec["delta_sha256"] = sha256_bytes((d / "delta.npz").read_bytes())
    (d / "patch.json").write_text(json.dumps(rec, indent=1))
    return rec


def load_patch(pid) -> dict:
    return json.loads((patches_dir() / pid / "patch.json").read_text())


def lineage(pid) -> list:
    chain = []
    while pid:
        rec = load_patch(pid)
        chain.append(pid)
        pid = rec["parent_id"]
    return chain[::-1]


def materialize(gold_id, patch_id=None, names=None) -> dict:
    """Gold tensors with the patch chain applied, as fresh writable copies (Gold itself is never touched)."""
    g = registry.load(gold_id, names)
    out = {k: (dt, np.array(a, copy=True)) for k, (dt, a) in g.items()}
    for pid in (lineage(patch_id) if patch_id else []):
        rec = load_patch(pid)
        assert rec["gold_id"] == gold_id, f"{pid} belongs to {rec['gold_id']}"
        with np.load(patches_dir() / pid / "delta.npz", allow_pickle=False) as z:
            for t in rec["tensors"]:
                if t["name"] not in out:
                    continue
                dt, a = out[t["name"]]
                assert sha256_array(a) == t["base_sha256"], f"{pid}: base of {t['name']} mismatch"
                flat = a.reshape(-1)
                flat[z[t["key"] + "_idx"]] = z[t["key"] + "_val"]
                assert sha256_array(a) == t["edited_sha256"], f"{pid}: {t['name']} rebuild hash mismatch"
    return out
