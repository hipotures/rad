#!/usr/bin/env python3
"""Adversarial controls for mismatched word, roles and profile provenance."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from bind_joint_word_certificate import local, read


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--axes', type=Path, required=True)
    p.add_argument('--word', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    assert not args.output.exists()
    row = read(args.axes)['axes']['23']
    graph = read(args.word)
    cases = []
    for name in ['changed-role-denominator','unrelated-transition-hash','changed-profile-block','wrong-dirty-orientation']:
        r, g = deepcopy(row), deepcopy(graph)
        if name == 'changed-role-denominator':
            r['profile']['R'] += 1
        elif name == 'unrelated-transition-hash':
            g['transition_sha256'] = '0'*64
        elif name == 'changed-profile-block':
            r['profile']['blocks'][1] += 1
        else:
            g['orientations'] = ['forward']
        try:
            local(r,g)
        except AssertionError:
            cases.append(dict(case=name,status='REJECTED AS REQUIRED'))
        else:
            raise AssertionError('Corrupt candidate was accepted: '+name)
    result = dict(status='PASS INDEPENDENT ADVERSARIAL BINDING CONTROLS',
                  created_utc=datetime.now(timezone.utc).isoformat(), cases=cases,
                  verifier_source_sha256=sha256(Path(__file__).with_name('bind_joint_word_certificate.py').read_bytes()).hexdigest(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
