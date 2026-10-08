#!/usr/bin/env python3
"""Close one-axis exact moment comparisons for already completed words.

This evaluates retained finite profiles; it launches no structural search.
Stock and full physical acceptance remain separate. Source credits and
conditional interfaces are inherited from the joint interval construction.
"""
import argparse
import copy
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profiles', type=Path, nargs='+', required=True)
    p.add_argument('--accepted-axes', type=Path, required=True)
    p.add_argument('--accepted-kappa', required=True)
    p.add_argument('--phase', type=Path, required=True)
    p.add_argument('--snapshot', type=Path, required=True)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.work.exists() and not a.output.exists()
    a.work.mkdir(parents=True)
    accepted = json.loads(a.accepted_axes.read_text())
    rows, seen = [], set()
    for receipt in a.profiles:
        for r in json.loads(receipt.read_text())['rows']:
            if r['returncode'] != 0:
                continue
            profile = r['profile']
            h = profile['h']
            index = (23,25).index(h)
            if profile['basis'] != accepted[index]['profile']['basis']:
                continue
            key = (r['input_binary_sha256'], r['basis'])
            if key in seen:
                continue
            seen.add(key)
            assert digest(r['binary']) == r['input_binary_sha256']
            assert digest(r['profile_path']) == r['profile_sha256']
            assert digest(r['transition_audit']) == r['transition_audit_sha256']
            work = a.work / ('case-%03d' % len(rows))
            work.mkdir()
            pair = copy.deepcopy(accepted)
            pair[index] = dict(config=dict(h=h,basis=r['basis'],transitions=r['binary']),
                               profile=profile,profile_path=r['profile_path'],
                               profile_sha256=r['profile_sha256'],
                               transition_audit=r['transition_audit'],
                               transition_audit_sha256=r['transition_audit_sha256'],
                               input_binary_sha256=r['input_binary_sha256'],
                               coordinate_order=r['coordinate_order'])
            axes, certificate = work/'axes.json', work/'certificate.json'
            axes.write_text(json.dumps(pair,indent=2)+'\n')
            command = [sys.executable,str(Path(__file__).with_name('compose_joint_word_profiles.py')),
                       '--axes',str(axes),'--phase',str(a.phase),
                       '--baseline',str(a.snapshot/'research/pair-assembly/frame/frame-certificate.json'),
                       '--assembly',str(a.snapshot/'references/frame-compiler/pr48/research/copied-fixed/balanced_assembly.py'),
                       '--geometry',str(a.data),'--output',str(certificate)]
            child = subprocess.run(command,capture_output=True,text=True)
            result = dict(case_id=r['case_id'],h=h,R=profile['R'],word_sha256=r['word_sha256'],
                          input_binary_sha256=r['input_binary_sha256'],returncode=child.returncode,
                          certificate=str(certificate),summary=child.stdout.strip(),error=child.stderr[-2000:])
            if child.returncode == 0:
                cert = json.loads(certificate.read_text())
                result.update(kappa=cert['kappa'],W=cert['bit']['W'],
                              rank_mass=cert['bit']['total_rank'],
                              exceeds_accepted=Fraction(cert['kappa'])>Fraction(a.accepted_kappa))
            rows.append(result)
    a.output.write_text(json.dumps(dict(status='COMPLETE',rows=rows,
        accepted_kappa=a.accepted_kappa,source_sha256=digest(__file__),
        inputs={str(p):digest(p) for p in [*a.profiles,a.accepted_axes,a.data]},
        scope='One-axis complete exact recurrence comparisons of previously executed networks. '
              'This is a necessary-condition comparison; no candidate stock or final physical acceptance is inferred.'),indent=2)+'\n')
    print(json.dumps(dict(completed=len(rows),exceeds_accepted=sum(r.get('exceeds_accepted',False) for r in rows))))


if __name__ == '__main__':
    main()
