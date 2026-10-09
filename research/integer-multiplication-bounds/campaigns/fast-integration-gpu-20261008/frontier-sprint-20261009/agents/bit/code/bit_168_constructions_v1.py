#!/usr/bin/env python3
"""Rebuild distinct binary constructions on immutable PR168 inputs.

The source module, graph generator, frame compiler, chronological gauges, and
all exported data are pinned. Each changed module gets a fresh graph, matching,
frames and chronology. The plain-frame variant retains the actual source
graph/arcs but recompiles frames and gauges. Every profile is independently
recounted from exported register chains and formally replayed over F2.

Inherited code and data retain Apache-2.0 and upstream assistance attribution.
New bounded integration glue prepared for RaD with OpenAI assistance.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import inspect
import json
import math
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True
from paired_bit_replay import Candidate

HEAD = '98c115b53742b6613ad630de4d493f37b0119da7'


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prefix_suffix(n):
    """Direct disjoint prefix/suffix all-but-one: 3n-6 additions."""
    args = [None]*n
    def add(a, b):
        args.append([a,b])
        return len(args)-1
    pre = {1:0}
    for k in range(1,n-1):
        pre[k+1] = add(pre[k],k)
    suf = {n-1:n-1}
    for k in range(n-2,0,-1):
        suf[k] = add(k,suf[k+1])
    roots = [suf[1]]+[add(pre[i],suf[i+1]) for i in range(1,n-1)]+[pre[n-1]]
    return dict(input_count=n,args=args,roots=roots)


def reverse_module(data):
    """Reverse input order while restoring original output indexing."""
    n = data['input_count']
    ren = lambda x:n-1-x if x<n else x
    args = [None]*n+[[ren(a),ren(b)] for a,b in data['args'][n:]]
    roots = [ren(x) for x in reversed(data['roots'])]
    return dict(input_count=n,args=args,roots=roots)


def check_module(data):
    n = data['input_count']; support=[]
    for i,ab in enumerate(data['args']):
        if ab is None:
            need(i<n,'all leaves first');support.append(1<<i)
        else:
            a,b=ab;need(0<=a<i and 0<=b<i,'module chronology')
            need(not support[a]&support[b],'module support disjointness')
            support.append(support[a]|support[b])
    need(all(support[r] == ((1<<n)-1)^(1<<i) for i,r in enumerate(data['roots'])),
         'exact all-but-one identities')


def moments(row):
    m,W=row['m'],row['W_per_vertex']
    H={int(r):n for r,n in row['child_histogram'].items()}
    need(all(0<r<m and n>0 for r,n in H.items()),'all complete children proper')
    need(sum(r*n for r,n in H.items())==row['rank_per_vertex'],'complete mass')
    lo,hi=0.,.01
    for _ in range(65):
        a=(lo+hi)/2
        value=math.fsum(n*r*math.exp(a*math.log(m/r)) for r,n in H.items())/(W*m)
        value+=1e-16*32*m*m*sum(H.values())*m**a/(W*m)
        if value<1:lo=a
        else:hi=a
    return dict(coarse_paid_root_screen=lo,edges=sum(H.values()),
                fallback_fraction='1/10000000000000000',fallback_per_edge=32*m*m,
                scope='DISCOVERY floating point only; native bit saving, not final kappa')


def load_generator(source):
    path=source/'research/paired-cube-bit/paired_cube_bit_word.py'
    spec=importlib.util.spec_from_file_location('immutable_pr168_generator',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def main():
    need(not sys.flags.optimize,'assertions enabled')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--variant',choices=['control','prefix-suffix','reverse-prefix','plain12'],required=True)
    args=ap.parse_args();source=args.source.resolve()
    need(not args.output.exists(),'fresh attempt required');args.output.mkdir(parents=True)
    export=args.output/'exports';export.mkdir()
    started=time.monotonic();mod=load_generator(source)
    paths=[Path('research/paired-cube-bit')/name for name in
           ['paired_cube_bit_word.py','check_paired_cube_bit.py','data/pair_module_p12.json','data/arcs_p12.json']]
    protocol=dict(source_commit=HEAD,variant=args.variant,
                  started_utc=datetime.now(timezone.utc).isoformat(),workers=1,numerical_library_threads=1,
                  source_files={str(p):dict(bytes=(source/p).stat().st_size,sha256=sha(source/p)) for p in paths},
                  replay_template_commit='15c702a929b7d640107a95e196186ad74e876c82',
                  program_sha256=sha(Path(__file__)),replay_sha256=sha(Path(__file__).with_name('paired_bit_replay.py')),
                  inherited_contracts=['weighted local-ring compiler','ordinary atom supplier','full fallback',
                                       'completed-core sharing','stopped recurrence'])
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2,sort_keys=True)+'\n')
    frozen=json.loads((source/'research/paired-cube-bit/data/arcs_p12.json').read_text())
    allbut=mod.nested_prefix(10)
    if args.variant=='prefix-suffix':
        allbut=prefix_suffix(10);frozen=None
    elif args.variant=='reverse-prefix':
        allbut=reverse_module(allbut);frozen=None
    elif args.variant=='plain12':
        # Expand only through nondegenerate value spans and retain the source's
        # exact operand-closure and linked-donor conditions. Rebuilt gauges and
        # all final chains are checked independently below.
        code=inspect.getsource(mod.compile_word)
        old='if args[x] and geo.dim(spans[x]) <= plain_k and all(y in cand for y in args[x]):'
        new='if args[x] and geo.dim(spans[x]) <= plain_k and all(y in cand for y in args[x]) and gram_nondegenerate_frame(list(geo.T.rows[spans[x]]), h):'
        need(code.count(old)==1,'pinned plain-frame patch point')
        exec(compile(code.replace(old,new),'<nondegenerate-plain12-patch>','exec'),mod.__dict__)
        patched=mod.compile_word
        mod.compile_word=lambda g,frozen=None:patched(g,frozen=frozen,plain_k=12)
        mod.PLAIN=12
    check_module(allbut)
    mod.nested_prefix=lambda n:allbut if n==10 else None
    (args.output/'allbutone.json').write_text(mod.dumps(allbut))
    packed,profile,arcs,exp=mod.build(12,frozen_arcs=frozen,log=lambda x:print(x,flush=True))
    (args.output/'arcs.json').write_text(mod.dumps(arcs))
    for name,data in exp.items():
        (export/(name+'_p12.json')).write_text(mod.dumps(data))
    (export/'profile_p12.json').write_text(mod.dumps(profile))
    (export/'word_p12.json.gz').write_bytes(gzip.compress(mod.dumps(packed).encode(),mtime=0))
    print(json.dumps(dict(stage='regenerated',seconds=time.monotonic()-started,R=profile['R'],
                         W=profile['W_per_vertex'],plain=profile['plain_frames'])),flush=True)
    word=Candidate([],export,source/'research/paired-cube-bit/check_paired_cube_bit.py')
    word.exact_frames();row=word.row()
    need({int(r):n for r,n in row['child_histogram'].items()}==
         {int(r):n for r,n in profile['child_histogram'].items()},'independent exported-word complete row')
    formal=word.formal(2);controls={}
    for tamper in ['omit_compensation','missing_partner']:
        try:word.formal(2,tamper)
        except ValueError:controls[tamper]='REJECTED'
        else:raise ValueError('adverse formal control accepted '+tamper)
    result=dict(status='DISCOVERY',protocol=protocol,formal_F2=formal,controls=controls,
                profile=row,screen=moments(row),allbutone_additions=len(allbut['args'])-10,
                exported_files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(export.iterdir())},
                wall_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Actual scalar DAG and all frames/chronology rebuilt. Exact finite row/F2; prime, moment and reflection gates pending.')
    (args.output/'profile.json').write_text(json.dumps(row,indent=2,sort_keys=True)+'\n')
    (args.output/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status='DISCOVERY',variant=args.variant,R=row['R'],W=row['W_per_vertex'],
                         screen=result['screen'],wall_seconds=result['wall_seconds'])),flush=True)


if __name__=='__main__':
    main()
