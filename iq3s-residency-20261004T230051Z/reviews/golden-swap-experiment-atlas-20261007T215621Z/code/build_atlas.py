#!/usr/bin/env python3
"""CPU-only retained-evidence derivation. Never starts inference or executes an old campaign runner."""
import argparse
import collections
import hashlib
import json
import time
import numpy as np
from common import *
from normalize import *

def write_payload(root,rel,value):
    save(root/rel,value)
    return '/evidence/browser-v1/'+str(rel)+'.gz'

def prepare_startup(run,s,layers,pairs):
    if run['model'].endswith('IQ3_S'):
        s['process_startup']={'state':'NOT_RECONSTRUCTED','reason':'IQ3_S recorded decode initial state is exact; a matching immutable startup profile revision is not attested here.'}
        return
    capacities=[x['slots'] for x in s['capacity']];selected=[]
    for dev in range(2):
        rows=[(rank,l,e) for rank,(l,e) in enumerate(pairs) if (l>=24)==bool(dev)]
        selected.extend((dev,slot,rank,l,e) for slot,(rank,l,e) in enumerate(rows[:capacities[dev]]))
    initial=set((l,x[3]) for l,d in enumerate(layers) for x in d['generations'] if x[1]==0)
    loaded=set((l,e) for _,_,_,l,e in selected)
    expectedclasses=[collections.Counter(layers[l]['byte_class'] for dev,slot,rank,l,e in selected if dev==d) for d in range(2)]
    observedclasses=[{int(k):v for k,v in x['classes'].items()} for x in s['capacity']]
    assert all(dict(c)==o for c,o in zip(expectedclasses,observedclasses)), 'Startup profile-prefix physical class parity'
    first={};counts=collections.Counter()
    for d in layers:
        for ev,e,*cs in d['demand']:
            first.setdefault((d['layer'],e),ev);counts[d['layer'],e]+=sum(cs[:4])
    for l,d in enumerate(layers):
        d['process_startup_columns']=['expert','slot','profile_rank','first_measured_demand','present_at_decode_boundary']
        d['process_startup']=[[e,slot,rank,first.get((l,e)),(l,e) in initial] for dev,slot,rank,ll,e in selected if ll==l]
    horizons=[1,4,16,64,256,s['windows']]
    s['process_startup']={'state':'SOURCE_RECONSTRUCTED_PROFILE_PREFIX','profile_sha256':'8f59b4aa8873209dff11c11e37bcda9529a1335b724a1afeea37bf6388975baf',
        'snapshot':'Process cache fill before warmup/prefill; not the tape decode-boundary initial state.',
        'physical_class_parity':True,'overlap_with_decode_initial':len(initial&loaded),'jaccard_decode_initial':len(initial&loaded)/len(initial|loaded),
        'replaced_before_decode':len(loaded-initial),'measured_demand_quality':[{'windows':h,'demanded':sum(first.get(k,10**12)<h*48 for k in loaded),'total':len(loaded)} for h in horizons],
        'prior_profile_training':'The exact ordering and source code are retained. The original routing dataset used to create this shared profile is not attested; no Q4-specific learning claim.'}

def reconcile_summary(run,s):
    mismatches=[]
    for k in ['windows','local','cpu','mapped']:
        old=run.get(k)
        if old is not None and run['kind']!='SIMULATION' and int(old)!=int(s[k]):mismatches.append({'field':k,'derived':s[k],'retained':old})
    # Old payload totals may include mandatory restoration; retain separate definitions.
    b=run.get('copy_bytes');restoration=17305600 if s['spare_donors'] else 0
    if b is not None and run['kind']!='SIMULATION' and abs(b-s['copy_bytes'])>2 and abs(b-s['copy_bytes']-restoration)>2:
        mismatches.append({'field':'copy_bytes','derived_ordinary':s['copy_bytes'],'retained':b,'possible_restoration':restoration})
    return {'run':run['id'],'state':'PASS' if not mismatches and s['validation']['state']=='PASS' else 'FAIL',
            'journal':s['validation'],'summary_mismatches':mismatches,'restoration_bytes_separate':restoration,
            'windows':s['windows'],'entries':s['entries'],'generations':s['generations'],'source_hashes':len(s['provenance'])}

