#!/usr/bin/env python3
"""Scoped source/center/DATA interface audit for authorized PR62+57+61.

No full source-family sweep, compiler regeneration or dirty-word replay.
Static actual-word source/terminal membership is checked completely. Local
flags and all framed-word/compiler/bridge hypotheses remain separate.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import gzip
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import time

PINS = {62:'ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
        57:'cd350f76c9bc01489ec83568bded532cb69be938',
        61:'afb7cb67d1858641315cfbf4ac768ee64a8eff3a'}


def record(path):
    return {'path':str(path),'bytes':path.stat().st_size,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshots-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    began = time.monotonic()
    manifest_path = args.snapshots_root/'snapshot-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    entries = {x['pr']:x for x in manifest['sources']}
    roots, permitted = {}, {}
    for number, pin in PINS.items():
        entry = entries[number];assert entry['pinned_commit'] == pin
        roots[number] = args.snapshots_root/f'pr{number}-{pin}'
        permitted[number] = {x['path']:x['sha256'] for x in entry['files']}
    consumed = {number:set() for number in PINS}
    def checked(number,relative):
        path = roots[number]/relative
        assert record(path)['sha256'] == permitted[number][relative]
        consumed[number].add(relative)
        return path
    for number in PINS:checked(number,'LICENSE')
    for relative in ('research/pair-assembly/PROOF.md','research/pair-assembly/pair_graph.py',
                     'research/pair-assembly/verify.py','research/pair-assembly/data_recovery.py',
                     'research/pair-assembly/data_corners.cpp','research/pair-assembly/data-corners.json',
                     'research/pair-assembly/reversed/geometry.py',
                     'research/pair-assembly/reversed/pr34/independent_controls.py',
                     'research/pair-assembly/frame/frame_compile.py','research/pair-assembly/frame/frame_verify.py',
                     'scripts/experiments/binary_frame_profile_prepare.py','scripts/experiments/binary_frame_profiles.cpp'):
        checked(62,relative)
    unchanged = []
    for name in ('binary_frame_compiler.py','binary_frame_profile_prepare.py','binary_frame_profiles.cpp'):
        relative = 'scripts/experiments/'+name
        left,right = checked(62,relative),checked(57,relative)
        assert left.read_bytes() == right.read_bytes()
        unchanged.append({'path':relative,'sha256':record(left)['sha256']})
    spec = importlib.util.spec_from_file_location('interval_joint_bounded_data',checked(62,'research/pair-assembly/verify.py'))
    verifier = importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    geometry = verifier.geometry()
    N = 4073300
    assert geometry['accepted_profile'] == {'singletons':9,'blocks':[21,17,481]}
    assert geometry['modular']['primary_good'] == N-10
    assert geometry['modular']['primary_fallback'] == 10
    assert geometry['modular']['good'] == N and geometry['modular']['fallback'] == 0
    own = Path(__file__).resolve().parent.parent
    prior_path = own/'gpu-parameter-results/pr54-IJ-conjugate-data-compatibility-20261008T1714.json'
    prior = json.loads(prior_path.read_text())
    assert [tuple(x) for x in prior['rows']] == geometry['inherited']['rows']
    assert [tuple(x) for x in prior['columns']] == geometry['inherited']['columns']
    bases = []
    for h in (23,25):
        choices=[]
        for beta in (F(-1),F(10,9*(h+1))):
            gamma=(9*beta-1)/(3*(1-h*beta))
            primal=(1-3*beta,-3*beta);dual=((1+gamma)/2,gamma/2)
            products=tuple(x*y for x,y in zip(primal,dual))
            k=F(h-9,4);c=(2-3*beta*(h-3))/(h-9)
            v=F(h-9)*(1-3*beta)/(12*(1-h*beta))
            center_primal=(1+c,c);center_dual=(v-k,v)
            assert all(primal) and all(dual) and all(center_primal) and all(center_dual)
            assert 3*products[0]+(h-3)*products[1]==1
            assert center_primal[0]*center_dual[0]+(h-1)*center_primal[1]*center_dual[1]==1
            choices.append({'beta':str(beta),'gamma':str(gamma),'source_primal':list(map(str,primal)),
                            'source_dual':list(map(str,dual)),'source_products':list(map(str,products)),
                            'center_primal':list(map(str,center_primal)),'center_dual':list(map(str,center_dual))})
        assert choices[0]['source_products']==choices[1]['source_products']
        assert all(F(a)==2*F(b) for a,b in zip(choices[1]['source_primal'],choices[0]['source_dual']))
        assert all(F(a)==-F(b)/F(h-9,4) for a,b in zip(choices[1]['center_primal'],choices[0]['center_dual']))
        bases.append({'h':h,'choices':choices,'all_source_and_center_coordinates_nonzero':True})
    compiler_record=json.loads(checked(62,'research/pair-assembly/frame/frame-compiler.json').read_text())
    word_scopes=[]
    for h in (23,25):
        path=checked(62,f'research/pair-assembly/frame/frame-word-{h}.json.gz')
        packed=path.read_bytes();raw=gzip.decompress(packed);word=json.loads(raw)
        axis=compiler_record['axes'][str(h)]
        assert hashlib.sha256(packed).hexdigest()==axis['gzip_sha256']
        assert hashlib.sha256(raw).hexdigest()==axis['word_sha256']
        triples=list(combinations(range(h),3));v=len(triples);R=word['R']
        assert word['h']==h and word['v']==v and R==axis['replay']['roles']
        frames=word['frames'];assert len({tuple(x) for x in frames})==len(frames)
        assert set(map(int,word['sources']))==set(range(v))
        assert len(set(word['sources'].values()))==v
        initial_sources={}
        for index,slot in word['sources'].items():
            assert 0<=slot<R
            mask=sum(1<<j for j in triples[int(index)])
            initial_sources[slot]=(mask,mask)
        # Actual compiled word records source frames directly through the
        # first incidence events; check those rather than node metadata.
        first_frames={}
        for slot,a,b in word['events']:
            if slot not in first_frames:first_frames[slot]=tuple(frames[b])
        assert all(first_frames[slot]==frame for slot,frame in initial_sources.items())
        output_slots=set();centers=set();ordinary=set()
        for slot,g,common,triple in word['outputs']:
            assert 0<=slot<R and slot not in output_slots;output_slots.add(slot)
            c,u=frames[g]
            assert c==1<<common
            if len(triple)==1:
                assert tuple(triple)==(common,) and u==(1<<h)-1
                centers.add(common)
            else:
                T=tuple(triple);assert T in triples and common in T
                assert u==((1<<h)-1)^sum(1<<j for j in T if j!=common)
                assert (common,T) not in ordinary;ordinary.add((common,T))
        assert centers==set(range(h))
        assert ordinary=={(common,T) for T in triples for common in T}
        transitions=json.loads(checked(62,f'research/pair-assembly/frame/frame-transitions-{h}.json').read_text())
        assert transitions['copied_centers']==h
        assert transitions['word_sha256']==hashlib.sha256(raw).hexdigest()
        assert transitions['rank_mass']==h*R+h*(h-1)
        word_scopes.append({'h':h,'v':v,'R':R,'source_frames_checked':v,'ordinary_outputs_checked':3*v,
                            'copied_centers_checked':h,'source_line_mapping':'Complete lexical triples in distinct actual source slots, first physical event frame equals that triple line.',
                            'center_charges':'Each actual full-cover output has copied-center entrance plus rank-one original cleanup in the retained transition extraction.',
                            'word':record(path),'word_sha256':hashlib.sha256(raw).hexdigest(),
                            'static_scope':'Source and terminal interface only; full XOR/dirty replay and fresh local profiles are separate coordinator/graph/geometry checks.'})
    checked(61,'research/matrix-exponent-synthesis/candidate/README.md')
    refinement=json.loads(checked(61,'research/matrix-exponent-synthesis/candidate/arithmetic.json').read_text())
    assert refinement['source_commit']==PINS[62]
    native_path=checked(62,refinement['source_certificate_path'])
    assert record(native_path)['sha256']==refinement['source_certificate_sha256']
    native=json.loads(native_path.read_text());assert refinement['source_profile']==native['bit']
    checked(61,'research/matrix-exponent-synthesis/candidate/verify_refinement.py')
    result={'created_utc':datetime.now(timezone.utc).isoformat(),
            'status':'PASS PINNED INTERVAL-JOINT SOURCE, COPIED-CENTER AND FULL DATA COMPATIBILITY',
            'pinned_commits':PINS,'current_heads_at_root_acquisition':{str(n):entries[n]['current_pr_head'] for n in PINS},
            'snapshot_manifest':record(manifest_path),'audit_source':record(Path(__file__)),
            'consumed_sources':{str(n):[record(roots[n]/s) for s in sorted(consumed[n])] for n in PINS},
            'unchanged_PR57_compiler_sources':unchanged,'basis_identities':bases,'actual_source_terminal_word_checks':word_scopes,
            'full_DATA_sources':N,'uniform_one_front_histogram':{'1':9*N,'17':N,'21':N,'481':N},
            'universal_data_identity':'Both conjugate choices on each axis have identical source coordinate products for every actual triple. R/C equal the prior pinned PR54 order. The same complete normalized DATA matrix is entrywise unchanged by interval scalar DAGs and joint auxiliary XOR words.',
            'bounded_geometry_scope':'Pinned geometry() checks universal rational all-weight rank cuts, retained full Cartesian coverage and ten exact Q recovery controls. No fullN source sweep regenerated.',
            'basis_combinations':[['-1','-1'],['-1','5/117'],['5/108','-1'],['5/108','5/117']],
            'exact_recovered_controls':geometry['modular']['exact_recovery'],
            'PR61_scope':'Exact identical PR62 source profile; arithmetic/assembly parameter refinement only, no DATA/frame basis change.',
            'remaining_obligations':'Conjugate local NE profiles transpose and must be recomputed on actual new transitions. Full XOR/dirty semantics, enlarged positive frames, scalar overhead, paid timeline, compiler, bridge, characteristic exclusions and assembly remain separate checks. No new kappa is claimed by this scoped audit.',
            'attribution':'Avi Eisenberg PR62 intervals and core-aware assembly; eumemic PR57 joint frame compiler; Alejandro Zarzuelo Urdiales (alejandrozu) PR61 parameter refinement; retained Chafik Boukhalfa/Rohan Arun/James Chang/icekylinx/Dominik Scholz and predecessor notices.',
            'elapsed_seconds':time.monotonic()-began}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'full_DATA_sources':N,'source_and_center_words':word_scopes,'elapsed_seconds':result['elapsed_seconds']}))


if __name__=='__main__':main()
