#!/usr/bin/env python3
"""Bind actual mixed coframe words, exact profiles, DATA and paid charges.

Unlike the original-word audits, this accepts fresh source-only rebuilt
words and derives their actual role volume and scalar charge. Every source
entrance, ordinary output and center is checked against its explicit global
source relabeling. No old word digest is substituted for the new word.
"""
import argparse
import copy
from pathlib import Path
from signed_positive_frame_interfaces import ordinary_frame
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'graph'/'code'))
import co_signed_source_frames as co
normalize, columns, contained = co.normalize, co.basis, co.contained
from datetime import datetime, timezone
from fractions import Fraction as F
import gzip
import hashlib
import importlib.util
from itertools import combinations
import json


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
        assert Path(fixture['source_only_receipt']).resolve() == path.resolve()
        assert fixture['source_only_receipt_sha256'] == record(path)['sha256']
        q = graph['source_permutation']
        assert sorted(q) == list(range(h)) and q == fixture['coordinate_order'] == proof['source_permutation']
        assert proof['coherent_source_output_labels'] and proof['exact_transition_multiset_from_word']
        assert graph['compiled']['complete_dirty_basis_both_orientations']
        assert graph['source_only'] and graph['word_regenerated_from_source_and_selected_carriers']
        assert graph['physical_matching_and_literal_xors_changed']
        assert graph['original_scalar_dag_outputs_preserved']
        assert graph['source_injection_frames_unchanged']
        assert graph['actual_frame_assignment_reconstructed']
        assert graph['selected_source_coframes']
        assert graph['explicit_coframe_allocation']
        allocation_path = Path(graph['allocation_path'])
        assert record(allocation_path)['sha256'] == graph['allocation_sha256']
        assert graph['original_envelope_floor_asserted'] is False
        assert graph['actual_old_frames_are_upper_bounds']
        assert graph['literal_xors_unchanged_from_selected_weighted_parent']
        assert graph['source_injection_spaces_mutually_checked']
        assert graph['copied_center_spaces_mutually_checked']
        parent_path=Path(graph['fresh_weighted_source_receipt_path'])
        assert record(parent_path)['sha256']==graph['fresh_weighted_source_receipt_sha256']
        parent=json.loads(parent_path.read_text())
        assert parent['source_only'] and parent['word_regenerated_from_source_and_selected_carriers']
        assert parent['every_selected_use_reconstructed'] and parent['strict_carrier_chronology']
        assert parent['independent']['word_sha256']==graph['actual_parent_word_sha256']
        assert parent['selected_matching_sha256']==graph['selected_matching_sha256']
        assert graph['compiled']['all_physical_frame_inclusions']
        assert graph['every_selected_use_reconstructed'] and graph['distinct_recipient_capacity']
        assert graph['donor_row_capacity_exactly_independent'] and graph['strict_carrier_chronology']
        # Actual byte equality is independently checked against the selected native input below.
        assert proof['frame_format'] == co.FORMAT
        carrier_path = Path(graph['selected_matching_path'])
        assert record(carrier_path)['sha256'] == graph['selected_matching_sha256']
        assert proof['orientations'] == ['forward','reverse-complement']
        word_path = Path(proof['word_path']);packed = word_path.read_bytes();raw = gzip.decompress(packed);word = json.loads(raw)
        assert hashlib.sha256(raw).hexdigest() == proof['word_sha256']
        assert hashlib.sha256(packed).hexdigest() == proof['word_gzip_sha256']
        assert word['h'] == h and word['R'] == proof['R']
        parent_packed=Path(parent['independent']['word_path']).read_bytes()
        parent_raw=gzip.decompress(parent_packed)
        assert hashlib.sha256(parent_raw).hexdigest()==parent['independent']['word_sha256']
        assert hashlib.sha256(parent_packed).hexdigest()==parent['independent']['word_gzip_sha256']
        parent_word=json.loads(parent_raw)
        for key in ('h','v','R','sources','scatter','source_permutation',
                    'source_label_permutation','source_label_inverse'):
            assert word[key]==parent_word[key]
        assert len(word['ops'])==len(parent_word['ops'])
        assert len(word['events'])==len(parent_word['events'])
        assert len(word['outputs'])==len(parent_word['outputs'])
        for (a,b,g),(pa,pb,pg) in zip(word['ops'],parent_word['ops']):
            assert (a,b)==(pa,pb)
            assert contained(normalize(word['frames'][g]),normalize(parent_word['frames'][pg]))
        for (slot,a,b),(pslot,pa,pb) in zip(word['events'],parent_word['events']):
            assert slot==pslot and (a==-1)==(pa==-1)
            assert contained(normalize(word['frames'][b]),normalize(parent_word['frames'][pb]))
        for (slot,g,common,T),(pslot,pg,pc,pT) in zip(word['outputs'],parent_word['outputs']):
            assert (slot,common,T)==(pslot,pc,pT)
            assert contained(normalize(word['frames'][g]),normalize(parent_word['frames'][pg]))
        triples = list(combinations(range(h),3));v = len(triples)
        assert word['v'] == v and len(word['sources']) == v and N%v == 0
        indices = {T:i for i,T in enumerate(triples)}
        triple_map = [indices[tuple(sorted(q[i] for i in T))] for T in triples]
        assert sorted(triple_map) == list(range(v)) and word['source_label_permutation'] == triple_map
        inverse = [0]*v
        for i,j in enumerate(triple_map):inverse[j]=i
        assert word['source_label_inverse'] == inverse
        assert set(map(int,word['sources'])) == set(range(v))
        assert len(set(word['sources'].values())) == v
        assert word['frame_format'] == co.FORMAT
        frames = [normalize(frame) for frame in word['frames']]
        assert len(set(frames)) == len(frames)
        complemented_frames=0
        for frame in frames:
            assert len(co.symbols(frame))==h and len(columns(frame))==frame[0]
            if len(frame)==4:
                complemented_frames+=1
                rank,forced,tag,symbols=frame
                assert tag==co.TAG and forced.bit_count()==1
                common=forced.bit_length()-1
                assert rank==h-1-len({abs(x) for x in symbols if abs(x)>1})
                # Direct kernel and positive H0 metric checks are not a ridge
                # assumption about payloads. Every vector in this address
                # subspace obeys these integer constraints.
                for vector in columns(frame):
                    assert sum(vector)==3*vector[common]
                    groups={}
                    for i,label in enumerate(symbols):
                        if i!=common and label:
                            groups[abs(label)]=groups.get(abs(label),0)+(1 if label>0 else -1)*vector[i]
                    assert not any(groups.values())
                    assert 9*sum(x*x for x in vector)-sum(vector)**2==9*sum(vector[i]**2 for i in range(h) if i!=common)>0

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
                assert contained(frames[a], frames[b]), 'Actual signed frame raise is not contained'
            first.setdefault(slot,tuple(frames[b]))
            current[slot] = b
        assert initializations == word['R'] and set(current) == set(range(word['R']))
        for key,slot in word['sources'].items():
            T = triples[triple_map[int(key)]];mask = sum(1<<i for i in T)
            assert 0 <= slot < word['R'] and first[slot] == (1, mask, tuple(int(mask >> i & 1) for i in range(h)))
        centers = set();ordinary = set();slots = set()
        ordinary_rank_histogram = {};side_singletons = 0
        dual_in, dual_out = map(F, interfaces[h]['source_dual'])
        assert dual_in - dual_out == F(1,2)
        assert dual_out - betas[h] * (3 * dual_in + (h - 3) * dual_out) == F(-1,6)
        for slot,fid,common,T in word['outputs']:
            assert 0 <= slot < word['R'] and slot not in slots;slots.add(slot)
            rank,forced=frames[fid][:2];symbols=co.symbols(frames[fid]);assert forced==1<<common
            assert all(3 * sum(row[i] for i in T) == sum(row) for row in columns(frames[fid]))
            if len(T)==1:
                assert T == [common] and rank == h - 1
                expected_frame = ordinary_frame(common, set(), h)
                assert contained(frames[fid], expected_frame) and contained(expected_frame, frames[fid])
                assert common not in centers;centers.add(common)
            else:
                T = tuple(T);assert T in indices and common in T
                expected_frame = ordinary_frame(common, set(T) - {common}, h)
                assert 1<=rank<=h-2
                # The actual source-containing space may be smaller than the
                # original envelope; annihilation and paid side components
                # are checked directly, with no original-envelope floor.
                ordinary_rank_histogram[rank] = ordinary_rank_histogram.get(rank, 0) + 1
                side_singletons += h - rank
                assert (common,T) not in ordinary;ordinary.add((common,T))
        assert centers == set(range(h))
        assert ordinary == {(i,T) for T in triples for i in T}
        assert side_singletons == proof['side_growth_singletons']
        assert proof['copied_centers'] == h == graph['copied_center_spaces_unchanged']
        assert graph['profile_transition_sha256'] == proof['transition_sha256']
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
        selected_binary=Path(selected['config']['transitions'])
        assert record(selected_binary)['sha256']==transition['sha256']
        assert transition_path.read_bytes()==selected_binary.read_bytes()
        assert transition_path.read_bytes()[:8]==b'RADCOF01'
        count = 4*len(word['ops'])+2*len(word['scatter'])+2*v
        assert count == proof['complete_word_length']
        axes.append({'h':h,'v':v,'R':word['R'],'invocations':N//v,
                     'graph_receipt':record(path),'geometry_fixture':record(fixture_path),
                     'fresh_weighted_parent_receipt':record(parent_path),
                     'explicit_coframe_allocation':record(allocation_path),
                     'source_generation_mode':graph['source_generation_mode'],
                     'old_frames_are_upper_bounds_not_floor':True,
                     'selected_actual_spaces_contained_in_old':True,
                     'complemented_source_space_frames_checked':complemented_frames,
                     'source_and_native_binary_bytes_independently_equal':True,
                     'selected_carrier_list':record(carrier_path),
                     'selected_carriers':graph['selected_carriers'],
                     'physical_matching_and_literal_xors_changed':True,
                     'word':record(word_path),'raw_word_sha256':proof['word_sha256'],
                     'actual_transition':transition,'selected_profile':record(profile_path),
                     'coordinate_permutation':q,'source_label_permutation':triple_map,
                     'source_label_inverse':inverse,'source_frames_checked':v,
                     'ordinary_outputs_checked':3*v,'copied_centers_checked':h,
                     'ordinary_output_rank_histogram':ordinary_rank_histogram,
                     'actual_side_growth_singletons':side_singletons,
                     'normalized_source_sink_identity':'mu_T L_beta x = (3 sum_T x − sum x)/6',
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
        'status':'PASS ACTUAL MIXED COFRAME SOURCE/CENTER/DATA AND PAID SCALAR/STOCK INTERFACES',
        'source':record(Path(__file__)),'normalization_helper':record(norm_helper),
        'independent_signed_frame_helper':record(own/'signed_positive_frame_interfaces.py'),
        'mixed_integer_frame_helper':record(Path(co.__file__)),
        'ordinary_integer_frame_helper':record(Path(co.__file__).parent/'check_compiled_witness.py'),
        'frame_scope':'Actual mixed signed directions and complemented normal kernel integer columns, every physical raise, all source injection spaces, all ordinary sink spaces and copied-center spaces are independently checked. Ordinary terminal spaces may be smaller than the original envelopes; every actual scalar source address is contained, and normalized sink annihilation is checked on every selected integer column. All additional terminal components are charged as side singletons. Copied-center spaces remain equal to their original spaces. No original-envelope floor or substitute matrix profile is used.',
        'positive_metric_identity':'On Gamma_c={x:sum(x)=3*x_c}, x^T(I-J/9)x=sum_{i!=c} x_i^2. This is positive on every nonzero address vector; a complemented frame is its subspace defined by the signed normal equations. No ridge restriction on arbitrary array payloads is assumed.',
        'dirty_scope':'The separately bound source-only verifier replays every F2 payload role in both orientations. Its address-array extension is the inherited exact frame-gauge conjugation/telescoping lemma, together with the actual rational frame/projector certificates and compiler realization assumptions; this receipt does not identify F2 role count with address dimension.',
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
