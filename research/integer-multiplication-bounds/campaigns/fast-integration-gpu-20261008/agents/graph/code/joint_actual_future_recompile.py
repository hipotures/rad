#!/usr/bin/env python3
"""Joint synthesis in future spaces constrained by a verified actual word.

Pinned interval graph: Avi Eisenberg PR62. Invertible binary synthesis,
carrier capacities and paid reclamation: eumemic PR57. Source-only changed
matching receipts provide an immutable parent. Its actual physical edges
and ordinary output kernels define future signed upper spaces. Identical
selected spaces may merge previously different scalar envelopes. All
selected source envelopes and scalar dependencies are independently checked
before compiling a new paid word; no decreasing-frame operation is used.
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

import joint_region_search_v3 as region
import joint_signed_word_recompile as joint
from joint_scalar_future_frames import original_signed, write_word
from check_compiled_witness import contained
from joint_word_check_v4 import check

GEOMETRY = Path(__file__).resolve().parents[2] / 'geometry' / 'code'
sys.path.insert(0, str(GEOMETRY))
from enlarge_actual_signed_word import enlarge_actual


def transform(frame, order):
    rank, forced, symbols = frame
    moved = [0] * len(order)
    for i, j in enumerate(order):
        moved[j] = symbols[i]
    return rank, sum(1 << order[i] for i in range(len(order)) if forced >> i & 1), tuple(moved)


def prepare(source, work, receipt_path, documents):
    receipt = json.loads(receipt_path.read_text())
    assert receipt['source_only'] is True
    assert receipt['source_head'] == 'ad0f25ff7b23cff7f08ad237c2254e6ecf74257e'
    h = receipt['h']
    document = next(d for d in documents if d['h'] == h)
    assert receipt['source_parent_sha256'] == document['word_sha256']
    Q = receipt['source_permutation']
    assert Q == document['Q']
    raw = gzip.decompress(Path(receipt['word_path']).read_bytes())
    assert sha256(raw).hexdigest() == receipt['word_sha256']
    word = json.loads(raw)
    metadata_bytes = Path(receipt['original_region_metadata_path']).read_bytes()
    assert sha256(metadata_bytes).hexdigest() == receipt['original_region_metadata_sha256']
    metadata = json.loads(metadata_bytes)
    joint.initialize(source, work)
    config = {k: v for k, v in document['configuration'].items() if k != 'kind'}
    c, blocks, _, _, owner, _, _, _ = region.build_regions(h, config)
    assert len(blocks) == len(metadata['preintern_selected_frames'])
    index = {tuple((r, f, tuple(s))): i for i, (r, f, s) in enumerate(word['frames'])}
    old_aliases = []
    for block, envelope, label in zip(blocks, metadata['original_scalar_region_envelopes'], metadata['preintern_selected_frames']):
        moved_envelope = [sum(1 << Q[i] for i in range(h) if value >> i & 1) for value in block['frame']]
        assert moved_envelope == envelope
        moved = transform(label, Q)
        old_aliases.append(index[moved])
        assert contained(original_signed(h, block['frame']), tuple((label[0], label[1], tuple(label[2]))))
    # Parent canonicalization may intern equal spaces from several original
    # regions. Retain the complete preintern mapping for the new synthesis.
    parent = dict(word, physical_region_address_aliases=old_aliases)
    return document, c, blocks, owner, parent, receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--parents', type=Path, required=True)
    p.add_argument('--parent-receipts', type=Path, nargs='+', required=True)
    p.add_argument('--modes', nargs='+', choices=['all', 'balanced', 'unbalanced'], default=['all'])
    p.add_argument('--thresholds', type=int, nargs='+', default=[0])
    p.add_argument('--groupings', nargs='+', choices=['merge-aliases', 'preserve-regions'], default=['merge-aliases'])
    p.add_argument('--carriers', nargs='+', choices=['original', 'large-rise', 'small-rise', 'terminal-first'], default=['original'])
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    (args.work / 'process.json').write_text(json.dumps(dict(pid=os.getpid(), command=sys.argv,
        started_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')
    documents = json.loads(args.parents.read_text())
    rows = []
    seen = {}
    for receipt_path in args.parent_receipts:
        document, c, old_blocks, old_owner, parent, receipt = prepare(args.source, args.work, receipt_path, documents)
        h, Q = c.h, document['Q']
        inverse = [Q.index(i) for i in range(h)]
        scalar = c.verify()
        for mode in args.modes:
            for threshold in args.thresholds:
                frame_start = time.monotonic()
                enlarged, _, frame_receipt = enlarge_actual(parent, [], threshold, mode, 'one-core')
                labels = [transform(enlarged['frames'][i], inverse) for i in enlarged['physical_region_address_aliases']]
                assert len(labels) == len(old_blocks)
                for block, label in zip(old_blocks, labels):
                    assert contained(original_signed(h, block['frame']), label)
                for x in sorted(c.active):
                    for y in c.args[x] or ():
                        assert contained(labels[old_owner[y]], labels[old_owner[x]])
                frame_seconds = time.monotonic() - frame_start
                for grouping in args.groupings:
                    for carrier in args.carriers:
                        case = f"h{h}-actual-future-{mode}-minrank{threshold}-{grouping}-{carrier}"
                        target = args.work / 'raw' / case
                        target.mkdir(parents=True)
                        start = time.monotonic()
                        assignment = sha256(json.dumps((labels, grouping, carrier), separators=(',', ':')).encode()).hexdigest()
                        config = dict(parent_source_receipt=str(receipt_path), parent_word_sha256=receipt['word_sha256'],
                                      mode=mode, threshold=threshold, grouping=grouping, carrier=carrier)
                        if assignment in seen:
                            result = dict(status='DEDUPLICATED exact future frame assignment and carrier configuration',
                                          case_id=case, configuration=config, duplicate_of=seen[assignment])
                        else:
                            seen[assignment] = case
                            try:
                                region.COMPILER.build = lambda dim: joint.build(c, labels, old_owner, grouping, carrier)
                                compiled, word = region.COMPILER.compile_(h, matching=True, reclaim=True, dirty=True)
                                word = joint.canonicalize(word, Q)
                                word_path = target / 'word.json.gz'
                                word_sha = write_word(word_path, word)
                                independent = check(word_path, target / 'signed-transitions.bin')
                                result = dict(status='DISCOVERY actual-future region synthesis full source/frames/both-dirty PASS',
                                    case_id=case, configuration=config, scalar=scalar, compiled=compiled, independent=independent,
                                    frame_receipt=frame_receipt, frame_assignment_seconds=frame_seconds,
                                    old_regions=len(old_blocks), new_regions=compiled['stats']['regions'],
                                    assignment_sha256=assignment, word_path=str(word_path), word_sha256=word_sha,
                                    actual_parent_word_sha256=receipt['word_sha256'], actual_parent_source_receipt_sha256=sha256(receipt_path.read_bytes()).hexdigest(),
                                    source_permutation=Q)
                            except Exception as error:
                                result = dict(status='REJECTED actual-future synthesis configuration', case_id=case,
                                              configuration=config, error=repr(error), frame_receipt=frame_receipt)
                        result.update(seconds=time.monotonic()-start, source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
                            source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                            completed_utc=datetime.now(timezone.utc).isoformat(),
                            limitations='New paid finite word. Actual rational matrix CRT, independent source-only replay, DATA/stock/moments/assembly and inherited all-size gauge/tape realization remain separate acceptance gates.')
                        (target / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
                        rows.append(result)
                        args.output.parent.mkdir(parents=True, exist_ok=True)
                        args.output.write_text(json.dumps(dict(status='running', command=sys.argv, rows=rows), indent=2) + '\n')
                        print(json.dumps(dict(case_id=case, status=result['status'], R=result.get('compiled', {}).get('roles'),
                                             regions=result.get('new_regions'), error=result.get('error'))), flush=True)
    args.output.write_text(json.dumps(dict(status='complete', command=sys.argv, rows=rows,
        completed_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')


if __name__ == '__main__':
    main()
