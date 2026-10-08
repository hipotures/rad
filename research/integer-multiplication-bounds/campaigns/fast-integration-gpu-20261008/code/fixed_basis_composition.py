#!/usr/bin/env python3
"""Changed producers with exact fixed-envelope middle profiles.

Fixed I+J profiles/CRT are icekylinx and Dominik Scholz PR32/35/38;
one-factor generic reversed compatibility is Rohan Arun PR39. PR40 proves
the same reversed data profile with both fixed factors, for unchanged
source triples and freshly certified original-envelope local profiles.
The new DAGs are this campaign's contribution. Profile entries replace
actual local transitions, never headline ratios or positive-frame counts.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

from exact_composition import reconstruct,choose,moment,bridge,js,read


def bit_profile(positive,fixed,mode):
    assert mode in ('generic','fixed-middle','fixed-both','fixed-both-reversed')
    rows=[dict(r) for r in positive]
    if mode!='generic':rows[1]=dict(fixed[1]['producer'])
    if mode in ('fixed-both','fixed-both-reversed'):rows[0]=dict(fixed[0]['producer'])
    bit=reconstruct(rows)
    for k in range(2):
        if mode=='generic' or (mode=='fixed-middle' and k==0):continue
        row=rows[k];h=row['h'];p=fixed[k]['fixed_profile'];copies=bit['N']//row['v']
        assert p['R']==row['R'] and p['rank_sum']==sum(t*n for t,n in enumerate(p['blocks']))==h*row['R']+2*row['loss']
        assert p['crt_disagreements']==0 and p['blocks'][h]>=h
        local=Counter({t:copies*n for t,n in enumerate(p['blocks']) if t and n})
        local[h]-=copies*h;local[1]+=copies*h
        bit['parts'][f'local_{k}']=+local
    if mode=='fixed-both':
        # Build the PR38 physical orientation25/23 at design time.
        bit['dimensions']=[25,23]
        bit['parts']['data']=Counter({1:26*2*bit['N'],21:2*bit['N'],481:2*bit['N']})
    hist=sum(bit['parts'].values(),Counter());hist={t:n for t,n in sorted(hist.items()) if n}
    assert sum(t*n for t,n in hist.items())==bit['W']*bit['m']-bit['N']+bit['L']
    bit['child_multiplicities']=hist;bit['maxchild']=max(hist)
    bit['basis_mode']=mode
    return bit


def main():
    p=argparse.ArgumentParser();p.add_argument('--positive',type=Path,required=True)
    p.add_argument('--fixed',type=Path,required=True);p.add_argument('--phase',type=Path,required=True)
    p.add_argument('--assembly',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    positive,fixed,pr=read(args.positive),read(args.fixed),read(args.phase)
    assert [x['h'] for x in positive]==[23,25] and [x['producer']['h'] for x in fixed]==[23,25]
    phase=reconstruct([pr,pr],True);cm=moment(phase,Q(717,10**7));assert cm['strict_gap']>0
    sp=importlib.util.spec_from_file_location('balanced',args.assembly);am=importlib.util.module_from_spec(sp);sp.loader.exec_module(am)
    results=[]
    for mode in ('generic','fixed-middle','fixed-both','fixed-both-reversed'):
        bit=bit_profile(positive,fixed,mode);bm=choose(bit);f=bridge(bit,phase,[pr,pr])
        a=bm['saving'];h=Q(1,10**12);q=a*(1-2*h);margin=(1-h)*q/(1+q)
        k=Q((margin*10**14).numerator//(margin*10**14).denominator,10**14);assert k<margin
        assembly=am.assembly(f,a,k);eventual=am.cutoffs(f,assembly)
        results.append(dict(mode=mode,bit=bit,bit_moment=bm,phase_moment=cm,finite_bridge=f,assembly=assembly,eventual=eventual,kappa=k,
            status='Complete exact conditional arithmetic; actual changed-projector finite/basis/dirty interfaces must be separately accepted'))
    output=dict(rows=results,input_sha256={str(f):sha256(f.read_bytes()).hexdigest() for f in (args.positive,args.fixed,args.phase,args.assembly)},
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),exact_core_sha256=sha256(Path(__file__).with_name('exact_composition.py').read_bytes()).hexdigest())
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(js(output),indent=2)+'\n')
    print(json.dumps([dict(mode=r['mode'],a=str(r['bit_moment']['saving']),kappa=str(r['kappa'])) for r in results]))


if __name__=='__main__':main()
