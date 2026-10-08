#!/usr/bin/env python3
"""Certify conjugate old/minimum profiles, then their exact four-state costs."""
import argparse
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    config = json.loads(args.input.read_text())
    minimum_input = config.pop('minimum_binary')
    parent_input = args.work / 'typed-parent.bin'
    parent_input.write_bytes(b'RADCOF01' + Path(config['parent_binary']).read_bytes())
    for label, source in [('parent', parent_input), ('minimum', Path(minimum_input))]:
        profile = args.work / f'{label}-profile.json'
        audit = args.work / f'{label}-audit.json'
        with (args.work / f'{label}-native.log').open('wb') as log:
            subprocess.run([str(args.binary), str(source), config['basis'], str(profile),
                            str(audit)], stdout=log, stderr=subprocess.STDOUT, check=True)
        config[f'{label}_profile'] = str(profile)
    exact_input = args.work / 'compiled-four-cost-input.json'
    exact_input.write_text(json.dumps(config, indent=2) + '\n')
    subprocess.run(['python3', '-u', str(Path(__file__).with_name('fixed_coframe_cost_table.py')),
                    '--input', str(exact_input), '--binary', str(args.binary),
                    '--work', str(args.work / 'four-cost'), '--output', str(args.output)],
                   check=True)


if __name__ == '__main__':
    main()
