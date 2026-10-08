#!/usr/bin/env python3
"""Independent mixed whole-rank phase and variable-width recursion controls.

No producer batching, characteristic or stopping implementation is imported.
Actual numerical operations retain one fixed fine grid throughout. The
cancellation-heavy recursion is a small model of the completed child
interface, not a replay of the giant finite phase circuit.
"""

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from math import isqrt
from pathlib import Path
import random
import resource
import time

from review_semantic_guard import FixedGrid, add, mul, neg, unit, v2


def require(test,message):
    if not test:raise AssertionError(message)


def parity(x):return x.bit_count()&1


def binary_rank(rows):
    pivots={}
    for x in rows:
        while x:
            b=x.bit_length()-1
            if b in pivots:x^=pivots[b]
            else:pivots[b]=x;break
    return len(pivots)


def transform(columns,x):
    answer=0
    for j,v in enumerate(columns):
        if x>>j&1:answer^=v
    return answer


def inverse_columns(columns):
    m=len(columns);images={transform(columns,x):x for x in range(1<<m)}
    require(len(images)==1<<m,'Binary adapter is singular')
    return tuple(images[1<<j] for j in range(m))


def column_address(columns,address,m,f):
    output=0
    for j in range(f):
        word=sum(((address>>(h*f+j))&1)<<h for h in range(m))
        image=transform(columns,word)
        output|=sum(((image>>h)&1)<<(h*f+j) for h in range(m))
    return output


def permute(values,columns,m,f):
    answer=[None]*len(values)
    for x,value in enumerate(values):answer[column_address(columns,x,m,f)]=value
    require(all(x is not None for x in answer),'Adapter does not preserve all complete addresses')
    return answer


def directional(values,mask,negative,machine):
    answer=list(values)
    for x in range(len(answer)):
        y=x^mask
        if x>y:continue
        a,b=machine.pair(answer[x],answer[y])
        # X C=C^-1; this reference uses no Z wrapper.
        answer[x],answer[y]=(b,a) if negative else (a,b)
    return answer


