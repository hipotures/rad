"""Edit DSL for Phase D editor outputs: parse (no eval), validate and apply to a copy of a target network.

Grammar (one statement per line; '#' comments and blank lines ignored; anything else is an error):
    NAME[IDX] OP NUMBER             OP in  =  +=  -=  *=
    NAME[IDX, IDX] OP NUMBER        IDX is an integer, ':' or 'a:b' (half-open, non-negative)
    swap NAME[IDX, IDX] NAME[IDX, IDX]      (or 1-D indices; both selections must have the same shape)
The edit block may be wrapped in ```edit ... ``` fences; only the first fenced block is used if fences are present.
Lenient mode (reported separately) skips lines that do not parse instead of rejecting the edit.
Limits: at most MAX_STATEMENTS statements and MAX_ENTRIES changed entries, values finite with |v| <= MAX_ABS.
"""
import re

import numpy as np

MAX_STATEMENTS, MAX_ENTRIES, MAX_ABS = 16, 256, 100.0
NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
IDX = r"(?:\d+|:|\d+:\d+)"
SEL = rf"([A-Za-z_]\w*)\[\s*({IDX})\s*(?:,\s*({IDX})\s*)?\]"
ASSIGN = re.compile(rf"^{SEL}\s*(=|\+=|-=|\*=)\s*({NUM})$")
SWAP = re.compile(rf"^swap\s+{SEL}\s+{SEL}$")


class EditError(ValueError):
    pass


def extract_block(text):
    m = re.search(r"```(?:edit)?\s*\n(.*?)```", text, re.S)
    return m.group(1) if m else text


def _index(tok, n):
    if tok is None:
        return None
    if tok == ":":
        return slice(0, n)
    if ":" in tok:
        a, b = (int(t) for t in tok.split(":"))
        if not 0 <= a < b <= n:
            raise EditError(f"slice {tok} out of range 0..{n}")
        return slice(a, b)
    i = int(tok)
    if not 0 <= i < n:
        raise EditError(f"index {i} out of range 0..{n - 1}")
    return i


def _sel(w, name, i, j):
    if name not in w:
        raise EditError(f"unknown tensor {name}")
    a = w[name]
    if (j is None) != (a.ndim == 1):
        raise EditError(f"{name} has {a.ndim} dimension(s)")
    return (_index(i, a.shape[0]),) if a.ndim == 1 else (_index(i, a.shape[0]), _index(j, a.shape[1]))


def parse(text, lenient=False, max_statements=MAX_STATEMENTS):
    """Return a list of statement dicts; raise EditError on the first invalid line (lenient: skip such lines)."""
    out = []
    for raw in extract_block(text).splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        m = ASSIGN.match(line)
        if m:
            name, i, j, op, val = m.groups()
            v = float(val)
            if not np.isfinite(v) or abs(v) > MAX_ABS:
                raise EditError(f"value out of range: {line}")
            out.append({"op": op, "name": name, "i": i, "j": j, "value": v, "text": line})
            continue
        m = SWAP.match(line)
        if m:
            n1, i1, j1, n2, i2, j2 = m.groups()
            out.append({"op": "swap", "a": (n1, i1, j1), "b": (n2, i2, j2), "text": line})
            continue
        if not lenient:
            raise EditError(f"cannot parse: {line[:80]}")
    if not out:
        raise EditError("empty edit")
    if len(out) > max_statements:
        raise EditError(f"{len(out)} statements > {max_statements}")
    return out


def apply(weights, stmts, max_entries=MAX_ENTRIES):
    """Apply statements to a copy of weights; return (edited, n_changed). Raises EditError if limits are exceeded."""
    w = {k: np.array(v, dtype=np.float32, copy=True) for k, v in weights.items()}
    for s in stmts:
        if s["op"] == "swap":
            ia, ib = _sel(w, *s["a"]), _sel(w, *s["b"])
            A, B = w[s["a"][0]][ia].copy(), w[s["b"][0]][ib].copy()
            if np.shape(A) != np.shape(B):
                raise EditError(f"swap shape mismatch: {s['text']}")
            w[s["a"][0]][ia], w[s["b"][0]][ib] = B, A
        else:
            ix = _sel(w, s["name"], s["i"], s["j"])
            t = w[s["name"]]
            v = np.float32(s["value"])
            if s["op"] == "=":
                t[ix] = v
            elif s["op"] == "+=":
                t[ix] += v
            elif s["op"] == "-=":
                t[ix] -= v
            else:
                t[ix] *= v
    for k, t in w.items():
        if not np.isfinite(t).all() or np.abs(t).max() > 1e4:
            raise EditError(f"{k}: non-finite or exploding values after edit")
    n = int(sum((w[k] != np.asarray(weights[k], np.float32)).sum() for k in w))
    if n > max_entries:
        raise EditError(f"{n} changed entries > {max_entries}")
    return w, n


def run(weights, text, lenient=False, max_statements=MAX_STATEMENTS, max_entries=MAX_ENTRIES):
    """Parse+apply; returns dict(valid, error, edited, n_changed, statements). lenient: ignore unparseable lines.
    Limits default to the v1 values; benchmark v2 passes per-family limits explicitly."""
    try:
        st = parse(text, lenient, max_statements)
        e, n = apply(weights, st, max_entries)
        return {"valid": True, "error": None, "edited": e, "n_changed": n, "statements": [s["text"] for s in st]}
    except EditError as ex:
        return {"valid": False, "error": str(ex), "edited": None, "n_changed": 0, "statements": []}
