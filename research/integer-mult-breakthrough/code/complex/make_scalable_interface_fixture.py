#!/usr/bin/env python3
"""Regenerate compact literal interface data for an independent reviewer."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import scalable_subspace_interfaces as compiler


def make_fixture():
    paired = tuple(3 << (2*j) for j in range(8))
    cases = [(3, (), (3, 5)),
             (4, (3,), (3, 4)),
             (4, (7,), (7, 8)),
             (4, (7, 8), (7,)),
             (4, (3,), (5,)),
             (16, paired[:4], paired),
             (16, (7,), tuple(1 << j for j in range(16))),
             (16, compiler.reference.perpendicular((7,), 16),
              compiler.reference.perpendicular((1,), 16)),
             (16, paired, tuple(1 << j for j in range(8)))]
    result = []
    for n, E, F in cases:
        normal = compiler.compile_interface(E, F, n)
        E, F = tuple(normal['source_subspace']), tuple(normal['target_subspace'])
        word = compiler.inverse_word(compiler.literal_word(E, n)) + compiler.literal_word(F, n)
        generators = compiler.assert_complete_tableau(normal, word)
        result.append(dict(n=n, source_subspace=list(E), target_subspace=list(F),
                           source_actual_spec=compiler.reference.frame_spec(E, n),
                           target_actual_spec=compiler.reference.frame_spec(F, n),
                           actual_relative_word=word, normal_form=normal,
                           generator_images_checked=generators,
                           exact_global_coefficient_checked=True))
    files = [Path(__file__), Path(compiler.__file__), Path(compiler.reference.__file__)]
    return dict(schema='compact-actual-subspace-interface-v1',
                generated_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256={file.name: sha256(file.read_bytes()).hexdigest() for file in files},
                cases=result,
                scope='Literal finite normal-form data. Reviewer must independently bind canonical operators, support, phase and global unit. No native payload or exponent certificate.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    fixture = make_fixture()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        stream.write(json.dumps(fixture, indent=2) + '\n')
    print(json.dumps(dict(cases=len(fixture['cases']), output=str(args.output),
                         sha256=sha256(args.output.read_bytes()).hexdigest())), flush=True)


if __name__ == '__main__':
    main()
