#!/usr/bin/env python3
"""Exact bounded frame exchanges for the frozen PR163 paired-cube bit word.

The source graph, partner mixing, gauges, target reads, role stock and weighted
compiler are frozen. Connected operations may share a new common frame only
when it contains all their value spans and incoming frames, lies in every
outgoing frame, and is rationally G-nondegenerate. All affected paid transitions
are scored with their actual multiplicity. Screening floats are never kappa.

Inherited word/compiler: eumemic and the upstream contributors named in PR161
and PR163; Apache-2.0. New search prepared with OpenAI assistance.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import resource
import sys
import time

sys.dont_write_bytecode = True


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_candidate(source):
    path = source / 'research/paired-cube-balanced-161/bit/word.py'
    spec = importlib.util.spec_from_file_location('retained_bit_word', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Candidate([])


class Model:
    def __init__(self, source, trial):
        self.source, self.trial = source, trial
        self.candidate = w = load_candidate(source)
        w.exact_frames()
        self.reference = w.row()
        self.C, self.h, self.m, self.ops = w.C, w.h, 3*w.h, w.ops
        self.current = list(w.opframe)
        self.original = [w.nf[x] for _, _, x in self.ops]
        self.initial = list(self.current)
        self.zero = w.register([])
        self.full = w.w['full_frame']
        self.f = [0.] + [r*math.expm1(trial*math.log(self.m/r)) for r in range(1,self.m+1)]
        self.spans = []
        for x, ab in enumerate(w.g['args']):
            self.spans.append(w.register([w.C.chi[x]]) if ab is None
                              else self.join(self.spans[ab[0]], self.spans[ab[1]]))
        starts = {role: w.w['source_frame'][leaf] for leaf, role in w.source.items()}
        starts.update({role: z['frame'] for role, z in w.gauge.items()})
        role_ops = defaultdict(list)
        for i, (a,b,_) in enumerate(self.ops):
            role_ops[a].append(i); role_ops[b].append(i)
        roots = defaultdict(list)
        for j, role in enumerate(w.w['rootroles']):
            roots[role].append(w.w['root_frame'][j])
        self.fixed, self.edges = [], []
        self.incoming, self.outgoing, self.neighbors = defaultdict(list), defaultdict(list), defaultdict(set)
        def fixed(frame):
            self.fixed.append(frame)
            return -len(self.fixed)
        for role in range(w.R):
            seq = [fixed(starts.get(role,self.zero))]+role_ops[role]
            seq.extend(fixed(frame) for frame in roots[role]); seq.append(fixed(self.full))
            for a,b in zip(seq,seq[1:]):
                edge = len(self.edges); self.edges.append((a,b))
                if b >= 0:self.incoming[b].append(edge)
                if a >= 0:self.outgoing[a].append(edge)
                if a >= 0 and b >= 0:
                    self.neighbors[a].add(b);self.neighbors[b].add(a)
        self.fixed_hist = Counter({int(r):n for r,n in self.reference['child_histogram'].items()})
        for a,b in self.edges:
            r=self.dim(self.frame(b))-self.dim(self.frame(a))
            if r:self.fixed_hist[r]-=3
        self.fixed_hist = Counter({r:n for r,n in self.fixed_hist.items() if n})
        need(all(n>=0 for n in self.fixed_hist.values()),'fixed complete ledger has no negative bins')
        self.validate()
        need(self.histogram()=={int(r):n for r,n in self.reference['child_histogram'].items()},'full control recount')

    def frame(self,i):
        return self.current[i] if i>=0 else self.fixed[-i-1]

    def dim(self,f):
        return self.C.dimf[f]

    @lru_cache(maxsize=200000)
    def join(self,a,b):
        if self.C.sub(a,b):return b
        if self.C.sub(b,a):return a
        return self.candidate.register(list(self.C.B[a])+list(self.C.B[b]))

    def join_many(self,frames):
        out=self.zero
        for f in frames:out=self.join(out,f)
        return out

    @lru_cache(maxsize=200000)
    def cap(self,a,b):
        if self.C.sub(a,b):return a
        if self.C.sub(b,a):return b
        ann,_=self.candidate.module.reduce_rows(list(self.C.A[a])+list(self.C.A[b]),self.h)
        basis,_=self.candidate.module.kernel(ann,self.h)
        return self.candidate.register(basis)

    @lru_cache(maxsize=100000)
    def nondeg(self,f):
        return self.C.nondeg(f)

    def groups(self,policy,max_nodes):
        if policy=='control':return []
        if policy=='singletons':return [(i,) for i in range(len(self.ops))]
        parent=list(range(len(self.ops)))
        def find(i):
            while parent[i]!=i:
                parent[i]=parent[parent[i]];i=parent[i]
            return i
        for a in range(len(self.ops)):
            for b in self.neighbors[a]:
                if a<b and (self.current[a]==self.current[b] or
                              self.C.sub(self.current[a],self.current[b]) and self.C.sub(self.current[b],self.current[a])):
                    ra,rb=find(a),find(b)
                    if ra!=rb:parent[rb]=ra
        blocks=defaultdict(list)
        for i in range(len(self.ops)):blocks[find(i)].append(i)
        blocks=sorted(map(tuple,blocks.values()),key=lambda g:g[0])
        if policy=='components':return [g for g in blocks if len(g)<=max_nodes]
        owner={i:k for k,g in enumerate(blocks) for i in g}
        links=set()
        for a in range(len(self.ops)):
            for b in self.neighbors[a]:
                x,y=owner[a],owner[b]
                if x!=y:links.add(tuple(sorted((x,y))))
        return [tuple(sorted(blocks[x]+blocks[y])) for x,y in sorted(links)
                if len(blocks[x])+len(blocks[y])<=max_nodes]

    def collapse(self,group):
        inside=set(group)
        inc=[e for b in group for e in self.incoming[b] if self.edges[e][0] not in inside]
        out=[e for a in group for e in self.outgoing[a] if self.edges[e][1] not in inside]
        internal=[e for a in group for e in self.outgoing[a] if self.edges[e][1] in inside]
        lower=self.join_many([self.spans[self.ops[i][2]] for i in group]
                             +[self.frame(self.edges[e][0]) for e in inc])
        upper=self.full
        for e in out:upper=self.cap(upper,self.frame(self.edges[e][1]))
        if not self.C.sub(lower,upper):return None,'infeasible'
        options=[f for f in (lower,upper) if self.nondeg(f)]
        if not options:return None,'degenerate_endpoints'
        affected=inc+internal+out
        old=math.fsum(self.f[self.dim(self.frame(b))-self.dim(self.frame(a))]
                      for a,b in (self.edges[e] for e in affected))
        def cost(f):
            return math.fsum([self.f[self.dim(f)-self.dim(self.frame(self.edges[e][0]))] for e in inc]
                            +[self.f[self.dim(self.frame(self.edges[e][1]))-self.dim(f)] for e in out])
        best=min(options,key=lambda f:(cost(f),self.dim(f),f));delta=cost(best)-old
        if delta>=-1e-12:return None,'no_gain'
        old_mass=sum(self.dim(self.frame(b))-self.dim(self.frame(a)) for a,b in (self.edges[e] for e in affected))
        new_mass=sum(self.dim(best)-self.dim(self.frame(self.edges[e][0])) for e in inc)
        new_mass+=sum(self.dim(self.frame(self.edges[e][1]))-self.dim(best) for e in out)
        need(old_mass==new_mass,'exchange preserves all paid rank mass')
        ranks=[self.dim(self.current[i]) for i in group]
        for i in group:self.current[i]=best
        return dict(ops=list(group),old_ranks=ranks,new_rank=self.dim(best),delta_excess=3*delta,
                    internal_edges=len(internal),lower_rank=self.dim(lower),upper_rank=self.dim(upper)), 'accepted'

    def histogram(self):
        hist=Counter(self.fixed_hist)
        for a,b in self.edges:
            r=self.dim(self.frame(b))-self.dim(self.frame(a));need(r>=0,'nonnegative charged transition')
            if r:hist[r]+=3
        return dict(sorted((r,n) for r,n in hist.items() if n))

    def validate(self):
        for i,(_,_,x) in enumerate(self.ops):
            need(self.C.sub(self.spans[x],self.current[i]),f'value span at operation {i}')
            need(self.nondeg(self.current[i]),f'G nondegenerate operation {i}')
        for a,b in self.edges:need(self.C.sub(self.frame(a),self.frame(b)),f'role edge {a},{b}')
        hist=self.histogram();need(sum(r*n for r,n in hist.items())==self.reference['rank_per_vertex'],'complete rank mass')
        return dict(exact_rational_value_containment=True,all_physical_role_chains_nested=True,
                    all_operation_frames_G_nondegenerate=True,complete_rank_mass_preserved=True,
                    unchanged_partner_K_and_target_readouts=True)

    def profile(self):
        w=self.candidate;w.opframe=list(self.current)
        w.changed_frames=[i for i,f in enumerate(self.current) if not self.C.sub(f,self.original[i])
                          or not self.C.sub(self.original[i],f)]
        for i,(a,b,_) in enumerate(self.ops):
            w.endframe[a]=self.current[i];w.endframe[b]=self.current[i]
        row=w.row()
        need({int(r):n for r,n in row['child_histogram'].items()}==self.histogram(),'separate inherited full row recount')
        return row

    def moments(self,hist):
        mass=sum(r*n for r,n in hist.items());W=self.reference['W_per_vertex']
        raw=math.fsum(n*r*math.exp(self.trial*math.log(self.m/r)) for r,n in hist.items())/(self.m*W)
        fallback=10**-16*32*self.m*self.m*sum(hist.values())*self.m**self.trial/(self.m*W)
        lo,hi=0.,.01
        for _ in range(65):
            mid=(lo+hi)/2
            H=math.fsum(n*r*math.exp(mid*math.log(self.m/r)) for r,n in hist.items())/(self.m*W)
            H+=10**-16*32*self.m*self.m*sum(hist.values())*self.m**mid/(self.m*W)
            if H<1:lo=mid
            else:hi=mid
        return dict(trial=self.trial,raw_moment=raw,fallback_added=fallback,paid_upper_screen=raw+fallback,
                    coarse_root_screen=lo,mass=mass,edge_count=sum(hist.values()),scope='DISCOVERY floating point only')


def main():
    need(not sys.flags.optimize,'assertions must be enabled')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--policy',choices=['control','singletons','components','component-pairs'],required=True)
    ap.add_argument('--order',choices=['forward','reverse','random','alternating','largest-first'],default='alternating')
    ap.add_argument('--max-nodes',type=int,default=256);ap.add_argument('--passes',type=int,default=4)
    ap.add_argument('--seed',type=int,default=20261009);ap.add_argument('--trial',type=float,default=0.000594653772288656)
    ap.add_argument('--start-plan',type=Path);args=ap.parse_args()
    need(not args.output.exists(),'fresh attempt directory required');args.output.mkdir(parents=True)
    started=time.monotonic();utc=datetime.now(timezone.utc).isoformat();source=args.source.resolve()
    protocol=dict(source_commit='15c702a929b7d640107a95e196186ad74e876c82',control_source_commit='d14e29157bc905be1ced0776dd893d0714013f3a',
                  started_utc=utc,policy=args.policy,order=args.order,passes=args.passes,max_nodes=args.max_nodes,
                  seed=args.seed,trial=args.trial,workers=1,numerical_library_threads=1,
                  frozen=['graph','gauges','partner_mix','root_readouts','ordinary_leaf','fallback','normalization'])
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2,sort_keys=True)+'\n')
    model=Model(source,args.trial);control=model.moments(model.histogram())
    if args.start_plan:
        plan=json.loads(args.start_plan.read_text());need(plan['p']==12,'start plan p12')
        model.current=list(model.original)
        for i,B in plan['frames']:
            need(type(i)is int and 0<=i<len(model.ops),'valid start index');model.current[i]=model.candidate.register(B)
        model.validate()
    start_frames=list(model.current);start_moments=model.moments(model.histogram())
    print(json.dumps(dict(stage='initialized',seconds=time.monotonic()-started,control=control)),flush=True)
    rng=random.Random(args.seed);moves=[];passes=[]
    for k in range(args.passes):
        groups=model.groups(args.policy,args.max_nodes)
        if args.order=='random':rng.shuffle(groups)
        elif args.order=='largest-first':groups.sort(key=lambda g:(-len(g),g))
        elif args.order=='reverse' or args.order=='alternating' and k%2:groups.reverse()
        counts=Counter()
        for group in groups:
            change,status=model.collapse(group);counts[status]+=1
            if change:moves.append(change)
        passes.append(dict(index=k,groups=len(groups),**dict(counts)))
        print(json.dumps(dict(stage='pass',**passes[-1],seconds=time.monotonic()-started)),flush=True)
        if not counts['accepted']:break
    checks=model.validate();row=model.profile()
    plan=dict(p=12,frames=[[i,list(map(list,model.C.B[model.current[i]]))] for i in model.candidate.changed_frames])
    (args.output/'frames.json').write_text(json.dumps(plan,separators=(',',':'))+'\n')
    (args.output/'moves.json').write_text(json.dumps(moves,separators=(',',':'))+'\n')
    (args.output/'profile.json').write_text(json.dumps(row,indent=2,sort_keys=True)+'\n')
    formal=model.candidate.formal(2)
    result=dict(status='DISCOVERY',protocol=protocol,moves=len(moves),passes=passes,local_checks=checks,formal_F2=formal,
                changes_from_start=sum(a!=b for a,b in zip(start_frames,model.current)),profile=row,
                control_moments=control,start_moments=start_moments,moments=model.moments(model.histogram()),
                wall_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                plan_sha256=sha(args.output/'frames.json'),search_sha256=sha(Path(__file__)),
                source_sha256={str(p):sha(source/p) for p in [Path('research/paired-cube-balanced-161/bit/word.py'),
                  Path('research/paired-cube-balanced-161/bit/descent.json'),Path('research/paired-cube-bit/check_paired_cube_bit.py'),
                  Path('research/paired-cube-bit/out/graph_p12.json'),Path('research/paired-cube-bit/out/word_p12.json'),
                  Path('research/paired-cube-bit/out/frames_p12.json'),Path('research/paired-cube-bit/out/kchron_p12.json')]},
                exclusions=['independent reflected word review','rigorous moment enclosure','exact new prime exclusions','final assembly kappa'])
    (args.output/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('status','moves','changes_from_start','moments','wall_seconds','peak_rss_kib')}),flush=True)


if __name__=='__main__':main()
