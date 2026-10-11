#!/usr/bin/env python3
"""Profile completed actual signed-word closures without proxy envelopes."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--basis', required=True)
    parser.add_argument('--alternate-basis', required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    cohort = json.loads(args.input.read_text())
    assert cohort['status'].upper() == 'COMPLETE'
    args.work.mkdir(parents=True)
    rows = [row for row in cohort['rows'] if 'word_path' in row]
    rows.sort(key=lambda row: (row['configuration']['mode'] != 'core-single',
        row['configuration']['value'] != 18, row['case_id']))
    configs = []
    seen = set()
    for row in rows:
        word = Path(row['word_path'])
        transition = word.with_name('signed-transitions.bin')
        assert transition.exists()
        digest = sha256(transition.read_bytes()).hexdigest()
        bases = [args.basis]
        if row['configuration']['mode'] == 'core-single':
            bases.append(args.alternate_basis)
        for basis in bases:
            key = (digest, basis)
            if key in seen:
                continue
            seen.add(key)
            configs.append(dict(case_id=row['case_id'] + '-' + basis.replace(':', '-'),
                transitions=str(transition), basis=basis,
                actual_signed_word_path=str(word),
                actual_signed_word_sha256=row['word_sha256']))
    assert configs
    path = args.work / 'actual-configurations.json'
    path.write_text(json.dumps(configs, indent=2) + '\n')
    (args.work / 'input-manifest.json').write_text(json.dumps(dict(
        cohort_sha256=sha256(args.input.read_bytes()).hexdigest(),
        configurations=len(configs), source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()
    ), indent=2) + '\n')
    command = [sys.executable, '-u', str(Path(__file__).with_name('run_joint_word_parameters.py')),
        '--input', str(path), '--binary', str(args.binary),
        '--work', str(args.work / 'profiles'), '--output', str(args.output)]
    subprocess.run(command, check=True)


if __name__ == '__main__':
    main()
