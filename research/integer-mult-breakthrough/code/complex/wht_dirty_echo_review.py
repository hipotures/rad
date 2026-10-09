#!/usr/bin/env python3
"""Import-free Algorithm-5 eight-point dirty-echo review.

This independently builds literal rational shears and checks every source,
sink and arbitrary dirty helper column. It certifies only scalar algebra.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import random
from time import perf_counter


def macro():
    nodes = []
    def node(*terms):
        index = 8+len(nodes)
        assert all(0 <= source < index for _, source in terms)
        nodes.append([(Q(c), source) for c, source in terms])
        return index
    a = 0
    b, c, d, e, f, g, h = [node((2, j)) for j in range(1, 8)]
    bc = node((1, b), (1, c))
    dh = node((1, d), (1, h))
    fg = node((1, f), (1, g))
    total = node((1, bc), (1, dh))
    total = node((1, total), (1, fg))
    total = node((1, total), (1, e))
    total = node((Q(1, 2), total))
    delta = node((1, a), (-1, total))
    dd = node((1, delta), (1, d))
    ee = node((1, delta), (1, e))
    hh = node((1, delta), (1, h))
    def plus3(x, y, z):
        return node((1, node((1, x), (1, y))), (1, z))
    outputs = [node((1, a), (1, total)), plus3(ee, c, g), plus3(ee, b, f),
               node((1, ee), (1, dh)), node((1, dd), (1, bc)),
               plus3(hh, c, f), plus3(hh, b, g), node((1, dd), (1, fg))]
    assert len(nodes) == 30
    return nodes, outputs


def word(nodes, outputs, zero=False, omit_inverse=False):
    # Physical coordinates: sources0..7, helpers8..37, sinks38..45.
    gates = [(8+j, source, c) for j, terms in enumerate(nodes)
             for c, source in terms if not(zero and source < 8)]
    read = [(38+j, source, Q(-1 if zero else 1)) for j, source in enumerate(outputs)
            if not(zero and source < 8)]
    inverse = [(target, source, -c) for target, source, c in reversed(gates)]
    return gates+read+(inverse if not omit_inverse else [])


def execute(gates, initial):
    result = initial[:]
    for target, source, c in gates:
        result[target] += c*result[source]
    return result


def wanted(initial):
    result = initial[:]
    for target in range(8):
        result[38+target] += sum((-1 if (target & source).bit_count() & 1 else 1)*initial[source]
                                 for source in range(8))
    return result


def worker(seed):
    nodes, outputs = macro()
    gates = word(nodes, outputs)+word(nodes, outputs, True)
    assert len(gates) == 206
    inverse = [(target, source, -c) for target, source, c in reversed(gates)]
    rng = random.Random(seed)
    columns = [[Q(int(i == j)) for i in range(46)] for j in range(46)]
    columns += [[Q(rng.randrange(-37, 38), 1 << rng.randrange(5)) for _ in range(46)] for _ in range(8)]
    checked = 0
    digest = sha256()
    for original in columns:
        actual = execute(gates, original)
        assert actual == wanted(original)
        assert execute(inverse, actual) == original
        checked += 2*46
        digest.update(','.join(map(str, actual)).encode())
    dirty = [Q(0)]*8+[Q(j+1, 8) for j in range(30)]+[Q(0)]*8
    assert execute(word(nodes, outputs), dirty) != wanted(dirty)
    assert execute(word(nodes, outputs, omit_inverse=True)+word(nodes, outputs, True), dirty) != wanted(dirty)
    return dict(seed=seed, complete_source_sink_helper_columns=46,
        additional_dyadic_dirty_fields=8, forward_inverse_values=checked,
        literal_shears=len(gates), omitted_zero_echo_rejected=True,
        omitted_first_inverse_rejected=True, output_sha256=digest.hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 4:
        raise ValueError('Use one to four workers')
    started = perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        cases = list(pool.map(worker, (20261009, 20261010, 20261011, 20261012)))
    result = dict(status='PASS INDEPENDENT EXACT SCALAR REVIEW', dimension=8,
        helper_banks=30, arithmetic_additions=22, literal_divisions=1,
        leaf_input_scales=7, worker_processes=args.workers, cases=cases,
        elapsed_seconds=perf_counter()-started,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source='Alman and Rao, arXiv:2211.06459v2, Algorithm 5; parent producer independently inspected',
        scope='Finite scalar arithmetic and complete arbitrary-dirty transcription only. Native address operators, phase frame transitions, precision transfer and exponent are not certified.')
    encoded = json.dumps(result, indent=2)+'\n'
    if args.output:
        if args.output.exists():
            raise FileExistsError('Use a fresh attempt path')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    else:
        print(encoded, end='')


if __name__ == '__main__':
    main()
