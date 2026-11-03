"""Phase D editor tasks on F1-F3 targets: probe text, tiers T0/T1/T2, answer parsing, and non-agent baselines.

Everything the editor sees is produced by `probe_text` from the *damaged* network and the instance's probe set
(192 labelled inputs). The test set and the ground truth are never shown.

Tiers (Phase D design section 3):
  T0 select       : four complete candidate edits (A-D), exactly one is the family's correct repair; answer a letter.
  T1 parameterize : the defect family is named and an edit template with blanks is given; fill in the numbers.
  T2 free-form    : write an edit in the DSL from the probes alone.
"""
import re

import numpy as np

from . import edit_dsl as E
from . import targets as T

DSL_HELP = """EDIT LANGUAGE (one statement per line):
  NAME[i] = v | NAME[i] += v | NAME[i] -= v | NAME[i] *= v          (1-D tensors b1, b2, b3)
  NAME[i, j] = v (same operators; i or j may be ':' or 'a:b')         (2-D tensors W1, W2, W3)
  swap NAME[...] NAME[...]                                            (exchange two equal-shaped selections)
At most 16 statements and 256 changed entries; |v| <= 100. Put the edit inside a ```edit fenced block."""


def _fmt(v, nd=2):
    return " ".join(f"{x:.{nd}f}" for x in np.asarray(v).ravel())


def probe_text(inst):
    w = inst["damaged"]
    xp, yp = inst["probe"]
    z, h1, h2 = T.forward(w, xp, True)
    pred = z.argmax(1)
    lines = ["NETWORK: x (20 inputs) -> h1 = relu(x @ W1 + b1) (32 units) -> h2 = relu(h1 @ W2 + b2) (24 units) -> "
             "logits = h2 @ W3 + b3 (6 classes); prediction = argmax(logits).",
             "SHAPES: W1 20x32, b1 32, W2 32x24, b2 24, W3 24x6, b3 6.",
             "TENSOR STATS (mean / std / min / max):"]
    for k in ("W1", "b1", "W2", "b2", "W3", "b3"):
        t = w[k]
        lines.append(f"  {k}: {t.mean():.3f} / {t.std():.3f} / {t.min():.3f} / {t.max():.3f}")
    lines += [f"b1 = [{_fmt(w['b1'])}]",
              f"b3 = [{_fmt(w['b3'])}]",
              f"PROBES on {len(yp)} labelled inputs (the network is known to have ONE defect):",
              f"  accuracy = {(pred == yp).mean():.3f}",
              f"  fraction of inputs where each h1 unit is active (>0): [{_fmt((h1 > 0).mean(0))}]",
              f"  true class counts      : {np.bincount(yp, minlength=6).tolist()}",
              f"  predicted class counts : {np.bincount(pred, minlength=6).tolist()}"]
    cm = np.zeros((6, 6), int)
    np.add.at(cm, (yp, pred), 1)
    lines.append("  confusion matrix (row = true class, column = predicted class):")
    lines += [f"    {r}: {cm[r].tolist()}" for r in range(6)]
    lines.append(f"  mean logits per true class (rows) : " + "; ".join(
        f"{c}: [{_fmt(z[yp == c].mean(0), 1)}]" for c in range(6) if (yp == c).any()))
    return "\n".join(lines)


def oracle_edit(inst):
    t = inst["truth"]
    if inst["family"] == "F1":
        return "\n".join(f"b1[{u}] = 0" for u in t["units"])
    if inst["family"] == "F2":
        a, b = t["classes"]
        return f"swap W3[:, {a}] W3[:, {b}]\nswap b3[{a}] b3[{b}]"
    return f"b3[{t['class']}] -= {t['shift']}"


def distractors(inst, rng):
    """Three plausible but wrong edits: other-family repairs at random targets, plus a wrong-target same-family one."""
    f = inst["family"]
    units = rng.choice(T.H1, 3, replace=False)
    a, b = rng.choice(6, 2, replace=False)
    c = int(rng.integers(0, 6))
    s = round(float(rng.uniform(5, 40)), 2)
    pool = {"F1": "\n".join(f"b1[{int(u)}] = 0" for u in units),
            "F2": f"swap W3[:, {a}] W3[:, {b}]\nswap b3[{a}] b3[{b}]",
            "F3": f"b3[{c}] -= {s}"}
    out = [v for k, v in pool.items() if k != f]
    # same family, wrong target
    if f == "F1":
        wrong = [u for u in range(T.H1) if u not in inst["truth"]["units"]]
        out.append("\n".join(f"b1[{int(u)}] = 0" for u in rng.choice(wrong, len(inst["truth"]["units"]), replace=False)))
    elif f == "F2":
        pairs = [(i, j) for i in range(6) for j in range(i + 1, 6) if [i, j] != inst["truth"]["classes"]]
        i, j = pairs[int(rng.integers(len(pairs)))]
        out.append(f"swap W3[:, {i}] W3[:, {j}]\nswap b3[{i}] b3[{j}]")
    else:
        cc = int(rng.choice([k for k in range(6) if k != inst["truth"]["class"]]))
        out.append(f"b3[{cc}] -= {inst['truth']['shift']}")
    return out


