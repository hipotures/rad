#!/usr/bin/env python3
"""Build the explicit immutable source/input identity for one integrated plan.

This does no discovery and does not accept finite verification flags.
Apache-2.0; prepared with OpenAI GPT-6.1 Sol assistance.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sprint', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Output must be fresh')
    root = args.sprint
    previous = json.loads((root/'agents/transfer/configs/rebuilt168-top169-ceiling-v2.json').read_text())
    inputs, sources = {}, dict(previous['sources'])
    def pin(path):
        raw = (root/path).read_bytes()
        return dict(path=path, bytes=len(raw), sha256=sha256(raw).hexdigest())
    def inp(key,path):
        inputs[key] = pin(path)
    def src(key,path):
        sources[key] = pin(path)
    complex_root = 'work/placement/fused168-joint-raise-frozen-20261009T0937Z/'
    for key,name in [('physical','profile.json'),('scalar','profile-before.json'),
                     ('complex_frames','physical-frames.json'),('complex_pairs','physical-pairs.json'),
                     ('complex_graph','graph.json'),('complex_word','word.json'),
                     ('complex_logical_frames','frames.json'),('complex_baseline','baseline.json'),
                     ('complex_protocol','protocol.json')]:
        inp(key,complex_root+name)
    inp('complex_base_protocol','work/signed/pr168-fusion-export-20261009T0848Z/protocol.json')
    bit_root = 'work/bit/pr168-lifetime-paired-both-20261009T0855/'
    inp('bit',bit_root+'selected/profile.json')
    inp('bit_frames',bit_root+'selected/frames.json')
    for key,name in [('bit_graph','graph_p12.json'),('bit_word','word_p12.json'),
                     ('bit_logical_frames','frames_p12.json'),('bit_kchron','kchron_p12.json'),
                     ('bit_logical_profile','profile_p12.json')]:
        inp(key,bit_root+'exports/'+name)
    for name in ('arcs','allbutone','protocol','merge'):
        inp('bit_'+name,bit_root+name+'.json')
    bit_package = 'agents/bit/candidates/binary-168-paired-lifetime-p12/'
    inp('bit_source_manifest',bit_package+'source-inputs.json')
    inp('bit_fixture_manifest',bit_package+'fixture-manifest.json')
    inp('frontier_claim','work/frontier/pr171-89d0c75/extracted/jon314159-integer-mult-bounds-89d0c75/research/paired-cube-refinement/certificate.json')
    manifest = json.loads((root/inputs['bit_source_manifest']['path']).read_text())
    source_roots = dict(source168='work/frontier/pr168-98c115b/extracted/eumemic-integer-mult-bounds-98c115b/',
                        source170='work/frontier/pr170-29892e2/extracted/huxint-integer-mult-bounds-29892e2/')
    for origin,base in source_roots.items():
        for relative,item in manifest[origin]['files'].items():
            actual = pin(base+relative)
            if actual['sha256'] != item['sha256'] or actual['bytes'] != item['bytes']:
                raise ValueError('Imported source manifest mismatch: '+relative)
            sources[origin+'/'+relative] = actual
    fixture_manifest = json.loads((root/inputs['bit_fixture_manifest']['path']).read_text())
    for relative,item in fixture_manifest['code'].items():
        actual=pin(bit_package+relative)
        if actual['sha256'] != item['sha256']:
            raise ValueError('Own finite binary checker source changed: '+relative)
        sources['own-bit/'+relative]=actual
    local_sources = [
        'agents/baseline/code/exact_aliased_core.py',
        'agents/signed/code/interval_moments.py',
        'agents/signed/code/screen_pr168_modules.py',
        'agents/signed/code/screen_signed_fusion.py',
        'agents/signed/code/check_pr165_signed_control.py',
        'agents/signed/code/continue_fused_pairs.py',
        'agents/placement/code/physical_search.py',
        'agents/placement/code/physical_exchanges.py',
        'agents/placement/code/physical_frontier.py',
        'agents/placement/code/physical_closure.py',
        'agents/placement/code/prepare_context.py',
        'agents/placement/code/prepare_alias_context.py',
        'agents/placement/code/freeze_frame_candidate.py']
    for path in local_sources:
        src('own-construction/'+Path(path).name,path)
    src('PR165-extended-plan','work/frontier/pr165-7518fed/extracted/chafreaky-integer-mult-bounds-7518fed/research/paired-cube-plateau-162/references/pr162/make_plan.py')
    src('PR163-balanced-proof','work/frontier/pr163-15c702a/extracted/chafreaky-integer-mult-bounds-15c702a/research/paired-cube-balanced-161/PROOF.md')
    src('PR163-original-47-proof','work/frontier/pr163-15c702a/extracted/chafreaky-integer-mult-bounds-15c702a/research/paired-cube-balanced-161/references/pr141/ORIGINAL-PROOF.md')
    # Verify every carried source pin, including the five licensed PR117 bytes
    # omitted by the historical 74-source arithmetic-only export.
    for item in sources.values():
        if pin(item['path']) != item:
            raise ValueError('Carried source changed: '+item['path'])
    inherited = json.loads((root/'agents/transfer/configs/integrated165-batch2.json').read_text())
    hypotheses = inherited['inherited_hypotheses'][:-1] + [
        'Eligible address primes retain every inherited finite denominator, ambient-Gram, projector and rank exclusion. New lifetime presentations require their separately audited exact unit witnesses; no claim that every prime above2^80 works is made.',
        'The conservative coarse ordinary external row reserve9909 and ordinary leaf reserve252 remain fully paid; new supplier selectors stay internally borrowed and restored rather than being inserted into external polynomial row stock.']
    config = dict(candidate_id='balanced-lifetime-fused-168-170-20261009',
        coarse='161677519/250000000000',atom='323158477/500000000000',
        complex_saving='617664283/1000000000000',phase_stop='1/1000000000',
        backoff='1/100000000',strict_weakening='1/10000000000',kappa='61728289/100000000000',
        bit_next_grid_step='1/1000000000000',complex_next_grid_step='1/1000000000000',
        comparison_public_head='89d0c75f8bf97131db21bc610e7546b699afcb9a',
        comparison_public_kappa='305534205135809/500000000000000000',required_publication_ratio='101/100',
        expected_bit_inventory=[72,22252,1600208,60],expected_bit_roles=[20492,18732,1760,1760,528],
        expected_bit_scalar_inventory=[22556,6624,8688,41288],
        expected_complex_inventory=[66,14843,978318,20],inputs=inputs,sources=sources,
        closure_requirements=[dict(section='sources',key=key,sha256=item['sha256'])
            for key,item in sources.items()],inherited_hypotheses=hypotheses,
        finite_prerequisites=[
            'Fresh selected binary lifetime word and complete arbitrary-dirty physical event program, both orientations and complemented bank reversal, integer/rational presentation ranks and all actual unit-prime witnesses; independently reviewed.',
            'Fresh complete signed singleton-fusion graph/closure/word/gauges, coherent alias and selected operation-frame plan, arbitrary-dirty response and exact input/output shear; independently reviewed.',
            'Literal reflected complex physical events, G-complement support and all returned role/target chains; independently reviewed.',
            'Fresh full source-bound arithmetic review and a live frontier refresh before any record/publication claim.'],
        recovery_scope='Full imported source closure includes the retained PR117 LICENSE,NOTICE,SOURCE.json,dag.json.gz,replayed.py. Frozen finite input bytes and own reproduction code are separately bound; finite correctness is not inferred from flags.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(config,sort_keys=True,indent=2)+'\n')
    print('PINNED '+config['candidate_id']+': '+str(len(inputs))+' inputs, '+str(len(sources))+' source records')


if __name__=='__main__':
    main()
