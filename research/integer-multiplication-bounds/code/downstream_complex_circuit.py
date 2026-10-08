#!/usr/bin/env python3
"""Cancellation-free triple deletion and binary-frame complex side prototype.

The complex correction is (disjoint sums - intersection-two sums)/2.
The circuit uses exact formal supports, and the proposed nested binary
frames are checked by explicit coordinate/norm-one witnesses. This is a
finite prototype; the tensor/frame/phase transfer needs separate review.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time

from downstream_gaussian import check_sources,require
from downstream_parameter_optimum import as_strings,saving_enclosure


def masks(points):
    return sum(1<<i for i in points)


class TripleSideCircuit:
    def __init__(self,h: int):
        require(h>=8 and h%2==0,"Binary-frame construction requires even h>=8")
        self.h=h
        self.inputs=list(combinations(range(h),3))
        self.variables={t:i+1 for i,t in enumerate(self.inputs)}
        self.support=[0]+[1<<i for i in range(len(self.inputs))]
        self.args=[None]*len(self.support)
        self.union=[0]+[masks(t) for t in self.inputs]
        self.core=list(self.union)
        self.family=['zero']+['input']*len(self.inputs)
        self.lookup={(None,s):i for i,s in enumerate(self.support)}
        self.special={}
        self.namespace='D'
        terms={t:self.variables[t] for t in self.inputs}
        deleted=self.hyper(list(range(h)),terms,3)
        self.outputs={('D',t):deleted[t] for t in self.inputs}
        self.namespace='E'
        strips={}
        for pair in combinations(range(h),2):
            other=[j for j in range(h) if j not in pair]
            values=[self.variables[tuple(sorted(pair+(j,)))] for j in other]
            _,one=self.vector(values)
            for j,value in zip(other,one): strips[pair,j]=value
        for target in self.inputs:
            values=[strips[pair,next(j for j in target if j not in pair)]
                    for pair in combinations(target,2)]
            first=self.add(values[0],values[1])
            self.special[first]=target
            last=self.add(first,values[2])
            self.special[last]=target
            self.outputs['E',target]=last
        self.active=set()
        stack=list(self.outputs.values())
        while stack:
            node=stack.pop()
            if not node or node in self.active: continue
            self.active.add(node)
            if self.args[node]: stack.extend(self.args[node])
        self.additions=sum(self.args[x] is not None for x in self.active)

    def add(self,a,b):
        if not a:return b
        if not b:return a
        require(not self.support[a]&self.support[b],"Overlapping formal summands")
        support=self.support[a]|self.support[b]
        key=self.namespace,support
        if key in self.lookup:return self.lookup[key]
        node=len(self.support)
        self.lookup[key]=node
        self.support.append(support); self.args.append((a,b))
        self.union.append(self.union[a]|self.union[b])
        self.core.append(self.core[a]&self.core[b])
        self.family.append(self.namespace)
        return node

    def total(self,values):
        values=[x for x in values if x]
        if not values:return 0
        if len(values)==1:return values[0]
        middle=len(values)//2
        return self.add(self.total(values[:middle]),self.total(values[middle:]))

    def vector(self,values):
        prefix=[0]
        for value in values:prefix.append(self.add(prefix[-1],value))
        suffix=[0]*(len(values)+1)
        for i in range(len(values)-1,-1,-1):suffix[i]=self.add(values[i],suffix[i+1])
        return prefix[-1],[self.add(prefix[i],suffix[i+1]) for i in range(len(values))]

    def hyper(self,points,terms,k):
        """Weighted degree<=k deletion sums through pair-block contraction."""
        if k==0:return {():self.total(list(terms.values()))}
        if k==1:
            values=[terms.get((i,),0) for i in points]+[terms.get((),0)]
            total,one=self.vector(values)
            return {():total,**{(i,):value for i,value in zip(points,one)}}
        if len(points)<=4:
            return {omit:self.total([value for edge,value in terms.items()
                                    if not set(edge)&set(omit)])
                    for size in range(k+1) for omit in combinations(points,size)}
        groups=[points[i:i+2] for i in range(0,len(points),2)]
        group_of={v:i for i,g in enumerate(groups) for v in g}
        coarse_lists=defaultdict(list)
        components=defaultdict(lambda:defaultdict(list))
        for edge,value in terms.items():
            coarse_lists[tuple(sorted({group_of[v] for v in edge}))].append(value)
            for size in range(1,len(edge)+1):
                for selected in combinations(edge,size):
                    selected_groups={group_of[v] for v in selected}
                    if len(selected_groups)!=size:continue
                    rest=[v for v in edge if v not in selected]
                    if any(group_of[v] in selected_groups for v in rest):continue
                    remaining_groups=tuple(sorted({group_of[v] for v in rest}))
                    components[selected][remaining_groups].append(value)
        coarse={edge:self.total(values) for edge,values in coarse_lists.items()}
        coarse_answers=self.hyper(list(range(len(groups))),coarse,k)
        component_answers={}
        for selected,pieces in components.items():
            selected_groups={group_of[v] for v in selected}
            other=[g for g in range(len(groups)) if g not in selected_groups]
            induced={edge:self.total(values) for edge,values in pieces.items()}
            component_answers[selected]=self.hyper(other,induced,k-len(selected))
        answers={}
        for size in range(k+1):
            for omit in combinations(points,size):
                touched={group_of[v] for v in omit}
                remaining=sorted(v for g in touched for v in groups[g] if v not in omit)
                values=[coarse_answers[tuple(sorted(touched))]]
                for count in range(1,len(remaining)+1):
                    for selected in combinations(remaining,count):
                        tables=component_answers.get(selected)
                        if tables is None:continue
                        outside=tuple(sorted(touched-{group_of[v] for v in selected}))
                        values.append(tables[outside])
                answers[omit]=self.total(values)
        return answers

    def verify(self):
        stripe=[0]*self.h
        for i,t in enumerate(self.inputs):
            bit=1<<i
            for v in t:stripe[v]|=bit
        full=(1<<len(self.inputs))-1
        digest=hashlib.sha256()
        for node in sorted(self.active):
            if self.args[node]:
                a,b=self.args[node]
                require(a<node and b<node and not self.support[a]&self.support[b],
                        "Disjoint DAG invariant failed")
                require(self.support[node]==self.support[a]|self.support[b],
                        "Formal DAG map changed")
            digest.update(f'{node}:{self.args[node]}\n'.encode())
        nonzero=0
        for (kind,t),node in sorted(self.outputs.items()):
            a,b,c=t
            expected=full&~(stripe[a]|stripe[b]|stripe[c]) if kind=='D' else (
                (stripe[a]&stripe[b]&~stripe[c])|
                (stripe[a]&stripe[c]&~stripe[b])|
                (stripe[b]&stripe[c]&~stripe[a]))
            require(self.support[node]==expected,"Complex side output is incorrect")
            require(expected.bit_count()==(comb(self.h-3,3) if kind=='D' else 3*(self.h-3)),
                    "Expected support size failed")
            nonzero+=expected.bit_count()
            digest.update(f'{kind}:{t}:{node}\n'.encode())
        return {"inputs":len(self.inputs),"designated_outputs":len(self.outputs),
                "generated_nodes":len(self.support)-1,"active_additions":self.additions,
                "baseline_physical_roles":self.additions+len(self.outputs),
                "all_disjoint_formal_additions":True,"all_output_coefficients_and_zeros_exact":True,
                "nonzero_side_coefficients":nonzero,"circuit_sha256":digest.hexdigest()}

    def frame(self,node):
        if self.args[node] is None:return ('line',self.union[node])
        if node in self.special:return ('kernel',masks(self.special[node]))
        if self.family[node]=='E':
            require(self.core[node].bit_count()==2,"Pair helper lost its common pair")
            return ('pair',self.core[node],self.union[node]&~self.core[node])
        require(self.family[node]=='D',"Unknown frame namespace")
        v=self.union[node]
        require(v.bit_count()<=self.h-3,"Used disjoint node covers too many coordinates")
        return ('coordinate',v) if v.bit_count()<=self.h-4 else ('kernel',((1<<self.h)-1)^v)

    def frame_edge(self,child,parent):
        """Return exact residual dimension and a norm-one witness if nonzero."""
        old,new=self.frame(child),self.frame(parent)
        full=(1<<self.h)-1
        if old==new:return 0,0
        if new[0]=='coordinate':
            require(old[0] in ['line','coordinate'] and not old[1]&~new[1],
                    "Coordinate frame does not contain child")
            residual=new[1].bit_count()-(1 if old[0]=='line' else old[1].bit_count())
            available=new[1]&~old[1]
            require(available,"Nonzero coordinate residual lacks a unit")
            return residual,available&-available
        if new[0]=='pair':
            pair,vertices=new[1],new[2]
            if old[0]=='line':
                require(old[1]&pair==pair and (old[1]&~pair).bit_count()==1,
                        "Triple input is outside pair frame")
                old_vertices=old[1]&~pair
            else:
                require(old[0]=='pair' and old[1]==pair,"Pair helper frames disagree")
                old_vertices=old[2]
            require(not old_vertices&~vertices,"Pair frame shrank")
            available=vertices&~old_vertices
            require(available,"Distinct pair frames have no residual")
            bit=available&-available
            return vertices.bit_count()-old_vertices.bit_count(),pair|bit
        require(new[0]=='kernel',"Unknown parent frame")
        target=new[1]
        outside=full^target
        if old[0]=='line':
            require((old[1]&target).bit_count()%2==0,"Input triple not target-orthogonal")
            available=outside&~old[1]
            require(available,"Triple-to-kernel residual is alternating at this ground size")
            return self.h-2,available&-available
        if old[0]=='coordinate':
            require(not old[1]&target,"Coordinate child meets target")
            available=outside&~old[1]
            require(available,"Premature full-coordinate child would create alternating residual")
            return self.h-1-old[1].bit_count(),available&-available
        require(old[0]=='pair' and old[1]&target==old[1] and not old[2]&target,
                "Pair child not contained in target kernel")
        available=outside&~old[2]
        if available:unit=available&-available
        else:
            a=old[1]&-old[1]
            third=target&~old[1]
            unit=a|third|outside
        require(unit.bit_count()%2==1 and (unit&target).bit_count()%2==0,
                "Kernel residual witness not a norm-one target-orthogonal vector")
        for j in range(self.h):
            if old[2]>>j&1:
                require((unit&(old[1]|(1<<j))).bit_count()%2==0,
                        "Kernel witness is not orthogonal to pair child")
        return self.h-1-old[2].bit_count(),unit

    def verify_frames(self):
        checked=nonzero=0
        dimensions=defaultdict(int)
        for node in sorted(self.active):
            frame=self.frame(node)
            if self.args[node]:
                for child in self.args[node]:
                    dimension,unit=self.frame_edge(child,node)
                    require(dimension>=0,"Frame dimension decreased")
                    if dimension:
                        require(unit.bit_count()%2==1,"Residual norm-one witness failed")
                        nonzero+=1
                    checked+=1;dimensions[dimension]+=1
        for (kind,t),node in self.outputs.items():
            require(self.frame(node)==('kernel',masks(t)),"Output does not reach exact target kernel")
        return {"directed_gate_edges_checked":checked,"nonzero_nonalternating_residuals":nonzero,
                "residual_dimension_histogram":dict(sorted(dimensions.items())),
                "all_frames_nondegenerate_nested":True,
                "every_nonzero_residual_has_explicit_norm_one_witness":True,
                "reverse_complement_residuals":"Isometric to corresponding forward residuals; same norm-one witnesses.",
                "terminal_complements":"Coordinate, pair, triple-line and target-kernel complements contain norm-one vectors for even h>=8."}

    def compile(self):
        users={x:[] for x in self.active}
        for node in sorted(self.active):
            if self.args[node]:
                for pos,x in enumerate(self.args[node]):users[x].append(('gate',node,pos))
        for target,node in sorted(self.outputs.items()):users[node].append(('output',target))
        edge={};sources={};outputs={};gates=[];size=0
        for node in sorted(self.active):
            if self.args[node]:
                ins=edge[node,0],edge[node,1];pivot=ins[0]
            else:
                pivot=size;size+=1;ins=(pivot,);sources[self.inputs[node-1]]=pivot
            outs=(pivot,)+tuple(range(size,size+len(users[node])-1))
            size+=len(users[node])-1
            require(len(set(ins))==len(ins) and set(ins)&set(outs)=={pivot},
                    "Physical roles collide")
            gates.append((node,ins,outs))
            for user,slot in zip(users[node],outs):
                if user[0]=='gate':edge[user[1],user[2]]=slot
                else:outputs[user[1]]=slot
        require(size==self.additions+len(self.outputs),"Baseline role formula failed")
        return {"roles":size,"sources":sources,"outputs":outputs,"gates":gates}


def mixer(values,code,inverse=False):
    gates=reversed(code['gates']) if inverse else code['gates']
    for _,ins,outs in gates:
        if inverse:
            for slot in outs[1:]:values[slot]-=values[ins[0]]
            for slot in ins[1:]:values[ins[0]]-=values[slot]
        else:
            for slot in ins[1:]:values[ins[0]]+=values[slot]
            for slot in outs[1:]:values[slot]+=values[ins[0]]


def invoke_complex(circuit,code,x,y,scratch,center):
    def inject(sign):
        for i,t in enumerate(circuit.inputs):
            difference=scratch[code['outputs']['D',t]]-scratch[code['outputs']['E',t]]
            require(difference%2==0,"Finite scaled scalar probe lost its dyadic convention")
            y[i]+=sign*(difference//2)
    def scatter(sign):
        for i,t in enumerate(circuit.inputs):
            value=sum(center[j] for j in t)-center[-1]
            require(value%2==0,"Central probe lost its dyadic convention")
            y[i]+=sign*(value//2)
    def copy(sign):
        for i,t in enumerate(circuit.inputs):scratch[code['sources'][t]]+=sign*x[i]
    def gather(sign):
        for i,t in enumerate(circuit.inputs):
            for j in t:center[j]+=sign*x[i]
            center[-1]+=sign*x[i]
    mixer(scratch,code);inject(-1);mixer(scratch,code,True)
    scatter(-1);copy(1);gather(1);scatter(1)
    mixer(scratch,code);inject(1);mixer(scratch,code,True)
    gather(-1);copy(-1)


def scalar_checks(circuit,code,all_basis):
    v=len(circuit.inputs);roles=code['roles'];h=circuit.h
    tests=[]
    for seed in [1,109,313]:
        def payload(i):return 2*(((i*97+seed*31)%509)-254)
        tests.append(([payload(i) for i in range(v)], [payload(v+i) for i in range(v)],
                      [payload(2*v+i) for i in range(roles)], [payload(2*v+roles+i) for i in range(h+1)]))
    if all_basis:
        for coordinate in range(v+roles+h+1):
            x,y,z,c=[0]*v,[0]*v,[0]*roles,[0]*(h+1)
            if coordinate<v:x[coordinate]=2
            elif coordinate<v+roles:z[coordinate-v]=2
            else:c[coordinate-v-roles]=2
            tests.append((x,y,z,c))
    for x,y,z,c in tests:
        before=[list(a) for a in (x,y,z,c)]
        invoke_complex(circuit,code,x,y,z,c)
        require(x==before[0] and y==[a+b for a,b in zip(before[1],before[0])]
                and z==before[2] and c==before[3],"Complex invocation/restoration failed")
    return {"signed_dirty_probes":3,"exact_local_basis_vectors":v+roles+h+1 if all_basis else 0,
            "all_data_shears_and_dirty_scratch_restoration_exact":True,
            "scaling":"Probe coordinates are multiples of2; linearity gives exact Gaussian-dyadic identity."}


def case(h,all_basis):
    start=time.monotonic()
    circuit=TripleSideCircuit(h)
    logical=circuit.verify();frames=circuit.verify_frames();code=circuit.compile()
    scalars=scalar_checks(circuit,code,all_basis)
    v,m,n=comb(h,3),h**3,comb(h,3)**3
    loss=3*v*v*(h+1)*h
    w=2*n+3*v*v*(code['roles']+h+1)
    deficit=2*n-2*loss
    counts={"h":h,"v":v,"m":m,"N":n,"R":code['roles'],"W":w,"L":loss,
            "s":w*m-deficit,"D":deficit,"eta":Q(deficit,w*m)}
    saving=saving_enclosure(counts['eta'],m) if deficit>0 else None
    return as_strings({"status":"PASS finite complex side circuit and proposed binary frames; full tensor/phase transfer pending independent review",
                       "h":h,"logical_circuit":logical,"binary_frames":frames,"scalar_checks":scalars,
                       "unshared_complex_counts":counts,"saving_enclosure_if_positive":saving,
                       "elapsed_seconds":time.monotonic()-start,
                       "scope":"Cancellation-free finite construction. Full rank sum, phase factorization, stage sharing and coefficient-depth transfer need separate review."})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--h',type=int,nargs='+',default=[8,10,12])
    parser.add_argument('--all-basis',action='store_true')
    args=parser.parse_args();source=Path(__file__);start=time.monotonic()
    result={"generated_at":datetime.now(timezone.utc).isoformat(),"campaign":"20261007T222521Z",
            "campaign_start":"2026-10-07T22:25:21Z","campaign_deadline":"2026-10-08T08:25:21Z",
            "provenance":check_sources(args.upstream),
            "source_sha256":{source.name:hashlib.sha256(source.read_bytes()).hexdigest()},"cases":[]}
    for h in args.h:
        print('Starting complex triple circuit h',h,flush=True)
        row=case(h,args.all_basis);result['cases'].append(row)
        result['elapsed_seconds']=time.monotonic()-start
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('PASS complex side h',h,'roles',row['unshared_complex_counts']['R'],flush=True)


if __name__=='__main__':main()
