#!/usr/bin/env python3
"""Evaluate coherent pairs of executed-word profiles at certified DATA bases.

Arithmetic discovery only: source/physical/stock acceptance remains separate.
Credits: Avi Eisenberg, eumemic, Rohan Arun and inherited public contributors.
Authored with OpenAI Codex assistance.
"""
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--receipts', nargs=2, type=Path, required=True)
    p.add_argument('--accepted-axes', type=Path, required=True)
    p.add_argument('--accepted-kappa', required=True)
    p.add_argument('--phase', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--assembly', type=Path, required=True)
    p.add_argument('--geometry', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists()
    a.work.mkdir(parents=True, exist_ok=False)
    accepted = json.loads(a.accepted_axes.read_text())
    populations, omitted = [], []
    for h, receipt, control in zip([23, 25], a.receipts, accepted):
        population = [('accepted', control)]
        for original in json.loads(receipt.read_text())['rows']:
            row = copy.deepcopy(original)
            if row['profile']['basis'] != control['profile']['basis']:
                omitted.append(row['config']['case_id'])
                continue  # A different basis requires its own complete DATA.
            source = json.loads(Path(row['config']['source_receipt']).read_text())
            sources = source.get('rows', [source])
            candidates = [s for s in sources
                          if s.get('word_sha256') == row['config']['word_sha256']]
            assert len(candidates) == 1
            fresh = candidates[0]['independent']
            assert fresh['word_sha256'] == row['config']['word_sha256']
            assert fresh['transition_sha256'] == row['input_binary_sha256']
            assert digest(row['config']['transitions']) == row['input_binary_sha256']
            assert digest(row['profile_path']) == row['profile_sha256']
            assert digest(row['transition_audit']) == row['transition_audit_sha256']
            assert fresh['R'] == row['profile']['R'] and fresh['h'] == h
            row['coordinate_order'] = fresh['source_permutation']
            assert sorted(row['coordinate_order']) == list(range(h))
            row['transition_binary_sha256'] = row['input_binary_sha256']
            population.append((row['config']['case_id'], row))
        populations.append(population)
    jobs = [pair for pair in itertools.product(*populations)
            if any(x[0] != 'accepted' for x in pair)]
    results = []
    driver = Path(__file__).with_name('compose_joint_word_profiles.py')
    for index, pair in enumerate(jobs):
        work = a.work / f'pair-{index:03d}'
        work.mkdir()
        axes = work / 'axes.json'
        axes.write_text(json.dumps([x[1] for x in pair], indent=2) + '\n')
        certificate = work / 'certificate.json'
        command = [sys.executable, str(driver), '--axes', str(axes),
                   '--phase', str(a.phase), '--baseline', str(a.baseline),
                   '--assembly', str(a.assembly), '--geometry', str(a.geometry),
                   '--output', str(certificate)]
        process = subprocess.run(command, text=True, capture_output=True)
        result = dict(index=index, cases=[x[0] for x in pair],
                      returncode=process.returncode, axes=str(axes),
                      certificate=str(certificate), summary=process.stdout.strip(),
                      error=process.stderr[-3000:])
        if process.returncode == 0:
            exact = json.loads(certificate.read_text())
            result.update(kappa=exact['kappa'], bit_saving=exact['bit_moment']['saving'],
                          W=exact['bit']['W'], rank_mass=exact['bit']['total_rank'],
                          exceeds_accepted=Fraction(exact['kappa']) > Fraction(a.accepted_kappa),
                          classification='EXACT CANDIDATE; independent stock and acceptance pending')
        results.append(result)
        evidence = dict(status='RUNNING' if len(results) < len(jobs) else 'COMPLETE',
                        utc=datetime.now(timezone.utc).isoformat(),
                        accepted_kappa=a.accepted_kappa, completed=len(results),
                        total=len(jobs), omitted_unproved_data_bases=omitted, rows=results,
                        input_sha256={str(x): digest(x) for x in
                                      [*a.receipts, a.accepted_axes, a.geometry, a.assembly]},
                        source_sha256=digest(__file__))
        a.output.write_text(json.dumps(evidence, indent=2) + '\n')
        print(json.dumps({k: result[k] for k in ['index', 'cases', 'returncode',
                                                'summary']}), flush=True)


if __name__ == '__main__':
    main()
