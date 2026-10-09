#!/usr/bin/env python3
"""Bounded literal closed-center source/sink/dirty and phase-interface check."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import closed_center_release as c


def verify():
    cases = []
    for columns, mode in [(1, 'all-columns'), (2, 'origin-columns')]:
        spec = c.component('orthogonal-color', 3)
        scalar = c.scalar_columns(spec)
        phase = c.matrix_controls(spec)
        physical = c.physical_probe(spec, columns, mode == 'all-columns')
        cases.append(dict(family='orthogonal-color', h=3, columns=columns,
                          scalar_columns=scalar, phase_edges=len(phase), physical_operator=physical,
                          chronology=c.ledger(3, 3, 1)))
    spec = c.component('single-total', 7)
    scalar = c.scalar_columns(spec)
    # One noncoordinate weight-five label checks the literal affine dual
    # routing/chirp normal form; the full experiment checked all 21 labels.
    one_label = dict(spec, labels=spec['labels'][:1])
    phase = c.matrix_controls(one_label)
    if not phase or phase[0]['relative_child_width'] != 6:
        raise ValueError('Bounded five-label single-child interface failed')
    cases.append(dict(family='single-total', h=7, columns=1, scalar_columns=scalar,
                      representative_phase_edge=phase[0], physical_operator=None,
                      chronology=c.ledger(7, 21, 21)))
    # A label of weight3 needs an affine offset; the no-offset control must
    # reject it rather than silently claim that the same interface applies.
    try:
        c.matrix_controls(dict(h=3, labels=[7]))
    except ValueError as error:
        phase_negative = str(error)
    else:
        raise ValueError('Out-of-scope weight-three normal was accepted')
    larger = []
    for h in (20, 28, 30):
        v, q = c.comb(h, 5), c.comb(h, 2)
        ledger = c.ledger(h, v, q)
        if ledger['deficit'] != 2 * v - 2 * q * h:
            raise ValueError('All-h component accounting changed')
        larger.append(dict(h=h, vertices=v, center_rank=q, chronology=ledger))
    return dict(status='PASS BOUNDED LITERAL CLOSED CENTER RELEASE',
                recorded_utc=datetime.now(timezone.utc).isoformat(), cases=cases,
                weight_three_interface_rejection=phase_negative,
                larger_component_ledgers=larger,
                scope='Center-only Kx: exact complete bounded physical source/sink/dirty operators, total-basis scalar columns and a literal one-child phase interface. Larger ledgers are algebraic component counts, not full multiplier certificates. Side integration, tape schedule and precision remain open.')


def source_paths():
    # Include transitive loaded modules, even the unused capacity interface.
    names = ['total_center_basis.py', 'total_center_capacity.py',
             'center_native_leverage.py', 'five_subset_envelope.py', 'characteristic.py',
             'center_basis_scalar_word.py', 'structured_center_basis.py', 'center_null_basis.py']
    return [Path(__file__), Path(c.__file__), Path(c.bank.__file__), Path(c.g.__file__),
            Path(c.f.__file__), Path(c.f.__file__).with_name('lagrangian_graph_completion.py'),
            Path(c.f.__file__).with_name('trimmed_zeta_dirty_probe.py'), c.f.SIDE_SOURCE] + [c.COMPLEX / name for name in names]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    hashes = {path: sha256(path.read_bytes()).hexdigest() for path in source_paths()}
    result = verify()
    if any(sha256(path.read_bytes()).hexdigest() != value for path, value in hashes.items()):
        raise ValueError('Effective source changed during component verification')
    result['source_sha256'] = {path.name: value for path, value in hashes.items()}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2, default=str) + '\n')
    print(json.dumps(dict(status=result['status'], cases=len(result['cases']),
                          explicit_physical_columns=72, covariant_physical_columns=576,
                          total_scalar_columns=63)))


if __name__ == '__main__':
    main()
