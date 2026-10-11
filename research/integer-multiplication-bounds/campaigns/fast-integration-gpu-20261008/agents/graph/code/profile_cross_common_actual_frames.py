#!/usr/bin/env python3
"""Profile actual future-frame families on new shared-pair physical words.

The source/scalar and paid physical words are retained from the cross-common
producer constructor. Every selected frame is derived from that NEW word's
literal transition graph and terminal kernels; no old physical profile is
reused. Full role-word replay and exact native matrix profiles are distinct
from later source-only reproduction, DATA, stock and assembly acceptance.
"""
import argparse
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

from check_compiled_witness import contained
from joint_word_check_v4 import check
from joint_scalar_future_frames import write_word

GEOMETRY = Path(__file__).resolve().parents[2] / 'geometry' / 'code'
sys.path.insert(0, str(GEOMETRY))
from enlarge_actual_signed_word import enlarge_actual


def mix(word, selected_variants, choices):
    lower = [(r, f, tuple(s)) for r, f, s in word['frames']]
    selected = [selected_variants[choices[forced.bit_length()-1]][i]
                if forced.bit_count() == 1 else lower[i]
                for i, (_, forced, _) in enumerate(lower)]
    for before, after in zip(lower, selected):
        assert contained(before, after)
    for slot, before, after in word['events']:
        if before >= 0:
            assert contained(selected[before], selected[after])
            if lower[before][1].bit_count() == 1:
                assert lower[before][1] == lower[after][1]
    frames, lookup, aliases = [], {}, []
    for frame in selected:
        if frame not in lookup:
            lookup[frame] = len(frames)
            frames.append(frame)
        aliases.append(lookup[frame])
    fresh = dict(word)
    old_aliases = word.get('physical_region_address_aliases')
    fresh.update(frames=frames, physical_region_address_aliases=
                 [aliases[i] for i in old_aliases] if old_aliases else aliases,
                 common_context_actual_future_choices=choices)
    fresh['ops'] = [(a, b, aliases[g]) for a, b, g in word['ops']]
    fresh['events'] = [(s, -1 if a < 0 else aliases[a], aliases[b]) for s, a, b in word['events']]
    fresh['outputs'] = [(s, aliases[g], c, t) for s, g, c, t in word['outputs']]
    return fresh


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs', nargs='+', type=Path, required=True)
    p.add_argument('--h', type=int, required=True)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    (args.work / 'process.json').write_text(json.dumps(dict(pid=os.getpid(), command=sys.argv,
        started_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')
    h = args.h
    assert h in (23, 25)
    basis = 'beta:1:15' if h == 23 else 'beta:7:207'
    choices = ['balanced12'] * h
    for common in ([20, 21, 22] if h == 23 else [0, 1, 2, 22, 24]):
        choices[common] = 'unbalanced12'
    if h == 25:
        for common in [11, 13, 15, 17]:
            choices[common] = 'all18'
    parents = []
    for source in args.inputs:
        for row in json.loads(source.read_text())['rows']:
            if row.get('independent', {}).get('h') == h:
                parents.append((source, row))
    rows = []
    kept_parent_objects = []
    env = dict(os.environ)
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[key] = '1'
    for source, parent in parents:
        raw = gzip.decompress(Path(parent['independent']['word_path']).read_bytes())
        assert sha256(raw).hexdigest() == parent['word_sha256']
        word = json.loads(raw)
        kept_parent_objects.append(word)
        variants = {}
        receipts = {}
        for name, mode, threshold in [('balanced12', 'balanced', 12), ('unbalanced12', 'unbalanced', 12), ('all18', 'all', 18)]:
            fresh, chosen, receipt = enlarge_actual(word, [], threshold, mode, 'one-core')
            variants[name] = chosen
            receipts[name] = receipt
        configs = [('balanced12', ['balanced12'] * h), ('all18', ['all18'] * h), ('multifamily', choices)]
        for name, family_choices in configs:
            case = parent['case_id'] + '-actual-' + name
            target = args.work / 'raw' / case
            target.mkdir(parents=True)
            start = time.monotonic()
            fresh = mix(word, variants, family_choices)
            word_path = target / 'word.json.gz'
            word_sha = write_word(word_path, fresh)
            transition = target / 'signed-transitions.bin'
            independent = check(word_path, transition)
            profile, audit = target / 'profile.json', target / 'transitions.json'
            command = [str(args.binary), str(transition), basis, str(profile), str(audit)]
            with (target / 'native.log').open('wb') as log:
                child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
                (target / 'process.json').write_text(json.dumps(dict(pid=child.pid, command=command), indent=2) + '\n')
                assert child.wait() == 0
            native = json.loads(profile.read_text())
            a = 1284995399 / 25000000000000
            phi = sum(t*n*math.expm1(a*math.log(575/t)) for t, n in enumerate(native['blocks']) if t and n)
            result = dict(status='EXACT CANDIDATE shared-pair graph with actual-future signed frames',
                case_id=case, source_receipt=str(source), parent_word_sha256=parent['word_sha256'],
                parent_scalar=parent.get('scalar'), parent_configuration=parent['configuration'],
                configuration=dict(family_choices=family_choices, basis=basis), frame_receipts=receipts,
                roles=fresh['R'], scalar_graph_and_literal_XORs_unchanged_from_new_parent=True,
                word_path=str(word_path), word_sha256=word_sha, independent=independent,
                profile=native, profile_path=str(profile), profile_sha256=sha256(profile.read_bytes()).hexdigest(),
                transition_audit=str(audit), transition_audit_sha256=sha256(audit.read_bytes()).hexdigest(),
                screen_a=a, screen_Phi=phi, seconds=time.monotonic()-start,
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                completed_utc=datetime.now(timezone.utc).isoformat(),
                limitations='New shared-pair scalar/physical parent is independently replayed; this is not an accepted exponent. Fresh source-only construction, DATA/source-family stock compatibility, complete moments and 47+7 assembly remain separate, with conditional all-size address/tape scope.')
            (target / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
            rows.append(result)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(dict(status='running', command=sys.argv, rows=rows), indent=2) + '\n')
            print(json.dumps(dict(case_id=case, R=fresh['R'], Phi=phi)), flush=True)
    args.output.write_text(json.dumps(dict(status='complete', command=sys.argv, rows=rows,
        completed_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')


if __name__ == '__main__':
    main()
