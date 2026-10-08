#!/usr/bin/env python3
"""Exact all-address normalized-H/CNOT simulation and word recovery controls.

This checks algebra and dyadic precision only. It does not implement native C
physical framing, pay access to a selected target mask, or establish a saving.
"""
import argparse
import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter


def tz_half(x):
    return x // 2 if x >= 0 else -((-x) // 2)


def half_hadamard(values, target, ledger):
    stride = 1 << target
    for base in range(0, len(values), stride * 2):
        for i in range(base, base + stride):
            a, b = values[i], values[i + stride]
            values[i] = tz_half(a + b)
            values[i + stride] = tz_half(a - b)
    ledger['pair_butterflies'] += len(values) // 2
    ledger['payload_word_reads'] += len(values)
    ledger['payload_word_writes'] += len(values)


def cnot_layer(values, pairs, group_width, ledger, omit_phase=False):
    # Disjoint SWAP endpoints make different CNOT pairs commute. Groups are
    # deliberately allowed to be noncontiguous; their native exposure is open.
    for start in range(0, len(pairs), group_width):
        group = pairs[start:start + group_width]
        for source, target in group:
            half_hadamard(values, target, ledger)
        if not omit_phase:
            for index, value in enumerate(values):
                parity = 0
                for source, target in group:
                    parity ^= ((index >> source) & (index >> target) & 1)
                if parity:
                    values[index] = -value
            ledger['parity_payload_scans'] += 1
            ledger['payload_word_reads'] += len(values)
            ledger['payload_word_writes'] += len(values)
        for source, target in group:
            half_hadamard(values, target, ledger)
        ledger['completed_H_calls'] += 2


def involutions(permutation):
    seen = set(); first = []; second = []
    for origin in range(len(permutation)):
        if origin in seen:
            continue
        cycle = []; current = origin
        while current not in seen:
            seen.add(current); cycle.append(current); current = permutation[current]
        assert current == origin
        length = len(cycle)
        # A(i)=-i and B(i)=1-i; B(A(i))=i+1 around the cycle.
        for reflection, pairs in [(0, first), (1, second)]:
            for i in range(length):
                j = (reflection - i) % length
                if i < j:
                    pairs.append((cycle[i], cycle[j]))
    a = list(range(len(permutation))); b = a.copy()
    for i,j in first: a[i],a[j] = a[j],a[i]
    for i,j in second: b[i],b[j] = b[j],b[i]
    assert [b[a[i]] for i in range(len(a))] == permutation
    return first, second


def address_map(index, permutation):
    output = 0
    for i, destination in enumerate(permutation):
        output |= ((index >> i) & 1) << destination
    return output


def nearest(x, shift):
    if shift <= 0:
        return x << (-shift)
    absolute = (abs(x) + (1 << (shift - 1))) >> shift
    return absolute if x >= 0 else -absolute


def run(config):
    start = perf_counter(); b = config['address_bits']; q = config['word_bits']
    rng = random.Random(config['seed']); permutation = list(range(b))
    rng.shuffle(permutation)
    if config.get('single_cycle'):
        order = permutation.copy()
        for i,bit in enumerate(order): permutation[bit] = order[(i+1)%b]
    first, second = involutions(permutation)
    loss = 3 * (len(first) + len(second)); assert loss <= 3*b
    guard = (12*b).bit_length() + 10
    p = q + loss + guard
    source = [rng.randrange(-(1 << (q-2)), 1 << (q-2)) for _ in range(1 << b)]
    oracle = [0] * len(source)
    for index,word in enumerate(source): oracle[address_map(index,permutation)] = word

    def attempt(work_bits, omit_phase=False, wrong_restoration=False):
        shift = work_bits-q
        values = [word << shift for word in source]
        ledger = {name:0 for name in ['pair_butterflies','payload_word_reads','payload_word_writes',
                                      'parity_payload_scans','completed_H_calls']}
        for pairs in [first,second]:
            cnot_layer(values,pairs,config['group_width'],ledger,omit_phase)
            cnot_layer(values,[(j,i) for i,j in pairs],config['group_width'],ledger,omit_phase)
            cnot_layer(values,pairs,config['group_width'],ledger,omit_phase)
        recovery_shift = work_bits-q-loss+(1 if wrong_restoration else 0)
        recovered = [nearest(word,recovery_shift) for word in values]
        failures = sum(a != b for a,b in zip(recovered,oracle))
        maximum = max(abs(a-b) for a,b in zip(recovered,oracle))
        return {'work_bits':work_bits,'omitted_phase':omit_phase,'wrong_restoration':wrong_restoration,
                'failures':failures,'maximum_integer_error':maximum,'ledger':ledger}

    positive = attempt(p)
    assert positive['failures'] == 0
    low = attempt(q+max(0,loss-8))
    assert low['failures'] > 0
    # Phase and normalization negatives use a prefix of addresses for larger
    # controls only if requested: full controls are retained by default.
    phase = attempt(p,omit_phase=True); assert phase['failures'] > 0
    restoration = attempt(p,wrong_restoration=True); assert restoration['failures'] > 0
    return {'config':config,'coordinate_permutation':permutation,'involution_pairs':[first,second],
            'restoration_bits':loss,'precision_guard_bits':guard,'rows':len(source),
            'positive':positive,'insufficient_precision_negative':low,
            'omitted_parity_negative':phase,'wrong_normalization_negative':restoration,
            'seconds':perf_counter()-start,
            'status':'exact coordinate permutation and bounded-word controls passed',
            'limitation':'Algebra and explicit dyadic butterfly simulation only; native C-only selected-mask framing and tape cost remain unproved.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    config=json.loads(Path(args.config).read_text());started=datetime.now(timezone.utc).isoformat()
    rows=[]
    for item in config:
        row=run(item);rows.append(row)
        (out/(item['id']+'.json')).write_text(json.dumps(row,indent=2)+'\n')
        print(json.dumps({'id':item['id'],'rows':row['rows'],'seconds':row['seconds'],
                          'loss':row['restoration_bits'],'status':row['status']}),flush=True)
    result={'start_utc':started,'end_utc':datetime.now(timezone.utc).isoformat(),'rows':rows,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
