#!/usr/bin/env python3
"""Full padded CRT pipeline with actual masked F_u inside guarded reflections.

This is a finite payload/address compiler, not an implementation or timing
measurement of the inherited fixed-tape machine. No inverse lookup table is
used. Every inner and outer repair computes reverse-program keys and actually
stable-radix-sorts the extracted records. Scratch bits are existing inactive
node coordinates. The complete reverse pipeline includes inverse repairs and
inverse monotone splitting.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import time
from crt_guard_controls import batched_add,inverse_batched_add,pack,unpack


class Bits:
    def __init__(self, positions):
        self.positions=tuple(positions);self.runs=[]
        for target,source in enumerate(self.positions):
            if self.runs and source==self.runs[-1][0]+self.runs[-1][1]:
                start,width,out=self.runs[-1];self.runs[-1]=(start,width+1,out)
            else:self.runs.append((source,1,target))
    def get(self,address):
        return sum(((address>>source)&((1<<width)-1))<<out
                   for source,width,out in self.runs)
    def put(self,value):
        return sum(((value>>out)&((1<<width)-1))<<source
                   for source,width,out in self.runs)
    def replace(self,address,value):
        mask=sum(((1<<width)-1)<<source for source,width,out in self.runs)
        return (address&~mask)|self.put(value)


def fields(widths):
    result=[];at=0
    for width in widths:
        result.append(Bits(range(at,at+width)));at+=width
    return result


def shape(group):
    return math.prod(group),sum((s-1).bit_length() for s in group)


def valid(address, shapes):
    at=0
    for s,width in shapes:
        if ((address>>at)&((1<<width)-1))>=s:return False
        at+=width
    return True


def apply_record_map(payload, function):
    output=[-1]*len(payload)
    for address,value in enumerate(payload):
        target=function(address)
        assert output[target]==-1,('nonbijective',address,target)
        output[target]=value
    assert -1 not in output
    return output


def apply_record_repair(payload,bad,key,width):
    extracted=[];holes=[]
    for address,value in enumerate(payload):
        if bad(address):
            destination=key(address)
            assert bad(destination),('repair escaped bad set',address,destination)
            extracted.append((destination,value));holes.append(address)
    for bit in range(width):
        zeros=[row for row in extracted if not ((row[0]>>bit)&1)]
        ones=[row for row in extracted if (row[0]>>bit)&1]
        extracted=zeros+ones
    assert [row[0] for row in extracted]==holes
    result=payload[:]
    for address,(destination,value) in zip(holes,extracted):
        assert address==destination;result[address]=value
    return result,len(holes)


def joint_embed(payload,old_shapes,new_shapes):
    def occupied():
        for address,value in enumerate(payload):
            if valid(address,old_shapes):yield value
            else:assert value==0,('nonzero padding consumed',address,value)
    source=occupied();result=[0]*len(payload);count=0
    for address in range(len(payload)):
        if valid(address,new_shapes):
            result[address]=next(source);count+=1
    assert next(source,None) is None
    return result,count


class Machine:
    def __init__(self,payload,width,progress):
        self.payload=payload;self.width=width;self.events=[];self.ledger=[]
        self.progress=progress
    def permutation(self,name,forward,inverse):
        self.payload=apply_record_map(self.payload,forward)
        self.events.append(('map',forward,inverse,None))
        self.ledger.append({'name':name,'records':len(self.payload),'kind':'permutation'})
    def repair(self,name,bad,key,inverse_key):
        self.payload,count=apply_record_repair(self.payload,bad,key,self.width)
        self.events.append(('repair',key,inverse_key,bad))
        self.ledger.append({'name':name,'records':count,'radix_passes':self.width,
                            'kind':'computed_inverse_key_repair'})
    def embedding(self,name,old,new):
        self.payload,count=joint_embed(self.payload,old,new)
        self.events.append(('embed',old,new,None))
        self.ledger.append({'name':name,'occupied_records':count,'kind':'joint_monotone_scan'})
    def emit(self,value):
        self.progress.append(value)
        print(json.dumps(value),flush=True)
    def inverse(self):
        for index,(kind,forward,inverse,bad) in enumerate(reversed(self.events)):
            if kind=='map':self.payload=apply_record_map(self.payload,inverse)
            elif kind=='repair':self.payload,_=apply_record_repair(self.payload,bad,inverse,self.width)
            else:self.payload,_=joint_embed(self.payload,inverse,forward)
            if (index+1)%20==0:self.emit({'inverse_events_completed':index+1,'total':len(self.events)})


def composed(events,inverse=False):
    def function(address):
        for kind,forward,backward,bad in reversed(events) if inverse else events:
            assert kind!='embed'
            f=backward if inverse else forward
            if kind=='map' or bad(address):address=f(address)
        return address
    return function


def bit_fanout(machine,ybits,ubits,scratch,owners,K=5,G=1):
    total=len(ybits);H=(total+K-1)//K
    assert len(scratch)>=3*H
    scratch=scratch[:3*H]
    middle=ybits+ubits+[bit for bit in range(machine.width)
                       if bit not in set(ybits+ubits+scratch)]
    U=Bits(scratch[:H]);T=Bits(scratch[H:2*H]);Y=Bits(middle);B=Bits(scratch[2*H:])
    middle_width=len(middle);mask=(1<<H)-1
    assert len(set(middle+scratch))==machine.width
    for rho in range(min(K,total)):
        active=tuple(i for i in range(H) if rho+i*K<total)
        targets=tuple(rho+i*K for i in active)
        source_positions=tuple(total+owners[target] for target in targets)
        actual_targets=tuple(ybits[target] for target in targets)
        actual_sources=tuple(ubits[owners[target]] for target in targets)
        def raw(address,inverse=False,active=active,targets=targets,sources=source_positions):
            q={'u':U.get(address),'t':T.get(address),'y':Y.get(address),'b':B.get(address)}
            widths={'u':H,'t':H,'y':middle_width,'b':H}
            def offset(kind):
                if kind in ('first','second'):
                    return sum(((q['u']>>i)&1)*(2*((q['t']>>i)&1) if kind=='first' else
                               1-2*((q['t']>>i)&1))*(1<<target)
                               for i,target in zip(active,targets))
                if kind=='source':
                    return sum(((q['y']>>source)&1)<<i for i,source in zip(active,sources))
                return sum((((q['y']>>target)&1)^(((q['u']>>i)&1) if kind=='unload_t' else 0))<<i
                           for i,target in zip(active,targets))
            identity=(('r','y','first',1),('s','t','b',0),('r','b','load_t',1),('s','t','b',0),
                      ('r','y','second',1),('s','t','b',0),('r','b','unload_t',-1),('s','t','b',0))
            ops=identity+(('s','u','b',0),('r','b','source',1),('s','u','b',0))+identity+(
                ('s','u','b',0),('r','b','source',-1),('s','u','b',0))
            for action,target,kind,sign in reversed(ops) if inverse else ops:
                if action=='s':q[target],q[kind]=q[kind],q[target]
                else:q[target]=(q[target]+(-sign if inverse else sign)*offset(kind))% (1<<widths[target])
            return U.put(q['u'])|T.put(q['t'])|Y.put(q['y'])|B.put(q['b'])
        def raw_inverse(address,raw=raw):return raw(address,True)
        def bad(address,active=active,targets=targets):
            u,t,y=U.get(address),T.get(address),Y.get(address)
            return any(((u>>i)&1) or ((t>>i)&1) or not (4<=((y>>target)&31)//2<12)
                       for i,target in zip(active,targets))
        def toggle(address,ts=actual_targets,ss=actual_sources):
            return address^sum(((address>>source)&1)<<target for target,source in zip(ts,ss))
        def key(address,toggle=toggle,raw_inverse=raw_inverse):return toggle(raw_inverse(address))
        def inverse_key(address,toggle=toggle,raw=raw):return raw(toggle(address))
        machine.permutation(f'F_u-rho{rho}-ten-rotations',raw,raw_inverse)
        machine.repair(f'F_u-rho{rho}-actual-radix-repair',bad,key,inverse_key)


def compiled_rotation(machine,node_specs,all_fields,donor_bits,case_metrics,G_outer=2):
    m=len(node_specs);target_widths=tuple(len(all_fields[right].positions) for left,right,sl,sr,mu in node_specs)
    ybits=[bit for left,right,sl,sr,mu in node_specs for bit in all_fields[right].positions]
    # The OUTER T guards are dormant during each completed BIT fanout. They
    # may be reused among its inner scratch fields, provided all U source
    # bits are excluded and the completed exact repair returns all scratch.
    K_inner=8
    H=(len(ybits)+K_inner-1)//K_inner;need=G_outer*m+max(G_outer*m,3*H)
    if len(donor_bits)<need:return False
    ubits=donor_bits[:G_outer*m];tbits=donor_bits[G_outer*m:2*G_outer*m];scratch=donor_bits[G_outer*m:G_outer*m+3*H]
    U=Bits(ubits);T=Bits(tbits)
    owner=[G_outer*i for i,width in enumerate(target_widths) for _ in range(width)]
    before=machine.payload[:];start=len(machine.events)
    def values(address):return tuple(all_fields[right].get(address) for left,right,sl,sr,mu in node_specs)
    def put_values(address,y):
        for value,(left,right,sl,sr,mu) in zip(y,node_specs):address=all_fields[right].replace(address,value)
        return address
    def offsets(address):
        return tuple((mu*all_fields[left].get(address))%sr if all_fields[left].get(address)<sl else 0
                     for left,right,sl,sr,mu in node_specs)
    def bounds(address,phase):
        fs=offsets(address)
        return tuple((0,sr) if phase==0 else (0,f) if phase==1 else (f,sr)
                     for f,(left,right,sl,sr,mu) in zip(fs,node_specs))
    def conditional(phase):
        bit_fanout(machine,ybits,ubits,scratch,owner,K=K_inner)
        def add(address,inverse=False):
            control=U.get(address);centers=bounds(address,phase)
            fs=tuple(((a+b)%(1<<width)) if ((control>>(G_outer*i))&1) else 0
                     for i,((a,b),width) in enumerate(zip(centers,target_widths)))
            y,guards=(inverse_batched_add if inverse else batched_add)(values(address),
                        unpack(T.get(address),(G_outer,)*m),fs,target_widths,G_outer)
            return T.replace(put_values(address,y),pack(guards,(G_outer,)*m))
        machine.permutation('actual-guarded-binary-addition',add,lambda address:add(address,True))
    for phase in range(3):
        conditional(phase)
        def load(address,sign=1,phase=phase):
            predicate=tuple(int(a<=y<b) for y,(a,b) in zip(values(address),bounds(address,phase)))
            new=(U.get(address)+sign*pack(predicate,(G_outer,)*m))% (1<<(G_outer*m))
            return U.replace(address,new)
        machine.permutation('computed-predicate-load',load,lambda address,load=load:load(address,-1))
        conditional(phase)
        machine.permutation('computed-predicate-unload',lambda address,load=load:load(address,-1),load)
    raw_events=machine.events[start:];forward=composed(raw_events);backward=composed(raw_events,True)
    def ideal(address,inverse=False):
        fs=offsets(address);y=[]
        for value,f,(left,right,sl,sr,mu) in zip(values(address),fs,node_specs):
            y.append((value+(-f if inverse else f))%sr if value<sr else value)
        return put_values(address,y)
    def bad(address):
        return any(x==(1<<G_outer)-1 for x in unpack(U.get(address),(G_outer,)*m)+unpack(T.get(address),(G_outer,)*m))
    def key(address):return ideal(backward(address))
    def inverse_key(address):return forward(ideal(address,True))
    wrong=sum(x!=y for x,y in zip(machine.payload,apply_record_map(before,ideal)))
    machine.repair('three-reflection-OUTER-repair',bad,key,inverse_key)
    assert machine.payload==apply_record_map(before,ideal),'compiled interval rotation mismatch'
    case_metrics.append({'active_nodes':m,'target_widths':target_widths,'donor_available_bits':len(donor_bits),
                         'borrowed_U_T_bits':2*G_outer*m,'outer_guard_bits':G_outer,'borrowed_F_u_scratch_bits':3*H,
                         'added_address_bits':0,'wrong_before_outer_repair':wrong,
                         'K_inner':K_inner,'inner_scratch_reuses_outer_T':True,
                         'actual_F_u_calls':6*min(K_inner,len(ybits)),
                         'actual_F_u_rotations':60*min(K_inner,len(ybits))})
    machine.emit({'compiled_node_batch':case_metrics[-1],'events_completed':len(machine.events)})
    return True


def ordinary_rotation(machine,spec,all_fields):
    left,right,sl,sr,mu=spec
    def f(address,inverse=False):
        a,b=all_fields[left].get(address),all_fields[right].get(address)
        shift=mu*a%sr if a<sl else 0
        return all_fields[right].replace(address,(b+(-shift if inverse else shift))%sr) if b<sr else address
    machine.permutation('bounded-small-node-ordinary-rotation',f,lambda address:f(address,True))


def run(primes):
    started=time.monotonic();N=sum((s-1).bit_length() for s in primes);S=math.prod(primes);T=1<<N
    initial=[i+1 if i<S else 0 for i in range(T)]
    progress=[];machine=Machine(initial[:],N,progress);groups=[tuple(primes)];metrics=[];level=0
    while any(len(group)>1 for group in groups):
        old=[shape(group) for group in groups];new_groups=[];nodes=[]
        for group in groups:
            if len(group)==1:new_groups.append(group)
            else:
                # Reserve the original last leaf after one ordinary root
                # split, then balance the remaining leaves. Depth stays
                # 1+O(log d); this is not a chain of d scalar splits.
                at=len(group)-1 if level==0 else len(group)//2
                left,right=group[:at],group[at:];i=len(new_groups)
                new_groups.extend((left,right));sl,_=shape(left);sr,_=shape(right)
                nodes.append((i,i+1,sl,sr,pow(sl,-1,sr)))
        new=[shape(group) for group in new_groups];machine.embedding('joint-split',old,new)
        fs=fields([width for s,width in new]);done=set()
        # Try all independent nodes together when there are enough inactive bits;
        # otherwise use inactive-node classes. No bank bit comes from an active
        # node's LEFT or RIGHT words.
        for batch in ([nodes] if len(nodes)>1 else [])+[[node] for node in nodes]:
            batch=[node for node in batch if node[0] not in done]
            if not batch:continue
            active={index for left,right,sl,sr,mu in batch for index in (left,right)}
            donors=[bit for i,field in enumerate(fs) if i not in active for bit in field.positions]
            if compiled_rotation(machine,batch,fs,donors,metrics):done.update(node[0] for node in batch)
        for node in nodes:
            if node[0] not in done:ordinary_rotation(machine,node,fs)
        assert all(value==0 or valid(address,new) for address,value in enumerate(machine.payload))
        level+=1;groups=new_groups
        machine.emit({'forward_CRT_level':level,'allocated_records':T,'valid_records':S,
                      'padding_restored':True,'compiled_batches':len(metrics)})
    caps=[1<<((s-1).bit_length()) for s in primes];expected=[0]*T;prefix=1;mus=[]
    for s in primes:mus.append(pow(prefix,-1,s));prefix*=s
    for k in range(S):
        digits=[mu*k%s for mu,s in zip(mus,primes)];target=0;stride=1
        for value,capacity in zip(digits,caps):target+=value*stride;stride*=capacity
        expected[target]=k+1
    assert machine.payload==expected,'full CRT leaf oracle mismatch'
    machine.emit({'full_CRT_leaf_oracle':'PASS','events':len(machine.events)})
    machine.inverse();assert machine.payload==initial,'full reverse pipeline mismatch'
    assert metrics,'family never invoked actual F_u compilation'
    return {'primes':primes,'address_bits':N,'allocated_records':T,'valid_records':S,
            'initial_padding_provenance':'input k+1 for0<=k<S; every other payload explicitly zero',
            'added_address_bits':0,'compiled_batches':metrics,'full_leaf_oracle':True,
            'full_reverse_pipeline':True,'all_padding_boundaries_restored':True,
            'events':len(machine.events),'ledger':machine.ledger,'wall_seconds':time.monotonic()-started}


def main():
    p=argparse.ArgumentParser();p.add_argument('--family',choices=('bank17','bank131'),required=True)
    p.add_argument('--output',required=True);a=p.parse_args()
    primes=(3,5,7,11,{'bank17':17,'bank131':131}[a.family])
    result=run(primes);result.update({'run_id':'20261008T1500Z-compiled-crt-guard2-'+a.family,'status':'PASS',
         'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'guard_dependency_sha256':hashlib.sha256(Path(__file__).with_name('crt_guard_controls.py').read_bytes()).hexdigest(),
         'workers':1,'native_threads':1,'scope':'Actual F_u inside compiled CRT, actual multistage reverse-key radix repairs; finite model, no tape complexity measurement'})
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'PASS','run_id':result['run_id'],'wall_seconds':result['wall_seconds']}),flush=True)


if __name__=='__main__':main()
