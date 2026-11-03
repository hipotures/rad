"""Unit tests for the WSE harness. Run from code/:  python -m pytest -q tests

Test state lives in a fresh directory under $WSE_WORK_ROOT/tmp (or the topic's ignored work/), never /tmp.
"""
import json
import os
import shutil
import stat
import sys
import uuid
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture()
def wroot(monkeypatch):
    base = Path(os.environ.get("WSE_WORK_ROOT") or Path(__file__).resolve().parents[2] / "work")
    d = base / "tmp" / f"pytest-{uuid.uuid4().hex[:8]}"
    d.mkdir(parents=True)
    monkeypatch.setenv("WSE_WORK_ROOT", str(d))
    yield d
    for p in [d, *d.rglob("*")]:
        if p.is_dir():
            p.chmod(p.stat().st_mode | stat.S_IWUSR)
    shutil.rmtree(d)


def tiny_gold(wroot, gid="g-test"):
    from wse import registry
    rng = np.random.default_rng(0)
    w = {"W1": rng.standard_normal((600, 32)).astype(np.float32), "b1": np.zeros(32, np.float32),
         "W2": rng.standard_normal((32, 32)).astype(np.float32), "b2": np.zeros(32, np.float32),
         "W3": rng.standard_normal((32, 6)).astype(np.float32), "b3": np.zeros(6, np.float32)}
    f = wroot / "src.npz"
    np.savez(f, **w)
    registry.register(gid, f, {"test": True})
    return gid, w


POLICY = {"allowed_tensors": ["W1", "b1", "W2", "b2", "W3", "b3"], "max_abs_value": 100.0,
          "max_changed_entries": 100, "forbid_uniform_scale": True}


def test_gold_is_readonly_and_verified(wroot):
    from wse import registry
    gid, w = tiny_gold(wroot)
    assert registry.verify(gid)
    t = registry.load(gid)
    with pytest.raises(ValueError):
        t["W1"][1][0, 0] = 1.0           # returned arrays are read-only
    f = registry.gold_dir(gid) / "weights.npz"
    with pytest.raises(PermissionError):
        open(f, "ab")
    assert registry.is_inside_gold(f)


def test_patch_roundtrip_lineage_and_gold_untouched(wroot):
    from wse import patch, registry
    gid, w = tiny_gold(wroot)
    b3 = w["b3"].copy(); b3[5] = 2.0
    p1 = patch.create(gid, {"b3": b3}, POLICY, {"method": "t"})
    W3 = w["W3"].copy(); W3[0, 0] += 1
    p2 = patch.create(gid, {"W3": W3}, POLICY, {"method": "t"}, parent_id=p1["patch_id"])
    assert patch.lineage(p2["patch_id"]) == [p1["patch_id"], p2["patch_id"]]
    m = patch.materialize(gid, p2["patch_id"])
    assert m["b3"][1][5] == 2.0 and m["W3"][1][0, 0] == W3[0, 0]
    assert np.array_equal(registry.load(gid)["b3"][1], w["b3"]) and registry.verify(gid)
    again = patch.create(gid, {"b3": b3}, POLICY, {"method": "t"})
    assert again["patch_id"] == p1["patch_id"]   # content-addressed; never overwritten


@pytest.mark.parametrize("name,mutate,needle", [
    ("W1", lambda a: a[:10], "shape"),
    ("W1", lambda a: np.where(np.arange(a.size).reshape(a.shape) == 0, np.nan, a).astype(np.float32), "non-finite"),
    ("W1", lambda a: (a * 2).astype(np.float32), "constant scaling"),
    ("W1", lambda a: a + np.float32(0.5), "changed entries"),
    ("b1", lambda a: a + np.float32(1000), "|value|"),
    ("nope", lambda a: a, "not a Gold tensor"),
])
def test_patch_refusals(wroot, name, mutate, needle):
    from wse import patch
    gid, w = tiny_gold(wroot)
    with pytest.raises(patch.PatchRefused, match=needle.replace("|", r"\|")):
        patch.create(gid, {name: mutate(w.get(name, w["b1"]))}, POLICY, {"method": "t"})


