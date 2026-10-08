#!/usr/bin/env python3
"""Independent support/link and complete-moment check of a changed native DAG.

The binary format and ordered (23,25) geometry are pinned PR40 interfaces.
This checker imports no producer, matcher, profiler or controller scorer.
It proves exact support and link validity for the supplied finite DAG, then
checks its supplied fixed-profile controller arithmetic. It does not replay
the large rational matrix profiler or certify the inherited tape compiler.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
from itertools import combinations
import json
from math import comb, factorial
from pathlib import Path
import struct


GRID = 1 << 128


def down(x):
    return F((x.numerator*GRID)//x.denominator, GRID)


def up(x):
    return F((x.numerator*GRID+x.denominator-1)//x.denominator, GRID)


def log_interval(x):
    x, k = F(x), 0
    assert x >= 1
    while x > 2:
        x /= 2
        k += 1
    def small(y):
        z = (y-1)/(y+1)
        low = 2*sum((z**(2*j+1)/(2*j+1) for j in range(32)), F())
        high = low+2*z**65/(65*(1-z*z))
        return low, high
    a, b = small(x)
    c, d = small(F(2))
    return down(a+k*c), up(b+k*d)


def exact_moment(widths, m, W, saving):
    low = high = F()
    for t, count in sorted(widths.items()):
        ll, lh = log_interval(F(m, t))
        x, y = saving*ll, saving*lh
        assert 0 <= x <= y < 1
        # First omitted term is x^9/9!, later ratios are <=x/10.
        el = sum((x**j/factorial(j) for j in range(9)), F())
        eh = sum((y**j/factorial(j) for j in range(9)), F())
        eh += y**9/(factorial(9)*(1-y/10))
        weight = F(count*t, m*W)
        low += weight*el
        high += weight*eh
    return dict(saving=str(saving), lower=str(down(low)), upper=str(up(high)),
                strict_gap_lower=str(down(1-high)),
                strictly_passes=high < 1, strictly_fails=low >= 1,
                enclosure="32-term atanh/geometric tail; Taylor8/geometric tail; outward2^-128 grid")


def parse_dag(path):
    data = path.read_bytes()
    h, v, n, q = struct.unpack_from('<4I', data)
    at = 16
    def array(code, count):
        nonlocal at
        values = struct.unpack_from('<%d%s' % (count, code), data, at)
        at += struct.calcsize(code)*count
        return values
    args = array('I', 2*n)
    core, cover = array('Q', n), array('Q', n)
    roots, kind = array('I', q), array('I', q)
    active = data[at:at+n]
    assert len(active) == n and at+n == len(data)
    assert v == comb(h, 3) and q == h*(comb(h-1, 2)+1)
    triples = list(combinations(range(h), 3))
    support, cores, covers = [0]*n, [0]*n, [0]*n
    adds, inputs = 0, 0
    ranks = [0]*n
    for x in range(1, n):
        if not active[x]:
            continue
        left, right = args[2*x:2*x+2]
        if left:
            assert 0 < left < x and 0 < right < x
            assert active[left] and active[right]
            assert not support[left] & support[right]
            support[x] = support[left] | support[right]
            cores[x], covers[x] = cores[left]&cores[right], covers[left]|covers[right]
            ranks[x] = covers[x].bit_count()-cores[x].bit_count()
            adds += 1
        else:
            assert not right and x <= v
            support[x] = 1 << (x-1)
            cores[x] = covers[x] = sum(1 << j for j in triples[x-1])
            ranks[x] = 1
            inputs += 1
        assert cores[x] == core[x] and covers[x] == cover[x] and cores[x]
        # A repeated two-point core is a complete pair-star, which justifies
        # interning a node by its core and cover across common-point circuits.
        if cores[x].bit_count() == 2:
            expected = sum(1 << i for i, t in enumerate(triples)
                           if sum(1 << j for j in t) & cores[x] == cores[x]
                           and not sum(1 << j for j in t) & ~covers[x])
            assert support[x] == expected
    assert inputs == v
    position, retained, output_loss = 0, 0, 0
    root_outputs = set()
    for common in range(h):
        head = [j for a in range(0, h-1, 2) if common not in (a, a+1) for j in (a, a+1)]
        points = head+[j for j in range(h) if j != common and j not in head]
        for excluded in [()]+list(combinations(range(h-1), 2)):
            root, is_total = roots[position], kind[position]
            assert active[root] and is_total == int(not excluded)
            exclude = {points[k] for k in excluded}
            expected = sum(1 << i for i, t in enumerate(triples)
                           if common in t and not exclude.intersection(t))
            assert support[root] == expected
            root_outputs.add((common, tuple(sorted((common, *exclude)))))
            if is_total:
                assert core[root] == 1 << common and cover[root] == (1 << h)-1
                assert ranks[root] == h-1
                retained += 1
                output_loss += ranks[root]
            position += 1
    assert position == q and len(root_outputs) == q and retained == h
    return dict(h=h, v=v, n=n, q=q, additions=adds, loss=output_loss,
                roots=roots, kind=kind, args=args, active=active,
                core=core, cover=cover, ranks=ranks)


def check_links(path, dag):
    data = path.read_bytes()
    n, count = struct.unpack_from('<2I', data)
    assert n == dag['n'] and len(data) == 8+8*count
    links = struct.unpack_from('<%dI' % (2*count), data, 8)
    donors, candidates = set(), {}
    root_uses = {}
    for j, root in enumerate(dag['roots']):
        root_uses.setdefault(root, []).append(j)
    for donor, target in zip(links[::2], links[1::2]):
        assert donor not in donors and dag['active'][donor]
        donors.add(donor)
        assert dag['args'][2*donor]
        # The pinned link export stores only (donor,target NODE), omitting the
        # occurrence tag distinguishing an addition input from a root use.
        # Recover admissible occurrences, then verify an injective assignment.
        assert 0 < target < n and dag['active'][target]
        ru, rt = dag['ranks'][donor], dag['ranks'][target]
        assert not dag['core'][target] & ~dag['core'][donor]
        assert not dag['cover'][donor] & ~dag['cover'][target]
        choices = []
        if ru < rt or (ru == rt and donor < target):
            for value in dag['args'][2*target:2*target+2]:
                if value and value in dag['args'][2*donor:2*donor+2]:
                    assert dag['ranks'][value] <= ru <= rt
                    choices.append(('gate', target, value))
        if ru <= rt and target in dag['args'][2*donor:2*donor+2]:
            for j in root_uses.get(target, []):
                choices.append(('root', j))
        assert choices
        candidates[donor] = choices
    assigned = {}
    def augment(donor, seen):
        for use in candidates[donor]:
            if use in seen:
                continue
            seen.add(use)
            if use not in assigned or augment(assigned[use], seen):
                assigned[use] = donor
                return True
        return False
    for donor in sorted(candidates):
        assert augment(donor, set())
    assert len(assigned) == count
    return dict(matched=count, R=dag['additions']+dag['q']-count,
                unique_donors=True, injective_valid_target_use_assignment=True,
                rank_time_order=True, all_original_envelope_links_nested=True,
                scope="Validity of supplied matching; maximum-cardinality is not asserted by this checker")


def controller(rows):
    a, b = (r['h'] for r in rows)
    assert (a, b) == (23, 25)
    m, N = a*b, comb(a, 3)*comb(b, 3)
    widths, banks, L = Counter(), [], 0
    for row in rows:
        h, v, R, loss = (row[k] for k in ('h', 'v', 'R', 'loss'))
        assert v == comb(h, 3) and loss == h*(h-1)
        blocks = list(row['blocks'])
        assert len(blocks) == h+1 and min(blocks) >= 0 and blocks[h] >= h
        assert sum(t*c for t, c in enumerate(blocks)) == row['rank_sum'] == h*R+2*loss
        blocks[h] -= h
        blocks[1] += h
        copies, bank = N//v, N//v*R
        banks.append(bank)
        L += copies*loss
        for t, count in enumerate(blocks):
            if t:
                widths[t] += copies*count
        widths[h] += bank
        widths[m-2*h] += bank
        widths[1] += 2*N
        widths[h-2] += 2*N
    widths[1] += 9*2*N+N
    for t in (21, 17, 481):
        widths[t] += 2*N
    W = 2*N+sum(banks)
    assert sum(t*c for t, c in widths.items()) == W*m-N+L
    return dict(m=m, N=N, W=W, L=L, banks=banks, total_rank=W*m-N+L,
                deficit=N-L, widths=dict(sorted(widths.items())), maxchild=max(widths))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dag', required=True, type=Path)
    ap.add_argument('--links', required=True, type=Path)
    ap.add_argument('--first', required=True, type=Path)
    ap.add_argument('--second', required=True, type=Path)
    ap.add_argument('--saving', required=True, type=F)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    assert __debug__, 'Run without Python -O'
    dag = parse_dag(args.dag)
    links = check_links(args.links, dag)
    rows = [json.loads(p.read_text()) for p in (args.first, args.second)]
    for key in ('h', 'v', 'loss'):
        assert rows[0][key] == dag[key]
    assert rows[0]['R'] == links['R']
    c = controller(rows)
    moment = exact_moment(c['widths'], c['m'], c['W'], args.saving)
    result = dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
                  status='independent_changed_dag_and_complete_controller_check',
                  dag={k: dag[k] for k in ('h', 'v', 'n', 'q', 'additions', 'loss')},
                  exact_supports=True, disjoint_additions=True, exact_core_cover=True,
                  all_retained_centers_exact=True, all_triple_exclusion_outputs_exact=True,
                  matching=links, controller=c, moment=moment,
                  inputs=[dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                          for p in (args.dag, args.links, args.first, args.second)],
                  checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Does not independently replay full fixed matrices or certify the inherited tape compiler')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'dag', 'matching')}, indent=2))
    print(json.dumps(dict(W=c['W'], total_rank=c['total_rank'], deficit=c['deficit'],
                          moment_pass=moment['strictly_passes'], gap_lower=moment['strict_gap_lower']), indent=2))


if __name__ == '__main__':
    main()
