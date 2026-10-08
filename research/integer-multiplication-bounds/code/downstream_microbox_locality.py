#!/usr/bin/env python3
"""Exact finite controls for principal-window resampling and fractional cores.

This checks operator locality, wrapped windows, clipped structured cells,
and tensor core composition. It does not implement a fixed-tape bulk router.
Every comparison relevant to a threshold uses rational or integer arithmetic.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from pathlib import Path
import time


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def norm(a):
    return max((sum(map(abs,row),Q(0)) for row in a),default=Q(0))


def matmul(a,b):
    if not a:
        return []
    n=len(b)
    return [[sum((a[i][k]*b[k][j] for k in range(n)),Q(0))
             for j in range(len(b[0]))] for i in range(len(a))]


def inverse(a):
    n=len(a)
    z=[list(row)+[Q(int(i==j)) for j in range(n)] for i,row in enumerate(a)]
    for k in range(n):
        pivot=z[k][k]
        require(pivot!=0,'Zero exact pivot')
        z[k]=[x/pivot for x in z[k]]
        for i in range(n):
            if i==k or not z[i][k]:
                continue
            coefficient=z[i][k]
            z[i]=[x-coefficient*y for x,y in zip(z[i],z[k])]
    result=[row[n:] for row in z]
    require(matmul(a,result)==[[Q(int(i==j)) for j in range(n)] for i in range(n)],
            'Exact inverse product failed')
    return result


def cyclic(n,gap,w=1,sign=-1):
    require(2*w<n,'Cyclic neighbors overlap')
    a=[[Q(int(i==j)) for j in range(n)] for i in range(n)]
    coefficient=(1-gap)/(2*w)
    for i in range(n):
        for delta in range(1,w+1):
            a[i][(i+delta)%n]=sign*coefficient
            a[i][(i-delta)%n]=sign*coefficient
    return a


def principal(a,indices):
    return [[a[i][j] for j in indices] for i in indices]


def row_gap(a):
    return min(a[i][i]-sum((abs(x) for j,x in enumerate(a[i]) if j!=i),Q(0))
               for i in range(len(a)))


def off_diagonal(a):
    return [[x-Q(int(i==j)) for j,x in enumerate(row)] for i,row in enumerate(a)]


def locality_controls():
    powers=windows=rows=0
    max_ratio=Q(0)
    negatives=[]
    for n,g,w,sign in [(17,Q(1,2),1,-1),(19,Q(1,16),1,-1),
                        (23,Q(1,256),1,1),(29,Q(1,8),2,-1)]:
        h=cyclic(n,g,w,sign)
        hi=inverse(h)
        f=off_diagonal(h)
        require(norm(f)==1-g and norm(hi)<=1/g,'Global gap/inverse bound failed')
        for J in (1,2,3):
            halo=J*w
            core=2
            m=2*halo+core+1
            if m>=n:
                continue
            for start in (0,1,n-halo-1,n-2):
                ii=[(start+i)%n for i in range(m)]
                local=principal(h,ii)
                li=inverse(local)
                fl=off_diagonal(local)
                pg=[[Q(int(i==j)) for j in range(n)] for i in range(n)]
                pl=[[Q(int(i==j)) for j in range(m)] for i in range(m)]
                for k in range(J):
                    for r in range(halo,halo+core):
                        embedded=[Q(0)]*n
                        for j,v in zip(ii,pl[r]):embedded[j]=v
                        require(embedded==pg[ii[r]],'Short Neumann row crossed artificial cut')
                        powers+=n
                    pg=matmul(pg,f);pl=matmul(pl,fl)
                bound=2*(1-g)**J/g
                for r in range(halo,halo+core):
                    embedded=[Q(0)]*n
                    for j,v in zip(ii,li[r]):embedded[j]=v
                    error=sum((abs(x-y) for x,y in zip(hi[ii[r]],embedded)),Q(0))
                    require(error<=bound,'Principal inverse tail bound failed')
                    max_ratio=max(max_ratio,error/bound);rows+=1
                require(row_gap(local)>=g and norm(li)<=1/g,'Principal gap/inverse norm failed')
                windows+=1
        # A locally changed coefficient already breaks the first path identity.
        ii=list(range(7));local=principal(h,ii);changed=[r[:] for r in local]
        changed[3][4]+=g/8
        require(row_gap(changed)>0 and off_diagonal(changed)[3]!=f[3][:7],
                'Local rerounding negative did not discriminate')
        negatives.append({'n':n,'local_rerounding_breaks_first_path':True})
    # Row DD with diagonal!=1 alone does not justify a Neumann series in H-I.
    a=[[Q(2),Q(9,10)],[Q(9,10),Q(2)]]
    require(row_gap(a)>0 and norm(off_diagonal(a))>1,'Nonunit diagonal negative failed')
    normalized=[[v/a[i][i] for v in row] for i,row in enumerate(a)]
    require(norm(off_diagonal(normalized))<1,'Explicit diagonal normalization failed')
    return dict(windows=windows,core_rows=rows,exact_short_path_entries=powers,
                maximum_error_to_tail_bound=str(max_ratio),local_rerounding_negatives=negatives,
                nonunit_diagonal_requires_normalization=True)


def nearest(s,t,j):
    return (2*t*j+s)//(2*s)


def phase_controls():
    s,t,w=31,34,2
    cells=[]
    for j in range(s):
        phase=nearest(s,t,j)-j
        if not cells or phase!=nearest(s,t,cells[-1][0])-cells[-1][0]:cells.append([])
        cells[-1].append(j)
    lookup={j:ci for ci,cell in enumerate(cells) for j in cell}
    weights={j:Q(1,2**(12*(j-cell[0]))) for cell in cells for j in cell}
    g=[Q(1)]+[Q(1,2**(40*delta*delta)) for delta in range(1,w+1)]
    h=[[Q(int(i==j)) for j in range(s)] for i in range(s)]
    tiny=Q(1,256)
    for i in range(s):
        for delta in range(-w,w+1):
            if not delta:continue
            j=(i+delta)%s
            if lookup[i]==lookup[j] and abs(i-j)<=w:
                h[i][j]=weights[i]*g[abs(delta)]/weights[j]
            else:
                h[i][j]=-(1-2*tiny) if delta==1 else Q(0)
    require(row_gap(h)>tiny,'Structured finite H is not row DD')
    windows=gs_entries=schur_entries=empty=short=0
    for start,m in [(0,17),(3,17),(8,17),(23,17),(29,17),(27,23)]:
        lifted=list(range(start,start+m))
        ii=[j%s for j in lifted]
        a=principal(h,ii)
        pieces=[]
        for position,j in enumerate(lifted):
            cell=(j//s,lookup[j%s])
            if not pieces or cell!=pieces[-1][0]:pieces.append((cell,[]))
            pieces[-1][1].append(position)
        boundary=[];interiors=[]
        for _,piece in pieces:
            if len(piece)<=4*w:
                boundary+=piece;short+=1;empty+=1
            else:
                boundary+=piece[:w]+piece[-w:]
                interiors.append(piece[w:-w])
        require(sorted(boundary+sum(interiors,[]))==list(range(m)), 'Clipped partition failed')
        all_i=sum(interiors,[])
        for left,right in product(interiors,repeat=2):
            if left is right:continue
            require(all(a[i][j]==0 for i in left for j in right),'Distinct clipped interiors interact')
        sb=principal(a,boundary)
        for interior in interiors:
            local=principal(a,interior);li=inverse(local)
            # The same global weights conjugate each clipped interior exactly.
            for r,i in enumerate(interior):
                for c,j in enumerate(interior):
                    distance=abs(i-j)
                    want=g[distance] if distance<=w else Q(0)
                    actual=local[r][c]*weights[ii[j]]/weights[ii[i]]
                    require(actual==want,'Clipped global Toeplitz similarity failed');gs_entries+=1
            ib=[[a[i][j] for j in boundary] for i in interior]
            bi=[[a[i][j] for j in interior] for i in boundary]
            correction=matmul(matmul(bi,li),ib)
            sb=[[v-correction[i][j] for j,v in enumerate(row)] for i,row in enumerate(sb)]
        require(row_gap(sb)>=row_gap(a),'Clipped Schur row gap decreased')
        require(norm(sb)<=norm(a),'Clipped Schur row norm increased')
        for i,row in enumerate(sb):
            for j,v in enumerate(row):
                require(abs(i-j)<=2*w or v==0,'Noncyclic clipped Schur bandwidth failed')
                schur_entries+=1
        # Compare the Schur composition to the full principal inverse.
        ai=inverse(a);si=inverse(sb)
        rhs=[Q((7*j%17)-8,16) for j in range(m)]
        y=[Q(0)]*m
        for interior in interiors:
            li=inverse(principal(a,interior))
            for i,row in zip(interior,li):y[i]=sum((v*rhs[j] for j,v in zip(interior,row)),Q(0))
        rb=[rhs[i]-sum((a[i][j]*y[j] for j in all_i),Q(0)) for i in boundary]
        xb=[sum((v*b for v,b in zip(row,rb)),Q(0)) for row in si]
        result=[Q(0)]*m
        for i,v in zip(boundary,xb):result[i]=v
        for interior in interiors:
            ri=[rhs[i]-sum((a[i][j]*v for j,v in zip(boundary,xb)),Q(0)) for i in interior]
            li=inverse(principal(a,interior))
            for i,row in zip(interior,li):result[i]=sum((v*b for v,b in zip(row,ri)),Q(0))
        direct=[sum((v*b for v,b in zip(row,rhs)),Q(0)) for row in ai]
        require(result==direct,'Clipped Schur recovery is not the principal inverse');windows+=1
    return dict(s=s,t=t,w=w,windows=windows,global_cell_lengths=list(map(len,cells)),
                clipped_or_tiny_boundary_pieces=short,zero_interior_pieces=empty,
                exact_global_weight_conjugation_entries=gs_entries,exact_schur_band_entries=schur_entries)


def tensor_apply(values,matrices):
    """Apply complete local axis matrices in order, without refreshing halos."""
    current=dict(values)
    shape=tuple(len(matrix) for matrix in matrices)
    for axis,matrix in enumerate(matrices):
        output={}
        for index in product(*(range(n) for n in shape)):
            total=Q(0)
            for j,v in enumerate(matrix[index[axis]]):
                src=list(index);src[axis]=j
                total+=v*current[tuple(src)]
            output[index]=total
        current=output
    return current


def tensor_controls():
    records=[]
    for axes in (2,3):
        specs=[(8,Q(1,2),6),(9,Q(1,8),7),(10,Q(1,64),8)][:axes]
        rows_global=[];rows_local=[];matrices=[];windows=[];cores=[]
        maxerrors=[];bounds=[]
        for n,g,start in specs:
            h=cyclic(n,g);hi=inverse(h)
            ii=[(start+j)%n for j in range(6)]
            li=inverse(principal(h,ii))
            scale=1
            while scale<4/g:scale*=2
            matrix=[[v/scale for v in row] for row in li]
            require(norm(matrix)<=Q(1,4),'Local normalized contraction failed')
            matrices.append(matrix);windows.append(ii);cores.append((2,3))
            rg=[];rl=[];error=Q(0)
            for j in (2,3):
                rg.append([v/scale for v in hi[ii[j]]])
                row=[Q(0)]*n
                for k,v in zip(ii,matrix[j]):row[k]=v
                rl.append(row)
                error=max(error,sum((abs(x-y) for x,y in zip(rg[-1],row)),Q(0)))
            rows_global.append(rg);rows_local.append(rl);maxerrors.append(error)
            bounds.append(2*(1-g)**2/(g*scale))
        shape=tuple(n for n,_,_ in specs)
        full={index:Q((sum((i+3)*(j+5) for i,j in enumerate(index))%29)-14,16)
              for index in product(*(range(n) for n in shape))}
        restricted={index:full[tuple(window[j] for window,j in zip(windows,index))]
                    for index in product(*(range(6) for _ in specs))}
        actual=tensor_apply(restricted,matrices)
        maximum=Q(0);entries=0
        for out in product((0,1),repeat=axes):
            global_value=local_value=Q(0)
            for source,value in full.items():
                cg=cl=Q(1)
                for axis,j in enumerate(source):
                    cg*=rows_global[axis][out[axis]][j]
                    cl*=rows_local[axis][out[axis]][j]
                global_value+=cg*value;local_value+=cl*value;entries+=1
            index=tuple(cores[axis][choice] for axis,choice in enumerate(out))
            require(actual[index]==local_value,'Sequential full-window tensor needs no halo refresh')
            error=abs(actual[index]-global_value)
            require(error<=sum(maxerrors,Q(0)),'Tensor core row-error telescoping failed')
            maximum=max(maximum,error)
        require(maximum>0,'Local tensor negative/approximation is vacuous')
        records.append(dict(axes=axes,global_shape=shape,initial_local_shape=[6]*axes,
              core_outputs=2**axes,exact_tensor_entries=entries,maximum_core_error=str(maximum),
              actual_row_telescoping_bound=str(sum(maxerrors,Q(0))),
              neumann_tail_bound=str(sum(bounds,Q(0))),halo_refreshes=0))
    return records


def ceil_q(x):
    return -((-x.numerator)//x.denominator)


def fractional_controls():
    cases=cores=wraps=selections=padding=0
    examples=[]
    for d,t,L,halo in product((2,4,8),(64,128,256),(4,8,16),(1,2,3)):
        if L>=t:continue
        for s in range(t//2+1,t,2):
            theta=Q(t-s,s)
            if not Q(1,4*d)<theta<Q(1,2*d-1):continue
            rho=Q(t,s);previous=0
            lengths=[]
            for k in range(t//L):
                left=(k*L*s)//t;right=((k+1)*L*s)//t
                require(left==previous and right>left,'Fractional cores do not partition source')
                previous=right;lengths.append(right-left)
                ilo=ceil_q((Q(k*L-halo)-Q(1,2))/rho)
                ihi=ceil_q((Q((k+1)*L+halo)-Q(1,2))/rho)
                require(nearest(s,t,ilo)>=k*L-halo and nearest(s,t,ilo-1)<k*L-halo,
                        'Lower nearest-window endpoint wrong')
                require(nearest(s,t,ihi)>= (k+1)*L+halo and nearest(s,t,ihi-1)<(k+1)*L+halo,
                        'Upper nearest-window endpoint wrong')
                require(left-ilo>=Q(halo,2)-3 and ihi-right>=Q(halo,2)-3,
                        'Fractional core source halo bound failed')
                for j in range(ilo,ihi):
                    require(k*L-halo<=nearest(s,t,j)<(k+1)*L+halo,'Local C leaves target halo')
                    require(nearest(s,t,j+s)==nearest(s,t,j)+t,'Periodic nearest seam failed')
                    selections+=1
                require(Q(L)-Q(right-left)>=Q(L,8*d)-1,'Near-one padding headroom failed')
                if ilo<0 or ihi>s:wraps+=1
                cores+=1
            require(previous==s and sum(lengths)==s,'Final source core endpoint wrong')
            # Full dyadic core padding equals t, regardless of floor/ceil lengths.
            require((t//L)*L==t,'Source padding does not equal target volume');padding+=1;cases+=1
            if len(examples)<6:examples.append(dict(d=d,s=s,t=t,L=L,halo=halo,source_lengths=lengths))
    exact_cutoffs=[]
    for p in (101,128,257):
        L=1<<((p**8-1).bit_length())
        halo=4096*p**3;d=p
        require(L>=p**8 and L>=64*d*halo,'Source halo does not fit dyadic L')
        require((L+2*halo)**d<2*L**d,'Target halo tensor volume is not bounded by two')
        require(32*p<2**(16*p),'Neumann tail below 2^-16p fails')
        require(halo//2-3>=512*p**3,'Compression halo is too short')
        exact_cutoffs.append(dict(p=p,d=d,L=L,halo=halo,source_halo_fit=True,target_volume_below_two=True))
    return dict(cases=cases,cores=cores,periodic_wrap_windows=wraps,ordered_selection_records=selections,
                full_source_padding_controls=padding,small_examples=examples,exact_integer_cutoffs=exact_cutoffs)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    require(not args.output.exists(),'Use a fresh result path')
    start=time.monotonic()
    result=dict(status='PASS exact finite principal-window, clipped-cell and tensor controls; fixed-tape bulk transfer unreviewed',
        campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',campaign_deadline='2026-10-08T08:25:21Z',
        generated_at=datetime.now(timezone.utc).isoformat(),
        locality=locality_controls(),phase=phase_controls(),tensor=tensor_controls(),fractional=fractional_controls(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        limitations=['Finite rational surrogates, not the asymptotic Gaussian threshold by simulation',
            'No fixed-tape microbox gathering/halo duplication implementation',
            'General routing and complete bulk transfer require independent written review'],
        elapsed_seconds=time.monotonic()-start)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS',result['locality']['windows'],'principal windows,',result['phase']['windows'],
          'clipped structured windows,',result['fractional']['cores'],'fractional cores',flush=True)


if __name__=='__main__':main()
