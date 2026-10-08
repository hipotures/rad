#!/usr/bin/env python3
"""Exact F9 payload Walsh bridge and scoped recursive-count controls.

Address fields remain binary. Host vector transforms are reference
algebra, not a fixed-tape implementation or a movement exponent claim.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import time

from downstream_gaussian import require


def add(x, y):
    return ((x % 3 + y % 3) % 3) + 3 * ((x // 3 + y // 3) % 3)


def neg(x):
    return (-x % 3) + 3 * (-(x // 3) % 3)


def mul(x, y):
    a, b, c, d = x % 3, x // 3, y % 3, y // 3
    return ((a * c - b * d) % 3) + 3 * ((a * d + b * c) % 3)


def power(x, n):
    out = 1
    while n:
        if n & 1:
            out = mul(out, x)
        x = mul(x, x)
        n >>= 1
    return out


def inverse(x):
    require(x != 0, 'F9 reciprocal of zero')
    out = power(x, 7)
    require(mul(x, out) == 1, 'F9 reciprocal differs')
    return out


I = 3  # i^2=-1; this is a payload symbol, not an address digit.
HALF = 2
CA = mul(HALF, add(1, I))
CB = mul(HALF, add(1, neg(I)))


def complex_tensor(values, bits):
    """Reference C^tensor(bits), in physical coordinate bit order."""
    out = list(values)
    require(len(out) == 1 << bits, 'Tensor input has wrong binary length')
    for j in range(bits):
        mask = 1 << j
        for index in range(len(out)):
            if index & mask:
                continue
            u, v = out[index], out[index | mask]
            out[index] = add(mul(CA, u), mul(CB, v))
            out[index | mask] = add(mul(CB, u), mul(CA, v))
    return out


def phase_s(values):
    return [mul(power(I, index.bit_count() % 4), value)
            for index, value in enumerate(values)]


def bridge_walsh(values, bits):
    factor = power(add(1, neg(I)), bits)
    return [mul(factor, z) for z in phase_s(complex_tensor(phase_s(values), bits))]


def reference_walsh(values):
    out = []
    for a in range(len(values)):
        total = 0
        for b, value in enumerate(values):
            total = add(total, neg(value) if (a & b).bit_count() & 1 else value)
        out.append(total)
    return out


def xor_bridge(values, bits):
    side = 1 << bits
    require(len(values) == side * side, 'Joint input has wrong binary volume')
    out = []
    normalization = inverse(power(2, bits))
    for control in range(side):
        first = bridge_walsh(values[control * side:(control + 1) * side], bits)
        diagonal = [neg(value) if (control & target).bit_count() & 1 else value
                    for target, value in enumerate(first)]
        out += [mul(normalization, z) for z in bridge_walsh(diagonal, bits)]
    return out


def reference_xor(values, bits):
    side = 1 << bits
    return [values[control * side + (target ^ control)]
            for control in range(side) for target in range(side)]


def field_controls():
    for x in range(9):
        require(add(x, neg(x)) == 0, 'F9 additive inverse differs')
        for y in range(9):
            require(mul(x, y) == mul(y, x), 'F9 product is not commutative')
            for z in range(9):
                require(mul(x, add(y, z)) == add(mul(x, y), mul(x, z)),
                        'F9 distributivity differs')
        if x:
            inverse(x)
    require(mul(I, I) == 2 and power(I, 4) == 1, 'F9 i relation differs')
    require(mul(add(1, I), add(1, neg(I))) == 2, 'Walsh scale norm differs')
    return dict(alphabet_size=9, address_alphabet_size=2, nonzero_reciprocals=8,
                distributivity_triples=729, payload_encoding='a+3b represents a+b*i over F3; i^2=-1')


def identity_controls():
    rng = random.Random(202610080350)
    walsh_probes = xor_probes = walsh_entries = xor_entries = 0
    negative_scale = negative_phase = 0
    for bits in range(0, 7):
        side = 1 << bits
        probes = [[int(j == index) for j in range(side)] for index in range(side)] if bits <= 4 else []
        probes += [[rng.randrange(9) for _ in range(side)] for _ in range(6)]
        for values in probes:
            actual = bridge_walsh(values, bits)
            require(actual == reference_walsh(values), 'F9 Walsh bridge differs')
            require(bridge_walsh(actual, bits) == [mul(power(2, bits), v) for v in values],
                    'Walsh square normalization differs')
            walsh_probes += 1
            walsh_entries += side
            if bits:
                raw = phase_s(complex_tensor(phase_s(values), bits))
                negative_scale += raw != actual
                raw_phase = [mul(power(add(1, neg(I)), bits), v)
                             for v in complex_tensor(values, bits)]
                negative_phase += raw_phase != actual
    for bits in range(1, 5):
        length = 1 << (2 * bits)
        probes = [[int(j == index) for j in range(length)] for index in range(length)] if bits <= 3 else []
        probes += [[rng.randrange(9) for _ in range(length)] for _ in range(8)]
        for values in probes:
            actual = xor_bridge(values, bits)
            require(actual == reference_xor(values, bits), 'F9 controlled word-XOR differs')
            require(xor_bridge(actual, bits) == values, 'Controlled XOR does not restore arbitrary payloads')
            require(all(0 <= z < 9 for z in actual), 'Fixed payload escaped its alphabet')
            xor_probes += 1
            xor_entries += length
    require(negative_scale and negative_phase, 'Omitted normalization/phase negative did not discriminate')
    return dict(walsh_input_probes=walsh_probes, walsh_output_entries=walsh_entries,
                controlled_xor_input_probes=xor_probes, controlled_xor_output_entries=xor_entries,
                omitted_scale_discriminating_probes=negative_scale,
                omitted_s_phase_discriminating_probes=negative_phase,
                xor_complex_calls=2, linear_diagonals=5,
                scope='Exact complete binary-address operators with F9 payloads; vector loops do not charge tape cost')


def count_controls(path):
    old = json.loads(path.read_text())
    row = next(r for r in old['witnesses'] if r['mode'] == 'tight')
    c = row['complex_counts']
    W, m, s, N, L, D = (c[k] for k in ('W', 'm', 's', 'N', 'L', 'D'))
    require(s == W * m - D and D == 2 * N - 2 * L and D > 0,
            'Accepted complex rank identities differ')
    lower_row_additions = 3 * N
    extra_children = 2 * lower_row_additions
    modified = s + extra_children
    require(modified > W * m, 'Scoped Walsh basis compiler unexpectedly has a rank saving')
    # Full-size B<=2C algebra cannot be used as an inductive contraction.
    require(Q(2) > 1, 'Same-size coupling control differs')
    growth = Q(modified, W * m)
    normalized = Q(1)
    values = []
    for depth in range(1, 7):
        normalized *= growth
        require(normalized > 1, 'Stopped recurrence unexpectedly shrinks')
        values.append(dict(depth=depth, rank_only_normalized_cost=str(normalized)))
    return dict(accepted_counts=c, accepted_normalized_children=str(Q(s, W)),
                lower_source_edge_basis_row_additions=lower_row_additions,
                extra_complex_children_for_that_compiler=extra_children,
                modified_children=modified, max_sublinear_children=W * m,
                exact_excess=modified - W * m,
                extra_to_deficit_ratio=str(Q(extra_children, D)),
                normalized_growth=str(growth), stopped_rank_only_controls=values,
                same_size_bridge='B_word(e) <= 2 C(e) + linear phases; coefficient 2 is not an inductive contraction',
                scoped_recurrence='Independent per-edge basis compiler: C(e) <= ((s+2A)/W) C(e/m)+linear, A>=3N',
                scope='Negative for this independent compiler and uncancelled same-size substitution only; no universal adapter obstruction')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--accepted-generic', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    require(not a.output.exists(), 'Use a fresh result path')
    started = time.monotonic()
    result = dict(status='PASS EXACT F9 WALSH BRIDGE; SCOPED UNTELESCOPED RECURRENCE FAILS TO IMPROVE MOVEMENT',
                  campaign='20261007T222521Z', campaign_start='2026-10-07T22:25:21Z',
                  campaign_original_deadline='2026-10-08T08:25:21Z', campaign_deadline='2026-10-08T10:00:00Z',
                  generated_at=datetime.now(timezone.utc).isoformat(),
                  input=dict(path=str(a.accepted_generic), bytes=a.accepted_generic.stat().st_size,
                             sha256=hashlib.sha256(a.accepted_generic.read_bytes()).hexdigest()),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  dependency_sha256=hashlib.sha256((Path(__file__).parent / 'downstream_gaussian.py').read_bytes()).hexdigest(),
                  field=field_controls(), exact_operators=identity_controls(),
                  count_model=count_controls(a.accepted_generic),
                  scope='Payload/address algebra and a declared recursive-count negative; no faster tape movement or new kappa',
                  elapsed_seconds=time.monotonic() - started)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], result['exact_operators'], flush=True)


if __name__ == '__main__':
    main()
