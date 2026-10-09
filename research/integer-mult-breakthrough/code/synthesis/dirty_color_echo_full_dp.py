#!/usr/bin/env python3
"""One preflighted full-Lagrangian dirty echo decision with four native threads.

The immutable serial kernel plus retained patch reconstructs the parallel
source. Memory is estimated from every actual factor scope before execution.
This is one complete n3 chronology, not a parameter sweep or multiplier claim.
"""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import time

import dirty_color_echo_dp as dp

PATCH=Path(__file__).resolve().parents[2]/'fixtures/synthesis/frame-elimination-openmp.patch'
FACTOR_MAX_ENTRIES=2**29


def preflight():
    n=m=3;word=dp.scalar_word(m,'side-inside');f=dp.f;zero=f.le((),n);full=f.le(tuple(1<<j for j in range(n)),n)
    starts=[f.le((1<<j,),n) for j in range(m)]+[zero]*(m+1);ends=[full]*m+[f.le(f.perpendicular((1<<j,),n),n) for j in range(m)]+[full]
    domain=f.lagrangians(n);D=len(domain);edges,boundaries,constant=f.incidence_graph(word,7,starts,ends)
    order=dp.minfill(len(word),edges);factors=[(j,) for j in range(len(word))]+[(a,b) for a,b,c in edges]
    decisions=0;peak=0;evaluations=0;stages=[]
    for variable in order:
        selected=[F for F in factors if variable in F];remaining=[F for F in factors if variable not in F]
        neighbors=tuple(sorted(set(v for F in selected for v in F if v!=variable)));entries=D**len(neighbors)
        if entries>FACTOR_MAX_ENTRIES:raise ValueError('Preflight factor exceeds declared storage cap')
        live=2*entries+sum(D**len(F) for F in selected+remaining)+decisions
        peak=max(peak,live);evaluations+=entries*D
        stages.append(dict(variable=variable,width=len(neighbors),factor_entries=entries,live_uint16_entries=live))
        decisions+=entries;factors=remaining+[neighbors]
    return dict(frame_domain=D,vertices=len(word),order=order,stages=stages,
                candidate_cost_evaluations=evaluations,peak_uint16_entries=peak,
                peak_factor_and_decision_bytes=2*peak,
                scope='Exact cost/choice vector payload estimate; allocator metadata, runtime and small original tables are extra. Reserve at least1GiB beyond the estimated payload.')


def full_solve(binary,work,edges,unary,table,constant=0,order=None):
    vertices=len(unary);domain=len(table);order=dp.minfill(vertices,edges) if order is None else order
    fields=[vertices,domain,constant,FACTOR_MAX_ENTRIES]+[x for row in table for x in row]+[x for row in unary for x in row]
    fields+=[len(edges)]+[x for edge in edges for x in edge]+order;path=work/'graph.txt';path.parent.mkdir(parents=True,exist_ok=False)
    path.write_text(' '.join(map(str,fields))+'\n');result=subprocess.run([str(binary.resolve()),str(path.resolve())],text=True,capture_output=True,check=True)
    receipt=json.loads(result.stdout)
    if receipt['optimum']!=dp.f.energy(receipt['assignment'],edges,unary,lambda a,b:table[a][b],constant):
        raise ValueError('Parallel complete min-sum witness fails independent graph replay')
    receipt['graph_input_sha256']=sha256(path.read_bytes()).hexdigest();receipt['elimination_order']=order
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--threads',type=int,default=4);parser.add_argument('--cxx',default='c++');parser.add_argument('--memory-budget-GiB',type=float,default=8)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False);estimate=preflight()
    if estimate['peak_factor_and_decision_bytes']+2**30>args.memory_budget_GiB*2**30:
        raise ValueError('Preflight exceeds declared memory budget including1GiB reserve')
    build=args.output.parent/'builds';build.mkdir(exist_ok=False);source=build/'frame_variable_elimination_parallel.cpp';binary=build/'frame-variable-elimination'
    subprocess.run(['patch','-o',str(source.resolve()),str(dp.CPP.resolve()),str(PATCH.resolve())],check=True,text=True,capture_output=True)
    subprocess.run([args.cxx,'-O3','-std=c++17','-fopenmp',str(source.resolve()),'-o',str(binary.resolve())],check=True,text=True,capture_output=True)
    compiler=subprocess.run([args.cxx,'--version'],check=True,text=True,capture_output=True).stdout.splitlines()[0]
    paths=[Path(__file__),Path(dp.__file__),dp.CPP,PATCH,Path(dp.f.__file__),Path(dp.f.__file__).with_name('lagrangian_graph_completion.py'),
           Path(dp.f.__file__).with_name('trimmed_zeta_dirty_probe.py'),dp.f.SIDE_SOURCE]
    hashes={p:sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),native_worker_threads=args.threads,
                  spec=dict(active_bits=3,color_size=3,frame_kind='all-Lagrangian',chronology='side-inside'),
                  source_sha256={p.name:v for p,v in hashes.items()},generated_parallel_source_sha256=sha256(source.read_bytes()).hexdigest(),
                  compiler=compiler,compile_flags=['-O3','-std=c++17','-fopenmp'],
                  memory_budget_GiB=args.memory_budget_GiB,preflight=estimate,
                  controls='16 bounded exact graph cases independently enumerated before full-domain execution')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    os.environ['OMP_NUM_THREADS']=str(args.threads);os.environ['OMP_DYNAMIC']='FALSE';dp.solve=full_solve
    controls=dp.controls(binary,args.output.parent/'derived/controls');started=time.monotonic()
    print(json.dumps(dict(status='PREFLIGHT AND PARALLEL CONTROLS PASS',payload_GiB=estimate['peak_factor_and_decision_bytes']/2**30,
                         candidate_evaluations=estimate['candidate_cost_evaluations'],threads=args.threads)),flush=True)
    result=dp.probe((3,3,'all-Lagrangian','side-inside',binary,args.output.parent/'derived/full-case'))
    if result['exact_min_sum']['peak_live_uint16_entries']!=estimate['peak_uint16_entries']:
        raise ValueError('Actual factor payload differs from exact memory preflight')
    if result['exact_min_sum']['parallel_worker_threads']!=args.threads:
        raise ValueError('Native parallel thread count differs from recorded configuration')
    if any(sha256(p.read_bytes()).hexdigest()!=v for p,v in hashes.items()):raise ValueError('Effective source changed during experiment')
    (args.output/'certificate.json').write_text(json.dumps(dict(controls=controls,case=result,seconds=time.monotonic()-started),indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('status','minimum_rank_charge','capacity','deficit','seconds')}),flush=True)


if __name__=='__main__':main()