def test_disallowed_tensor_refused(wroot):
    from wse import patch
    gid, w = tiny_gold(wroot)
    pol = dict(POLICY, allowed_tensors=["W3"])
    b = w["b3"].copy(); b[0] = 1
    with pytest.raises(patch.PatchRefused, match="not an editable"):
        patch.create(gid, {"b3": b}, pol, {"method": "t"})


def test_bf16_roundtrip_and_values():
    from wse.patch import values
    from wse.tensors import bf16_bits_to_f32, f32_to_bf16_bits
    x = np.array([1.0, -2.5, 3.140625, 0.0], np.float32)
    bits = f32_to_bf16_bits(x)
    assert np.array_equal(bf16_bits_to_f32(bits), x)
    assert np.allclose(values("BF16", bits), x)
    # round to nearest even
    assert f32_to_bf16_bits(np.array([1.00390625], np.float32))[0] == f32_to_bf16_bits(np.array([1.0], np.float32))[0]


def test_safetensors_roundtrip(wroot):
    from wse.tensors import st_load, st_save
    t = {"a": ("BF16", np.arange(6, dtype=np.uint16).reshape(2, 3)), "b": ("F32", np.ones(4, np.float32))}
    st_save(wroot / "x.safetensors", t, {"format": "pt"})
    r = st_load(wroot / "x.safetensors")
    assert r["a"][0] == "BF16" and np.array_equal(r["a"][1], t["a"][1]) and np.array_equal(r["b"][1], t["b"][1])


def test_minatar_paired_determinism():
    pytest.importorskip("minatar")
    from wse import minatar_eval as M
    rng = np.random.default_rng(1)
    w = {k: (rng.standard_normal(s) * 0.1).astype(np.float32) for k, s in M.SHAPES.items()}
    s1, e1 = M.evaluate("seaquest", w, range(5), workers=1)
    s2, e2 = M.evaluate("seaquest", w, range(5), workers=1, chunk=2)
    assert [e["score"] for e in e1] == [e["score"] for e in e2]
    assert [e["length"] for e in e1] == [e["length"] for e in e2]
    p = M.paired(e1, e2)
    assert p["mean_diff"] == 0


def test_controls_match_size_and_avoid_candidate(wroot):
    from wse.heldout import controls
    rng = np.random.default_rng(0)
    g = {"W": rng.standard_normal((50, 4)).astype(np.float32), "b": np.zeros(4, np.float32)}
    c = {k: v.copy() for k, v in g.items()}
    c["W"][3, :] += 1.0
    cs = controls(g, c, 2)
    d_c = c["W"] - g["W"]
    for name, w in cs.items():
        d = w["W"].astype(np.float64) - g["W"]
        assert (d != 0).sum() == 4
        assert np.isclose(np.linalg.norm(d), np.linalg.norm(d_c), rtol=1e-5)
        if name != "flip":
            assert not (d[3, :] != 0).any()


def test_sandbox_isolation(wroot):
    if not shutil.which("bwrap"):
        pytest.skip("bwrap missing")
    venv = Path(os.environ.get("WSE_SANDBOX_VENV", ""))
    if not (venv / "bin" / "python").exists():
        pytest.skip("set WSE_SANDBOX_VENV to the numpy-only sandbox venv")
    from wse.sandbox import Sandbox
    g = wroot / "gold"; g.mkdir()
    (g / "description.json").write_text(json.dumps({"shapes": {"W": [2, 2]}, "editable": ["W"]}))
    np.save(g / "W.npy", np.eye(2, dtype=np.float32))
    for p in g.iterdir():
        p.chmod(0o444)
    g.chmod(0o555)
    sb = Sandbox(venv, g, wroot / "work", wroot / "tmp", timeout=20, mem=1 << 30)
    checks = sb.selftest([str(Path(__file__).resolve().parents[1]), str(Path.home() / ".ssh")])
    assert all(v is True for k, v in checks.items()), checks
    r = sb.run("w = load('W'); w[0,0] = 5; save('W', w); print(saved(), gold('W')[0,0])")
    assert "['W'] 1.0" in r["output"]
    assert sb.run("save('X', np.zeros(2))")["returncode"] != 0
    assert "timed out" in Sandbox(venv, g, wroot / "work", wroot / "tmp", timeout=3).run("while True: pass")["output"]


