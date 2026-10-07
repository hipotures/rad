"""Bounded P0 paired fresh starts: exactly three attempts per workload/profile/policy."""
import argparse, hashlib, json, pathlib, time
from lab import ROOT, Session, load, save, deadline
ap=argparse.ArgumentParser();ap.add_argument('--family',choices=['standard']);ap.add_argument('--profile',choices=['32k','128k']);ap.add_argument('--diagnostic',action='store_true');a=ap.parse_args()
base=ROOT/'experiments/E027-pool-baseline';manifest=base/'workloads/manifest.json'
cells=[(f,p) for f in ['standard'] for p in ['32k','128k'] if (not a.family or f==a.family) and (not a.profile or p==a.profile)]
for ci,(family,profile) in enumerate(cells):
    for n in [1,2,3]:
        order=['default','sleep100us']
        if (ci+n)%2==0:order.reverse()
        for role in order:
            variant='p1-pool-default' if role=='default' else 'p1-baseline'
            path=base/'v1'/family/profile/role/f'rep{n}'
            if path.exists():
                if (path/'results.json').exists():print('PRESERVED_SKIP',path,flush=True);continue
                raise RuntimeError('Incomplete existing attempt requires separate repair version: '+str(path))
            save(path/'protocol.json',{'parent_protocol':str(base/'protocol.json'),'family':family,'profile':profile,'role':role,'replicate':n,'pair_order':order,'attempts_per_point_maximum':3})
            with Session(variant,profile,path) as s:
                warm=s.request('warmup','warmup','warmup',manifest)
                assert warm['state']=='VALID',warm.get('invalid_reasons')
                r=s.request(f'{family}-{profile}-run{n}','run','measured',manifest)
                ids=path/'raw/output-ids-request2.json'
                if ids.exists():
                    values=load(ids);r['actual_output_ids_path']=str(ids);r['output_ids_sha256']=hashlib.sha256(ids.read_bytes()).hexdigest();r['captured_output_ids_count']=len(values)
                    r['output_ids']='ACTUAL_ENGINE_TOKEN_IDS_CAPTURED_AT_FRONTEND'
                else:r.setdefault('invalid_reasons',[]).append('MISSING_OUTPUT_ID_CAPTURE');r['state']='INVALID_PROTOCOL'
                incoming=load(path/'raw/output-ids-input-request2.json')
                r['service_actual_input_ids']=incoming
                if incoming['sha256']!=r['payload']['input_ids_sha256']:
                    r.setdefault('invalid_reasons',[]).append('ACTUAL_INPUT_IDS_HASH_MISMATCH');r['state']='INVALID_PROTOCOL'
                if r.get('actual_output_tokens') and r.get('captured_output_ids_count')!=r['actual_output_tokens']:
                    r.setdefault('invalid_reasons',[]).append('OUTPUT_ID_COUNT_MISMATCH');r['state']='INVALID_PROTOCOL'
                save(path/'raw/run.json',r)
                save(path/'results.json',{'run':r,'warmup':warm,'fixed_length_valid':r['state']=='VALID','no_retry':True})
            save(base/'progress.json',{'last':str(path),'updated_epoch':time.time(),'remaining_hours':(deadline()-time.time())/3600})
print('P1_REQUESTS_COMPLETE',flush=True)
