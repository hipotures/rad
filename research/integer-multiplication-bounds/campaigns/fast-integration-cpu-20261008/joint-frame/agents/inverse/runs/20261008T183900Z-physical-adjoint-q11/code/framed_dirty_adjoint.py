#!/usr/bin/env python3
"""Execute the literal reverse-transposed physical word and owned-copy adjoint.

Unlike the forward fixture's exchanged data roles, this reverses EVERY
physical event and transposes every role XOR. A center read transposes to
a zero-initialized gather, one inverse copy permutation, and an addition.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import time

from framed_dirty_cube import identity, inverse, matrix_multiply, partial_swap, projector


def fixture(p, basis, output):
    started = time.monotonic()
    full = partial_swap(identity(3), p)
    triple = partial_swap(projector(((1, 1, 1),), p), p)
    endpoint = matrix_multiply(full, triple, p)
    centers = []
    for c in range(3):
        cols = []
        for j in range(3):
            if j != c:
                col = [0]*3
                col[c], col[j] = pow(2, -1, p), 1
                cols.append(tuple(col))
        centers.append(partial_swap(projector(tuple(cols), p), p))
    size = p**6

    @lru_cache(None)
    def indices(matrix):
        answer = []
        for address in range(size):
            z, digits = address, []
            for _ in range(6):
                digits.append(z % p)
                z //= p
            out = [sum(x*y for x, y in zip(row, digits)) % p for row in matrix]
            answer.append(sum(x*p**j for j, x in enumerate(out)))
        assert len(set(answer)) == size
        return tuple(answer)

    def move(row, matrix):
        return [row[i] for i in indices(matrix)]

    if basis:
        initial = [[1 << (r*size+a) for a in range(size)] for r in range(5)]
    else:
        initial = [[((r*size+a+1)*0xD6E8FEB86659FD93) & ((1 << 64)-1)
                    for a in range(size)] for r in range(5)]
    mixer = [(3, 2), (4, 2), (2, 3), (3, 2), (2, 3)]
    events = []

    def xors(gates, phase):
        events.extend(("xor", a, b, phase) for a, b in gates)

    xors(mixer, "first-mixer")
    xors([(1, r) for r in range(2, 5)], "first-scatter")
    xors(reversed(mixer), "first-inverse")
    events.append(("move", 2, triple, "first-injection-frame"))
    xors([(2, 0)], "first-injection")
    for r in (3, 4):
        events.append(("move", r, triple, "middle-entrance"))
    xors(mixer, "middle-mixer")
    for r, center in zip(range(2, 5), centers):
        events.append(("move", r, matrix_multiply(center, triple, p), "center-envelope"))
        events.append(("read", 1, (r, center), "owned-center-copy"))
    events.append(("move", 1, endpoint, "target-frame"))
    for r, center in zip(range(2, 5), centers):
        events.append(("move", r, matrix_multiply(full, center, p), "auxiliary-cleanup"))
    xors(reversed(mixer), "last-inverse")
    events.append(("move", 0, endpoint, "last-source-frame"))
    xors([(2, 0)], "last-injection")

    def execute(mode):
        rows = list(initial)
        copies = 0
        for kind, a, b, phase in reversed(events):
            if kind == "xor":
                # Transpose the ACTUAL stored XOR, including both inverse mixers.
                rows[b] = [x ^ y for x, y in zip(rows[b], rows[a])]
            elif kind == "move":
                if mode == "omit-adjoint-cleanup" and phase == "auxiliary-cleanup":
                    continue
                rows[a] = move(rows[a], inverse(b, p))
            elif kind == "read":
                r, transform = b
                # Paid zero gather, inverse transform, addition, erasure.
                port = [0]*size
                port = [x ^ y for x, y in zip(port, rows[a])]
                if mode != "omit-inverse-copy-transform":
                    port = move(port, inverse(transform, p))
                rows[r] = [x ^ y for x, y in zip(rows[r], port)]
                del port
                copies += 1
            else:
                raise AssertionError(kind)
        mismatches, first = 0, None
        eidx, fidx = indices(endpoint), indices(full)
        for r, row in enumerate(rows):
            mapping = eidx if r < 2 else fidx
            for a, got in enumerate(row):
                expected = initial[r][mapping[a]]
                if r == 0:
                    expected ^= initial[1][fidx[a]]
                if got != expected:
                    mismatches += 1
                    if first is None:
                        first = {"physical_role": r, "address": a,
                                 "differing_basis_column": (got ^ expected).bit_length()-1 if basis else None}
        return {"mode": mode, "mismatches": mismatches,
                "first_mismatch": first, "owned_zero_gather_ports": copies}

    controls = [execute(mode) for mode in ("complete", "omit-inverse-copy-transform", "omit-adjoint-cleanup")]
    assert controls[0]["mismatches"] == 0
    assert all(c["mismatches"] > 0 for c in controls[1:])
    result = {"status": "PASS_LITERAL_PHYSICAL_ADJOINT_AND_NEGATIVES",
              "prime": p, "addresses_per_role": size, "original_roles": 5,
              "all_basis_columns": 5*size if basis else None,
              "all_addresses_checked": True, "full_dirty_basis": basis,
              "frozen_words": None if basis else "Distinct deterministic 64-bit role/address words",
              "forward_physical_events": len(events), "all_events_reversed": True,
              "every_role_XOR_transposed": True,
              "copied_ports": "Owned zeroed work stream; original dirty roles are never initialized or erased",
              "expected": ["S_triple_perp*x+S_full*y", "S_triple_perp*y", "S_full*d"],
              "controls": controls, "workers": 1, "native_threads": 1,
              "seconds": time.monotonic()-started,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "dependency_sha256": hashlib.sha256(Path(__file__).with_name("framed_dirty_cube.py").read_bytes()).hexdigest(),
              "scope": "Exact finite physical reverse-transposed event program, including three actual zero-gather copy adjoints. Not the literal public 23/25-axis address cube or an all-size tape implementation."}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "prime": p, "seconds": result["seconds"]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prime", type=int, choices=(5, 11), required=True)
    parser.add_argument("--full-basis", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    assert not args.full_basis or args.prime == 5
    fixture(args.prime, args.full_basis, args.output)
