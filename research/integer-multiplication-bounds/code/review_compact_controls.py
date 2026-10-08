#!/usr/bin/env python3
"""Independent exact modular address/repair and row-layout compact audit.

The control model is reconstructed from the written four-update identity.
No upstream control implementation is imported. Tests include full small
rectangles, nonempty guard boundaries, both source orders and bad carries.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
import resource
import subprocess
import time

PIN = '6e564879f51ae16f23d392e9e196c605f36d90df'


def specification(f, K, G, rho, later):
    assert f >= 2 and K >= 1 and G >= 1 and 0 <= rho < K
    n = f-1
    widths = dict(u=n*G, t=n*G, x=f*K, y=f*K, b=n*G)
    order = ('u', 't', 'y', 'x', 'b') if later else ('u', 't', 'x', 'y', 'b')
    positions = {name:i for i, name in enumerate(order)}
    ops = []
    controls = 'u' if later else 'x'

    def rotation(target, kind, sign=1):
        dependence = {'first':(controls, 't'), 'second':(controls, 't'),
                      'load_t':('y',), 'unload_t':('y', controls), 'load_u':('x',)}[kind]
        assert target not in dependence
        assert all(positions[name] < positions[target] for name in dependence)
        ops.append(('rotate', target, kind, sign))

    def identity():
        rotation('y', 'first')
        ops.append(('swap', 't', 'b', 0)); rotation('b', 'load_t'); ops.append(('swap', 't', 'b', 0))
        rotation('y', 'second')
        ops.append(('swap', 't', 'b', 0)); rotation('b', 'unload_t', -1); ops.append(('swap', 't', 'b', 0))

    identity()
    if later:
        ops.append(('swap', 'u', 'b', 0)); rotation('b', 'load_u'); ops.append(('swap', 'u', 'b', 0))
        identity()
        ops.append(('swap', 'u', 'b', 0)); rotation('b', 'load_u', -1); ops.append(('swap', 'u', 'b', 0))
    assert sum(op[0] == 'swap' for op in ops) == (12 if later else 4)
    assert sum(op[0] == 'rotate' for op in ops) == (10 if later else 4)
    return widths, order, ops


def digit(v, i, G):
    return (v >> (i*G)) & ((1 << G)-1)


def execute(state, f, K, G, rho, later, inverse=False):
    widths, order, ops = specification(f, K, G, rho, later)
    q = dict(zip(order, state))
    assert all(0 <= q[name] < 1 << width for name, width in widths.items())
    n = f-1

    def source(i):
        return digit(q['u'], i, G) & 1 if later else (q['x'] >> (rho+i*K)) & 1

    def offset(kind):
        if kind in ('first', 'second'):
            return sum(source(i)*(2*digit(q['t'], i, G) if kind == 'first'
                                  else 1-2*digit(q['t'], i, G)) << (rho+i*K) for i in range(n))
        if kind == 'load_u':
            bits = [(q['x'] >> (rho+i*K)) & 1 for i in range(n)]
        else:
            bits = [((q['y'] >> (rho+i*K)) & 1) ^ (source(i) if kind == 'unload_t' else 0)
                    for i in range(n)]
        return sum(bit << (i*G) for i, bit in enumerate(bits))

    for action, target, other, sign in reversed(ops) if inverse else ops:
        if action == 'swap':
            q[target], q[other] = q[other], q[target]
        else:
            q[target] = (q[target]+(-sign if inverse else sign)*offset(other)) % (1 << widths[target])
    return tuple(q[name] for name in order)


def ideal(state, f, K, G, rho, later, highest=False):
    _, order, _ = specification(f, K, G, rho, later)
    q = dict(zip(order, state))
    indices = range(f) if highest else range(f-1)
    q['y'] ^= sum(((q['x'] >> (rho+i*K)) & 1) << (rho+i*K) for i in indices)
    return tuple(q[name] for name in order)


def bad(state, f, K, G, rho, later):
    _, order, _ = specification(f, K, G, rho, later)
    q = dict(zip(order, state)); B = 1 << G
    for i in range(f-1):
        if digit(q['t'], i, G) == B-1 or later and digit(q['u'], i, G) == B-1:
            return True
        guard = ((q['y'] >> (rho+i*K)) & ((1 << K)-1)) >> 1
        if not 2*B <= guard < (1 << (K-1))-2*B:
            return True
    return False


def key(state, widths, order):
    result = 0
    for field, value in zip(order, state):
        result = (result << widths[field]) | value
    return result


def exhaustive(K, rho, later):
    f, G = 2, 1
    widths, order, _ = specification(f, K, G, rho, later)
    states = list(product(*(range(1 << widths[name]) for name in order)))
    images = []
    holes = []
    extracted = []
    initial = list(range(len(states)))
    actual = [None]*len(states)
    expected = [None]*len(states)
    good = 0
    for identity, state in enumerate(states):
        image = execute(state, f, K, G, rho, later)
        assert execute(image, f, K, G, rho, later, True) == state
        assert execute(execute(state, f, K, G, rho, later, True), f, K, G, rho, later) == state
        target = ideal(state, f, K, G, rho, later)
        assert bad(target, f, K, G, rho, later) == bad(state, f, K, G, rho, later)
        assert bad(image, f, K, G, rho, later) == bad(state, f, K, G, rho, later)
        if not bad(state, f, K, G, rho, later):
            assert image == target
            good += 1
        actual[key(image, widths, order)] = identity
        expected[key(target, widths, order)] = identity
        images.append(key(image, widths, order))
    assert len(set(images)) == len(states)
    for i, q in enumerate(states):
        if bad(q, f, K, G, rho, later):
            holes.append(i)
            destination = ideal(execute(q, f, K, G, rho, later, True), f, K, G, rho, later)
            assert bad(destination, f, K, G, rho, later)
            extracted.append((key(destination, widths, order), actual[i]))
    # Independent stable binary radix passes realize the repair key sort.
    for position in range(sum(widths.values())):
        extracted = [item for item in extracted if not item[0] & (1 << position)] + [
            item for item in extracted if item[0] & (1 << position)]
    assert [item[0] for item in extracted] == holes
    for hole, (_, payload) in zip(holes, extracted):
        actual[hole] = payload
    assert actual == expected
    delta = min(Q(1), (f-1)*(Q(2 if later else 1, 1 << G)+Q(8*(1 << G), 1 << K)))
    assert Q(len(holes), len(states)) <= delta
    return dict(K=K, rho=rho, later_source=later, addresses=len(states), good=good,
                bad=len(holes), exact_bad_fraction=str(Q(len(holes), len(states))),
                claimed_bad_fraction_bound=str(delta), inverse_and_bijection=True,
                stable_radix_exceptional_repair_exact=True)


def boundaries(seed=109):
    rng = random.Random(seed)
    checks = good = repaired = 0
    for f, G, extra, rho_choice, later in product(range(2, 6), range(1, 5), (4, 5, 8), (0, 1), (False, True)):
        K = G+extra;rho = K-1 if rho_choice else 0
        widths, order, _ = specification(f, K, G, rho, later);B = 1 << G
        lower, upper = 2*B, (1 << (K-1))-2*B
        for selected, t_edge, u_edge, guard_edge, parity in product(range(1 << f), (0, B-2, B-1),
                (0, B-2, B-1), (lower-1, lower, upper-1, upper), (0, 1)):
            values = {name:rng.randrange(1 << width) for name, width in widths.items()}
            for i in range(f-1):
                j = rho+i*K
                values['x'] = (values['x'] & ~(1 << j)) | (((selected >> i) & 1) << j)
                values['y'] = (values['y'] & ~(((1 << K)-1) << j)) | ((2*guard_edge+parity) << j)
                mask = (B-1) << (i*G)
                values['t'] = (values['t'] & ~mask) | (t_edge << (i*G))
                values['u'] = (values['u'] & ~mask) | (u_edge << (i*G))
            state = tuple(values[name] for name in order)
            image = execute(state, f, K, G, rho, later)
            assert execute(image, f, K, G, rho, later, True) == state
            assert bad(image, f, K, G, rho, later) == bad(state, f, K, G, rho, later)
            if not bad(state, f, K, G, rho, later):
                assert image == ideal(state, f, K, G, rho, later)
                good += 1
            destination = ideal(execute(image, f, K, G, rho, later, True), f, K, G, rho, later)
            assert destination == ideal(state, f, K, G, rho, later)
            # The omitted top bit is disjoint and can be supplied afterward.
            q = dict(zip(order, destination))
            j = rho+(f-1)*K
            q['y'] ^= ((q['x'] >> j) & 1) << j
            assert tuple(q[name] for name in order) == ideal(state, f, K, G, rho, later, True)
            repaired += image != destination
            checks += 1
    return dict(seed=seed, adversarial_address_checks=checks, nonempty_good_checks=good,
                nontrivial_repairs=repaired, both_source_orders=True,
                highest_rho_boundary=True, digit_overflows_and_guard_endpoints=True)


def row_layouts():
    layouts = splits = fallback = 0
    for m, W, d, K, G in product((2, 3, 7), (3, 5, 13), (2, 3, 8, 17, 64), (1, 2, 7, 31), (1, 3, 6)):
        log_w = (W-1).bit_length()
        depth = 0
        while m**depth < d:depth += 1
        padded_depth = 0
        while m**padded_depth < 2*d:padded_depth += 1
        q0 = log_w*padded_depth; H = d*G
        front = (2*H+K-1)//K;back = (H+K-1)//K
        Q0 = q0+front+back
        rows = 1 << (q0*K)
        padded = ((rows+W**depth-1)//W**depth)*W**depth
        assert rows >= W**depth and rows <= padded < 2*rows
        for D in (0, 1, min(d, Q0), d):
            if D <= Q0:
                assert D <= min(d, Q0)
                fallback += 1
                continue
            active = D-Q0
            assert q0*K+2*H+(front*K-2*H)+active*K+H+(back*K-H) == D*K
            assert front*K >= 2*H and back*K >= H
            for j in range(depth+1):
                assert padded % W**(depth-j) == 0
                count = padded//W**j
                if j < depth:
                    assert count % W == 0
                    # Only row coordinates divide. Every role gets the
                    # full identical within-row compact field product.
                    for u in (0, 1, count//2, count-1):
                        g, w = divmod(u, W)
                        assert 0 <= g < count//W and 0 <= w < W and W*g+w == u
                        splits += 1
            for f in (1, min(active, m), active):
                assert max(f-1, 0)*G <= H
            layouts += 1
    for p in range(2, 2049):
        ell = (p-1).bit_length();G = 4*ell+6;K = G+4*ell+10
        fraction = (p-1)*(Q(2, 1 << G)+Q(8*(1 << G), 1 << K))
        assert fraction <= Q(5, 128*p**3)
    return dict(layout_configurations=layouts, sampled_exact_row_splits=splits,
                small_D_fallbacks=fallback, exact_cutoff_fraction_checks=2047,
                no_independent_address_coordinates_added=True,
                compact_fields_excluded_from_row_index=True,
                zero_rows_pad_whole_complete_within_row_ranges=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args();assert not args.output.exists()
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=args.reference, text=True).strip()
    assert commit == PIN
    start = time.monotonic();started = datetime.now(timezone.utc).isoformat()
    exact = [exhaustive(K, rho, later) for K, rho in ((2, 0), (2, 1), (3, 0), (3, 2)) for later in (False, True)]
    print('PASS complete small address rectangles', sum(row['addresses'] for row in exact), flush=True)
    result = dict(status='PASS', reference_commit=commit, started_utc=started,
                  exhaustive_rectangles=exact, adversarial_guards=boundaries(), complete_layouts=row_layouts(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  input_sha256={name:sha256((args.reference/name).read_bytes()).hexdigest() for name in
                                ('notes/compact-control-movement.tex', 'notes/compact-control-layout.tex',
                                 'notes/compact-control-guard.tex', 'notes/independent-complex.tex')},
                  completed_utc=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic()-start,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Independent finite exact modular address, inverse, exception repair and complete-field layout controls; tape costs and all-size transfer require written proof review')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS adversarial guards', result['adversarial_guards']['adversarial_address_checks'], flush=True)


if __name__ == '__main__':main()
