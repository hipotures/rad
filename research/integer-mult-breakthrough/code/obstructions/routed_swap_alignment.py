#!/usr/bin/env python3
"""Exact routed signed-SWAP alignment and its single-interface rank boundary.

An address permutation can align different odd source/sink labels, but it
also restores the full mixing rank at the corresponding routed interface.
This is not a lower bound on shared, nonunitary or arbitrary circuits.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import canonical_framed_shear_boundary as literal
from unitary_dyadic import ONE, ZERO


def permute_label(label, permutation):
    return sum(((label >> j) & 1) << destination
               for j, destination in enumerate(permutation))


def permute(values, permutation, columns):
    out = [ZERO] * len(values)
    for address, value in enumerate(values):
        target = sum(((address >> (j * columns + c)) & 1)
                     << (destination * columns + c)
                     for j, destination in enumerate(permutation)
                     for c in range(columns))
        out[target] = value
    return out


def translate(values, label, h, columns):
    mask = sum(((label >> j) & 1) << (j * columns + c)
               for j in range(h) for c in range(columns))
    return [values[a ^ mask] for a in range(len(values))]


def relative(values, u, t, permutation, h, columns, routed):
    values = literal.line(values, u, h, columns, True)
    if routed:
        values = permute(values, permutation, columns)
    values = literal.line(values, t, h, columns, True)
    return literal.full(values, h * columns)


def probe(case):
    h, u, permutation, columns = case
    t = permute_label(u, permutation)
    if u.bit_count() % 2 != 1 or t.bit_count() % 2 != 1 or (u & t).bit_count() % 2:
        raise ValueError('This discriminator requires orthogonal odd labels')
    if sorted(permutation) != list(range(h)):
        raise ValueError('The address router is not a coordinate permutation')
    inverse = tuple(permutation.index(j) for j in range(h))
    size = 1 << (h * columns)
    support_unrouted = set()
    support_routed = set()
    digest = sha256()
    coefficients = 0
    for address in range(size):
        values = [ONE if a == address else ZERO for a in range(size)]
        unmoved = relative(values, u, t, permutation, h, columns, False)
        moved = relative(values, u, t, permutation, h, columns, True)
        expected = literal.full(translate(permute(values, permutation, columns), t, h, columns), h * columns)
        if moved != expected:
            raise AssertionError('F A_t^-1 P A_u^-1 is not F X_t P')
        # The router commutes with F, but not with an unmatched line frame.
        if permute(literal.full(values, h * columns), permutation, columns) != literal.full(permute(values, permutation, columns), h * columns):
            raise AssertionError('Coordinate routing failed to commute with the full tensor')
        support_unrouted.add(sum(z != ZERO for z in unmoved))
        support_routed.add(sum(z != ZERO for z in moved))
        digest.update(str((unmoved, moved)).encode())
        coefficients += 2 * size
    if support_unrouted != {1 << ((h - 2) * columns)} or support_routed != {size}:
        raise AssertionError('Routed or unrouted exact support has the wrong mixing rank')
    # Input frames diag(A_u,I), output frames diag(F,F A_t^-1),
    # virtual SWAP [[0,P^-1],[-P,0]]. Native monomial corrections
    # return uniform F on both labeled raw data banks.
    columns_checked = 0
    unmatched_control = False
    for bank in range(2):
        for address in range(size):
            x = [ONE if bank == 0 and a == address else ZERO for a in range(size)]
            y = [ONE if bank == 1 and a == address else ZERO for a in range(size)]
            output_x = literal.full(permute(y, inverse, columns), h * columns)
            output_y = [-z for z in relative(x, u, t, permutation, h, columns, True)]
            repaired_x = [-z for z in permute(translate(output_y, t, h, columns), inverse, columns)]
            repaired_y = permute(output_x, permutation, columns)
            target = literal.full(x, h * columns), literal.full(y, h * columns)
            if (repaired_x, repaired_y) != target:
                raise AssertionError('Routed signed-SWAP monomial correction failed')
            wrong_y = [-z for z in relative(x, u, t, permutation, h, columns, False)]
            wrong_repaired_x = [-z for z in permute(translate(wrong_y, t, h, columns), inverse, columns)]
            unmatched_control |= (wrong_repaired_x, repaired_y) != target
            columns_checked += 1
    if not unmatched_control:
        raise AssertionError('Unmatched virtual router was not discriminating')
    return dict(h=h, columns=columns, source_label=u, sink_label=t,
                coordinate_permutation=permutation, orthogonal_odd_labels=True,
                exact_interface_coefficients=coefficients,
                complete_pair_operator_columns=columns_checked,
                unrouted_selected_rank=h-2, routed_selected_rank=h,
                unrouted_physical_support=1 << ((h-2)*columns),
                routed_physical_support=size,
                raw_signed_swap_canonicalization_passed=True,
                unmatched_router_rejected=True, interface_output_sha256=digest.hexdigest(),
                scope='Exact actual interfaces and raw pair end map. The full-support routed relative cannot have a single C_(h-2) child with only monomial/diagonal wrappers. This does not exclude shared implementations or establish an asymptotic native lower bound.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('Positive worker count required')
    if args.output and args.output.exists():
        raise FileExistsError('Use a fresh evidence directory')
    cases = [(4, 7, (3, 1, 2, 0), 1)] if args.bounded else [
        (3, 1, (2, 1, 0), 1), (3, 1, (2, 1, 0), 2),
        (4, 1, (3, 1, 2, 0), 1), (4, 7, (3, 1, 2, 0), 1)]
    sources = [Path(__file__), Path(literal.__file__), Path(literal.geometry.__file__),
               Path(literal.geometry.arithmetic.__file__), Path(__file__).with_name('unitary_dyadic.py')]
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    cases=cases, source_sha256={str(p): sha256(p.read_bytes()).hexdigest() for p in sources},
                    seed=None, scope='Single routed Clifford interface and canonical pair algebra; no helper chronology or multiplier transfer')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(probe, cases))
    if any(sha256(Path(name).read_bytes()).hexdigest() != digest for name, digest in protocol['source_sha256'].items()):
        raise ValueError('An effective source changed during verification')
    summary = dict(status='PASS ROUTED SWAP ALIGNMENT BOUNDARY', cases=results,
                   multiplier_exponent_established=False)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(status=summary['status'], cases=len(results),
                          complete_operator_columns=sum(c['complete_pair_operator_columns'] for c in results))))


if __name__ == '__main__':
    main()
