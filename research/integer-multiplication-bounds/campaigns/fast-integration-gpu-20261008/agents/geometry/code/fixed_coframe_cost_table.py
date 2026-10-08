#!/usr/bin/env python3
"""Exact four-state matrix costs for fixed-word old/minimum frame allocation.

The exported native input is a DISCOVERY matrix probe, not a physical network.
Actual allocation, continuation, cleanup and endpoint multiplicities come
from the source-bound parent. Both uniform physical histograms are rebuilt.
"""
import argparse
from collections import Counter
from decimal import Decimal,localcontext
from datetime import datetime,timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import struct
import subprocess
import time

from fixed_word_source_coframes import select_fixed_word_coframes,normalize,contained,TAG
from decompose_common_context_profiles import pivot_run_histogram


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--binary',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    config=json.loads(args.input.read_text())
    raw=gzip.decompress(Path(config['parent']['word_path']).read_bytes())
    assert sha256(raw).hexdigest()==config['parent']['word_sha256']
    word=json.loads(raw);h=word['h'];started=time.monotonic()
    _,minimum,minimum_receipt=select_fixed_word_coframes(word)
    old=[normalize(frame) for frame in word['frames']]
    data=Path(config['parent_binary']).read_bytes()
    assert sha256(data).hexdigest()==config['parent_binary_sha256']
    H=struct.unpack_from('<6I2Q',data);_,v,R,nf,nt,singles,mass,loss=H
    assert h==H[0] and R==word['R'] and nf==len(old)+2
    offset=40+nf*(12+h)
    physical=[struct.unpack_from('<2Iq',data,offset+16*i) for i in range(nt)]
    pool=[(0,0,(0,)*h),(h,0,(0,)*h)]+old
    lookup={frame:i for i,frame in enumerate(pool)}
    states=[(0,0),(1,1)]
    variables=[]
    for i,(before,after) in enumerate(zip(old,minimum)):
        if before[0]==after[0]:
            states.append((i+2,i+2))
        else:
            assert before[0]-after[0]==1
            if after not in lookup:
                lookup[after]=len(pool);pool.append(after)
            states.append((lookup[after],i+2))
            variables.append(i+2)
    variable_set=set(variables)
    def legal(a,b):
        if pool[b][0]<=pool[a][0]:return False
        return a==0 or b==1 or contained(pool[a],pool[b])
    probes=set();rows=[];implications=[]
    for at,(a,b,count) in enumerate(physical):
        cases={}
        for xa in (0,1):
            for xb in (0,1):
                p,q=states[a][xa],states[b][xb]
                good=legal(p,q)
                cases[f'{xa}{xb}']=dict(legal=good,probe=[p,q])
                if good:probes.add((p,q))
        assert cases['00']['legal'] and cases['11']['legal'] and cases['01']['legal']
        if not cases['10']['legal']:
            assert a in variable_set and b in variable_set
            implications.append([a,b])
        rows.append(dict(a=a,b=b,count=count,states=cases))
        if at%20000==0:print(json.dumps(dict(phase='exact legal-state matrix compilation',completed=at,total=nt)),flush=True)
    probe_mass=sum(pool[b][0]-pool[a][0] for a,b in probes)
    binary=args.work/'four-state-matrices.bin'
    with binary.open('wb') as stream:
        stream.write(b'RADCOF01');stream.write(struct.pack('<6I2Q',h,0,0,len(pool),len(probes),0,probe_mass,0))
        for frame in pool:
            rank,forced=frame[:2]
            if len(frame)==4:assert frame[2]==TAG;forced|=1 << 63;symbols=frame[3]
            else:symbols=frame[2]
            stream.write(struct.pack('<QI',forced,rank));stream.write(struct.pack(f'<{h}b',*symbols))
        for a,b in sorted(probes):stream.write(struct.pack('<2Iq',a,b,1))
    print(json.dumps(dict(phase='native four-state CRT',frames=len(pool),matrices=len(probes),variables=len(variables))),flush=True)
    profile_path,audit_path=args.work/'probe-profile.json',args.work/'probe-audit.json'
    with (args.work/'native.log').open('wb') as log:
        subprocess.run([str(args.binary),str(binary),config['basis'],str(profile_path),str(audit_path)],stdout=log,stderr=subprocess.STDOUT,check=True)
    audit=json.loads(audit_path.read_text())
    audit_rows={(r['a'],r['b']):r for r in audit['transitions']}
    histograms={}
    for a,b in probes:
        rank=pool[b][0]-pool[a][0]
        if rank==1:histograms[a,b]=Counter({1:1})
        elif (a,b)==(0,1):histograms[a,b]=Counter({h:1})
        else:
            r=audit_rows[a,b];assert r['count']==1 and r['rank']==rank
            histograms[a,b]=pivot_run_histogram(r['pivots'])
    side_counts=Counter(frame+2 for slot,frame,c,target in word['outputs'] if len(target)==3)
    uniform=[]
    for state in (0,1):
        hist=Counter()
        hist[1]=sum((h-pool[states[fid][state]][0])*count for fid,count in side_counts.items())
        for row in rows:
            p,q=row['states'][f'{state}{state}']['probe']
            for width,n in histograms[p,q].items():hist[width]+=n*row['count']
        expected=json.loads(Path(config['minimum_profile' if state==0 else 'parent_profile']).read_text())['blocks']
        assert [hist[t] for t in range(h+1)]==expected,'Uniform physical histogram was not exactly reconstructed'
        assert sum(t*n for t,n in hist.items())==mass
        uniform.append([hist[t] for t in range(h+1)])
    with localcontext() as context:
        context.prec=100
        exponent=Decimal(str(config['screen_a']))
        weights={t:Decimal(t)*((exponent*(Decimal(575)/Decimal(t)).ln()).exp()-1) for t in range(1,h+1)}
        def cost(hist):return sum(Decimal(n)*weights[t] for t,n in hist.items())
        submod=dict(exact_zero_histogram=0,numerically_negative=0,numerically_positive=0,uncertain=0,hard_implication=len(implications))
        margins=[]
        for row in rows:
            for state,entry in row['states'].items():
                if entry['legal']:
                    hist=histograms[tuple(entry['probe'])]
                    entry['histogram']={str(t):n for t,n in hist.items()}
                    entry['screen_cost']=str(cost(hist)*row['count'])
            if row['a'] not in variable_set or row['b'] not in variable_set or not row['states']['10']['legal']:
                continue
            delta=Counter()
            for state,sign in [('00',1),('11',1),('01',-1),('10',-1)]:
                for t,n in row['states'][state]['histogram'].items():delta[int(t)]+=sign*n
            delta={t:n for t,n in delta.items() if n}
            if not delta:submod['exact_zero_histogram']+=1;continue
            value=cost(delta)*row['count']
            key='uncertain' if abs(value)<Decimal('1e-70') else 'numerically_positive' if value>0 else 'numerically_negative'
            submod[key]+=1
            if len(margins)<24 and key=='numerically_positive':margins.append(dict(a=row['a'],b=row['b'],delta_histogram=delta,decimal_delta=str(value)))
        phi=[str(cost({t:n for t,n in enumerate(hist) if t and n})) for hist in uniform]
    payload=dict(classification='DISCOVERY MATRIX COST TABLE, NOT A PHYSICAL NETWORK',
        h=h,basis=config['basis'],parent_word_sha256=config['parent']['word_sha256'],
        physical_rank_mass=mass,physical_R=R,variables=variables,implications=implications,
        side_counts={str(k):v for k,v in side_counts.items()},
        rows=rows,probe_frame_descriptors=pool,variable_states=states,
        objective='x=0 minimum, x=1 old; illegal10 means old_a implies old_b. '
                  'All exact physical transition multiplicities plus output singleton unaries.',
        uniform_histograms_exactly_reconstructed=uniform)
    table=args.work/'four-state-cost-table.json'
    table.write_text(json.dumps(payload,separators=(',',':'))+'\n')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(dict(
        status='EXACT FOUR-STATE COFRAME MATRICES; NUMERICAL OPTIMIZATION DISCOVERY',
        h=h,basis=config['basis'],variables=len(variables),physical_transition_types=nt,
        probe_matrices=len(probes),uniform_histograms_exactly_reconstructed=True,
        minimum_Phi=phi[0],old_Phi=phi[1],submodularity_screen=submod,
        positive_submodularity_counterexamples=margins,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        input_binary_sha256=sha256(binary.read_bytes()).hexdigest(),
        cost_table_path=str(table),cost_table_sha256=sha256(table.read_bytes()).hexdigest(),
        profile_path=str(profile_path),audit_path=str(audit_path),
        minimum_receipt=minimum_receipt,elapsed_seconds=time.monotonic()-started,
        completed_utc=datetime.now(timezone.utc).isoformat(),
        scope='Every legal matrix cost certified by native bounded-minor CRT; both '
              'uniform whole-word histograms reproduced exactly. Decimal submodularity '
              'screening is discovery, not a global optimum or exponent certificate. '
              'Any selected binary allocation requires complete actual-word reconstruction.'),indent=2)+'\n')
    print(json.dumps(dict(status='complete',h=h,submodularity=submod,elapsed_seconds=time.monotonic()-started)),flush=True)


if __name__=='__main__':main()
