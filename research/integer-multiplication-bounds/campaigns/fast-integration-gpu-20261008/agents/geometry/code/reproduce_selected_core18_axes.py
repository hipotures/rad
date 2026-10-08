#!/usr/bin/env python3
"""Rebuild the selected signed core18 axes from pinned public scalar code.

The finite word, dirty-state replay, exact native CRT profiles and independent
Fraction controls are reproduced here. Full DATA and assembly binders remain
separate acceptance gates. The public interval construction is Avi Eisenberg's
PR62 and joint compilation is eumemic's PR57.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys


PINS = {
    23: (3584, 'beta:1:15',
         '40e40425b52408f9cf4be7f6bce5ffe5c46fcc1d551990553db53ed1baf2515f',
         'b8e3e030e49585145aee0b8fbb50ef99f9dda27af091324717ac0ca0fab55e19',
         '4dd20f628b863c6b273eed914da5fffb51a1838f003235d04ff78266fb26637e'),
    25: (5120, 'beta:7:207',
         '5af6e1bdf2e6fafe888fd6b224bfa1e940fceb264df5362bb66a2d40592259c8',
         '84c11453798a37b2c0525fb0cfcb0bdaca5943428c43caffcc43472cb52f4039',
         'a59cafdc6efe3348583f2afb84de561e4f18781ba3488af0ba51803d51f8341e')
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--native', type=Path)
    parser.add_argument('--axes', nargs='+', type=int, choices=(23, 25), default=[23, 25])
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.source = args.source.resolve()
    args.work = args.work.resolve()
    source_head = subprocess.check_output(
        ['git', '-C', str(args.source), 'rev-parse', 'HEAD'], text=True).strip()
    assert source_head == 'ad0f25ff7b23cff7f08ad237c2254e6ecf74257e'
    args.work.mkdir(parents=True)
    code = Path(__file__).resolve().parent
    graph = code.parent.parent / 'graph' / 'code'
    environment = dict(os.environ)
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        environment[key] = '1'
    commands = []

    def run(command, name):
        command = [str(value) for value in command]
        commands.append(command)
        with (args.work / f'{name}.log').open('wb') as log:
            subprocess.run(command, check=True, env=environment,
                           stdout=log, stderr=subprocess.STDOUT)

    native = args.native.resolve() if args.native else args.work / 'signed_joint_word_profiles'
    if args.native is None:
        run(['g++', '-O3', '-std=c++17', code / 'signed_joint_word_profiles.cpp',
             '-o', native], 'build-native')
    cases = []
    for h in args.axes:
        budget, basis, parent_hash, word_hash, transition_hash = PINS[h]
        order = list(range(h))
        order[h - 3], order[h - 2] = order[h - 2], order[h - 3]
        receipt = args.work / f'h{h}-source.json'
        run([sys.executable, graph / 'source_only_selective_signed_joint.py',
             '--source', args.source, '--work', args.work / f'h{h}-source',
             '--output', receipt, '--h', h, '--budget', budget,
             '--order', *order, '--mode', 'core-single', '--value', 18,
             '--expected-parent-sha256', parent_hash,
             '--expected-word-sha256', word_hash], f'h{h}-source')
        source = json.loads(receipt.read_text())
        transitions = Path(source['independent']['transition_path'])
        assert sha256(transitions.read_bytes()).hexdigest() == transition_hash
        profile = args.work / f'h{h}-profile.json'
        audit = args.work / f'h{h}-matrix-audit.json'
        run([native, transitions, basis, profile, audit], f'h{h}-native')
        cases.append(dict(case_id=f'h{h}-selected-core18', binary=str(transitions),
                          basis=basis, audit=str(audit)))
    controls_input = args.work / 'independent-controls-input.json'
    controls_input.write_text(json.dumps(cases, indent=2) + '\n')
    controls = args.work / 'independent-controls.json'
    run([sys.executable, code / 'review_signed_joint_word_profiles.py',
         '--input', controls_input, '--work', args.work / 'independent-controls',
         '--output', controls, '--samples', 48], 'independent-controls')
    result = dict(status='PASS SELECTED CORE18 FINITE AXIS REPRODUCTION',
                  source_head=source_head, axes=args.axes, commands=commands,
                  controls=controls.name,
                  driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  completed_utc=datetime.now(timezone.utc).isoformat(),
                  scope='Pinned scalar construction, complete both-dirty literal word, '
                        'actual signed transition byte identity, full rational CRT native '
                        'profiles and 48 independent Gram/pivot/minor controls per axis. '
                        'Source-pair DATA coverage, stock, complete recurrence, assembly '
                        'and conditional all-size assumptions require separate binders.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], axes=args.axes)), flush=True)


if __name__ == '__main__':
    main()
