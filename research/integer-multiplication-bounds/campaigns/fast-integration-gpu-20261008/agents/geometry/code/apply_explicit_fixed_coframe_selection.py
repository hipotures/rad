#!/usr/bin/env python3
"""Reconstruct a selected legal old/minimum allocation as an actual mixed word."""
import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
import time

from fixed_word_source_coframes import select_fixed_word_coframes, normalize, contained, FORMAT
from partial_fixed_word_coframes import check


def apply_selection(word, minimum_frame_ids):
    _, minimum, receipt = select_fixed_word_coframes(word)
    old = [normalize(frame) for frame in word['frames']]
    minimum_frame_ids = set(minimum_frame_ids)
    assert all(0 <= i < len(old) and minimum[i][0] < old[i][0]
               for i in minimum_frame_ids)
    chosen = [minimum[i] if i in minimum_frame_ids else frame for i, frame in enumerate(old)]
    for i, frame in enumerate(chosen):
        assert contained(minimum[i], frame) and contained(frame, old[i])
    for slot, a, b in word['events']:
        if a >= 0 and a != b:
            assert contained(chosen[a], chosen[b]) and chosen[a][0] < chosen[b][0]
    aliases, frames, lookup = [], [], {}
    for frame in chosen:
        if frame not in lookup:
            lookup[frame] = len(frames)
            frames.append(frame)
        aliases.append(lookup[frame])
    fresh = dict(word, frames=frames, frame_format=FORMAT)
    previous = word.get('physical_region_address_aliases')
    fresh['physical_region_address_aliases'] = [aliases[i] for i in previous] if previous else aliases
    fresh['ops'] = [(a, b, aliases[g]) for a, b, g in word['ops']]
    fresh['events'] = [(slot, -1 if a < 0 else aliases[a], aliases[b])
                       for slot, a, b in word['events']]
    fresh['outputs'] = [(slot, aliases[g], c, target) for slot, g, c, target in word['outputs']]
    fresh['explicit_fixed_word_coframes'] = dict(minimum_frame_ids=sorted(minimum_frame_ids),
        frame_id_scope='zero-based frame IDs of the source-bound parent word')
    return fresh, chosen, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    started = time.monotonic()
    config = json.loads(args.input.read_text())
    parent = config['parent']
    raw = gzip.decompress(Path(parent['word_path']).read_bytes())
    assert sha256(raw).hexdigest() == parent['word_sha256']
    word = json.loads(raw)
    allocation = json.loads(Path(config['allocation']).read_text())
    assert allocation['parent_word_sha256'] == parent['word_sha256']
    offset = config['frame_id_offset']
    selected_ids = [i-offset for i in allocation['minimum_frame_ids']]
    fresh, chosen, minimum_receipt = apply_selection(word, selected_ids)
    table_raw = Path(config['cost_table']).read_bytes()
    table = json.loads(table_raw)
    assert sha256(table_raw).hexdigest() == allocation.get('table_sha256', allocation.get('input_cost_table_sha256'))
    variables = set(table['variables'])
    binary_ids = {i+2 for i in selected_ids}
    assert binary_ids <= variables
    state = {i: int(i not in binary_ids) for i in variables}
    predicted = Counter()
    pool = table['probe_frame_descriptors']; states = table['variable_states']; h = word['h']
    for frame, count in table['side_counts'].items():
        frame = int(frame)
        predicted[1] += (h-pool[states[frame][state.get(frame, 0)]][0])*count
    for row in table['rows']:
        key = f"{state.get(row['a'],0)}{state.get(row['b'],0)}"
        entry = row['states'][key]
        assert entry['legal']
        for width, count in entry['histogram'].items():
            predicted[int(width)] += count*row['count']
    raw = (json.dumps(fresh, separators=(',', ':'))+'\n').encode()
    path = args.work/'word.json.gz'
    with path.open('wb') as stream:
        with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0) as out:
            out.write(raw)
    binary = args.work/'mixed-transitions.bin'
    independent = check(path, binary)
    profile_path, audit_path = args.work/'profile.json', args.work/'transitions.json'
    with (args.work/'native.log').open('wb') as log:
        subprocess.run([str(args.binary), str(binary), config['basis'], str(profile_path),
                        str(audit_path)], stdout=log, stderr=subprocess.STDOUT, check=True)
    profile = json.loads(profile_path.read_text())
    assert profile['blocks'] == [predicted[t] for t in range(h+1)]
    assert profile['rank_sum'] == table['physical_rank_mass']
    a = config['screen_a']
    phi = sum(t*n*math.expm1(a*math.log(575/t)) for t, n in enumerate(profile['blocks']) if t and n)
    args.output.write_text(json.dumps(dict(status='EXACT CANDIDATE EXPLICIT OLD/MINIMUM COFRAME WORD',
        config=config, unchanged_R=word['R'], unchanged_every_XOR=True,
        minimum_selected_old_containment=True, selected_minimum_frames=len(selected_ids),
        minimum_receipt=minimum_receipt, independent=independent,
        exact_predicted_histogram_equals_independent_word_native=True,
        word_path=str(path), word_sha256=sha256(raw).hexdigest(),
        input_binary_sha256=sha256(binary.read_bytes()).hexdigest(),
        profile=profile, profile_path=str(profile_path),
        profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
        transition_audit=str(audit_path), transition_audit_sha256=sha256(audit_path.read_bytes()).hexdigest(),
        screen_Phi=phi, screen_a=a, assignment_sha256=sha256(json.dumps(chosen).encode()).hexdigest(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(), elapsed_seconds=time.monotonic()-started,
        scope='Actual literal mixed word, arbitrary binary dirty restoration in both orientations, '
              'source/center/sink/frame obligations and exact native physical histogram. '
              'Fresh public-source replay, independent rational matrix controls, stock/DATA '
              'interface and full assembly remain acceptance gates.'), indent=2)+'\n')
    print(json.dumps(dict(status='complete', h=h, Phi=phi, smaller_frames=len(selected_ids))), flush=True)


if __name__ == '__main__':
    main()
