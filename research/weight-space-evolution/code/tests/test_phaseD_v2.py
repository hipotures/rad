"""Tests for the Phase D v2 benchmark and the persistent-evaluator transition specs (no GPU, no MinAtar episodes).

Run from code/ with the wse environment:  python -m pytest -q tests/test_phaseD_v2.py
"""
import json
import os
import re
import shutil
import sys
import uuid
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wse import edit_dsl as E  # noqa: E402
from wse import pd2_algo, pd2_bench, pd2_mlp  # noqa: E402


def first_accepted(build, fam, sub, seed=12345):
    """Like pd2_bench.build_one: the next seed is tried when a draw is rejected by the acceptance rules."""
    for k in range(8):
        try:
            return build(fam, sub, seed + k), seed + k
        except RuntimeError:
            continue
    raise AssertionError("no accepted draw")


@pytest.fixture()
def bdir(monkeypatch):
    base = Path(os.environ.get("WSE_WORK_ROOT") or Path(__file__).resolve().parents[2] / "work")
    d = base / "tmp" / f"pytest-pd2-{uuid.uuid4().hex[:8]}"
    d.mkdir(parents=True)
    monkeypatch.setenv("WSE_BENCH_DIR", str(d))
    yield d
    shutil.rmtree(d)


def test_dsl_limits_default_to_v1_and_are_overridable():
    w = {"W": np.zeros((40, 40), np.float32)}
    assert not E.run(w, "W[:, :] = 1")["valid"]                       # 1600 > v1 limit 256
    assert E.run(w, "W[:, :] = 1", max_entries=4096)["valid"]
    many = "\n".join(f"W[{i}, 0] = 1" for i in range(17))
    assert not E.run(w, many)["valid"] and E.run(w, many, max_statements=17)["valid"]


@pytest.mark.parametrize("fam,sub", [("F1", "mixed"), ("F1", "in_scale"), ("F2", "out_perm"), ("F2", "hidden_swap"),
                                     ("F3", "out_bias_pair"), ("F3", "layer_bias"), ("F1", "sign_flip")])
def test_mlp_instances_are_deterministic_and_invertible(fam, sub):
    a, seed = first_accepted(pd2_mlp.build, fam, sub)
    b = pd2_mlp.build(fam, sub, seed)
    assert a["oracle"] == b["oracle"]
    assert all(np.array_equal(a["damaged"][k], b["damaged"][k]) for k in a["damaged"])
    assert a["ceiling"] - a["damaged_metric"] >= pd2_mlp.MIN_GAP
    r = E.run(a["damaged"], a["oracle"], **pd2_mlp.LIMITS)
    assert r["valid"] and pd2_mlp.metric(a, r["edited"]) >= a["ceiling"] - 0.05 * (a["ceiling"] - a["damaged_metric"])


def test_f5_transformer_numpy_forward_and_oracle():
    a, _ = first_accepted(pd2_algo.build, "F5", "unembed_swap", 777)
    assert a["ceiling"] >= 0.95
    r = E.run(a["damaged"], a["oracle"], **pd2_algo.LIMITS)
    assert r["valid"] and pd2_algo.metric(a, r["edited"]) == pytest.approx(a["ceiling"])


def test_build_one_render_regex_baselines_and_roundtrip(bdir):
    row = pd2_bench.build_one("pilot", "F1", "mixed", 0)
    inst = pd2_bench.load("pilot", row["id"])
    assert all(np.array_equal(inst["damaged"][k], pd2_bench.load("pilot", row["id"])["damaged"][k]) for k in inst["damaged"])
    T = inst["tiers"]
    fenced = "```edit\n" + inst["oracle"] + "\n```"
    assert re.fullmatch(T["T1"]["regex"], fenced) and re.fullmatch(T["T2"]["regex"], fenced)
    # T0: 4 rotations, oracle once at every position, same option set
    assert [rot["options"].index(inst["oracle"]) for rot in T["T0"]] == [0, 1, 2, 3]
    assert all(sorted(rot["options"]) == sorted(T["T0"][0]["options"]) for rot in T["T0"])
    assert "?" in T["T1"]["template"] and not re.search(r"\d+\.\d+", T["T1"]["template"])
    s = pd2_bench.score_edit(inst, inst["oracle"])
    assert s["valid"] and s["recovery"] >= 0.95
    assert pd2_bench.score_edit(inst, "not an edit")["recovery"] == 0.0
    assert pd2_bench.score_edit(inst, None)["valid"] is False
    b = inst["baselines"]
    assert b["noop"] == 0.0 and b["oracle"] >= 0.95 and len(b["random_matched"]) == 8


def test_retarget_is_consistent():
    inst = {"damaged": {"W1": np.zeros((10, 8)), "b1": np.zeros(8), "W2": np.zeros((8, 3))}}
    rng = np.random.default_rng(0)
    out = pd2_bench.retarget(inst, "W1[:, 5] *= 8\nb1[5] *= 8\nW2[5, :] *= 2", rng)
    idx = re.findall(r"\[(?::, )?(\d+)", out)
    assert len(set(idx)) == 1, out


def test_secret_salt_changes_heldout_seeds_only(bdir):
    assert pd2_bench.seed_of("dev", "F1", "mixed", 0, 0) == pd2_bench.seed_of("dev", "F1", "mixed", 0, 0)
    s1 = pd2_bench.seed_of("test", "F1", "mixed", 0, 0)
    (bdir / "secret_salt.txt").chmod(0o600)
    (bdir / "secret_salt.txt").write_text("other")
    assert pd2_bench.seed_of("test", "F1", "mixed", 0, 0) != s1
    assert len(pd2_bench.salt_commitment()) == 64


def test_swap_spec_roundtrip(bdir):
    from wse.swap_engine import write_spec
    cur = {"model.language_model.layers.0.mlp.down_proj.weight": np.arange(12, dtype=np.uint16).reshape(3, 4)}
    tgt = {k: v.copy() for k, v in cur.items()}
    tgt["model.language_model.layers.0.mlp.down_proj.weight"][1, 2] = 999
    man = {"tensors": {k: {"sha256": "x"} for k in cur}}
    info = write_spec(bdir / "spec", cur, tgt, man)
    spec = json.loads((bdir / "spec.json").read_text())
    z = np.load(spec["npz"])
    t = spec["tensors"][0]
    assert info == {"tensors": 1, "entries": 1} and t["runtime_name"] == "model.layers.0.mlp.down_proj.weight"
    flat = cur["model.language_model.layers.0.mlp.down_proj.weight"].reshape(-1).copy()
    flat[z[t["key"] + "_idx"]] = z[t["key"] + "_val"]
    assert np.array_equal(flat.reshape(3, 4), tgt["model.language_model.layers.0.mlp.down_proj.weight"])
