#!/usr/bin/env python3
"""Mix one-core component families on one immutable actual signed word.

Every selected space contains the existing physical space. The region-to-frame
map is composed, and all literal events are checked again. This constructor
never replaces the changed matching with an original-envelope schedule.
"""
import argparse
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
import time

from enlarge_actual_signed_word import actual_upper_spaces, enlarge_actual, contained, check


def family_parameters(name):
    if name == 'none':
        return dict(core_mode='none', mode='all', threshold=0)
    for prefix in ('balanced', 'unbalanced', 'all'):
        if name.startswith(prefix) and name[len(prefix):].isdigit():
            return dict(core_mode='one-core', mode=prefix,
                        threshold=int(name[len(prefix):]))
    raise ValueError(f'Unknown component family: {name}')


def select_actual_future_families(word, choices):
    """Return the actual word, per-old-frame selected spaces, and exact checks."""
    h = word['h']
    assert len(choices) == h
    lower, upper, successors, upper_receipt = actual_upper_spaces(word, True)
    variants = {}
    variant_receipts = {}
    for name in sorted(set(choices)):
        params = family_parameters(name)
        _, variants[name], variant_receipts[name] = enlarge_actual(word, [], **params)
    selected = [variants[choices[forced.bit_length()-1]][i]
                if forced.bit_count() == 1 else before
                for i, before in enumerate(lower) for forced in [before[1]]]
    for before, after, maximum in zip(lower, selected, upper):
        assert contained(before, after) and contained(after, maximum)
        if before[1].bit_count() != 1:
            assert before == after
    for old, targets in enumerate(successors):
        for new in targets:
            assert contained(selected[old], selected[new]), 'Mixed literal event containment failed'
    source_roles = set(word['sources'].values())
    for slot, before, after in word['events']:
        if before < 0 and slot in source_roles:
            assert contained(selected[after], lower[after])
    for slot, frame, common, target in word['outputs']:
        if len(target) == 1:
            assert contained(selected[frame], lower[frame])
    frames, lookup, aliases = [], {}, []
    for frame in selected:
        if frame not in lookup:
            lookup[frame] = len(frames)
            frames.append(frame)
        aliases.append(lookup[frame])
    fresh = dict(word)
    old_aliases = word.get('physical_region_address_aliases')
    fresh.update(frames=frames,
                 physical_region_address_aliases=[aliases[i] for i in old_aliases]
                 if old_aliases is not None else aliases,
                 actual_signed_word_growth=dict(component_families_by_common=choices,
                                                mandatory_lower='actual parent signed spaces'))
    fresh['ops'] = [(a, b, aliases[frame]) for a, b, frame in word['ops']]
    fresh['events'] = [(slot, -1 if old < 0 else aliases[old], aliases[new])
                       for slot, old, new in word['events']]
    fresh['outputs'] = [(slot, aliases[frame], common, target)
                        for slot, frame, common, target in word['outputs']]
    receipt = dict(upper_receipt, choices=choices, families=variant_receipts,
                   unchanged_R=word['R'], unchanged_every_XOR=True,
                   non_single_core_spaces_unchanged=True,
                   current_signed_lower_containment=True,
                   every_mixed_literal_transition_containment=True,
                   source_and_copied_center_spaces_unchanged=True,
                   composed_original_region_address_aliases=True)
    return fresh, selected, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    rows = []
    started = time.monotonic()
    for config in json.loads(args.input.read_text()):
        parent = config['parent']
        raw = gzip.decompress(Path(parent['word_path']).read_bytes())
        assert sha256(raw).hexdigest() == parent['word_sha256']
        word = json.loads(raw)
        fresh, selected, summary = select_actual_future_families(word, config['choices'])
        work = args.work / config['case_id']
        work.mkdir()
        raw = (json.dumps(fresh, separators=(',', ':'))+'\n').encode()
        word_path = work / 'word.json.gz'
        with word_path.open('wb') as stream:
            with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0) as output:
                output.write(raw)
        binary = work / 'signed-transitions.bin'
        independent = check(word_path, binary)
        profile_path, audit = work / 'profile.json', work / 'transitions.json'
        with (work / 'native.log').open('wb') as log:
            subprocess.run([str(args.binary), str(binary), config['basis'],
                            str(profile_path), str(audit)], check=True,
                           stdout=log, stderr=subprocess.STDOUT)
        profile = json.loads(profile_path.read_text())
        a = config['screen_a']
        phi = sum(t*n*math.expm1(a*math.log(575/t))
                  for t, n in enumerate(profile['blocks']) if t and n)
        if 'predicted_actual_histogram' in config:
            assert profile['blocks'] == config['predicted_actual_histogram'], \
                'Mixed actual word does not reproduce its separately reconstructed histogram'
        row = dict(status='EXACT CANDIDATE MIXED ACTUAL SIGNED FRAME WORD',
                   config=config, summary=summary, independent=independent,
                   word_path=str(word_path), word_sha256=sha256(raw).hexdigest(),
                   input_binary_sha256=sha256(binary.read_bytes()).hexdigest(),
                   profile=profile, profile_path=str(profile_path),
                   profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
                   transition_audit=str(audit),
                   transition_audit_sha256=sha256(audit.read_bytes()).hexdigest(),
                   screen_Phi=phi, screen_a=a)
        rows.append(row)
        (args.work / 'completed-rows.json').write_text(json.dumps(rows, indent=2)+'\n')
        print(json.dumps(dict(case=config['case_id'], status=row['status'], Phi=phi,
                              elapsed_seconds=time.monotonic()-started)), flush=True)
    module = Path(__file__).with_name('enlarge_actual_signed_word.py')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(status='COMPLETE MIXED ACTUAL FRAME COHORT',
        rows=rows, source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        lower_upper_constructor_sha256=sha256(module.read_bytes()).hexdigest(),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        completed_utc=datetime.now(timezone.utc).isoformat(),
        scope='One actual source-bound changed matching with complete physical/source/dirty '
              'replay and full actual native CRT profile. Fresh scalar-source reconstruction, '
              'independent Fraction/DATA/stock/recurrence assembly and all-size conditional '
              'premises remain acceptance gates.'), indent=2)+'\n')


if __name__ == '__main__':
    main()