FAMILY_TEXT = {"F1": ("dead units: some first-layer units never activate because their bias b1 was set to a large "
                      "negative value", "b1[?] = 0   (one line per dead unit)"),
               "F2": ("two output classes were swapped (their columns of W3 and their entries of b3 were exchanged)",
                      "swap W3[:, ?] W3[:, ?]\nswap b3[?] b3[?]"),
               "F3": ("one output bias was increased by a large amount, so that class is over-predicted",
                      "b3[?] -= ?")}


def render(inst, tier, rng):
    """Return (prompt, meta). meta holds what is needed to score the answer (T0 options)."""
    head = ("You are repairing a small damaged neural-network classifier by editing its weights directly.\n\n"
            + probe_text(inst) + "\n\n")
    if tier == "T0":
        opts = distractors(inst, rng) + [oracle_edit(inst)]
        order = rng.permutation(4)
        opts = [opts[i] for i in order]
        letters = "ABCD"
        body = "Which ONE of these edits repairs the defect?\n\n" + "\n\n".join(
            f"Option {letters[i]}:\n{o}" for i, o in enumerate(opts))
        body += "\n\nAnswer with the option letter only, on the last line as: ANSWER: <letter>"
        return head + body, {"options": opts}
    if tier == "T1":
        desc, tmpl = FAMILY_TEXT[inst["family"]]
        body = (f"The defect type is: {desc}.\nFill in the numbers (?) of this edit template and output the completed "
                f"edit in a ```edit fenced block:\n{tmpl}\n\n{DSL_HELP}")
        return head + body, {}
    if tier == "T2":
        return head + "Find the defect and write an edit that repairs it.\n\n" + DSL_HELP, {}
    raise ValueError(tier)


def answer_to_edit(tier, text, meta):
    if tier == "T0":
        m = re.findall(r"ANSWER\s*[:：]\s*\**\s*\(?([ABCD])\b", text, re.I)
        if not m:
            return None
        return meta["options"]["ABCD".index(m[-1])]
    return text


def evaluate_answer(inst, tier, text, meta, lenient=False):
    """Score one editor answer: valid flag, held-out accuracy/recovery (invalid -> treated as no-op)."""
    edit = answer_to_edit(tier, text, meta)
    r = E.run(inst["damaged"], edit, lenient) if edit is not None else {"valid": False, "error": "no answer", "n_changed": 0}
    sc = T.score(inst, r["edited"]) if r["valid"] else {"acc": inst["damaged_acc"], "delta": 0.0, "recovery": 0.0}
    return {"valid": r["valid"], "error": r.get("error"), "n_changed": r["n_changed"], **sc}


# ------------------------------------------------------------------------------------------------ non-agent baselines
def heuristic_edits(inst):
    """Family-agnostic rule-based repair candidates computed from the probes only."""
    w = inst["damaged"]
    xp, yp = inst["probe"]
    z, h1, _ = T.forward(w, xp, True)
    pred = z.argmax(1)
    out = []
    dead = np.flatnonzero((h1 > 0).mean(0) == 0)
    if len(dead):
        med = float(np.median(np.delete(w["b1"], dead)))
        out.append("\n".join(f"b1[{int(u)}] = {med:.4f}" for u in dead[:16]))
    cm = np.zeros((6, 6), int)
    np.add.at(cm, (yp, pred), 1)
    off = cm + cm.T
    np.fill_diagonal(off, 0)
    a, b = np.unravel_index(off.argmax(), off.shape)
    out.append(f"swap W3[:, {a}] W3[:, {b}]\nswap b3[{a}] b3[{b}]")
    over = np.bincount(pred, minlength=6) - np.bincount(yp, minlength=6)
    c = int(over.argmax())
    margin = z.max(1) - z[:, c]
    out.append(f"b3[{c}] -= {float(np.percentile(np.abs(z[:, c] - np.sort(z, 1)[:, -2]), 50)):.2f}")
    return out


def heuristic_best(inst):
    """Best-of heuristic candidates selected on the PROBE set (not the test set)."""
    xp, yp = inst["probe"]
    best, best_acc = None, T.accuracy(inst["damaged"], xp, yp)
    for e in heuristic_edits(inst):
        r = E.run(inst["damaged"], e)
        if r["valid"]:
            acc = T.accuracy(r["edited"], xp, yp)
            if acc > best_acc:
                best, best_acc = e, acc
    return best


def random_edit(inst, rng, n_entries, scale):
    """Random edit of n_entries entries with values ~ N(current, scale) at random positions (size-matched control)."""
    names = list(T.SHAPES)
    sizes = np.array([np.prod(T.SHAPES[k]) for k in names])
    lines = []
    for _ in range(max(1, min(n_entries, 16))):
        k = names[rng.choice(len(names), p=sizes / sizes.sum())]
        idx = [int(rng.integers(0, d)) for d in T.SHAPES[k]]
        lines.append(f"{k}[{', '.join(map(str, idx))}] += {float(rng.normal(0, scale)):.4f}")
    return "\n".join(lines)
