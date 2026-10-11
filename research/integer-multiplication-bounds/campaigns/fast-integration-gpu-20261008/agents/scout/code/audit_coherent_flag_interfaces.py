#!/usr/bin/env python3
"""Bind coherent flagged literal words to source bijections and unchanged DATA.

The actual convention keeps the physical tensor order R/C fixed. Literal
source identifiers are interpreted through the retained complete triple
permutation; normalized DATA matrices agree with the previous family under
that bijection, rather than for a fixed unchanged triple name.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path


def record(path):
    data = path.read_bytes()
    return {'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,required=True)
    ap.add_argument('--graph-receipts',type=Path,nargs='+',required=True)
    ap.add_argument('--data-certificates',type=Path,nargs='+',required=True)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    checked_axes = []
    for path in args.graph_receipts:
        saved = json.loads(path.read_text());proof = saved['independent']
        h = proof['h'];assert h in (23,25)
        q = saved['source_permutation']
        assert sorted(q) == list(range(h)) and q == proof['source_permutation']
        assert proof['coherent_source_output_labels'] and proof['exact_transition_multiset_from_word']
        assert saved['compiled']['complete_dirty_basis_both_orientations']
        source = args.snapshot/f'research/pair-assembly/frame/frame-word-{h}.json.gz'
        original_raw = gzip.decompress(source.read_bytes());original = json.loads(original_raw)
        flagged_path = Path(proof['word_path'])
        flagged_raw = gzip.decompress(flagged_path.read_bytes());flagged = json.loads(flagged_raw)
        assert hashlib.sha256(flagged_raw).hexdigest() == proof['word_sha256']
        assert record(flagged_path)['sha256'] == proof['word_gzip_sha256']
        def permute(mask):
            return sum(1<<q[i] for i in range(h) if mask>>i&1)
        for key in ('h','v','R','ops','scatter','events','sources'):
            assert original[key] == flagged[key]
        assert flagged['frames'] == [[permute(c),permute(u)] for c,u in original['frames']]
        assert flagged['outputs'] == [[slot,frame,q[common],sorted(q[i] for i in T)]
                                      for slot,frame,common,T in original['outputs']]
        triples = list(combinations(range(h),3));indices = {T:i for i,T in enumerate(triples)}
        triple_map = [indices[tuple(sorted(q[i] for i in T))] for T in triples]
        assert sorted(triple_map) == list(range(len(triples)))
        assert saved['source_label_permutation'] == triple_map
        inverse = [0]*len(triples)
        for i,j in enumerate(triple_map):inverse[j]=i
        assert saved['source_label_inverse'] == inverse
        first = {}
        for slot,a,b in flagged['events']:
            first.setdefault(slot,tuple(flagged['frames'][b]))
        for key,slot in flagged['sources'].items():
            T = triples[triple_map[int(key)]]
            mask = sum(1<<i for i in T)
            assert first[slot] == (mask,mask)
        center_outputs = [(common,T) for slot,g,common,T in flagged['outputs'] if len(T)==1]
        assert sorted(center_outputs) == [(i,[i]) for i in range(h)]
        assert proof['copied_centers'] == h and proof['rank_mass'] == h*flagged['R']+h*(h-1)
        transitions = Path(proof['transition_path'])
        assert record(transitions)['sha256'] == proof['transition_sha256']
        profile_input = Path(saved['profile_transition_path'])
        assert record(profile_input)['sha256'] == proof['transition_sha256']
        full_word = 4*len(flagged['ops'])+2*len(flagged['scatter'])+2*len(triples)
        assert full_word == proof['complete_word_length']
        checked_axes.append({'h':h,'coordinate_permutation':q,
            'triple_label_permutation':triple_map,'triple_label_inverse':inverse,
            'literal_graph_receipt':record(path),'original_word':record(source),
            'original_word_raw_sha256':hashlib.sha256(original_raw).hexdigest(),
            'flagged_word':record(flagged_path),'flagged_word_raw_sha256':proof['word_sha256'],
            'exact_flagged_transition':record(transitions),
            'geometry_transition_bytes_identical':True,'full_local_XOR_word':full_word,
            'all_source_frames_checked':len(triples),'all_copied_center_outputs_checked':h,
            'source_key_convention':'The serialized sources slot dictionary is unchanged. Its key k denotes the Q-relabeled logical triple indexed by triple_label_permutation[k], explicitly recorded in the literal graph receipt; source payload routing uses this mapping.',
            'isometry':'Q1=1 and 1^T Q=1^T imply Q commutes with H0=I-J/9 and every L_beta. Thus every original or enlarged common-basis projector is Q-conjugated, including sources and centers; all exact normalizations and nonzero coordinate conditions are preserved.'})
    assert len({x['h'] for x in checked_axes}) == len(checked_axes)
    data = []
    for path in args.data_certificates:
        receipt = json.loads(path.read_text())
        N = receipt.get('pairs',receipt.get('full_DATA_sources'))
        assert N == 4073300
        hist = receipt.get('one_front_histogram',receipt.get('uniform_one_front_histogram'))
        assert hist == {'1':9*N,'17':N,'21':N,'481':N}
        data.append(record(path))
    result = {'created_utc':datetime.now(timezone.utc).isoformat(),
        'status':'PASS COHERENT FLAG SOURCE, COPIED-CENTER AND COMPLETE DATA BIJECTION',
        'source':record(Path(__file__)),'axes':checked_axes,'closed_DATA_inputs':data,
        'actual_execution_convention':'Common physical DATA permutation and R/C stay fixed; flagged local frame/source/output labels are all interpreted using the same global coordinate permutation. If one axis is not listed, its map is the identity.',
        'full_DATA_identity':'For beta-fixed axis weights x_beta(T), coordinate relabeling gives x_beta(QT). At the unchanged physical R/C, the flagged normalized matrix M_flag(T,S) equals M_old(Q23(T),Q25(S)). The two lexical source maps are bijections, so their Cartesian map covers all N exactly once and preserves the complete profile histogram. An unchanged triple name does not in general give entrywise equality.',
        'copied_center_identity':'Each center i is relabeled Qi along with its actual singleton-core/full-cover output; all h centers remain present. L_beta and H0 commute Q, so normalized primal/dual pairs, copied entrance and still-paid rank-one cleanup transfer exactly.',
        'scalar_stock_identity':'Ops, scatter, event IDs, role allocation and complete word length are unchanged. The previously counted scalar charge and row stock transfer to this coherent relabeling. Fresh local NE flag profiles remain separately required and are not inferred from rank invariance.',
        'remaining_gates':'The literal graph receipt binds the source-routing permutation. Full conditional address lifting, fresh local bounded-minor profiles and complete characteristic/bridge composition are separate. No kappa is claimed here.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'axes':[x['h'] for x in checked_axes],'complete_DATA_pairs':4073300,'source_triples_checked':sum(x['all_source_frames_checked'] for x in checked_axes)}))


if __name__ == '__main__':
    main()
