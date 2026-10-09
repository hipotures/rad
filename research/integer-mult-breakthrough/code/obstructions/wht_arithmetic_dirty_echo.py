#!/usr/bin/env python3
"""Exact Alman--Rao arithmetic macro and an explicitly paid dirty transcription.

Algorithm 5 of arXiv:2211.06459v2 supplies the arithmetic recursion. This
independent implementation also builds a four-pass reversible transcription
on arbitrary dirty scalar banks. Neither operation count is a native rank
certificate or an integer-multiplication exponent. OpenAI Codex assisted.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import time


class Program:
    """SSA signals become shears into distinct arbitrary dirty helper banks."""

    def __init__(self, n: int):
        assert n > 0 and n & (n - 1) == 0
        self.n = n
        self.nodes: list[tuple[str, tuple[tuple[Q, int], ...]]] = []
        self.outputs: list[int] = []

    def node(self, kind: str, *terms: tuple[Q | int, int]) -> int:
        result = self.n + len(self.nodes)
        assert all(0 <= ref < result for _, ref in terms)
        self.nodes.append((kind, tuple((Q(c), r) for c, r in terms)))
        return result

    def add(self, a: int, b: int, sign: int = 1) -> int:
        return self.node("add", (1, a), (sign, b))

    def scale(self, a: int, exponent: int) -> int:
        if exponent == 0:
            return a
        coefficient = Q(2**exponent) if exponent >= 0 else Q(1, 2**-exponent)
        return self.node("divide" if exponent < 0 else "input_scale", (coefficient, a))

    def butterfly(self, inputs: list[int]) -> list[int]:
        if len(inputs) == 1:
            return inputs
        half = len(inputs) // 2
        left = self.butterfly(inputs[:half])
        right = self.butterfly(inputs[half:])
        return [self.add(a, b) for a, b in zip(left, right)] + [
            self.add(a, b, -1) for a, b in zip(left, right)
        ]

    def recursion(self, inputs: list[int], exponent: int = 0) -> list[int]:
        if len(inputs) <= 4:
            return self.butterfly([self.scale(x, exponent) for x in inputs])
        size = len(inputs) // 8
        children = [
            self.recursion(inputs[j * size : (j + 1) * size], exponent + (j != 0))
            for j in range(8)
        ]
        result = [[] for _ in range(8)]
        for column in range(size):
            a, b, c, d, e, f, g, h = [x[column] for x in children]
            bc, dh, fg = self.add(b, c), self.add(d, h), self.add(f, g)
            total = self.scale(self.add(self.add(self.add(bc, dh), fg), e), -1)
            delta = self.add(a, total, -1)
            dd, ee, hh = self.add(delta, d), self.add(delta, e), self.add(delta, h)
            values = [
                self.add(a, total),
                self.add(self.add(ee, c), g),
                self.add(self.add(ee, b), f),
                self.add(ee, dh),
                self.add(dd, bc),
                self.add(self.add(hh, c), f),
                self.add(self.add(hh, b), g),
                self.add(dd, fg),
            ]
            for block, value in zip(result, values):
                block.append(value)
        return [value for block in result for value in block]

    def build(self) -> "Program":
        assert not self.nodes
        self.outputs = self.recursion(list(range(self.n)))
        return self

    def evaluate(self, inputs: list[Q]) -> list[Q]:
        values = list(inputs)
        for _, terms in self.nodes:
            values.append(sum((c * values[r] for c, r in terms), Q(0)))
        return [values[r] for r in self.outputs]

    def symbolic(self) -> dict:
        """Complete clean SSA coefficient rows, including scale temporaries."""
        rows = [{j: Q(1)} for j in range(self.n)]
        max_l1 = Q(1)
        max_fractional_bits = 0
        max_scale_exponent = 0
        for kind, terms in self.nodes:
            row: dict[int, Q] = {}
            for coefficient, ref in terms:
                # A multiplication temporary can exceed the final sum.
                temporary = sum((abs(coefficient * x) for x in rows[ref].values()), Q(0))
                max_l1 = max(max_l1, temporary)
                for key, value in rows[ref].items():
                    row[key] = row.get(key, Q(0)) + coefficient * value
            row = {key: value for key, value in row.items() if value}
            rows.append(row)
            max_l1 = max(max_l1, sum(map(abs, row.values()), Q(0)))
            for value in row.values():
                denominator = value.denominator
                assert denominator & (denominator - 1) == 0
                max_fractional_bits = max(max_fractional_bits, denominator.bit_length() - 1)
            if kind == "input_scale":
                max_scale_exponent = max(max_scale_exponent, terms[0][0].numerator.bit_length() - 1)
        for output, ref in enumerate(self.outputs):
            expected = {j: Q((-1) ** ((output & j).bit_count() % 2)) for j in range(self.n)}
            assert rows[ref] == expected, (self.n, output)
        digest = hashlib.sha256(json.dumps(
            [[str(rows[r][j]) for j in range(self.n)] for r in self.outputs],
            separators=(",", ":"),
        ).encode()).hexdigest()
        return {"matrix_sha256": digest, "clean_prefix_max_row_l1": str(max_l1),
                "clean_prefix_extra_fractional_bits": max_fractional_bits,
                "maximum_leaf_scale_exponent": max_scale_exponent}

    def dirty_echo(self, inputs: list[Q], sinks: list[Q], helpers: list[Q],
                   *, skip_zero_pass: bool = False) -> tuple[list[Q], list[Q], int, Q, int]:
        """T_x/read/T_x^-1, then T_0/negative-read/T_0^-1.

        Every source-to-helper and helper-to-helper term is a literal shear.
        The zero pass omits source terms and keeps all helper terms. Output
        accumulation and every inverse shear are included in the gate count.
        Helpers are never initialized to zero or silently overwritten.
        """
        assert len(inputs) == len(sinks) == self.n and len(helpers) == len(self.nodes)
        state = list(inputs) + list(helpers)
        output = list(sinks)
        gates = 0
        peak = max((abs(x) for x in state + output), default=Q(0))
        fractional = 0

        def observe(*values: Q) -> None:
            nonlocal peak, fractional
            for value in values:
                peak = max(peak, abs(value))
                denominator = value.denominator
                assert denominator & (denominator - 1) == 0
                fractional = max(fractional, denominator.bit_length() - 1)

        def pass_word(zero: bool, inverse: bool) -> None:
            nonlocal gates
            indexed = list(enumerate(self.nodes))
            if inverse:
                indexed.reverse()
            for j, (_, original_terms) in indexed:
                terms = reversed(original_terms) if inverse else original_terms
                for coefficient, ref in terms:
                    if zero and ref < self.n:
                        continue
                    term = (-1 if inverse else 1) * coefficient * state[ref]
                    state[self.n + j] += term
                    gates += 1
                    observe(term, state[self.n + j])

        def read(zero: bool, sign: int) -> None:
            nonlocal gates
            for j, ref in enumerate(self.outputs):
                if zero and ref < self.n:
                    continue
                term = sign * state[ref]
                output[j] += term
                gates += 1
                observe(term, output[j])

        pass_word(False, False)
        read(False, 1)
        pass_word(False, True)
        if not skip_zero_pass:
            pass_word(True, False)
            read(True, -1)
            pass_word(True, True)
        assert state[:self.n] == inputs
        assert state[self.n:] == helpers
        return output, state[self.n:], gates, peak, fractional


def reference(inputs: list[Q]) -> list[Q]:
    return [sum(((-1) ** ((i & j).bit_count() % 2) * x for j, x in enumerate(inputs)), Q(0))
            for i in range(len(inputs))]


def exact_counts(n: int) -> dict:
    bits = n.bit_length() - 1
    levels, remainder = divmod(bits, 3)
    return {"add": 22 * (n // 8) * levels + remainder * n,
            "divide": (n // 8) * levels,
            # Multiplication by one is an alias, including the first base block.
            "input_scale": n - 2**remainder}


def probe(bits: int) -> dict:
    n = 2**bits
    start = time.perf_counter()
    program = Program(n).build()
    counts = dict(Counter(kind for kind, _ in program.nodes))
    expected_counts = exact_counts(n)
    assert all(counts.get(k, 0) == v for k, v in expected_counts.items())
    symbolic = program.symbolic()
    rng = random.Random(20261009 + bits)
    checks = 0
    peak = Q(0)
    max_fractional = 0
    gate_counts = set()
    for sample in range(n + 5):
        x = [Q(j == sample) for j in range(n)] if sample < n else [
            Q(rng.randrange(-19, 20), 2**rng.randrange(4)) for _ in range(n)
        ]
        y = [Q(rng.randrange(-11, 12), 2**rng.randrange(4)) for _ in range(n)]
        helpers = [Q(rng.randrange(-13, 14), 2**rng.randrange(4)) for _ in program.nodes]
        wanted = reference(x)
        assert program.evaluate(x) == wanted
        output, _, gates, sample_peak, fractional = program.dirty_echo(x, y, helpers)
        assert output == [a + b for a, b in zip(y, wanted)]
        peak = max(peak, sample_peak)
        max_fractional = max(max_fractional, fractional)
        gate_counts.add(gates)
        checks += n
    assert len(gate_counts) == 1
    # Arbitrary dirty garbage remains at the readout if the second echo is omitted.
    x = [Q(0)] * n
    helpers = [Q(1)] * len(program.nodes)
    contaminated, _, _, _, _ = program.dirty_echo(x, [Q(0)] * n, helpers, skip_zero_pass=True)
    assert contaminated != reference(x)
    return {"bits": bits, "n": n, "status": "PASS", "arithmetic_counts": expected_counts,
            "arithmetic_total": len(program.nodes), "helper_banks": len(program.nodes),
            "dirty_echo_scalar_shears": gate_counts.pop(), "checked_output_values": checks,
            "dirty_echo_observed_peak": str(peak),
            "dirty_echo_observed_fractional_bits": max_fractional,
            "omitted_zero_echo_rejected": True, **symbolic,
            "elapsed_seconds": time.perf_counter() - start,
            "scope": "Exact scalar SSA and arbitrary-dirty transcription; no paid address routing/native frame ledger"}


def bounded() -> dict:
    cases = [probe(bits) for bits in (1, 3)]
    assert cases[1]["arithmetic_counts"] == {"add": 22, "divide": 1, "input_scale": 7}
    assert cases[1]["arithmetic_total"] == 30
    try:
        Program(6)
    except AssertionError:
        invalid_size_rejected = True
    else:
        raise AssertionError("Nonpower-of-two input was admitted")
    return {"status": "PASS", "cases": cases, "invalid_size_rejected": invalid_size_rejected,
            "scope": "Literal arithmetic and dirty echo controls only; no improved exponent"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--bounded", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.bounded:
        result = bounded()
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe, (3, 4, 6, 7)))
        result = {"status": "PASS", "workers": args.workers, "cases": cases,
                  "source": "https://arxiv.org/pdf/2211.06459v2, Algorithm 5; independent implementation",
                  "scope": "Arithmetic constants and explicitly dirty scalar transcription; no exponent certificate"}
    serialized = json.dumps(result, indent=2) + "\n"
    if args.output:
        if args.output.exists():
            raise SystemExit("Refusing to replace an existing result")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized)
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
