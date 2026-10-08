#!/usr/bin/env python3
"""Fresh weighted joint word with selected smaller source-span coframes.

Scalar source: Avi Eisenberg PR62. Joint invertible binary synthesis and
paid reclamation: eumemic PR57. Complete selected carrier lists regenerate
the source-bound parent; pure constructors select nested smaller spaces.
The actual old spaces are UPPER bounds, never mandatory lower floors.
"""
import argparse
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import time

import source_only_matrix_weighted_joint as weighted
import co_signed_source_frames as co
from joint_scalar_future_frames import write_word
from joint_word_check_v5 import check

GEOMETRY = Path(__file__).resolve().parents[2] / 'geometry' / 'code'
sys.path.insert(0, str(GEOMETRY))
from fixed_word_source_coframes import select_fixed_word_coframes
from partial_fixed_word_coframes import removed_direction_balances, select_partial


def same_space(a, b):
    return co.contained(co.normalize(a), co.normalize(b)) and co.contained(co.normalize(b), co.normalize(a))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--choices-file', type=Path, required=True)
    parser.add_argument('--selected-matching', type=Path, required=True)
    parser.add_argument('--coframe-config', type=Path, required=True)
    parser.add_argument('--h', type=int, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile-transitions', type=Path)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    (args.work / 'process.json').write_text(json.dumps(dict(pid=os.getpid(), command=sys.argv,
        started_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')
    started = time.monotonic()
    config = next(c for c in json.loads(args.coframe_config.read_text()) if c['h'] == args.h)
    parent_receipt = args.work / 'fresh-weighted-source.json'
    saved = sys.argv
    try:
        sys.argv = [str(Path(weighted.__file__)), '--source', str(args.source),
            '--choices-file', str(args.choices_file), '--selected-matching', str(args.selected_matching),
            '--h', str(args.h), '--work', str(args.work / 'fresh-weighted'), '--output', str(parent_receipt),
            '--expected-word-sha256', config['parent_word_sha256']]
        weighted.main()
    finally:
        sys.argv = saved
    parent = json.loads(parent_receipt.read_text())
    assert parent['source_only'] and parent['h'] == args.h
    raw = gzip.decompress(Path(parent['word_path']).read_bytes())
    assert sha256(raw).hexdigest() == config['parent_word_sha256']
    word = json.loads(raw)
    _, minimum, minimum_receipt = select_fixed_word_coframes(word, config['minimum_policy'])
    old = [co.normalize(frame) for frame in word['frames']]
    balances = removed_direction_balances(old, minimum)
    fresh, selected, selection_receipt = select_partial(word, minimum, balances,
        config['protect_ordinary'], config['restore_rank_below'], config['restore_removed_direction'])
    assert fresh['R'] == word['R']
    assert fresh['sources'] == word['sources'] and fresh['scatter'] == word['scatter']
    assert [(a, b) for a, b, _ in fresh['ops']] == [(a, b) for a, b, _ in word['ops']]
    assert all(co.contained(minimum[i], selected[i]) and co.contained(selected[i], old[i]) for i in range(len(old)))
    old_initial = {s: word['frames'][g] for s, before, g in word['events'] if before < 0}
    new_initial = {s: fresh['frames'][g] for s, before, g in fresh['events'] if before < 0}
    source_slots = list(word['sources'].values())
    assert all(same_space(old_initial[s], new_initial[s]) for s in source_slots)
    old_centers = {(s, c): word['frames'][g] for s, g, c, target in word['outputs'] if len(target) == 1}
    new_centers = {(s, c): fresh['frames'][g] for s, g, c, target in fresh['outputs'] if len(target) == 1}
    assert old_centers.keys() == new_centers.keys() and len(old_centers) == args.h
    assert all(same_space(old_centers[key], new_centers[key]) for key in old_centers)
    path = args.work / 'word.json.gz'
    digest = write_word(path, fresh)
    assert digest == config['word_sha256']
    independent = check(path, args.work / 'mixed-transitions.bin')
    assert independent['R'] == parent['R']
    assert independent['elementary_middle_xors'] == parent['independent']['elementary_middle_xors']
    assert independent['transition_sha256'] == config['transition_sha256']
    if args.profile_transitions:
        assert (args.work / 'mixed-transitions.bin').read_bytes() == args.profile_transitions.read_bytes()
    compiled = dict(roles=independent['R'], h=args.h,
        elementary_xors=independent['elementary_middle_xors'], rank_mass=independent['rank_mass'],
        histogram=independent['rank_histogram'], stats=parent['compiled']['stats'],
        complete_dirty_basis_both_orientations=True, all_physical_frame_inclusions=True)
    result = dict(status='source-only changed matching and selected source-span coframes full finite PASS',
        source_only=True, h=args.h, R=independent['R'], source_head=parent['source_head'],
        source_parent_sha256=parent['source_parent_sha256'], source_parent_configuration=parent['source_parent_configuration'],
        source_permutation=parent['source_permutation'], scalar=parent['scalar'], compiled=compiled,
        compiled_parent=parent['compiled_parent'], configuration=dict(parent=parent['configuration'], partial_coframes=config),
        fresh_weighted_source_receipt_path=str(parent_receipt), fresh_weighted_source_receipt_sha256=sha256(parent_receipt.read_bytes()).hexdigest(),
        actual_parent_word_sha256=config['parent_word_sha256'], selected_carriers=parent['selected_carriers'],
        selected_matching_path=parent['selected_matching_path'], selected_matching_sha256=parent['selected_matching_sha256'],
        every_selected_use_reconstructed=True, distinct_recipient_capacity=True,
        donor_row_capacity_exactly_independent=True, strict_carrier_chronology=True,
        source_injection_frames_unchanged=True, source_injection_spaces_mutually_checked=len(source_slots),
        copied_center_spaces_unchanged=args.h, copied_center_spaces_mutually_checked=True,
        original_scalar_dag_outputs_preserved=True, physical_matching_and_literal_xors_changed=True,
        literal_xors_unchanged_from_selected_weighted_parent=True,
        word_regenerated_from_source_and_selected_carriers=True, actual_frame_assignment_reconstructed=True,
        selected_source_coframes=True, original_envelope_floor_asserted=False,
        actual_old_frames_are_upper_bounds=True,
        minimum_receipt=minimum_receipt, frame_summary=selection_receipt,
        word_path=str(path), word_sha256=digest, independent=independent,
        profile_transition_sha256=independent['transition_sha256'],
        profile_bytes_independently_compared=bool(args.profile_transitions),
        original_region_metadata_path=parent['original_region_metadata_path'],
        original_region_metadata_sha256=parent['original_region_metadata_sha256'],
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(), seconds=time.monotonic()-started,
        completed_utc=datetime.now(timezone.utc).isoformat(),
        limitations='Fresh scalar/use/capacity/chronology, smaller actual rational spaces and complete finite mixed F2 role word. Native CRT/NE, independent Fraction/DATA/stock, moments/47+7 assembly and conditional all-size address/gauge/tape realization remain separate.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], h=args.h, R=result['R'], word_sha256=digest,
        smaller_frames=selection_receipt['strictly_smaller_frames'], seconds=result['seconds'])), flush=True)


if __name__ == '__main__':
    main()
