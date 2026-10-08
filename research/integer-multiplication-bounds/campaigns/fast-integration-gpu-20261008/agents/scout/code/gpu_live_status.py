#!/usr/bin/env python3
"""Compact live status; exact sampled catalogue coverage from recorded RNG."""
import argparse
import csv
from datetime import datetime,timezone
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import subprocess
import time
import numpy as np

def tail(path):
    if not path.exists():return {}
    with path.open('rb') as stream:
        stream.seek(0,2);size=stream.tell();stream.seek(max(0,size-8192))
        lines=stream.read().splitlines()
    for line in reversed(lines):
        try:return json.loads(line)
        except (ValueError,UnicodeDecodeError):pass
    return {}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--work-root',type=Path,required=True)
    parser.add_argument('--interval',type=int,default=30);args=parser.parse_args()
    own=Path(__file__).parent
    modes={hashlib.sha256((own/'gpu_basis_parameter_discovery.py').read_bytes()).hexdigest():None,
           hashlib.sha256((own/'gpu_basis_parameter_vectorized.py').read_bytes()).hexdigest():np.int32}
    review_path=own.parent/'gpu-parameter-results/initial-candidate-rational-review.json'
    reviews={item['candidate_path']:item for item in json.loads(review_path.read_text()).get('records',[])} if review_path.exists() else {}
    coverage={};root=args.work_root/'derived/scout';root.mkdir(parents=True,exist_ok=True)
    while True:
        records=[]
        for protocol_path in sorted(root.glob('gpu-basis-*/protocol.json')):
            directory=protocol_path.parent
            try:protocol=json.loads(protocol_path.read_text())
            except ValueError:continue
            summary=directory/'summary.json'
            record=json.loads(summary.read_text()) if summary.exists() else tail(directory/'progress.jsonl')
            attempts=record.get('attempts',0);num=protocol['parameter_pairs'];batch=protocol['batch']
            key=str(directory)
            known=protocol['source_sha256'] in modes or protocol.get('parameter_rng_dtype') in ('int32','int64')
            dtype={'int32':np.int32,'int64':np.int64}.get(protocol.get('parameter_rng_dtype'),modes.get(protocol['source_sha256']))
            if key not in coverage and known:
                coverage[key]=[np.random.default_rng(protocol['seed']),np.zeros((2,num),bool),0,dtype]
            unique=None;per_source=None;replayed=0
            if key in coverage:
                rng,seen,done,dtype=coverage[key]
                while done<attempts//batch and not seen.all():
                    ids=rng.integers(0,num,size=batch) if dtype is None else rng.integers(0,num,size=batch,dtype=dtype)
                    seen[0,ids[::2]]=True;seen[1,ids[1::2]]=True;done+=1
                coverage[key][2]=done;unique=int(np.count_nonzero(seen.any(axis=0)));per_source=seen.sum(axis=1).tolist();replayed=done*batch
            weight_count=None;weight_unique=None;weight_per_source=None
            class_path=directory/'source-weight-class-index.json'
            if class_path.exists() and key in coverage:
                classes=json.loads(class_path.read_text())
                if classes['protocol_sha256']==hashlib.sha256(protocol_path.read_bytes()).hexdigest():
                    class_ids=np.asarray(classes['pair_index_to_weight_class'],dtype=np.int32)
                    assert len(class_ids)==num
                    weight_count=classes['source_weight_classes']
                    weight_unique=len(np.unique(class_ids[seen.any(axis=0)]))
                    weight_per_source=[len(np.unique(class_ids[row])) for row in seen]
            elif protocol.get('source_weight_classes_deduplicated') and key in coverage:
                weight_count=num;weight_unique=unique;weight_per_source=per_source
            candidates=[]
            for path in sorted(directory.glob('candidate-*.json')):
                value=json.loads(path.read_text())
                candidates.append({k:value.get(k) for k in ('source_id','beta23','beta25','entropy','baseline_entropy','runs','sample_rational_check')})
                candidates[-1]['path']=str(path);candidates[-1]['classification']='SAMPLE DISCOVERY ONLY'
                weight_key=[]
                for h in (23,25):
                    b=value[f'beta{h}'];beta=Fraction(b['numerator'],b['denominator'])
                    outside=-beta*(9*beta-1)/(2*(1-h*beta))
                    weight_key.append({'numerator':outside.numerator,'denominator':outside.denominator})
                candidates[-1]['source_weight_class']=weight_key
                if str(path) in reviews:
                    review=reviews[str(path)]
                    actual_hash=hashlib.sha256(path.read_bytes()).hexdigest()
                    if actual_hash==review['candidate_sha256']:
                        candidates[-1]['sample_rational_check']=review['saved_prime_matches_q']
                        candidates[-1]['classification']='SAMPLE DISCOVERY ONLY' if review['saved_prime_matches_q'] else 'REJECTED BAD-PRIME SAMPLE'
                        candidates[-1]['independent_rational_review']=str(review_path)
            records.append({'run_id':directory.name,'state':'complete' if summary.exists() else 'running','device':protocol['device'],'seed':protocol['seed'],'utc':record.get('utc',record.get('finish_utc')),'attempts_may_repeat':attempts,'parameter_catalogue_pairs':num,'tested_canonical_beta_pairs':unique,'tested_pairs_by_source_fixture':per_source,'source_weight_catalogue_classes':weight_count,'tested_source_weight_classes':weight_unique,'tested_weight_classes_by_source_fixture':weight_per_source,'coverage_method':'Exact NumPy RNG index replay to actual recorded batch count; stops once all catalogue indices observed. Weight classes use exact rational conjugacy. No matrix replay.','coverage_rng_blocks_replayed':replayed,'elapsed_seconds':record.get('elapsed_seconds',record.get('elapsed')),'next_batch':None if summary.exists() else {'size':batch,'varying_parameter_pairs':True,'source_fixtures':2,'fields':len(protocol.get('primes',[protocol.get('prime')])), 'mutations':'cycle1,0,0,2,0,0'},'sample_candidates':candidates})
        gpu=[];applications=[]
        for query,target in [('index,uuid,utilization.gpu,memory.used',gpu),('pid,gpu_uuid,process_name',applications)]:
            kind='gpu' if target is gpu else 'compute-apps'
            response=subprocess.run(['nvidia-smi',f'--query-{kind}={query}','--format=csv,noheader,nounits'],capture_output=True,text=True)
            if response.returncode==0:
                for row in csv.reader(io.StringIO(response.stdout)):
                    target.append([x.strip() for x in row])
        processes=[]
        for pid,uuid,name in applications:
            try:argv=(Path('/proc')/pid/'cmdline').read_bytes().decode().split('\0')
            except (OSError,UnicodeDecodeError):continue
            if not any('gpu_basis_parameter_' in x for x in argv):continue
            device=int(argv[argv.index('--device')+1]) if '--device' in argv else None
            processes.append({'pid':int(pid),'gpu_uuid':uuid,'device':device,'script':next(x for x in argv if 'gpu_basis_parameter_' in x)})
        value={'updated_utc':datetime.now(timezone.utc).isoformat(),'status_scope':'Actual sampled parameter discovery only; no full family, local frame, bridge or kappa certificate.','completed_experiments':sum(x['state']=='complete' for x in records),'running_experiments':sum(x['state']=='running' for x in records),'gpu_observation':[{'device':int(x[0]),'uuid':x[1],'utilization_percent':int(x[2]),'memory_mib':int(x[3])} for x in gpu],'actual_gpu_processes':processes,'experiments':records}
        temporary=root/'live-status.json.tmp';temporary.write_text(json.dumps(value,indent=2)+'\n');temporary.replace(root/'live-status.json')
        time.sleep(args.interval)

if __name__=='__main__':main()
