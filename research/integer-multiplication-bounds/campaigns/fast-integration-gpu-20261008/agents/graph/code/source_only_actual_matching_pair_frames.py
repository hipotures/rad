#!/usr/bin/env python3
"""Fresh selected-matching word followed by actual-word pair enlargement.

Reconstruct pinned scalar DAG, all selected carrier capacities and physical
word first. The frozen enlargement constructor then derives its upper
spaces from THAT word, preserves every current signed lower space and
replays every literal transition. No original-envelope schedule or saved
discovery word is substituted. Public sources: Avi Eisenberg PR62, eumemic
PR57; predecessor attributions and AI assistance are inherited.
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
from joint_scalar_future_frames import write_word
from joint_word_check_v4 import check

GEOMETRY = Path(__file__).resolve().parents[2] / 'geometry' / 'code'
sys.path.insert(0, str(GEOMETRY))
from enlarge_actual_signed_word import enlarge_actual


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--choices-file', type=Path, required=True)
    p.add_argument('--selected-matching', type=Path, required=True)
    p.add_argument('--pair-config', type=Path, required=True)
    p.add_argument('--h', type=int, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--profile-transitions', type=Path)
    args = p.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    (args.work / 'process.json').write_text(json.dumps(dict(pid=os.getpid(), command=sys.argv,
        started_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')
    start = time.monotonic()
    config = next(d for d in json.loads(args.pair_config.read_text()) if d['h'] == args.h)
    base_output = args.work / 'fresh-weighted-source.json'
    old_argv = sys.argv
    try:
        sys.argv = [str(Path(weighted.__file__)), '--source', str(args.source), '--choices-file', str(args.choices_file),
            '--selected-matching', str(args.selected_matching), '--h', str(args.h), '--work', str(args.work / 'fresh-weighted'),
            '--output', str(base_output), '--expected-word-sha256', config['parent_word_sha256']]
        weighted.main()
    finally:
        sys.argv = old_argv
    parent = json.loads(base_output.read_text())
    assert parent['source_only'] and parent['h'] == args.h
    raw = gzip.decompress(Path(parent['word_path']).read_bytes())
    assert sha256(raw).hexdigest() == config['parent_word_sha256']
    word = json.loads(raw)
    fresh, selected, frame_summary = enlarge_actual(word, config['pairs'], config['threshold'],
                                                    config['component_mode'], 'pair')
    assert fresh['R'] == word['R'] and fresh['ops'] != []
    assert len(fresh['ops']) == len(word['ops'])
    assert [(a, b) for a, b, _ in fresh['ops']] == [(a, b) for a, b, _ in word['ops']]
    word_path = args.work / 'word.json.gz'
    digest = write_word(word_path, fresh)
    assert digest == config['word_sha256']
    independent = check(word_path, args.work / 'signed-transitions.bin')
    assert independent['R'] == parent['R']
    assert independent['elementary_middle_xors'] == parent['independent']['elementary_middle_xors']
    assert independent['transition_sha256'] == config['transition_sha256']
    if args.profile_transitions:
        assert (args.work / 'signed-transitions.bin').read_bytes() == args.profile_transitions.read_bytes()
    # Counts are rebound to the newly executed frame schedule. Its rank
    # histogram is not copied from the smaller weighted parent.
    compiled = dict(roles=independent['R'], h=args.h,
        elementary_xors=independent['elementary_middle_xors'], rank_mass=independent['rank_mass'],
        histogram=independent['rank_histogram'], stats=parent['compiled']['stats'],
        complete_dirty_basis_both_orientations=True, all_physical_frame_inclusions=True)
    result = dict(status='source-only changed matching plus actual pair-frame enlargement full finite PASS',
        source_only=True, h=args.h, R=independent['R'], source_head=parent['source_head'],
        source_parent_sha256=parent['source_parent_sha256'], source_parent_configuration=parent['source_parent_configuration'],
        source_permutation=parent['source_permutation'], scalar=parent['scalar'], compiled=compiled,
        compiled_parent=parent['compiled_parent'], configuration=dict(parent=parent['configuration'], pair_frames=config),
        fresh_weighted_source_receipt_path=str(base_output), fresh_weighted_source_receipt_sha256=sha256(base_output.read_bytes()).hexdigest(),
        actual_parent_word_sha256=config['parent_word_sha256'],
        selected_carriers=parent['selected_carriers'], selected_matching_path=parent['selected_matching_path'],
        selected_matching_sha256=parent['selected_matching_sha256'], every_selected_use_reconstructed=True,
        distinct_recipient_capacity=True, donor_row_capacity_exactly_independent=True, strict_carrier_chronology=True,
        source_injection_frames_unchanged=True, copied_center_spaces_unchanged=args.h,
        original_scalar_dag_outputs_preserved=True, physical_matching_and_literal_xors_changed=True,
        literal_xors_unchanged_from_selected_weighted_parent=True, word_regenerated_from_source_and_selected_carriers=True,
        actual_frame_assignment_reconstructed=True, current_signed_lower_spaces_preserved=True,
        frame_summary=frame_summary, word_path=str(word_path), word_sha256=digest,
        independent=independent, profile_transition_sha256=independent['transition_sha256'],
        profile_bytes_independently_compared=bool(args.profile_transitions),
        original_region_metadata_path=parent['original_region_metadata_path'],
        original_region_metadata_sha256=parent['original_region_metadata_sha256'],
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(), seconds=time.monotonic()-start,
        completed_utc=datetime.now(timezone.utc).isoformat(),
        limitations='Fresh scalar/use/capacity/chronology and finite mixed-frame word proof. Native ranks, independent Fraction controls, DATA/stock, exact recurrence/assembly and conditional all-size gauge/tape realization remain separate.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], h=args.h, R=result['R'], word_sha256=digest,
                         seconds=result['seconds'])), flush=True)


if __name__ == '__main__':
    main()