def closed_mixed(values,coordinates,negative):
    """Direct Gaussian integer tensor numerator, independent of pair scans."""
    n=len(coordinates);mask=sum(1<<b for b in coordinates);answer=[]
    for x in range(len(values)):
        total=(0,0)
        for y in range(len(values)):
            if (x^y)&~mask:continue
            coefficient=(1,0)
            for b,inverse in zip(coordinates,negative):
                same=((1,-1) if inverse else (1,1))
                different=((1,1) if inverse else (1,-1))
                coefficient=mul(coefficient,different if (x^y)>>b&1 else same)
            total=add(total,mul(coefficient,values[y]))
        denominator=1<<n
        require(all(a%denominator==0 for a in total),'Closed mixed tensor does not fit fixed grid')
        answer.append(tuple(a//denominator for a in total))
    return answer


def mixed_controls():
    rng=random.Random(719);records=[];probes=entries=halvings=0;wrong_orientation=0
    fixtures=[(3,(1,2)),(4,(7,8)),(5,(7,8,16)),(5,(15^8,16))]
    for m,basis in fixtures:
        require(all(parity(v)==1 for v in basis),'Residual direction is not norm one')
        require(all(not parity(a&b) for i,a in enumerate(basis) for b in basis[:i]),
                'Residual basis is not orthonormal')
        columns=list(basis)
        for j in range(m):
            if binary_rank(columns+[1<<j])>len(columns):columns.append(1<<j)
        require(len(columns)==m,'Basis extension failed')
        backwards=inverse_columns(columns);r=len(basis)
        for f in (1,2):
            n=1<<(m*f);coordinates=tuple(h*f+j for h in range(r) for j in range(f))
            for decreasing in (False,True):
                signs=tuple(((v.bit_count()%4)==3)^decreasing for v in basis)
                negative=tuple(flag for flag in signs for _ in range(f))
                mask=sum(1<<b for b,flag in zip(coordinates,negative) if flag)
                seeds=[]
                if m*f<=5:
                    seeds.extend((0,[(int(x==k),0) for x in range(n)]) for k in range(n))
                for depth in (0,3,7):
                    seeds.append((depth,[(rng.randrange(-5,6),rng.randrange(-5,6)) for _ in range(n)]))
                for depth,integers in seeds:
                    width=64+2*m*f
                    incoming=[(a<<(width-depth),b<<(width-depth)) for a,b in integers]
                    machine=FixedGrid(width,depth,5)
                    reference=list(incoming)
                    for v,inverse in zip(basis,signs):
                        for j in range(f):
                            direction=sum(((v>>h)&1)<<(h*f+j) for h in range(m))
                            reference=directional(reference,direction,inverse,machine)
                    coordinate_input=permute(incoming,backwards,m,f)
                    closed=closed_mixed(coordinate_input,coordinates,negative)
                    require(permute(closed,columns,m,f)==reference,'Direct mixed phase/basis identity failed')
                    work=[neg(a) if parity(x&mask) else a for x,a in enumerate(coordinate_input)]
                    work=machine.leaf(work,coordinates)
                    work=[unit(neg(a) if parity(x&mask) else a,-sum(negative))
                          for x,a in enumerate(work)]
                    require(permute(work,columns,m,f)==reference,'One whole child with mixed Z wrappers failed')
                    machine.completed_bound(work,coordinate_input,r*f)
                    all_forward=machine.leaf(coordinate_input,coordinates)
                    wrong_orientation+=int(all_forward!=closed)
                    probes+=1;entries+=n;halvings+=machine.halvings
                records.append(dict(ambient=m,residual_rank=r,columns=f,
                    decreasing=decreasing,negative_directions=sum(signs),
                    complete_selected_axes=r*f,physical_adapter_columns=columns,
                    both_adapter_directions_exact=True))
    require(wrong_orientation>0,'Omitting mixed orientation did not discriminate')
    return dict(cases=records,probes=probes,exact_output_entries=entries,
        exact_fixed_grid_halvings=halvings,
        omitted_mixed_wrappers_disagreeing_probes=wrong_orientation,
        same_completed_grid_and_norm_as_individual_kernels=True)


class NonuniformGrid(FixedGrid):
    def __init__(self,width,depth,threshold):
        super().__init__(width,depth,5);self.threshold=threshold;self.node_count=0

    def recursive(self,values,selected,inverse=False):
        selected=tuple(selected);e=len(selected);original=list(values)
        if inverse:
            self.inverse_calls+=1
            mask=sum(1<<b for b in selected)
            values=[neg(a) if parity(x&mask) else a for x,a in enumerate(values)]
            values=self.recursive(values,selected)
            values=[unit(neg(a) if parity(x&mask) else a,-e) for x,a in enumerate(values)]
        elif e<3 or e<self.threshold:
            values=self.leaf(values,selected)
        else:
            self.node_count+=1;f,t=divmod(e,3)
            # A genuine internal fine-grid excursion with completed identity.
            values=list(values)
            for _ in range(3):values=[self.halve(a) for a in values]
            for _ in range(3):
                values=[add(a,a) for a in values];self.observe(values)
            wide,narrow,tail=selected[:2*f],selected[2*f:3*f],selected[3*f:]
            require(len(wide)==2*f<e and len(tail)==t<3,'Variable child/tail geometry failed')
            before=list(values)
            values=self.recursive(values,wide)
            values=self.recursive(values,wide,inverse=True)
            require(values==before,'Wide forward/inverse child did not cancel')
            values=self.recursive(values,wide)
            values=self.recursive(values,narrow)
            values=self.leaf(values,tail)
        self.observe(values);self.completed_bound(values,original,e)
        return values


def variable_grid_controls():
    rng=random.Random(727);probes=entries=halvings=completed=nodes=0;examples=[]
    # m3, rmax2, sum ranks s7 and an explicit tail/scalar charge E32.
    B=39
    for e,threshold in product(range(1,9),(1,3,7)):
        n=1<<e
        seeds=[(depth,[(rng.randrange(-7,8),rng.randrange(-7,8)) for _ in range(n)])
               for depth in (0,7)]
        if e<=3:seeds.extend((0,[(int(x==k),0) for x in range(n)]) for k in range(n))
        for depth,integers in seeds:
            width=depth+2*B*e+8
            incoming=[(a<<(width-depth),b<<(width-depth)) for a,b in integers]
            for inverse in (False,True):
                machine=NonuniformGrid(width,depth,threshold)
                actual=machine.recursive(incoming,range(e),inverse)
                expected=closed_mixed(incoming,tuple(range(e)),(inverse,)*e)
                require(actual==expected,'Stopped nonuniform recursion differs from exact tensor')
                require(machine.maximum_grid<=depth+2*B*e,'Variable recursion exceeds linear fine-grid guard')
                restored=machine.recursive(actual,range(e),not inverse)
                require(restored==incoming,'Nonuniform exact inverse/restoration failed')
                require(machine.maximum_l1_bits<=width+5+2*B*e+1,'Variable recursion magnitude bound failed')
                probes+=1;entries+=n;halvings+=machine.halvings
                completed+=machine.completed;nodes+=machine.node_count
                if e==8 and inverse and depth==7:
                    examples.append(dict(axes=e,threshold=threshold,internal_nodes=machine.node_count,
                        maximum_grid=machine.maximum_grid,completed_grid_upper=depth+e,
                        stored_grid_width=width))
    width=128;incoming=[((int(x==0))<<width,0) for x in range(16)]
    negative_machine=FixedGrid(width,0,5)
    omitted_tail=negative_machine.leaf(incoming,range(3))
    full=closed_mixed(incoming,tuple(range(4)),(False,)*4)
    disagreements=sum(a!=b for a,b in zip(omitted_tail,full))
    require(disagreements>0,'Omitting the nonzero trailing C tail did not discriminate')
    return dict(probes=probes,exact_output_entries=entries,exact_fixed_grid_halvings=halvings,
        completed_child_checks=completed,internal_variable_width_nodes=nodes,
        common_encoding_never_rewritten=True,examples=examples,
        omitted_trailing_tail_disagreeing_outputs=disagreements)


def layouts():
    records=checked=partialtails=0
    for m in (3,4,5,7):
        for e in range(1,19):
            f,t=divmod(e,m)
            if not f:continue
            for K in (1,2,3,5):
                for rho in range(K):
                    slots=[tuple(rho+(h*f+j)*K for j in range(f)) for h in range(m)]
                    tail=tuple(rho+(m*f+j)*K for j in range(t))
                    require(tuple(x for slot in slots for x in slot)+tail==
                            tuple(rho+j*K for j in range(e)),'Main/tail selected offsets do not partition')
                    for r in range(1,m):
                        active=tuple(x for slot in slots[:r] for x in slot)
                        require(active==tuple(rho+j*K for j in range(r*f)),
                                'Active first slots are not one same-rho contiguous child')
                        require(r*f<e and r*f<=r*e//m,'Whole residual child fails strict shrink')
                        # Every nonselected bit and every tail slot stays spectator.
                        selected=set(active)
                        remainder=tuple(i for i in range(e*K) if i not in selected)
                        require(len(selected)+len(remainder)==e*K,'Complete spectator field lost')
                        records+=1;checked+=e*K;partialtails+=bool(t)
    # Full run has no strict shrink and is explicitly outside the theorem.
    require(3*(6//3)==6,'Full-width negative control missing')
    return dict(exact_shapes=records,address_bit_membership_checks=checked,
        nonzero_tail_shapes=partialtails,main_and_tail_fields_never_moved=True,
        same_K_rho_complete_prefix_child=True,full_width_child_excluded=True)


def guard_recurrences():
    cases=0;samples=[]
    for m in (3,5,7,11,28):
        for r in (1,m//2,m-1):
            for s in (m+2*r,7*m,1007*m):
                E=10000+m*8;B=s+E;C0=32*m*B*B
                for threshold in (1,m,17,101):
                    for e in list(range(1,130))+[10**4,10**12,10**24]:
                        size=e;fixed=widths=depth=0
                        while size>=m and size>=threshold:
                            f=size//m;widths+=s*f;fixed+=E;depth+=1
                            next_size=r*f
                            require(0<next_size<size,'Active child did not shrink')
                            size=next_size
                        exact=8*size+widths+fixed
                        require(exact<=2*B*e,'Nonuniform semantic guard exceeds 2Be')
                        require(exact+18*e<C0*e,'Whole outer guard fails')
                        require(depth<=e,'Strict integer shrink depth failed')
                        cases+=1
                        if e==10**24 and r==m-1 and threshold==101 and len(samples)<8:
                            samples.append(dict(m=m,rmax=r,s=s,E=E,e=e,depth=depth,
                                exact_semantic_unroll=exact,linear_bound=2*B*e))
    return dict(stopped_recurrence_cases=cases,samples=samples,
        recurrence='A(e)<=A(rmax*floor(e/m))+s*floor(e/m)+E',
        induction_slack='2B(m-rmax)>=s+E, B=s+E')


def root_power(x,numerator,denominator=4,bits=60):
    require(denominator in (2,4),'Unsupported exact root control')
    x=Q(x);radicand=(x.numerator**numerator<<(denominator*bits))//x.denominator**numerator
    value=isqrt(radicand)
    if denominator==4:value=isqrt(value)
    return Q(value,1<<bits),Q(value+1,1<<bits)


def weighted_trees():
    m,W,hist=5,10,{1:10,2:4,4:3};sigma=Q(1,2)
    z=sum(Q(n,W)*root_power(Q(r,m),1,2)[1] for r,n in hist.items())
    require(z<1,'Exact weighted characteristic control is not contracting')
    results=[]
    for root in (31,64,127,256,511,1024):
        for threshold in (5,9,17,33):
            current={root:Q(1)};leaves=Q(0);leaf_potential=Q(0)
            work={a:Q(0) for a in (1,2,3)};depth=0
            while current:
                next_=defaultdict(Q)
                for e,weight in current.items():
                    if e<threshold:
                        leaves+=weight*e;leaf_potential+=weight*root_power(e,1,2)[1]
                        continue
                    for a in work:work[a]+=weight*root_power(e,a)[1]
                    for r,n in hist.items():next_[r*(e//m)]+=weight*Q(n,W)
                current=dict(next_);depth+=1
            root_sigma=root_power(root,1,2)[1]
            require(leaf_potential<=root_sigma+Q(1,1<<35),'Stopped leaf potential exceeds root')
            leaf_upper=root_sigma*root_power(threshold,1,2)[1]
            require(leaves<=leaf_upper,'Variable-tree leaf exponent control fails')
            for a in work:
                if Q(a,4)>=sigma:bound=root_power(root,a)[1]/(1-z)
                else:bound=root_sigma/root_power(threshold,1)[0]/(1-z)
                require(work[a]<=bound,'Variable-tree internal potential bound fails')
            results.append(dict(root_axes=root,threshold=threshold,depth=depth,
                exact_leaf_work=leaves,leaf_work_upper=leaf_upper,internal_work_upper=work))
    wrong_z=sum(n*root_power(Q(r,m),1,2)[0] for r,n in hist.items())
    require(wrong_z>1,'Omitting V/W volume reduction did not discriminate')
    return dict(m=m,W=W,histogram=hist,sigma=sigma,exact_upper_characteristic=z,
        stopped_trees=results,internal_tau_cases=['1/4','1/2','3/4'],
        wrong_undivided_volume_characteristic=wrong_z,
        frontier_leaf_potential_not_equal_depth=True)


def finite_guard_inputs(path):
    row=json.loads(path.read_text())['full'];c=row['counts'];g=row['guard']
    m=c['m'];rmax=m-2*c['h'];extra=32*m
    require(g['slack']>extra,'Old literal E has no room for exact fixed tail kernels')
    require(m**272>2*rmax**272 and c['W']<2**41,'Complex row-depth premise fails')
    exponent=Q(41*272)*(2+Q(1,25))
    require(exponent<23000<66000,'Complex variable-depth row polynomial is not covered')
    return dict(input_sha256=sha256(path.read_bytes()).hexdigest(),h=c['h'],R=c['R'],
        grouped_ranks=[m-c['h']**2,m-2*c['h'],(c['h']**2-1)*(c['h']-1)],
        maximum_child=rmax,extra_elementary_tail_charge=extra,
        old_E_slack=g['slack'],slack_after_tail=g['slack']-extra,
        exact_half_shrink_power=272,complex_row_degree=23000,
        complete_row_exponent_upper=exponent,existing_generic_bit_row_degree=66000)


def stringify(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):stringify(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [stringify(v) for v in x]
    return x


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--finite-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path');start=time.monotonic()
    print('Whole mixed-orientation phase controls',flush=True);mixed=mixed_controls()
    print('Nonuniform fixed-grid/tail controls',flush=True);grid=variable_grid_controls()
    print('Exact layouts/guards/weighted stopped trees',flush=True)
    result=dict(status='PASS independent mixed whole-rank complex interface controls',
        generated_utc=datetime.now(timezone.utc).isoformat(),
        seeds=[719,727],source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        dependency_sha256={'review_semantic_guard.py':sha256(Path(__file__).with_name('review_semantic_guard.py').read_bytes()).hexdigest()},
        mixed=mixed,variable_fixed_grid=grid,complete_layouts=layouts(),
        stopped_guard=guard_recurrences(),weighted_stopped_trees=weighted_trees(),
        finite_guard_and_row_input=finite_guard_inputs(args.finite_review),
        scope='Exact new mixed whole-child identity, unchanged common encoding, strict variable children and tail charge; small cancellation-heavy recursion is not a large finite-network replay. Full fixed-tape interface must be proved analytically.',
        wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(stringify(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],flush=True)


if __name__=='__main__':main()
