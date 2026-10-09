#!/usr/bin/env python3
"""Fresh PR168 scalar core with paid PR170 output merging and lifetime cuts.

Neither exported frame IDs nor physical aliases are transplanted. Graph,
carrier matching, rational frames, gauges, chronology and compensated aliases
are rebuilt against the selected scalar module. Full register-chain rows and
all source/dirty F2 variables are checked before native moment certification.
Inherited Apache-2.0 source and assistance credits remain in their snapshots.
New bounded glue prepared for RaD/hipotures with OpenAI assistance.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode=True
from bit_168_constructions import nested_prefix_depth, check_module, moments

SPECS=(('face1','edge01'),('face2','edge02'))


def need(ok,msg):
    if not ok:raise ValueError(msg)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def merged_graph(gen,specs,allbut):
    """Literal support-disjoint channel sums; retain original source K."""
    module=gen.HERE/'data'/gen.MODULES[12]
    builder=gen.BitGraph(12)
    original=builder.finish(json.loads(module.read_text()),allbut)
    need(gen.check_decoder(original)==0,'original exact decoder')
    groups={channel:k for k,spec in enumerate(specs) for channel in spec}
    found,keep,centers={},[],[]
    for root in original['roots']:
        if root['kind']=='center':centers.append(root)
        elif root['channel'] in groups:
            need(len(root['targets'])==1,'only singleton roots merge')
            key=groups[root['channel']],root['targets'][0],root['channel']
            need(key not in found,'unique singleton channel')
            found[key]=root['node']
        else:keep.append(root)
    merged=[];multiplicity=Counter()
    for group,target in sorted({(k,t) for k,t,_ in found}):
        left,right=(found[group,target,c] for c in specs[group])
        need(not builder.s[left]&builder.s[right],'support-disjoint merged inputs')
        node=builder.add(left,right)
        need(builder.s[node]==builder.s[left]^builder.s[right],'exact merged contribution')
        merged.append(dict(node=node,targets=[target],kind='side',channel='paired'+str(group)))
        multiplicity[target]+=1
    need(multiplicity==Counter({t:len(specs) for t in range(original['v'])}),'all selected pairs merged')
    graph=dict(original,roots=keep+merged+centers,args=builder.a)
    need(graph['partner_mix']==original['partner_mix'],'source partner mix retained')
    need(gen.check_decoder(graph)==0,'merged complete decoder')
    return graph,dict(original_roots=len(original['roots']),merged_roots=len(graph['roots']),
                      new_additions=len(graph['args'])-len(original['args']),specs=specs,
                      pair_module_sha256=sha(module))


def main():
    need(not sys.flags.optimize,'assertions enabled')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source168',type=Path,required=True)
    ap.add_argument('--source170',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--variant',choices=['paired-both','face1-only','paired-both-depth2'],required=True)
    ap.add_argument('--rounds',type=int,default=4)
    ap.add_argument('--seed',type=int,default=20261009)
    args=ap.parse_args();s168=args.source168.resolve();s170=args.source170.resolve()
    need(not args.output.exists(),'fresh attempt required');args.output.mkdir(parents=True)
    export=args.output/'exports';export.mkdir();started=time.monotonic()
    paths={
        'source168':['research/paired-cube-bit/paired_cube_bit_word.py',
                     'research/paired-cube-bit/check_paired_cube_bit.py',
                     'research/paired-cube-bit/data/pair_module_p12.json'],
        'source170':['research/paired-cube-lifetime/bit.py','research/paired-cube-lifetime/parameters.py',
                     'research/paired-cube-lifetime/bit_merge.py','research/paired-cube-bit/check_paired_cube_bit.py',
                     'scripts/audit_community_candidate.py','scripts/certify.py',
                     'scripts/paired_cube_network.py','scripts/structured_bulk_assembly.py']}
    protocol=dict(source168_commit='98c115b53742b6613ad630de4d493f37b0119da7',
                  source170_commit='29892e2fe8a90714ef61bd8cbfb1a74bec6f8fd4',
                  variant=args.variant,rounds=args.rounds,seed=args.seed,
                  started_utc=datetime.now(timezone.utc).isoformat(),workers=1,numerical_library_threads=1,
                  program_sha256=sha(Path(__file__)),
                  source_files={key:{p:dict(bytes=(root/p).stat().st_size,sha256=sha(root/p)) for p in paths[key]}
                                for key,root in [('source168',s168),('source170',s170)]},
                  scope='Actual source168 graph regenerated; source170 frame/lifetime method, fresh aliases only.')
    need(sha(s168/'research/paired-cube-bit/check_paired_cube_bit.py')==
         sha(s170/'research/paired-cube-bit/check_paired_cube_bit.py'),'same exact source checker format')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2,sort_keys=True)+'\n')
    gen=load('actual168_generator',s168/'research/paired-cube-bit/paired_cube_bit_word.py')
    sys.path.insert(0,str(s170/'research/paired-cube-bit'))
    lifetime=load('retained170_lifetime',s170/'research/paired-cube-lifetime/bit.py')
    depth=2 if args.variant=='paired-both-depth2' else 1
    allbut=nested_prefix_depth(10,depth);check_module(allbut)
    need(nested_prefix_depth(10,1)==gen.nested_prefix(10),'actual source168 depth-one module')
    specs=SPECS[:1] if args.variant=='face1-only' else SPECS
    graph,merge=merged_graph(gen,specs,allbut)
    profile,witness=gen.compile_word(graph,frozen=None,plain_k=8)
    gauges,internal,target,word=gen.select_gauges(graph,profile,witness)
    row=gen.profile(profile,gauges,internal,target)
    arcs=sorted([x-1,witness['usecode'][u]] for x,u in witness['arcs'].items())
    exp=gen.export(12,graph,profile,witness,word,row);exp['profile']=row
    for name,data in exp.items():(export/(name+'_p12.json')).write_text(gen.dumps(data))
    (args.output/'arcs.json').write_text(gen.dumps(arcs))
    (args.output/'allbutone.json').write_text(gen.dumps(allbut))
    (args.output/'merge.json').write_text(json.dumps(merge,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(stage='actual merged graph exported',seconds=time.monotonic()-started,
                         R=row['R'],W=row['W_per_vertex'],matched=row['matched'],gauges=row['selected_rank_histogram'])),flush=True)
    experiment=lifetime.Experiment(baseline=export,p=12,alpha=.000617399518,quiet=True)
    before=experiment.profile()
    experiment.optimize(rounds=args.rounds,seed=args.seed)
    before_alias=experiment.profile()
    experiment.match_pairs(gauge_rank=21)
    experiment.optimize(rounds=args.rounds,seed=args.seed+1)
    accepted=experiment.save(args.output/'selected',replay=True)
    parameters=load('retained170_native_parameters',s170/'research/paired-cube-lifetime/parameters.py')
    native=parameters.counts(accepted)
    cert=parameters.select_supplier(native,bit=True)
    atom=parameters.choose_atom(cert['saving'])
    result=dict(status='SOURCE_BOUND_FINITE',protocol=protocol,merge=merge,
                before_profile=before,before_alias_profile=before_alias,profile=accepted,
                screening=moments(accepted),native_moment=cert,paid_atom=atom,
                plan_sha256=sha(args.output/'selected/frames.json'),
                profile_sha256=sha(args.output/'selected/profile.json'),
                exported_files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(export.iterdir())},
                wall_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                exclusions=['independent full reflected scalar/frame/alias replay','exact selected projector prime audit',
                            'same-source final complex/transfer/row-stock assembly'])
    (args.output/'result.json').write_text(json.dumps(parameters.js(result),indent=2,sort_keys=True)+'\n')
    (args.output/'moment.json').write_text(json.dumps(parameters.js(cert),indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'],R=accepted['physical_R'],W=accepted['W_per_vertex'],
                         coarse=str(cert['saving']),ordinary=str(atom['effective_saving']),
                         frames=accepted['changed_operation_frames'],pairs=accepted['pairs'],
                         seconds=result['wall_seconds'])),flush=True)


if __name__=='__main__':main()
