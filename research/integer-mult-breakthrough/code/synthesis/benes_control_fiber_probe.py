#!/usr/bin/env python3
"""Exact control-preserving Benes word with complete-slot dependency ledger.

This executes Boolean endpoint XOR words, not the eight native rotations
inside each word. Their guarded native implementation remains conditional.
All inactive letters and full control fibers remain in the address cube.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import random
import time


def permute_bits(value, permutation):
    return sum(((value >> source) & 1) << target for source, target in enumerate(permutation))


def inverse_permutation(permutation):
    inverse = [0]*len(permutation)
    for source, target in enumerate(permutation):
        inverse[target] = source
    return inverse


def stable_compaction(active, f):
    order = [i for i in range(f) if active >> i & 1]+[i for i in range(f) if not active >> i & 1]
    inverse = [0]*f
    for target, source in enumerate(order):
        inverse[source] = target
    return inverse


def benes(permutation):
    """Return distance/mask stages by alternating-cycle input/output colors."""
    n = len(permutation)
    if sorted(permutation) != list(range(n)) or n & (n-1):
        raise ValueError('A power-of-two permutation is required')
    if n == 1:
        return []
    if n == 2:
        return [(1, int(permutation[0] == 1))]
    inverse = inverse_permutation(permutation); color = [None]*n
    for start in range(n):
        if color[start] is not None:
            continue
        color[start] = 0; todo = [start]
        while todo:
            edge = todo.pop()
            for mate in (edge ^ 1, inverse[permutation[edge] ^ 1]):
                wanted = color[edge] ^ 1
                if color[mate] is None:
                    color[mate] = wanted; todo.append(mate)
                elif color[mate] != wanted:
                    raise AssertionError('The alternating-cycle Benes coloring is inconsistent')
    first = sum(color[i] << i for i in range(0, n, 2))
    last = 0
    for output in range(0, n, 2):
        if color[inverse[output]] == 1:
            last |= 1 << output
    sub = [[None]*(n//2) for _ in range(2)]
    for source, target in enumerate(permutation):
        sub[color[source]][source//2] = target//2
    routes = [benes(permutation) for permutation in sub]
    if len(routes[0]) != len(routes[1]):
        raise AssertionError('The two equal subnetworks have different depths')
    middle = []
    for (d0, mask0), (d1, mask1) in zip(*routes):
        if d0 != d1:
            raise AssertionError('Subnetwork stage distances differ')
        mask = sum(((mask0 >> i) & 1) << (2*i) for i in range(n//2))
        mask |= sum(((mask1 >> i) & 1) << (2*i+1) for i in range(n//2))
        middle.append((2*d0, mask))
    return [(1, first), *middle, (1, last)]


def reference_switch(value, distance, mask, f):
    for lower in range(f):
        if not lower & distance and mask >> lower & 1:
            other = lower+distance
            if (value >> lower ^ value >> other) & 1:
                value ^= (1 << lower) | (1 << other)
    return value


def alignment(f, distance):
    bit = distance.bit_length()-1; log = f.bit_length()-1
    return [(i & (distance-1)) | ((i >> (bit+1)) << bit) | (((i >> bit) & 1) << (log-1))
            for i in range(f)]


def linear_pair(values, permutation):
    """Six endpoint XOR words implement(P*x,P^-1*y), companion z restored."""
    x, y, z = values; inverse = inverse_permutation(permutation)
    x ^= y; y ^= x; x ^= y
    x ^= permute_bits(y, permutation)
    y ^= permute_bits(x, inverse)
    x ^= permute_bits(y, permutation)
    return x, y, z


def quarter_stage(values, f, distance, mask, wrong_controls=False):
    permutation = alignment(f, distance); inverse = inverse_permutation(permutation)
    x, y, z = linear_pair(values, permutation)
    decoded_y = y if wrong_controls else permute_bits(y, permutation)
    if not wrong_controls and decoded_y != values[1]:
        raise AssertionError('The inverse-oriented control slot was decoded incorrectly')
    half = f//2; quarter = f//4; qmask = (1 << quarter)-1
    aligned_mask = sum(((mask >> inverse[j]) & 1) << j for j in range(half))
    pieces = [x >> (j*quarter) & qmask for j in range(4)]
    controls = (decoded_y, z)
    # Each tuple names target, donor, distinct borrowed quarter and mask half.
    events = [(0, 2, 1, 0), (1, 3, 0, 1), (2, 0, 3, 0),
              (3, 1, 2, 1), (0, 2, 1, 0), (1, 3, 0, 1)]
    for target, donor, companion, which in events:
        if len({target, donor, companion}) != 3:
            raise AssertionError('A quarter mask reads its target or companion')
        old_companion = pieces[companion]
        pieces[target] ^= pieces[donor] & (aligned_mask >> (which*quarter) & qmask)
        if pieces[companion] != old_companion or controls != (decoded_y, z):
            raise AssertionError('A borrowed quarter/control changed at a word endpoint')
    x = sum(value << (j*quarter) for j, value in enumerate(pieces))
    result = linear_pair((x, y, z), inverse)
    if result[1:] != values[1:]:
        raise AssertionError('The aligned stage did not restore both complete control slots')
    return result


def compile_word(y, z, f):
    active = (~(y | z)) & ((1 << f)-1)
    permutation = stable_compaction(active, f)
    stages = benes(permutation)
    return active, permutation, stages


def run_word(x, y, z, f, stages, reverse=False):
    values = (x, y, z)
    for distance, mask in (list(reversed(stages)) if reverse else stages):
        values = quarter_stage(values, f, distance, mask)
    return values


def physical_positions(f, K):
    quarter = f//4
    return [[((slot*4+q)*(quarter+1)+j)*K+K-1
             for q in range(4) for j in range(quarter)] for slot in range(3)]


def physical_embed(values, f, K, spectator):
    positions = physical_positions(f, K); n = 12*(f//4+1)*K
    selected = {position for slot in positions for position in slot}
    address = 0; iterator = 0
    for position in range(n):
        if position not in selected:
            address |= ((spectator >> iterator) & 1) << position; iterator += 1
    for value, slot in zip(values, positions):
        address |= sum(((value >> i) & 1) << position for i, position in enumerate(slot))
    return address


def physical_apply(address, f, K, stages, reverse=False):
    positions = physical_positions(f, K)
    values = tuple(sum(((address >> position) & 1) << i for i, position in enumerate(slot)) for slot in positions)
    result = run_word(*values, f, stages, reverse=reverse)
    output = address
    for value, slot in zip(result, positions):
        for i, position in enumerate(slot):
            output = (output & ~(1 << position)) | (((value >> i) & 1) << position)
    return output


def probe(task):
    f, K, seed = task; started = time.monotonic(); rng = random.Random(seed)
    if f < 4 or f & (f-1):
        raise ValueError('This twelve-quarter probe needs a power-of-two f>=4')
    if f == 4:
        controls = [(y, z) for y in range(1 << f) for z in range(1 << f)]
        actions = list(range(1 << f))
    elif f == 8:
        controls = [(~active & ((1 << f)-1), 0) for active in range(1 << f)]
        actions = list(range(1 << f))
    else:
        controls = [(rng.getrandbits(f), rng.getrandbits(f)) for _ in range(32)]
        controls += [(0, 0), ((1 << f)-1, 0), (0, (1 << f)-1)]
        actions = [0, (1 << f)-1, *[1 << i for i in range(f)], *[rng.getrandbits(f) for _ in range(4)]]
    checked = 0; wrong_control_counterexample = None
    n = 12*(f//4+1)*K; selected = sum(1 << p for slot in physical_positions(f, K) for p in slot)
    for y, z in controls:
        active, permutation, stages = compile_word(y, z, f)
        for action in actions:
            direct = action
            for distance, mask in stages:
                direct = reference_switch(direct, distance, mask, f)
            wanted = permute_bits(action, permutation)
            if direct != wanted:
                raise AssertionError('The alternating-cycle network misses its desired permutation')
            actual = run_word(action, y, z, f, stages)
            if actual != (wanted, y, z) or run_word(*actual, f, stages, reverse=True) != (action, y, z):
                raise AssertionError('The literal complete control-preserving word or inverse failed')
            spectator = rng.getrandbits(n-3*f)
            physical = physical_embed((action, y, z), f, K, spectator)
            transported = physical_apply(physical, f, K, stages)
            if (transported ^ physical) & ~selected or physical_apply(transported, f, K, stages, reverse=True) != physical:
                raise AssertionError('Full guard/spectator address planes did not restore')
            checked += 1
    return dict(status='PASS EXACT BENES CONTROL-FIBER ENDPOINT WORD', f=f, K=K, seed=seed,
                control_cases=len(controls), action_cases=len(actions), complete_selected_cube=f == 4,
                finite_physical_address_cases=checked, complete_address_bits=n,
                active_selected_bits=3*f, retired_guard_chunks=12,
                stages_each=2*(f.bit_length()-1)-1, packed_xor_words_per_stage=18,
                native_rotation_word_count_if_available=144*(2*(f.bit_length()-1)-1),
                restored=['Both control slots','Every borrowed quarter at each endpoint','All guard and unselected address bits'],
                xor_native_interface_assumed_not_executed=True,
                guard_preprocessing_and_child_layout=False,
                residual_child_and_precision_bill=False,
                native_faster_zeta_supplier=False,
                scope='Exact Boolean endpoint/companion chronology. Gaussian coefficient transport is the induced monomial permutation; native eight-rotation implementation, shape/cost and child recurrence remain conditional.',
                seconds=time.monotonic()-started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    source = Path(__file__); digest = sha256(source.read_bytes()).hexdigest()
    tasks = [(4, 1, 20261009091), (4, 2, 20261009092), (8, 1, 20261009093), (16, 2, 20261009094)]
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,
                    source_sha256={source.name:digest},tasks=tasks,stdlib_only=True,
                    resource_preflight=dict(aggregate_memory_bytes_upper=1024*1024*1024),
                    hypothesis='Restored opposite linear slot gauges can align Benes pairs while unused action quarters supply logically independent complete companions.')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(probe,tasks):
            results.append(result);print(json.dumps({k:result[k] for k in ('f','K','status','finite_physical_address_cases','seconds')}),flush=True)
    if sha256(source.read_bytes()).hexdigest()!=digest:
        raise AssertionError('The effective endpoint-word source changed during execution')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__':
    main()
