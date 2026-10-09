#!/usr/bin/env python3
"""Exact address/payload controls for the conditional packed native GL route.

The fixed-tape cost is the pinned original packed-XOR lemma, not the timing of
these Python reference arrays. This file independently transcribes its literal
variable-control rotations, repair, and a row-operation GL factorization.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import random
import time


ORIGINAL_REVISION = 'adc7f1241b42e322a6451854ab7e4b4c146bf78a'
ORIGINAL_LAYERS_SHA256 = '20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594'
WORD = ((0, -1, 0), (1, -1, 0), (0, 1, 0), (1, 1, 0),
        (1, 1, 1), (0, 1, 1), (1, -1, 1), (0, -1, 1))


def selected(k, f, rho, omit_top=False):
    if k < 1 or f < 1 or not 0 <= rho < k:
        raise ValueError('invalid packed slots')
    return tuple(rho + j*k for j in range(f - int(omit_top)))


def offset(x, other, positions, parity):
    return sum(1 << bit for bit in positions
               if (x >> bit & 1) and (other >> bit & 1) == parity)


def rotate_word(x, y, z, k, f, rho, inverse=False):
    mask = (1 << (k*f)) - 1
    used = selected(k, f, rho, True)
    for target, sign, parity in (reversed(WORD) if inverse else WORD):
        sign *= -1 if inverse else 1
        if target == 0:
            y = (y + sign*offset(x, z, used, parity)) & mask
        else:
            z = (z + sign*offset(x, y, used, parity)) & mask
    return x, y, z


def bad(y, z, k, f, rho):
    mask = (1 << (k-1)) - 1
    return any(not 10 <= (a >> (bit+1) & mask) <= (1 << (k-1))-11
               for a in (y, z) for bit in selected(k, f, rho, True))


def ideal(x, y, z, k, f, rho, omit_top=False):
    toggles = sum(1 << bit for bit in selected(k, f, rho, omit_top)
                  if x >> bit & 1)
    return x, y ^ toggles, z


def repair(x, y, z, k, f, rho):
    if not bad(y, z, k, f, rho):
        return x, y, z
    old = rotate_word(x, y, z, k, f, rho, inverse=True)
    return ideal(*old, k, f, rho, omit_top=True)


def program(x, y, z, k, f, rho):
    a, b, c = repair(*rotate_word(x, y, z, k, f, rho), k, f, rho)
    top = rho + (f-1)*k
    return a, b ^ ((a >> top & 1) << top), c


def matrix_apply(columns, x):
    value = 0
    for j, column in enumerate(columns):
        if x >> j & 1:
            value ^= column
    return value


def gl_word(columns):
    """Chronological elementary transvections implementing columns over F2."""
    n = len(columns)
    if n < 1 or any(not 0 <= c < 1 << n for c in columns):
        raise ValueError('invalid binary matrix')
    rows = [sum((columns[j] >> i & 1) << j for j in range(n)) for i in range(n)]
    reduction = []
    for pivot in range(n):
        if not rows[pivot] >> pivot & 1:
            candidate = next((j for j in range(pivot+1, n) if rows[j] >> pivot & 1), None)
            if candidate is None:
                raise ValueError('singular binary route')
            # A row exchange is three additions; it does not rename a bank.
            for target, source in ((pivot, candidate), (candidate, pivot), (pivot, candidate)):
                rows[target] ^= rows[source]
                reduction.append((target, source))
        for target in range(n):
            if target != pivot and rows[target] >> pivot & 1:
                rows[target] ^= rows[pivot]
                reduction.append((target, pivot))
    if rows != [1 << j for j in range(n)]:
        raise AssertionError('row reduction failed')
    result = tuple(reversed(reduction))
    if len(result) > n*(n-1)+3*(n-1):
        raise AssertionError('uniform transvection count exceeded')
    return result


def apply_word(word, x):
    for target, source in word:
        x ^= ((x >> source & 1) << target)
    return x


def payload(rank):
    # Two independent Gaussian integers on any common power-two grid.
    # All four fields depend on the complete record rank, including spectators.
    return (3*rank-5, 7*rank+11, -13*rank-17, 19*rank+23)


def unit(value, exponent):
    exponent %= 4
    a, b, c, d = value
    return ((a, b, c, d), (-b, a, -d, c),
            (-a, -b, -c, -d), (b, -a, d, -c))[exponent]


def decode(rank, n, width, prefix=1, suffix=1):
    tail = rank % suffix
    rank //= suffix
    chunks = [0]*n
    mask = (1 << width)-1
    for j in range(n-1, -1, -1):
        chunks[j] = rank & mask
        rank >>= width
    if not 0 <= rank < prefix:
        raise AssertionError('record counter left complete rectangle')
    return rank, chunks, tail


def encode(head, chunks, tail, width, suffix=1):
    rank = head
    for chunk in chunks:
        rank = (rank << width) | chunk
    return rank*suffix+tail


def scatter(values, destination):
    """Exact finite permutation oracle; no native random-access time claim."""
    out = [None]*len(values)
    for rank, value in enumerate(values):
        q = destination(rank)
        if not 0 <= q < len(values) or out[q] is not None:
            raise AssertionError('complete payload operation is not a permutation')
        out[q] = value
    if any(value is None for value in out):
        raise AssertionError('a payload record was omitted')
    return out


def stream_transvection(values, n, k, f, rho, target, source, prefix=1, suffix=1):
    """Literal rotations + exceptional full-record sort + top-bit completion."""
    if n < 3 or target == source:
        raise ValueError('needs three existing distinct complete address slots')
    companion = next(j for j in range(n) if j not in (target, source))
    width = k*f
    used = selected(k, f, rho, True)
    original = values
    for changed, sign, parity in WORD:
        def destination(rank):
            head, chunks, tail = decode(rank, n, width, prefix, suffix)
            slot = target if changed == 0 else companion
            other = companion if changed == 0 else target
            chunks[slot] = (chunks[slot] + sign*offset(chunks[source], chunks[other], used, parity)) & ((1 << width)-1)
            return encode(head, chunks, tail, width, suffix)
        values = scatter(values, destination)
    exceptions, holes = [], []
    for rank, value in enumerate(values):
        head, chunks, tail = decode(rank, n, width, prefix, suffix)
        if bad(chunks[target], chunks[companion], k, f, rho):
            holes.append(rank)
            x, y, z = repair(chunks[source], chunks[target], chunks[companion], k, f, rho)
            chunks[source], chunks[target], chunks[companion] = x, y, z
            exceptions.append((encode(head, chunks, tail, width, suffix), value))
    # Reference stable key sort. The paid lemma uses binary radix passes over
    # ALL payload fields, retaining the full stream until reinsertion.
    exceptions.sort(key=lambda row: row[0])
    if [rank for rank, _ in exceptions] != holes:
        raise AssertionError('repair keys are not exactly the exceptional holes')
    for (rank, value), hole in zip(exceptions, holes):
        if rank != hole:
            raise AssertionError('exceptional record lost')
        values[rank] = value
    top = rho + (f-1)*k
    def finish(rank):
        head, chunks, tail = decode(rank, n, width, prefix, suffix)
        chunks[target] ^= (chunks[source] >> top & 1) << top
        return encode(head, chunks, tail, width, suffix)
    values = scatter(values, finish)
    def direct(rank):
        head, chunks, tail = decode(rank, n, width, prefix, suffix)
        chunks[target] ^= sum((chunks[source] >> b & 1) << b for b in selected(k, f, rho))
        return encode(head, chunks, tail, width, suffix)
    if values != scatter(original, direct):
        raise AssertionError('literal rotations/repair cropped payload or failed companion restoration')
    return values, len(exceptions)


def controlled_case(task):
    k, f, rho, seed, samples = task
    used = selected(k, f, rho, True)
    period = 1 << (max(used)+1) if used else 1
    if period > 512:
        raise ValueError('finite representative period is deliberately bounded')
    masks = [sum((m >> j & 1) << bit for j, bit in enumerate(used)) for m in range(1 << len(used))]
    wrong, witness = 0, None
    for x in masks:
        for y in range(period):
            for z in range(period):
                q = rotate_word(x, y, z, k, f, rho)
                if rotate_word(*q, k, f, rho, inverse=True) != (x, y, z):
                    raise AssertionError('literal inverse failed')
                goal = ideal(x, y, z, k, f, rho, True)
                if q != goal:
                    wrong += 1
                    witness = witness or dict(input=[x, y, z], unrepaired=list(q), ideal=list(goal))
    rng = random.Random(seed)
    size = 1 << (k*f)
    guards = 0
    for _ in range(samples):
        x, y, z = (rng.randrange(size) for _ in range(3))
        q = rotate_word(x, y, z, k, f, rho)
        if not bad(y, z, k, f, rho):
            guards += 1
            if q != ideal(x, y, z, k, f, rho, True):
                raise AssertionError('safe guard failed')
        if bad(q[1], q[2], k, f, rho) != bad(y, z, k, f, rho):
            raise AssertionError('exception set is not invariant')
        if program(x, y, z, k, f, rho) != ideal(x, y, z, k, f, rho):
            raise AssertionError('complete transvection did not restore arbitrary companion')
        increments = [rng.randrange(size//period)*period for _ in range(2)]
        shifted = rotate_word(x, (y+increments[0]) % size, (z+increments[1]) % size, k, f, rho)
        if shifted != (q[0], (q[1]+increments[0]) % size, (q[2]+increments[1]) % size):
            raise AssertionError('high-quotient representative lift failed')
    count = len(masks)*period*period
    bound = min(Fraction(1), Fraction(80*(f-1), 1 << k))
    fraction = Fraction(wrong, count)
    if k >= 6 and fraction > bound:
        raise AssertionError('failure mass exceeded original union bound')
    return dict(kind='variable-control-address-word', k=k, f=f, rho=rho, seed=seed,
                native_guard_contract=k >= 6, exact_representatives=count,
                samples=samples, sampled_safe_guards=guards,
                unrepaired_failure_fraction=str(fraction), guard_union_bound=str(bound),
                omitted_repair_witness=witness, arbitrary_companion_restored=True)


def stream_case(task):
    n, k, f, rho, columns, prefix, suffix = task
    columns = tuple(columns)
    word = gl_word(columns)
    for x in range(1 << n):
        if apply_word(word, x) != matrix_apply(columns, x):
            raise AssertionError('GL transvection orientation failed')
        if apply_word(tuple(reversed(word)), matrix_apply(columns, x)) != x:
            raise AssertionError('GL inverse failed')
    width = k*f
    count = prefix*(1 << (n*width))*suffix
    if count > 300000:
        raise ValueError('no large payload sweeps')
    original = [payload(rank) for rank in range(count)]
    values = original
    exception_counts = []
    for target, source in word:
        values, exceptions = stream_transvection(values, n, k, f, rho, target, source, prefix, suffix)
        exception_counts.append(exceptions)
    def direct(rank):
        head, chunks, tail = decode(rank, n, width, prefix, suffix)
        for bit in selected(k, f, rho):
            x = sum((chunk >> bit & 1) << j for j, chunk in enumerate(chunks))
            y = matrix_apply(columns, x)
            for j in range(n):
                chunks[j] = (chunks[j] & ~(1 << bit)) | ((y >> j & 1) << bit)
        return encode(head, chunks, tail, width, suffix)
    if values != scatter(original, direct):
        raise AssertionError('complete GL map or spectator preservation failed')
    for target, source in reversed(word):
        values, _ = stream_transvection(values, n, k, f, rho, target, source, prefix, suffix)
    if values != original:
        raise AssertionError('complete arbitrary-dirty GL round trip failed')
    # Chirp: one unit per column, INCLUDING a nonzero column constant.
    q = dict(constant=3, linear=[(j+1) % 4 for j in range(n)],
             cross=[(j, j+1, 2) for j in range(n-1)])
    phase_values = []
    for rank, value in enumerate(original):
        _, chunks, _ = decode(rank, n, width, prefix, suffix)
        exponent = 0
        for bit in selected(k, f, rho):
            bits = [chunk >> bit & 1 for chunk in chunks]
            exponent += q['constant'] + sum(c*b for c, b in zip(q['linear'], bits))
            exponent += sum(c*bits[i]*bits[j] for i, j, c in q['cross'])
        changed = unit(value, exponent)
        if unit(changed, -exponent) != value or sum(a*a for a in changed) != sum(a*a for a in value):
            raise AssertionError('unit chirp corrupted fixed-grid Gaussian fields')
        phase_values.append(changed)
    if f % 4 != 1:
        difference = (3*f-3) % 4
        if difference and not any(unit(v, difference) != v for v in original):
            raise AssertionError('column-constant negative did not discriminate')
    return dict(kind='complete-payload-GL-and-unit-chirp', h=n, k=k, f=f, rho=rho,
                columns=list(columns), transvections=len(word), word=[list(g) for g in word],
                prefix=prefix, suffix=suffix, complete_records=count,
                full_fields=4, exact_roundtrip_fields=4*count,
                exceptional_full_records_per_forward_gate=exception_counts,
                unit_chirp_fields=4*count, chirp=q, native_guard_contract=k >= 6,
                finite_array_reference_only=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    before = sha256(Path(__file__).read_bytes()).hexdigest()
    utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    samples = 256 if args.bounded else 2048
    controlled = [(6, 1, 5, 202610090301, samples), (6, 2, 5, 202610090302, samples),
                  (6, 3, 0, 202610090303, samples)]
    streams = [(3, 1, 2, 0, (3, 6, 4), 2, 2)]
    if not args.bounded:
        controlled += [(8, 3, 0, 202610090304, samples),
                       (2, 3, 0, 202610090305, samples)]
        streams += [(3, 2, 2, 1, (3, 6, 4), 2, 2),
                    (4, 2, 2, 0, (2, 1, 12, 8), 1, 1),
                    (3, 6, 1, 5, (3, 6, 4), 1, 1)]
    jobs = [(controlled_case, task) for task in controlled] + [(stream_case, task) for task in streams]
    if args.workers == 1:
        cases = [function(task) for function, task in jobs]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(function, task) for function, task in jobs]
            cases = [future.result() for future in futures]
    after = sha256(Path(__file__).read_bytes()).hexdigest()
    if before != after:
        raise AssertionError('source changed during run')
    if not any(c.get('omitted_repair_witness') for c in cases):
        raise AssertionError('omitted repair negative was not exercised')
    result = dict(status='PASS', scope='Exact finite address/payload controls. Fixed-tape route cost remains conditional on the pinned original stream primitives, complete three-slot shape and long-record/guard band; no native runtime or exponent measured.',
                  started_utc=utc, completed_utc=datetime.now(timezone.utc).isoformat(),
                  workers=args.workers, bounded=args.bounded, source_sha256=before,
                  original_revision=ORIGINAL_REVISION, original_layers_sha256=ORIGINAL_LAYERS_SHA256,
                  cases=cases, source_freeze_verified=True, seconds=time.monotonic()-started)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status=result['status'], cases=len(cases), workers=args.workers,
                          exact_address_representatives=sum(c.get('exact_representatives', 0) for c in cases),
                          complete_payload_records=sum(c.get('complete_records', 0) for c in cases),
                          seconds=result['seconds'], scope=result['scope'])), flush=True)


if __name__ == '__main__':
    main()
