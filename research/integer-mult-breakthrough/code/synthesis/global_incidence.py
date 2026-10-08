#!/usr/bin/env python3
"""Exact binary incidence identities and auxiliary reversible CNOT words.

Authored with OpenAI Codex. The geometric formulas used by the companion
probe come from the pinned PR58/PR48 fixed-I+J predecessor chain; they are
independently replayed here. This module claims no physical framed network
and no asymptotic integer-multiplication improvement.
"""
from fractions import Fraction as Q
from itertools import combinations
from math import comb


def triples(h):
    return list(combinations(range(h), 3))


def incidence_rows(h):
    inputs = triples(h)
    totals = [sum(1 << j for j, t in enumerate(inputs) if c in t)
              for c in range(h)]
    pairs = {p: sum(1 << j for j, t in enumerate(inputs) if set(p) <= set(t))
             for p in combinations(range(h), 2)}
    return inputs, totals, pairs


def side_rows(h):
    inputs, totals, pairs = incidence_rows(h)
    sides, summed = [], []
    for j, t in enumerate(inputs):
        collected = 0
        for c in t:
            a, b = [x for x in t if x != c]
            row = totals[c] ^ pairs[tuple(sorted((c, a)))] ^ pairs[tuple(sorted((c, b)))] ^ (1 << j)
            expected = sum(1 << k for k, u in enumerate(inputs)
                           if c in u and a not in u and b not in u)
            if row != expected:
                raise ValueError('Partial side identity failed')
            sides.append(((c, t), row))
            collected ^= row
        expected = sum(1 << k for k, u in enumerate(inputs) if len(set(t) & set(u)) == 1)
        candidate = (1 << j) ^ totals[t[0]] ^ totals[t[1]] ^ totals[t[2]]
        if collected != expected or collected != candidate:
            raise ValueError('Summed global incidence identity failed')
        summed.append(collected)
    return inputs, sides, summed


def dirty_word(h, separate_sides=False):
    """Return paid CNOTs, source/sink maps and arbitrarily dirty scratch.

    Each CNOT is (destination, source). The input and output banks are
    distinct. Every scratch line starts with an independent dirty variable.
    Echo: compute scratch ^= Bx; output ^= Cscratch; undo computation;
    output ^= Cscratch. This restores scratch and cancels every dirty bit.
    """
    inputs = triples(h)
    v = len(inputs)
    sink_count = 3 * v if separate_sides else v
    total_base = v + sink_count
    total_slots = list(range(total_base, total_base + h))
    pair_list = list(combinations(range(h), 2)) if separate_sides else []
    pair_slots = {p: total_base + h + k for k, p in enumerate(pair_list)}
    scratch = total_slots + list(pair_slots.values())
    compute = []
    for j, t in enumerate(inputs):
        for c in t:
            compute.append((total_slots[c], j))
        if separate_sides:
            for p in combinations(t, 2):
                compute.append((pair_slots[p], j))
    uses, direct = [], []
    sink_targets = []
    if separate_sides:
        for j, t in enumerate(inputs):
            for offset, c in enumerate(t):
                sink = v + 3 * j + offset
                a, b = [x for x in t if x != c]
                uses.extend([(sink, total_slots[c]),
                             (sink, pair_slots[tuple(sorted((c, a)))]),
                             (sink, pair_slots[tuple(sorted((c, b)))])])
                direct.append((sink, j))
                sink_targets.append((c, t))
    else:
        for j, t in enumerate(inputs):
            uses.extend((v + j, total_slots[c]) for c in t)
            direct.append((v + j, j))
            sink_targets.append(t)
    return dict(h=h, inputs=inputs, source_slots=list(range(v)),
                sink_slots=list(range(v, v + sink_count)), sink_targets=sink_targets,
                scratch_slots=scratch, roles=v + sink_count + len(scratch),
                cnot_word=compute + uses + list(reversed(compute)) + uses + direct,
                separate_sides=separate_sides)


def replay_dirty_word(word):
    """Replay all source, destination and dirty columns simultaneously."""
    h, v = word['h'], comb(word['h'], 3)
    states = [1 << i for i in range(word['roles'])]
    initial = list(states)
    for target, source in word['cnot_word']:
        if not (0 <= target < word['roles'] and 0 <= source < word['roles']) or target == source:
            raise ValueError('Invalid CNOT')
        states[target] ^= states[source]
    _, sides, summed = side_rows(h)
    expected = [r for _, r in sides] if word['separate_sides'] else summed
    for source in word['source_slots']:
        if states[source] != initial[source]:
            raise ValueError('Source restoration failed')
    for sink, row in zip(word['sink_slots'], expected):
        if states[sink] != initial[sink] ^ row:
            raise ValueError('Wrong source/sink map or surviving dirty contribution')
    for scratch in word['scratch_slots']:
        if states[scratch] != initial[scratch]:
            raise ValueError('Dirty scratch was not restored')
    return dict(source_columns=v, arbitrary_dirty_columns=len(word['scratch_slots']),
                arbitrary_destination_columns=len(word['sink_slots']),
                source_and_dirty_restored=True, full_map_exact=True,
                paid_cnots=len(word['cnot_word']), roles=word['roles'])


def source_line(h, t):
    return [Q(3 + (i in t)) for i in range(h)]


def projector(h, core, cover):
    """Independent rational reconstruction of pinned fixed-I+J formula."""
    if core & ~cover:
        raise ValueError('Core is outside cover')
    c = core.bit_count()
    n = (cover & ~core).bit_count()
    if c == 3:
        if core != cover:
            raise ValueError('Unsupported triple envelope')
        den = 6 * (h + 1)
        return [[Q((3 + ((core >> i) & 1)) *
                   (3 * (h + 1) * ((core >> j) & 1) - 10), den)
                 for j in range(h)] for i in range(h)]
    if c not in (1, 2):
        raise ValueError('Unsupported envelope core')
    s, outside = 3 - c, cover & ~core
    den = 3 * (h + 1) * (s * s + (c - 1) * n)
    result = []
    for i in range(h):
        oi, wi = (outside >> i) & 1, 3 + ((core >> i) & 1)
        row = []
        for j in range(h):
            oj, zj = (outside >> j) & 1, 3 * (h + 1) * ((core >> j) & 1) - 10
            num = den * (i == j) * oi + s * oi * zj + 3 * (h + 1) * s * wi * oj + n * wi * zj - 3 * (h + 1) * (c - 1) * oi * oj
            row.append(Q(num, den))
        result.append(row)
    return result


def subtract(a, b):
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def identity(h):
    return [[Q(i == j) for j in range(h)] for i in range(h)]


def multiply(a, b):
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), Q())
             for j in range(len(b[0]))] for i in range(len(a))]


def rank(matrix):
    a = [list(row) for row in matrix]
    r = 0
    for j in range(len(a[0]) if a else 0):
        p = next((i for i in range(r, len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        value = a[r][j]
        for k in range(j, len(a[r])):
            a[r][k] /= value
        for i in range(r + 1, len(a)):
            scale = a[i][j]
            if scale:
                for k in range(j, len(a[i])):
                    a[i][k] -= scale * a[r][k]
        r += 1
    return r
