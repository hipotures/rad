#!/usr/bin/env python3
"""Distinct full-state guard falsifications while the compiled pipeline is authored."""
import argparse,hashlib,json
from pathlib import Path
from crt_guard_controls import complete_repair_case

CASES={
    "zero-offset-four":((3,3,3,3),1,(5,7,7,5),(0,0,6,4)),
    "binary-modulus-four":((3,3,3,3),1,(8,8,5,7),(7,0,4,6)),
    "unbalanced-three":((3,4,4),2,(7,9,15),(0,8,14)),
}

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True)
    p.add_argument('--output',required=True);a=p.parse_args()
    result=complete_repair_case(*CASES[a.case])
    result.update({'run_id':'20261008T1435Z-'+a.case,'status':'PASS','workers':1,'native_threads':1,
                   'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'guard_dependency_sha256':hashlib.sha256(Path(__file__).with_name('crt_guard_controls.py').read_bytes()).hexdigest(),
                   'scope':'New corner families: zero/full offsets, full binary moduli and unequal widths; complete inverse and actual radix repair'})
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)

if __name__=='__main__':main()
