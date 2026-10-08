#!/usr/bin/env python3
"""Batched legal old/minimum coframe assignment discovery on exact cost tables.

Every implication is closed before scoring. Four-state costs already include
physical multiplicities; no link count or original-envelope proxy is used.
GPU scores select hypotheses only. Literal mixed-word compilation, native
CRT, source/center/DATA and conditional assembly remain independent gates.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import time

import cupy as cp
import numpy as np


CLOSURE = r'''
extern "C" __global__ void close(int*x,const int*a,const int*b,int nv,int ne,int np,int*changed){
 int z=blockIdx.x*blockDim.x+threadIdx.x;if(z>=ne*np)return;
 int pop=z/ne,e=z%ne;if(x[pop*nv+a[e]] && !x[pop*nv+b[e]]){
  atomicExch(x+pop*nv+b[e],1);atomicExch(changed,1);
 }
}
'''


def stamp():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(doc):
    variables = doc['variables']; index = {fid: i for i, fid in enumerate(variables)}
    n = len(variables); linear = np.zeros(n); constant = 0.; pairs = []
    unit = next(Decimal(r['states']['00']['screen_cost']) / r['count']
                for r in doc['rows'] if r['states']['00']['legal']
                and r['states']['00']['histogram'] == {'1': 1})
    for r in doc['rows']:
        a, b = index.get(r['a']), index.get(r['b'])
        d = r['states']
        assert all(d[s]['legal'] for s in ('00', '01', '11'))
        with localcontext() as context:
            context.prec = 110
            c00, c01, c11 = (Decimal(d[s]['screen_cost']) for s in ('00', '01', '11'))
            c10 = Decimal(d['10']['screen_cost']) if d['10']['legal'] else c11-c01+c00
            delta = c11-c10-c01+c00
        if a is None and b is None:
            constant += float(c11)
        elif a is None:
            constant += float(c10); linear[b] += float(c11-c10)
        elif b is None:
            constant += float(c01); linear[a] += float(c11-c01)
        else:
            constant += float(c00); linear[a] += float(c10-c00); linear[b] += float(c01-c00)
            if abs(delta) > Decimal('1e-70'):
                assert delta > 0, 'Unexpected negative interaction; preserve model scope'
                pairs.append((a, b, float(delta)))
    for key, count in doc['side_counts'].items():
        fid = int(key); minimum, old = doc['variable_states'][fid]
        r0, r1 = doc['probe_frame_descriptors'][minimum][0], doc['probe_frame_descriptors'][old][0]
        if fid in index:
            constant += float(unit * (doc['h']-r0) * count)
            linear[index[fid]] += float(unit * (r0-r1) * count)
        else:
            assert minimum == old
            constant += float(unit * (doc['h']-r1) * count)
    implications = [(index[a], index[b]) for a, b in doc['implications']
                    if a in index and b in index]
    return variables, linear, constant, pairs, implications, float(unit)


def cpu_energy(doc, variables, state, unit):
    lookup = dict(zip(variables, map(int, state)))
    terms = []
    for row in doc['rows']:
        key = str(lookup.get(row['a'], 1)) + str(lookup.get(row['b'], 1))
        cell = row['states'][key]; assert cell['legal']
        terms.append(float(cell['screen_cost']))
    for key, count in doc['side_counts'].items():
        fid = int(key); chosen = doc['variable_states'][fid][lookup.get(fid, 1)]
        terms.append(unit * (doc['h']-doc['probe_frame_descriptors'][chosen][0]) * count)
    assert all(not lookup.get(a, 1) or lookup.get(b, 1) for a, b in doc['implications'])
    return math.fsum(terms)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--table', type=Path, required=True)
    ap.add_argument('--device', type=int, choices=(0, 1), required=True)
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--batches', type=int, default=8192)
    ap.add_argument('--population', type=int, default=256)
    ap.add_argument('--initial', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args(); assert not args.output.exists(); args.output.mkdir(parents=True)
    doc = json.loads(args.table.read_text())
    variables, linear, constant, pairs, implications, unit = prepare(doc)
    n, npop, ne = len(variables), args.population, len(implications)
    protocol = {'utc': stamp(), 'classification': 'DISCOVERY LEGAL MIXED-COFRAME FLAGS',
                'h': doc['h'], 'basis': doc['basis'], 'table_sha256': digest(args.table),
                'parent_word_sha256': doc['parent_word_sha256'], 'physical_R': doc['physical_R'],
                'physical_rank_mass': doc['physical_rank_mass'], 'device': args.device,
                'seed': args.seed, 'population': npop, 'batches': args.batches,
                'variables': n, 'implications': ne, 'positive_interactions': len(pairs),
                'weight_one': unit, 'source_sha256': digest(__file__),
                'objective': 'Exact table multiplicities and side singleton unaries, numerical discovery only',
                'scope': 'No claim of optimum, no original-envelope floor, no accepted exponent.'}
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    if args.initial:
        protocol['initial_flags_sha256'] = digest(args.initial)
        (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    cp.cuda.Device(args.device).use(); cp.get_default_memory_pool().set_limit(size=8*1024**3)
    rng = cp.random.RandomState(args.seed); close = cp.RawKernel(CLOSURE, 'close')
    ia = cp.asarray([a for a,b in implications], cp.int32)
    ib = cp.asarray([b for a,b in implications], cp.int32)
    u = cp.asarray(linear); pa = cp.asarray([a for a,b,d in pairs], cp.int32)
    pb = cp.asarray([b for a,b,d in pairs], cp.int32); delta = cp.asarray([d for a,b,d in pairs])
    old = cp.ones((npop,n),cp.int32); minimum = cp.zeros((npop,n),cp.int32)
    score = lambda x: constant+x@u+cp.sum(x[:,pa]*x[:,pb]*delta,axis=1)
    control = score(old)[0].item(); minimum_control = score(minimum)[0].item()
    for state, target in [(np.ones(n,np.int32), control),(np.zeros(n,np.int32),minimum_control)]:
        assert abs(cpu_energy(doc,variables,state,unit)-target)<1e-7
    best_score, best = control, old[0].copy()
    if args.initial:
        initial = json.loads(args.initial.read_text())
        assert initial['table_sha256'] == protocol['table_sha256']
        assert initial['parent_word_sha256'] == protocol['parent_word_sha256']
        selected_minimum = set(initial['minimum_frame_ids'])
        state=np.asarray([int(f not in selected_minimum) for f in variables],np.int32)
        value=cpu_energy(doc,variables,state,unit)
        assert abs(value-initial['screen_cost'])<1e-7
        best_score,best=value,cp.asarray(state)
    fingerprint_source = r'''
    extern "C" __global__ void fingerprints(const int*x,int nv,unsigned long long*out){
      int pop=blockIdx.x;unsigned long long z=0;__shared__ unsigned long long parts[128];
      for(int j=threadIdx.x;j<nv;j+=blockDim.x)if(x[pop*nv+j]){
        unsigned long long q=(unsigned long long)(j+1)+0x9e3779b97f4a7c15ULL;
        q=(q^(q>>30))*0xbf58476d1ce4e5b9ULL;q=(q^(q>>27))*0x94d049bb133111ebULL;
        z^=q^(q>>31);
      }
      parts[threadIdx.x]=z;__syncthreads();
      for(int k=64;k;k>>=1){if(threadIdx.x<k)parts[threadIdx.x]^=parts[threadIdx.x+k];__syncthreads();}
      if(threadIdx.x==0)out[pop]=parts[0];
    }
    '''
    fingerprint=cp.RawKernel(fingerprint_source,'fingerprints');seen_fingerprints=set()
    fingerprints_output=cp.empty(npop,cp.uint64)
    started = time.monotonic(); closed_rounds=0
    candidates = 0; scale = max(float(np.abs(linear).mean()), unit)
    with (args.output/'progress.jsonl').open('x') as log:
        for batch in range(args.batches):
            temperature = scale * (0.03,0.1,0.3,1.,3.,10.,30.,100.)[batch%8]
            preferred = linear if batch%3 == 0 else cp.asnumpy(u + cp.bincount(
                cp.concatenate((pa,pb)), weights=cp.concatenate((delta*best[pb],delta*best[pa])),minlength=n))
            noise = rng.standard_normal((npop,n),dtype=cp.float32)
            states = (noise*temperature + cp.asarray(preferred)[None,:] < 0).astype(cp.int32)
            if batch%5 == 0:
                probability = (batch%101)/100.
                states = (rng.random_sample((npop,n),dtype=cp.float32)<probability).astype(cp.int32)
            states[0] = best
            rounds=0
            while True:
                changed = cp.zeros(1,cp.int32)
                close(((ne*npop+255)//256,), (256,),
                      (states,ia,ib,np.int32(n),np.int32(ne),np.int32(npop),changed))
                rounds+=1
                if not changed.item():break
                assert rounds <= n+1
            closed_rounds += rounds
            fingerprint((npop,),(128,),(states,np.int32(n),fingerprints_output))
            seen_fingerprints.update(map(int,fingerprints_output.get()))
            values = score(states); at = int(cp.argmin(values).item())
            value = float(values[at].item()); candidates += npop
            if value < best_score-1e-10:
                best_score, best = value, states[at].copy()
                selected=best.get(); exact_cpu=cpu_energy(doc,variables,selected,unit)
                assert abs(exact_cpu-best_score)<1e-7
                (args.output/'best-flags.json').write_text(json.dumps({
                    **protocol,'screen_cost':best_score,'uniform_old_cost':control,
                    'uniform_minimum_cost':minimum_control,'gain':control-best_score,
                    'tested_candidates':candidates,'minimum_frame_ids':[f for f,s in zip(variables,selected) if s==0],
                    'old_frame_ids':[f for f,s in zip(variables,selected) if s==1],
                    'all_legal_rows_independently_checked':len(doc['rows']),
                    'cpu_recomputed_cost':exact_cpu},indent=2)+'\n')
            if batch%16==0 or batch+1==args.batches:
                status={'utc':stamp(),'batches':batch+1,'candidates':candidates,
                        'best_cost':best_score,'uniform_old_cost':control,'gain':control-best_score,
                        'unique_state_fingerprints_lower_bound':len(seen_fingerprints),
                        'implication_closure_rounds':closed_rounds,'elapsed_seconds':time.monotonic()-started}
                log.write(json.dumps(status)+'\n');log.flush();print(json.dumps(status),flush=True)
    if not (args.output/'best-flags.json').exists():
        selected=best.get()
        (args.output/'best-flags.json').write_text(json.dumps({**protocol,'gain':control-best_score,
            'minimum_frame_ids':[f for f,t in zip(variables,selected) if t==0],
            'old_frame_ids':[f for f,t in zip(variables,selected) if t==1],
            'screen_cost':best_score,'all_legal_rows_independently_checked':len(doc['rows'])},indent=2)+'\n')
    summary={**protocol,'status':'COMPLETE LEGAL MIXED COFRAME FLAG DISCOVERY',
             'candidates':candidates,'unique_state_fingerprints_lower_bound':len(seen_fingerprints),
             'fingerprint_scope':'Deterministic XOR of splitmix64 coordinate labels; collisions can only undercount distinct states.',
             'best_cost':best_score,'uniform_old_cost':control,
             'gain':control-best_score,'elapsed_seconds':time.monotonic()-started,
             'best_flags_sha256':digest(args.output/'best-flags.json')}
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')


if __name__=='__main__':
    main()