def test_active_masks_and_active_controls_change_policy_paths():
    from wse.heldout import active_masks, controls
    g = {"W1": np.zeros((600, 32), np.float32), "b1": np.zeros(32, np.float32), "W2": np.zeros((32, 32), np.float32),
         "b2": np.zeros(32, np.float32), "W3": np.zeros((32, 6), np.float32), "b3": np.zeros(6, np.float32)}
    g["W1"][5, 3] = 1.0; g["W2"][3, 7] = 1.0; g["W3"][7, 2] = 1.0     # one live path: input 5 -> h1[3] -> h2[7] -> a2
    g["W1"][9, 4] = 1.0                                                 # h1[4] has no outgoing weight: dead
    m = active_masks(g)
    assert m["W1"][5, 3] and not m["W1"][9, 4] and not m["W1"][0, 3]
    assert m["W2"][3, 7] and not m["W2"][4, 7] and m["b1"][3] and not m["b1"][4]
    assert m["W3"][7].all() and not m["W3"][0].any()
    c = {k: v.copy() for k, v in g.items()}
    c["W1"][5, 3] = 2.0
    cs = controls(g, c, 2, active=True)
    for name in ("permuted_0", "gaussian_1"):
        d = cs[name]["W1"] != g["W1"]
        assert d.sum() == 1 and m["W1"][d].all()


def test_holm_and_p_values():
    from wse.compare_candidates import holm, p_two_sided
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert p_two_sided(0.0, 1.0) == pytest.approx(1.0)
    assert p_two_sided(1.959964, 1.0) == pytest.approx(0.05, abs=1e-5)


def test_export_patches_sparse_delta(wroot):
    from wse import patch
    from wse.export_patches import main
    gid, w = tiny_gold(wroot)
    W3 = w["W3"].copy(); W3[2, 1] = 7.0
    p = patch.create(gid, {"W3": W3}, POLICY, {"method": "t"})
    main(["--out", str(wroot / "exp"), p["patch_id"]])
    d = json.loads((wroot / "exp" / f"{p['patch_id']}.delta.json").read_text())
    assert d == {"W3": {"flat_indices": [2 * 6 + 1], "new_values": [7.0]}}


def test_targets_deterministic_and_oracle_repairs():
    from wse import editor_tasks as K, targets as T
    for fam in T.FAMILIES:
        a, b = T.build(fam, "pilot", 0), T.build(fam, "pilot", 0)
        assert a["seed"] == b["seed"] and np.array_equal(a["damaged"]["W1"], b["damaged"]["W1"])
        assert a["ceiling"] - a["damaged_acc"] > 0.05            # the defect is measurable
        r = K.evaluate_answer(a, "T2", K.oracle_edit(a), {})
        assert r["valid"] and r["recovery"] > 0.85


def test_edit_dsl_refusals_and_swap():
    from wse import edit_dsl as E
    w = {"W": np.arange(6, dtype=np.float32).reshape(2, 3), "b": np.zeros(3, np.float32)}
    r = E.run(w, "```edit\nswap W[:, 0] W[:, 2]\nb[1] += 2.5\n```")
    assert r["valid"] and r["edited"]["W"][0, 0] == 2 and r["edited"]["b"][1] == 2.5 and r["n_changed"] == 5
    for bad in ["import os", "W[5, 0] = 1", "b[0] = 1e9", "W[0] = 1", "nope[0] = 1", "", "swap W[0, 0:2] b[:]"]:
        assert not E.run(w, bad)["valid"], bad
    assert E.run(w, "\n".join(f"b[0] += 1" for _ in range(17)))["error"].startswith("17 statements")


def test_t0_answer_parsing():
    from wse import editor_tasks as K, targets as T
    inst = T.build("F2", "pilot", 1)
    p, meta = K.render(inst, "T0", np.random.default_rng(0))
    good = "ABCD"[meta["options"].index(K.oracle_edit(inst))]
    assert K.evaluate_answer(inst, "T0", f"blah\nANSWER: {good}", meta)["recovery"] > 0.85
    assert not K.evaluate_answer(inst, "T0", "no idea", meta)["valid"]
