#!/usr/bin/env python3
"""Exact fixed-grid C factorization and same-volume full guard allocation.

At each node, elementary C kernels preprocess one complete K-axis chunk per
slot plus remainders. Child active chunks compact by paid equal-K swaps and
return by exact inverse swaps. No payload rows or address range are added.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time

TOPIC=Path(__file__).resolve().parents[2]
CONFIG=TOPIC/'configs/transfers/guarded-slot-layout.json'


def plan(e,h,root_r=None):
    labels=list(range(e));events=[];paid=Counter();children=[]
    def kernel(axis,category,level):
        events.append(('kernel',axis,category,level,labels[axis]));paid[labels[axis]]+=1
    def swap(a,b,level,direction):
        events.append(('chunk_swap',a,b,level,direction));labels[a],labels[b]=labels[b],labels[a]
    def node(active,level,r=None):
        if active<2*h:
            for axis in range(active):kernel(axis,'elementary-leaf',level)
            return
        f=active//h-1;r=h if r is None else r
        guards=[i*(f+1)+f for i in range(h)]
        remainder=list(range(h*(f+1),active))
        guard_labels=[labels[x] for x in guards]
        for axis in guards:kernel(axis,'complete-slot-guard',level)
        for axis in remainder:kernel(axis,'remainder',level)
        selected=[i*(f+1)+j for i in range(r) for j in range(f)]
        selected_labels={labels[x] for x in selected};length=r*f
        holes=sorted(set(range(length))-set(selected))
        donors=sorted(set(selected)-set(range(length)))
        if len(holes)!=len(donors) or len(holes)>r:raise ValueError('More than r full-K compaction swaps needed')
        swaps=list(zip(holes,donors));original=list(labels)
        for a,b in swaps:swap(a,b,level,'enter')
        if {labels[i] for i in range(length)}!=selected_labels:raise ValueError('Child active axes not contiguous after paid compaction')
        if any(label in guard_labels for label in labels[:length]):raise ValueError('An already processed guard entered child active range')
        if length>=active:raise ValueError('The apparent same-width child did not decrease actual e')
        children.append(dict(parent_e=active,level=level,native_r=r,columns=f,
            complete_slot_K_chunks=f+1,guard_axes=guards,remainder_axes=remainder,
            elementary_preprocessing=len(guards)+len(remainder),child_e=length,
            old_child_upper=r*(active//h),compaction_swaps=[list(x) for x in swaps],
            child_active_axes_contiguous=True,already_transformed_guards_excluded=True,
            complete_payload_volume_unchanged=True))
        node(length,level+1)
        for a,b in reversed(swaps):swap(a,b,level,'return')
        if labels!=original:raise ValueError('Logical chunk names not restored after child')
    node(e,0,root_r)
    if labels!=list(range(e)) or any(count!=1 for count in paid.values()):raise ValueError('A logical axis was transformed twice or not restored')
    if root_r==h or root_r is None:
        if set(paid)!=set(range(e)):raise ValueError('Full C factorization omitted an axis')
    return dict(e=e,h=h,root_r=h if root_r is None else root_r,events=events,
        kernel_original_axes=dict(sorted(paid.items())),children=children,
        root_target_axes=sorted(paid),total_elementary_C=sum(paid.values()),
        total_whole_K_swaps=sum(event[0]=='chunk_swap' for event in events),
        maximum_depth=max([event[3] if event[0]=='kernel' else event[3] for event in events],default=0))


def axis_kernel(payload,axis,k,rho,e,prefix,suffix,fixed_grid=False):
    mask=1<<(axis*k+rho);size=1<<(e*k);result=list(payload)
    for head in range(prefix):
        for address in range(size):
            if address&mask:continue
            for tail in range(suffix):
                low=(head*size+address)*suffix+tail;high=low+mask*suffix
                a=payload[low];b=payload[high];left=[];right=[]
                for j in (0,2):
                    ar,ai=a[j:j+2];br,bi=b[j:j+2]
                    left += [ar-ai+br+bi,ar+ai+bi-br]
                    right += [ar+ai+br-bi,ai-ar+br+bi]
                if fixed_grid:
                    if any(x%2 for x in left+right):raise ValueError('Fixed physical grid reserve exhausted')
                    left=[x//2 for x in left];right=[x//2 for x in right]
                result[low]=tuple(left);result[high]=tuple(right)
    return result


def chunk_swap(payload,a,b,k,e,prefix,suffix):
    size=1<<(e*k);mask=(1<<k)-1;result=[None]*len(payload)
    for head in range(prefix):
        for address in range(size):
            av=(address>>(a*k))&mask;bv=(address>>(b*k))&mask
            changed=address ^ ((av^bv)<<(a*k)) ^ ((av^bv)<<(b*k))
            for tail in range(suffix):result[(head*size+changed)*suffix+tail]=payload[(head*size+address)*suffix+tail]
    if any(x is None for x in result):raise ValueError('Complete chunk swap omitted a record')
    return result


def run(spec,payload,k,rho,prefix,suffix,negative=None,fixed_grid=False):
    reserve=spec['total_elementary_C'] if fixed_grid else 0
    data=[tuple(x<<reserve for x in row) for row in payload];grid=3+reserve;guards_omitted=False
    for event in spec['events']:
        if event[0]=='kernel':
            _,axis,category,level,label=event
            if negative=='omit guard' and category=='complete-slot-guard' and not guards_omitted:
                guards_omitted=True;continue
            data=axis_kernel(data,axis,k,rho,spec['e'],prefix,suffix,fixed_grid)
            if not fixed_grid:grid+=1
            if negative=='duplicate guard' and category=='complete-slot-guard' and not guards_omitted:
                data=axis_kernel(data,axis,k,rho,spec['e'],prefix,suffix,fixed_grid)
                if not fixed_grid:grid+=1
                guards_omitted=True
        else:
            _,a,b,level,direction=event
            if negative=='omit return swap' and direction=='return':continue
            data=chunk_swap(data,a,b,k,spec['e'],prefix,suffix)
    return data,grid


def equal(a,b):
    av,abits=a;bv,bbits=b
    return len(av)==len(bv) and all(tuple(x<<bbits for x in row)==tuple(x<<abits for x in other) for row,other in zip(av,bv))


def reference(spec,payload,k,rho,prefix,suffix):
    data=list(payload)
    for axis in spec['root_target_axes']:data=axis_kernel(data,axis,k,rho,spec['e'],prefix,suffix)
    return data,3+len(spec['root_target_axes'])


def literal_tensor_column(e,address,field):
    # Direct coefficient alpha^e * (-i)^popcount(a xor b), with no
    # factorization/permutation code and no fraction normalization.
    real,imag=1,0
    for _ in range(e):real,imag=real-imag,real+imag
    result=[]
    for output in range(1<<e):
        q=(field%2-(output^address).bit_count())%4
        pair=((real,imag),(-imag,real),(-real,-imag),(imag,-real))[q]
        result.append((*pair,0,0) if field<2 else (0,0,*pair))
    return result,3+e


def probe(case):
    e,k,rho,prefix,suffix,r,all_columns=case;started=time.monotonic();spec=plan(e,4,r);size=prefix*(1<<(e*k))*suffix
    digest=sha256();columns=0;field_receipts=[]
    if all_columns:
        if (k,rho,prefix,suffix,r)!=(1,0,1,1,4):raise ValueError('Complete tensor-column oracle only covers declared K1 full-target case')
        for address in range(size):
            for field in range(4):
                values=[(0,0,0,0)]*size;unit=[0]*4;unit[field]=1;values[address]=tuple(unit)
                actual=run(spec,values,k,rho,prefix,suffix)
                wanted=literal_tensor_column(e,address,field)
                if not equal(actual,wanted):raise ValueError('Complete literal tensor C coefficient failed')
                columns+=1;digest.update(str(actual).encode())
    for field in range(2):
        values=[((i*7+field*11)%31-15,(i*13+field*17)%29-14,(i*19+field*5)%37-18,(i*23+field*3)%41-20) for i in range(size)]
        actual=run(spec,values,k,rho,prefix,suffix);wanted=reference(spec,values,k,rho,prefix,suffix)
        if not equal(actual,wanted):raise ValueError('Complete dirty Gaussian field factorization failed')
        fixed=run(spec,values,k,rho,prefix,suffix,fixed_grid=True)
        if fixed!=actual or fixed[1]!=3+spec['total_elementary_C']:
            raise ValueError('Literal fixed physical grid replay differs from variable-grid reference')
        digest.update(str(actual).encode());field_receipts.append(dict(final_grid_bits=actual[1],maximum_numerator_bits=max(abs(x).bit_length() for row in actual[0] for x in row)))
    names=['omit guard','duplicate guard']
    has_return=any(event[0]=='chunk_swap' and event[-1]=='return' for event in spec['events'])
    if has_return:names.append('omit return swap')
    controls={name:not equal(run(spec,values,k,rho,prefix,suffix,name),wanted) for name in names}
    if not all(controls.values()):raise ValueError('An applicable guard/complete-return negative did not discriminate')
    # Sparse row/suffix origins bind block-diagonal endpoint semantics.
    for head in range(prefix):
        for tail in range(suffix):
            values=[(0,0,0,0)]*size;values[(head*(1<<(e*k)))*suffix+tail]=(1,2,3,4)
            transformed,_=run(spec,values,k,rho,prefix,suffix)
            for index,value in enumerate(transformed):
                if value!=(0,0,0,0) and (index//((1<<(e*k))*suffix),index%suffix)!=(head,tail):
                    raise ValueError('A row-prefix or suffix changed at the complete endpoint')
    return dict(e=e,k=k,rho=rho,prefix=prefix,suffix=suffix,root_native_r=r,
        complete_records=size,all_payload_fields=4,complete_input_columns=columns,
        complete_literal_tensor_coefficients=columns*size,full_dirty_fields=2,
        plan=spec,physical_global_grid_never_reduced=True,literal_fixed_physical_grid_replayed=True,
        fixed_physical_grid_bits=3+spec['total_elementary_C'],integer_C_halves_exact_without_normalization=True,field_receipts=field_receipts,
        complete_guard_axes_transformed_exactly_once=True,row_prefix_and_suffix_unchanged=True,
        child_selected_axes_contiguous_and_guard_free=True,same_width_actual_e_strictly_decreases=True,
        no_rows_or_address_ranges_added=True,negative_controls=controls,
        return_swap_control_applicable=has_return,
        output_sha256=digest.hexdigest(),seconds=time.monotonic()-started,
        scope='Exact finite guard preprocessing/compaction/C-factorization with complete four-field records; original tape costs and whole native network remain conditional')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4);parser.add_argument('--small',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args();config=json.loads(CONFIG.read_text());paths=[Path(__file__).resolve(),CONFIG]
    pins={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,source_config_sha256=pins,seed=None,
        producer_imports=False,scope=config['scope'],native_threads_per_worker=1)
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False);(args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    cases=[(8,1,0,1,1,4,True),(12,1,0,2,2,4,False),(8,2,1,1,1,2,False),(9,1,0,3,2,1,False)]
    if args.small:cases=[(8,1,0,1,1,4,False),(9,1,0,3,2,1,False)]
    started=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:results=list(pool.map(probe,cases))
    if any(sha256((TOPIC/path).read_bytes()).hexdigest()!=value for path,value in pins.items()):raise ValueError('Source changed during immutable attempt')
    summary=dict(status='EXACT SAME-VOLUME FULL GUARD C FACTORIZATION PASS',cases=results,seconds=time.monotonic()-started,
        scope=config['scope'],whole_new_native_profile_certified=False,new_exponent=False)
    if args.output:(args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ['status','seconds','scope']}))


if __name__=='__main__':main()