def main():
    q=argparse.ArgumentParser(description=__doc__)
    q.add_argument('--output',type=Path,default=work_root()/'derived/browser-v1')
    q.add_argument('--selection',type=Path,default=REVIEW/'configs/source-selection.json')
    q.add_argument('--only',help='Bounded regeneration of one run ID into a fresh output directory')
    q.add_argument('--resume',action='store_true',help='Validate and reuse complete derived run files in this output, never originals')
    q.add_argument('--profile',type=Path,help='Pinned original profile binary; otherwise use its retained pair snapshot')
    q.add_argument('--map-path',action='append',default=[],help='Relocate a recorded absolute prefix: OLD=NEW')
    args=q.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    selection=load(args.selection)
    if selection.get('selection_archive'):
        archive=REVIEW/selection['selection_archive']
        import gzip,hashlib
        with gzip.open(archive,'rb') as f:raw=f.read()
        assert hashlib.sha256(raw).hexdigest()==selection['uncompressed_sha256']
        selection=json.loads(raw)
    runs=selection['runs'];audits=[];sources={};start=time.monotonic()
    mappings=[v.split('=',1) for v in args.map_path]
    def relocated(value):
        for old,new in sorted(mappings,key=lambda v:-len(v[0])):
            if isinstance(value,str) and (value==old or value.startswith(old+'/')):return new+value[len(old):]
        return value
    for r in runs:
        for key in ['raw_dir','tape_path','trace_prefix','simulation_path']:
            if key in r:r[key]=relocated(r[key])
    profile=args.profile or Path(load(REVIEW/'input-manifest.json')['profile']['path'])
    if profile.exists():
        assert digest(profile)=='8f59b4aa8873209dff11c11e37bcda9529a1335b724a1afeea37bf6388975baf'
        pairs=profile_pairs(profile);profile_snapshot={'provenance':reference(profile),'pairs':pairs,'order':'Preserved file rank; not sorted at runtime.'}
    else:
        profile_snapshot=load(REVIEW/'evidence/browser-v1/startup-profile.json.gz');pairs=profile_snapshot['pairs']
        assert profile_snapshot['provenance']['sha256']=='8f59b4aa8873209dff11c11e37bcda9529a1335b724a1afeea37bf6388975baf'
    q4_blobs=np.asarray(load(REVIEW/'fixtures/q4-blob-bytes.json')['bytes'],dtype=np.uint64)
    save(args.output/'startup-profile.json',profile_snapshot)
    chosen=[r for r in runs if r['detail'] and (not args.only or r['id']==args.only)]
    lifecycle_total=0
    for i,r in enumerate(chosen):
        f=args.output/'runs'/r['id']/'summary.json';done=args.output/'runs'/r['id']/'complete.json'
        status('DERIVE',f"run {i+1}/{len(chosen)} {r['label']}; elapsed {time.monotonic()-start:.0f}s",completed=i,total=len(chosen))
        try:
            if args.resume and done.exists():
                s=load(f);audit=load(done)['audit']
                assert all(Path(p['path']).exists() and reference(p['path'])['sha256']==p['sha256'] for p in s['provenance'])
            else:
                s,layers=derive(r,q4_blobs)
                prepare_startup(r,s,layers,pairs)
                audit=reconcile_summary(r,s)
                # An analysis discrepancy is retained, never promoted to a valid visual trajectory.
                if audit['state']!='PASS':
                    save(args.output/'failures'/(r['id']+'.json'),audit)
                    r['detail']=False;r['evidence_quality']='detail reconstruction failed; retained aggregate only'
                    audits.append(audit);print('DERIVATION_FAILURE',r['id'],audit,flush=True);continue
                for d in layers:write_payload(args.output,Path('runs')/r['id']/f'layer-{d["layer"]}.json',d)
                write_payload(args.output,Path('runs')/r['id']/'summary.json',s)
                save(done,{'audit':audit})
            for ref in s['provenance']:sources[ref['path']]=ref
            lifecycle_total+=s['generations'];audits.append(audit)
            r.update(windows=s['windows'],resident_slots=s['initial_residents'],promotions=s['admissions'],evictions=s['evictions'],
                copy_bytes=s['copy_bytes'],local=s['local'],cpu=s['cpu'],mapped=s['mapped'],local_pct=100*s['local']/s['entries'],
                summary_url='/evidence/browser-v1/runs/'+r['id']+'/summary.json.gz',
                layer_url='/evidence/browser-v1/runs/'+r['id']+'/layer-{layer}.json.gz',generation_count=s['generations'])
            tape_ref=next((p for p in s['provenance'] if p['path']==r.get('tape_path')),None)
            if tape_ref:r['alignment_id']='tape:'+tape_ref['sha256']
            else:r['alignment_id']='trace:'+r.get('trace_prefix','unknown')
            print('RECONCILED',r['label'],s['entries'],s['generations'],flush=True)
        except Exception as ex:
            import traceback
            failure={'run':r['id'],'state':'EXCEPTION','error':str(ex),'traceback':traceback.format_exc()}
            save(args.output/'failures'/(r['id']+'.json'),failure);audits.append(failure)
            r['detail']=False;r['evidence_quality']='reconstruction exception; aggregate retained'
            print('DERIVATION_EXCEPTION',r['id'],str(ex),flush=True)
    if args.only:
        save(args.output/'bounded-regeneration.json',{'audits':audits});return
    for r in runs:
        r['future']=bool('ORACLE' in r['policy'] or r['policy'].startswith(('PLANNER','future','F64','F256','FF','64F','64/','full')) or r['campaign'].startswith('golden-swap-phase4'))
        if r['policy']=='NATURAL_CURRENT':r['future']=False
    catalog={'schema':1,'title':'Golden Swap Experiment Atlas','experiments':selection['experiments'],
             'runs':[{k:v for k,v in r.items() if k not in ['summary_record']} for r in runs],
             'counts':{'experiments':len(selection['experiments']),'runs':len(runs),'detailed_runs':sum(bool(r.get('summary_url')) for r in runs),
                       'expert_lifecycles':lifecycle_total},'selection':selection['detail_selection']}
    save(REVIEW/'site/data/catalog.json',catalog)
    save(REVIEW/'results/derivation-audit.json',{'state':'PASS' if all(a['state']=='PASS' for a in audits) else 'PARTIAL_WITH_RETAINED_FAILURES',
        'runs':audits,'elapsed_cpu_wall_s':time.monotonic()-start,'gpu_inference_runs':0,'counts':catalog['counts']})
    save(REVIEW/'input-manifest.json',{'sources':list(sources.values()),'profile':profile_snapshot['provenance'],'immutable':True})
    counter_source=Path(selection['counter_source'])
    if not counter_source.exists():counter_source=REVIEW/'evidence/browser-v1/catalog-counters.json.gz'
    save(args.output/'catalog-counters.json',load(counter_source))
    status('DERIVATION_DONE',f"{catalog['counts']} complete; raw inputs unchanged")

if __name__=='__main__':main()
