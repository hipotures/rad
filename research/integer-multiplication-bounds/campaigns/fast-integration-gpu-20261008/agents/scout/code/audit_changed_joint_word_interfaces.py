#!/usr/bin/env python3
"""Bind changed literal joint words, exact profiles, DATA reuse and paid charges.

Unlike the original-word audits, this accepts fresh source-only rebuilt
words and derives their actual role volume and scalar charge. Every source
entrance, ordinary output and center is checked against its explicit global
source relabeling. No old word digest is substituted for the new word.
"""
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction as F
import gzip
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path


def record(path):
    data = path.read_bytes()
    return {'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def load_module(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    value = importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--phase-snapshot',type=Path,required=True)
    ap.add_argument('--graph-receipts',type=Path,nargs=2,required=True)
    ap.add_argument('--geometry-fixtures',type=Path,nargs=2,required=True)
    ap.add_argument('--data-certificate',type=Path,required=True)
    ap.add_argument('--beta23',type=F,required=True)
    ap.add_argument('--beta25',type=F,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    own = Path(__file__).resolve().parent
    norm_helper = own/'audit_source_center_basis_interfaces.py'
    norms = load_module('changed_word_normalization',norm_helper)
    old = json.loads((args.phase_snapshot/'research/pair-assembly/frame/frame-certificate.json').read_text())
    arithmetic_path = args.phase_snapshot/'research/pair-assembly/balanced_assembly.py'
    arithmetic = load_module('changed_word_phase_arithmetic',arithmetic_path)
    data = json.loads(args.data_certificate.read_text())
    assert data['status'] == 'PASS COMPLETE RATIONAL UNIFORM DATA FAMILY'
    N = data['pairs'];assert N == 4073300
    assert data['one_front_histogram'] == {'1':9*N,'17':N,'21':N,'481':N}
    geometry = {json.loads(p.read_text())['h']:(p,json.loads(p.read_text())) for p in args.geometry_fixtures}
    assert set(geometry) == {23,25}
    betas = {23:args.beta23,25:args.beta25}
    interfaces = {h:norms.basis(h,beta) for h,beta in betas.items()}
    assert [[str(1/F(z)) for z in interfaces[h]['source_coordinate_products']] for h in (23,25)] == data['inverse_source_products']
    axes = []
    for path in args.graph_receipts:
        graph = json.loads(path.read_text());proof = graph['independent']
        h = proof['h'];assert h in geometry
        fixture_path,fixture = geometry[h]
        q = graph['source_permutation']
        assert sorted(q) == list(range(h)) and q == fixture['coordinate_order'] == proof['source_permutation']
        assert proof['coherent_source_output_labels'] and proof['exact_transition_multiset_from_word']
        assert graph['compiled']['complete_dirty_basis_both_orientations']
        assert proof['orientations'] == ['forward','reverse-complement']
        word_path = Path(proof['word_path']);packed = word_path.read_bytes();raw = gzip.decompress(packed);word = json.loads(raw)
        assert hashlib.sha256(raw).hexdigest() == proof['word_sha256']
        assert hashlib.sha256(packed).hexdigest() == proof['word_gzip_sha256']
        assert word['h'] == h and word['R'] == proof['R']
        triples = list(combinations(range(h),3));v = len(triples)
        assert word['v'] == v and len(word['sources']) == v and N%v == 0
        indices = {T:i for i,T in enumerate(triples)}
        triple_map = [indices[tuple(sorted(q[i] for i in T))] for T in triples]
        assert sorted(triple_map) == list(range(v)) and graph['source_label_permutation'] == triple_map
        inverse = [0]*v
        for i,j in enumerate(triple_map):inverse[j]=i
        assert graph['source_label_inverse'] == inverse
        assert set(map(int,word['sources'])) == set(range(v))
        assert len(set(word['sources'].values())) == v
        frames = word['frames'];assert all(len(f)==2 and all(type(x)==int for x in f) for f in frames)
        physical_registers = word['R']+2*v
        assert proof['complete_basis_vectors'] == physical_registers
        first = {};current = {};initializations = 0
        for slot,a,b in word['events']:
            assert 0 <= slot < word['R'] and 0 <= b < len(frames)
            if a == -1:
                assert slot not in current
                initializations += 1
            else:
                assert 0 <= a < len(frames) and current[slot] == a
            first.setdefault(slot,tuple(frames[b]))
            current[slot] = b
        assert initializations == word['R'] and set(current) == set(range(word['R']))
        for key,slot in word['sources'].items():
            T = triples[triple_map[int(key)]];mask = sum(1<<i for i in T)
            assert 0 <= slot < word['R'] and first[slot] == (mask,mask)
        centers = set();ordinary = set();slots = set()
        for slot,fid,common,T in word['outputs']:
            assert 0 <= slot < word['R'] and slot not in slots;slots.add(slot)
            c,u = frames[fid];assert c == 1<<common
            if len(T)==1:
                assert T == [common] and u == (1<<h)-1
                assert common not in centers;centers.add(common)
            else:
                T = tuple(T);assert T in indices and common in T
                assert u == ((1<<h)-1)^sum(1<<i for i in T if i!=common)
                assert (common,T) not in ordinary;ordinary.add((common,T))
        assert centers == set(range(h))
        assert ordinary == {(i,T) for T in triples for i in T}
        assert proof['copied_centers'] == h
        assert proof['rank_mass'] == h*word['R']+h*(h-1)
        key = f'beta:{betas[h].numerator}:{betas[h].denominator}'
        selected = [x for x in fixture['profiles'] if x['config']['basis'] == key]
        assert len(selected)==1;selected=selected[0];profile=selected['profile']
        profile_path = Path(selected['profile_path'])
        assert record(profile_path)['sha256'] == selected['profile_sha256']
        assert json.loads(profile_path.read_text()) == profile
        assert profile['R'] == word['R'] and profile['v'] == v and profile['h'] == h
        assert profile['rank_sum'] == proof['rank_mass']
        assert sum(i*n for i,n in enumerate(profile['blocks'])) == proof['rank_mass']
        transition_path = Path(proof['transition_path'])
        transition = record(transition_path)
        assert transition['sha256'] == proof['transition_sha256'] == selected['input_binary_sha256']
        assert record(Path(selected['config']['transitions']))['sha256'] == transition['sha256']
        count = 4*len(word['ops'])+2*len(word['scatter'])+2*v
        assert count == proof['complete_word_length']
        axes.append({'h':h,'v':v,'R':word['R'],'invocations':N//v,
                     'graph_receipt':record(path),'geometry_fixture':record(fixture_path),
                     'word':record(word_path),'raw_word_sha256':proof['word_sha256'],
                     'actual_transition':transition,'selected_profile':record(profile_path),
                     'coordinate_permutation':q,'source_label_permutation':triple_map,
                     'source_label_inverse':inverse,'source_frames_checked':v,
                     'ordinary_outputs_checked':3*v,'copied_centers_checked':h,
                     'basis_interface':interfaces[h],'mixer_xors':len(word['ops']),
                     'scatter_xors':len(word['scatter']),'source_xors':v,
                     'complete_local_XOR_word':count,'weighted_local_XOR_word':count*(N//v),
                     'complete_physical_registers_per_axis':physical_registers,
                     'scratch_initializations_checked':initializations,
                     'chronological_frame_events_checked':len(word['events']),
                     'additional_copied_center_groups':2*h*(N//v),
                     'local_rank_mass':proof['rank_mass']})
    assert {x['h'] for x in axes} == {23,25}
    axes.sort(key=lambda x:x['h'])
    W = 2*N+sum(x['R']*x['invocations'] for x in axes)
    loss = sum(x['h']*(x['h']-1)*x['invocations'] for x in axes)
    mass = W*575-N+loss
    paid = sum(x['weighted_local_XOR_word'] for x in axes)
    center_groups = sum(x['additional_copied_center_groups'] for x in axes)
    bit_G = paid+3*N+center_groups
    bridge = copy.deepcopy(old['finite_bridge'])
    bridge['bit']['W'] = W
    bridge['bit']['wire_bits'] = W.bit_length()
    validated = arithmetic.validate_bridge(bridge)
    phase_G = validated['complex']['scalar_group_upper']
    assert bit_G < phase_G
    assert W <= validated['complex']['W'] and 575 <= validated['complex']['m']
    assert mass <= validated['complex']['s']
    literal = 2*bit_G*W**2+8*mass+4*W+4+32*575
    assert literal < validated['semantic']['literal_charge'] < validated['semantic']['E']
    result = {'created_utc':datetime.now(timezone.utc).isoformat(),
        'status':'PASS CHANGED LITERAL WORD SOURCE/CENTER/DATA TRANSFER AND PAID SCALAR/STOCK INTERFACES',
        'source':record(Path(__file__)),'normalization_helper':record(norm_helper),
        'phase_arithmetic_source':record(arithmetic_path),'closed_uniform_DATA':record(args.data_certificate),
        'axes':axes,'N':N,'m':575,'W':W,'L':loss,'total_rank':mass,
        'paid_local_XOR_steps':paid,'additional_center_groups':center_groups,
        'global_bank_exchange_XOR_bound':3*N,'conservative_bit_scalar_upper':bit_G,
        'retained_phase_scalar_upper':phase_G,'scalar_domination_gap':phase_G-bit_G,
        'bit_literal_upper':literal,'retained_phase_literal_charge':validated['semantic']['literal_charge'],
        'retained_semantic_E':validated['semantic']['E'],'new_bit_bridge':bridge['bit'],'rows':bridge['rows'],
        'source_and_center_scope':'Every actual changed-word entrance, ordinary output and copied-center target is checked against complete lexical source maps. Source/center coordinates and exact normalizations use the stated common L_beta, not an old scalar-word digest.',
        'DATA_transfer':'Physical R/C retain the certified order. With the explicit source-index maps, M_new(T,S)=M_certified(Q23T,Q25S). The Cartesian triple map is a bijection, so the full exact DATA histogram transfers. The changed auxiliary word does not enter the normalized DATA formula; no fullN replay is performed.',
        'scalar_stock_scope':'4M+2J+2V is recounted on the actual two changed serialized words. Three XORs per global bank exchange and copied-center groups are included. The inherited phase guard dominates the resulting count, rank and role charges. Product stock is recomputed using the actual new W and unchanged recursive maximum width.',
        'remaining_gates':'This binds finite source, target, data and paid scalar/stock interfaces. The graph full-dirty proof and fresh local profile certificates are separately source-bound dependencies. Complete exact moment/semantic assembly and general conditional lifting remain coordinator obligations; no kappa is claimed.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','W','L','total_rank','paid_local_XOR_steps','conservative_bit_scalar_upper','scalar_domination_gap')}))


if __name__ == '__main__':
    main()
