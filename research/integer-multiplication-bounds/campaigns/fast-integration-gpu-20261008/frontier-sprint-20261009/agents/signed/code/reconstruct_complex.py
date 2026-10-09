#!/usr/bin/env python3
"""Reconstruct the frozen lifetime-fused complex supplier from pinned sources.

RaD; OpenAI GPT-6.1 Sol assistance. Apache-2.0. The signed paired-cube
construction/compiler is credited to icekylinx; PR117, searched pair/nested
modules and physical checker to eumemic; extended closure to DaysSky;
compensated reuse to jamesyc; complete fusion antecedent to PR165/Chafik.
Original source LICENSE/NOTICE and AI-assistance disclosures are retained.
This portable wrapper never imports the RaD research workspace.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import importlib
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode=True

DIAGNOSTICS=('numerical_complex_root','status','gauge_selection','gauge_cost_rejections','gauge_trial_saving')
OLD_COUNT="assert record['selected_roles']==len(seen)==2970 and birth==Counter({18:2970})"
NEW_COUNT="assert record['selected_roles']==len(seen) and birth==Counter({int(k):c for k,c in record['selected_rank_histogram'].items()})"


def need(condition,message):
    if not condition:raise ValueError(message)


def normal(value):return json.loads(json.dumps(value))


def encoded(value):return (json.dumps(value,separators=(',',':'))+'\n').encode()


def mathematical_record(record):return {key:value for key,value in record.items() if key not in DIAGNOSTICS}


def full_fusion(graph,builder):
    """Exact positive-first signed fusion of face2/edge02/edge12 per port."""
    channels=('face2','edge02','edge12');roots=[]
    channel_order={'disjoint':0,'face0':1,'face1':2,'edge01':3}
    for cube in range(graph['v']//8):
        local=[root for root in graph['roots'] if root['kind']=='side' and root['targets'][0]//8==cube]
        broad=[root for root in local if root['channel'] not in channels]
        roots.extend(sorted(broad,key=lambda root:(-len(root['targets']),tuple(root['targets']),channel_order[root['channel']])))
        terms={(root['targets'][0],root['channel']):(root['node'],Fraction(root['coefficients'][0]))
               for root in local if root['channel'] in channels}
        for target in range(8*cube,8*cube+8):
            parts=[terms[target,channel] for channel in channels]
            need({abs(coef) for node,coef in parts}=={Fraction(1,2)},'unit fusion coefficient')
            positive=[node for node,coef in parts if coef>0];negative=[node for node,coef in parts if coef<0]
            need(bool(positive),'positive anchor');node=positive[0]
            for operand in positive[1:]:node=builder.add(node,operand)
            for operand in negative:node=builder.add(node,operand,-1)
            roots.append(dict(node=node,targets=[target],coefficients=['1/2'],kind='side',channel='complete_signed_fusion'))
    return dict(graph,args=builder.a,signs=builder.signs,
                roots=roots+[root for root in graph['roots'] if root['kind']=='center'])


def reconstruct(source,data,output):
    need(not sys.flags.optimize,'Run without -O: finite assertions must remain enabled')
    start=time.monotonic();source=source.resolve();data=data.resolve();output=output.resolve()
    manifest=json.loads((data/'manifest.json').read_text())
    need(manifest['schema']=='lifetime-fused-complex-v1','fixture manifest schema')
    for filename,pin in manifest['fixture_pins'].items():
        need(sha256((data/filename).read_bytes()).hexdigest()==pin['sha256'],'fixture pin: '+filename)
    for filename,digest in manifest['original_source_pins'].items():
        need(sha256((source/filename).read_bytes()).hexdigest()==digest,'original source pin: '+filename)
    sys.path.insert(0,str(source/'scripts'))
    from paired_cube.graph import Graph
    from paired_cube.modules import restricted_triples_from,pair_module_from,all_but_one_from
    from paired_cube.closure import compile_closure
    from paired_cube.gauges import select
    from paired_cube_physical import physical
    verifier=importlib.import_module('paired_cube.verify')
    for name in ('paired_cube.graph','paired_cube.modules','paired_cube.closure','paired_cube.gauges','paired_cube.verify','paired_cube_physical'):
        need(Path(sys.modules[name].__file__).resolve().is_relative_to(source),'unexpected cached module: '+name)
    src=source/'references/paired-cube/sources'
    builder=Graph(11)
    graph=builder.finish(restricted_triples_from(src/'h20_g1.json.gz',[0,1,2,3,4,5,6,7,8,9,16]),
                         pair_module_from(src/'pmod_G37_w02_5.6098194e-4.json',10),all_but_one_from(src/'qmod_nested_prefix.json',9))
    graph=full_fusion(graph,builder);graph['matching_frames']='coordinate'
    arcs=json.loads((data/'matching-arcs.json').read_text())
    baseline,witness=compile_closure(graph,arcs);record,word=select(graph,baseline,witness)
    need(normal(baseline)==json.loads((data/'baseline.json').read_text()),'fresh complete baseline')
    expected=json.loads((data/'profile-before.json').read_text())
    need(normal(mathematical_record(record))==mathematical_record(expected),'fresh chronological gauges and selected ledger')
    generated={'graph.json':graph,'frames.json':witness,'word.json':word}
    for filename,digest in manifest['expected_generated_sha256'].items():
        need(sha256(encoded(generated[filename])).hexdigest()==digest,'fresh graph/closure/word pin: '+filename)
    original_verifier=Path(verifier.__file__).read_bytes();verifier_text=original_verifier.decode()
    need(verifier_text.count(OLD_COUNT)==1,'declared local count adaptation does not apply')
    adapted=verifier_text.replace(OLD_COUNT,NEW_COUNT)
    namespace=dict(__name__='paired_cube.verify_actual_selected_count',__package__='paired_cube')
    exec(compile(adapted,'paired_cube.verify[actual-selected-count]','exec'),namespace)
    checks=namespace['verify'](graph,baseline,witness,word,record)
    frames=json.loads((data/'physical-frames.json').read_text());pairs=json.loads((data/'physical-pairs.json').read_text())
    paid=physical(graph,witness,word,record,frames,pairs)
    need(normal(paid)==json.loads((data/'profile.json').read_text()),'fresh complete coherent physical profile')
    output.mkdir(parents=True,exist_ok=False)
    files={filename:encoded(value) for filename,value in generated.items()}
    # Saved formatting is retained only after every mathematical field has
    # been freshly reconstructed and compared. Discovery floats are excluded
    # from the selected-ledger proof comparison; they prove no inequality.
    for filename in ('baseline.json','profile-before.json','physical-frames.json','physical-pairs.json','profile.json'):
        files[filename]=(data/filename).read_bytes()
    for filename,raw in files.items():(output/filename).write_bytes(raw);(output/filename).chmod(0o444)
    pins={filename:dict(sha256=sha256(raw).hexdigest(),bytes=len(raw)) for filename,raw in files.items()}
    protocol=dict(schema='lifetime-fused-finite-export-v1',input_pins=pins,source_head=manifest['source_head'],
                  original_source_pins=manifest['original_source_pins'],fixture_manifest_sha256=sha256((data/'manifest.json').read_bytes()).hexdigest(),
                  original_verifier_sha256=sha256(original_verifier).hexdigest(),adapted_verifier_sha256=sha256(adapted.encode()).hexdigest(),
                  verifier_adaptation=dict(old=OLD_COUNT,new=NEW_COUNT),constructor_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Fresh source modules/signed fusion, frozen legal carrier choices with complete acyclic closure, '
                        'fresh chronological gauges/literal word, and freshly checked coherent physical frames/pairs/full '
                        'paid inventory. Historical optimization search is not required or claimed; independent exact '
                        'dirty scalar, complemented reflection and all-size/analytic assembly remain separate checks.')
    (output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    result=dict(status='PASS_REGENERATED_FROZEN_COMPLEX_CONSTRUCTION',finite_checks=checks,paid=paid,
                c=record['c'],q=record['q'],matched=record['matched'],literal_M=record['total_M_operations'],
                logical_R=record['R'],physical_R=paid['physical_R'],input_pins=pins,
                original_verifier_sha256=protocol['original_verifier_sha256'],adapted_verifier_sha256=protocol['adapted_verifier_sha256'],
                verifier_adaptation=protocol['verifier_adaptation'],elapsed_seconds=time.monotonic()-start,
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,proof_scope=protocol['scope'])
    (output/'reconstruction.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS freshly reconstructed complex: c%d q%d arcs%d M%d logicalR%d physicalR%d W%d %.3fs' %
          (record['c'],record['q'],record['matched'],record['total_M_operations'],record['R'],paid['physical_R'],paid['W_per_vertex'],result['elapsed_seconds']))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root',type=Path,required=True)
    p.add_argument('--data-dir',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args();reconstruct(a.source_root,a.data_dir,a.output_dir)


if __name__=='__main__':main()
