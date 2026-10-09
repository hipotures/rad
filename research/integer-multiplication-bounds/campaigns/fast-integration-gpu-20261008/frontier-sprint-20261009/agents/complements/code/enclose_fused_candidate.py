#!/usr/bin/env python3
"""Independent inventory recount and exact rational moments of a frozen candidate.

Imports only the separate rational interval kernel, never a producer or saved
verdict. Complete physical costs and ordinary endpoint dimensions are bound
before moment evaluation. This accepts a native complex trial, not final kappa.
Prepared with GPT-6.1 Sol assistance; Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time


def need(condition,message):
    if not condition:raise ValueError(message)


def main():
    p=argparse.ArgumentParser()
    for key in ('profile','logical-record','interval-code','output'):
        p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--target',type=Fraction,default=Fraction(617560360,10**12))
    p.add_argument('--root-grid',type=int,required=True)
    args=p.parse_args()
    need(not sys.flags.optimize,'assertion-disabled execution rejected')
    need(not args.output.exists(),'output already exists')
    started=time.monotonic()
    physical=json.loads(args.profile.read_text())
    row=json.loads(args.logical_record.read_text())
    histogram=Counter()
    for key in ('local_histogram','source_data_histogram','target_data_histogram'):
        histogram.update({int(r):3*n for r,n in physical[key].items() if int(r) and n})
    histogram.update({3*int(r):n for r,n in physical['physical_gauge_histogram'].items() if int(r) and n})
    histogram[2]+=2*physical['v']
    need(dict(histogram)=={int(r):n for r,n in physical['child_histogram'].items()},'paid histogram recount')
    m,W=physical['m'],physical['W_per_vertex']
    mass=sum(r*n for r,n in histogram.items())
    need(m==3*physical['h'] and W==2*physical['v']+physical['physical_R'],'physical dimensions')
    need(physical['physical_R']==row['R']-physical['pairs'],'physical role stock')
    need(m*W-mass==physical['deficit_per_vertex']==2*physical['v']-3*physical['loss'],'telescoping deficit')
    spec=importlib.util.spec_from_file_location('fused_exact_moments',args.interval_code)
    kernel=importlib.util.module_from_spec(spec);spec.loader.exec_module(kernel)
    trials={}
    for saving in (args.target,Fraction(args.root_grid,10**12),Fraction(args.root_grid+1,10**12)):
        lower,upper=kernel.moment(m,W,dict(histogram),saving)
        trials[str(saving)]={'lower':str(lower),'upper':str(upper),'gap_lower':str(1-upper),
            'gap_lower_decimal':float(1-upper),'classification':'ACCEPTED' if upper<1 else
            'REJECTED' if lower>1 else 'UNRESOLVED'}
    need(trials[str(Fraction(args.root_grid,10**12))]['classification']=='ACCEPTED' and
         trials[str(Fraction(args.root_grid+1,10**12))]['classification']=='REJECTED','root grid not separated')
    result={'status':'EXACT_RATIONAL_COMPLEX_MOMENTS','target':str(args.target),'trials':trials,
        'm':m,'W':W,'mass':mass,'deficit':m*W-mass,'max_child':max(histogram),
        'complete_children':dict(histogram),'input_sha256':{name:hashlib.sha256(path.read_bytes()).hexdigest()
            for name,path in [('profile',args.profile),('logical_record',args.logical_record),
                              ('interval_code',args.interval_code)]},'elapsed_seconds':time.monotonic()-started,
        'scope':'Independent complete physical-part recount and rigorous rational complex moments only; '
                'finite signed/reflected construction, binary supplier, 47 assembly constraints, seven margins '
                'and inherited all-size assumptions are separately required. No final kappa claimed.'}
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({key:result[key] for key in ('status','target','trials','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
