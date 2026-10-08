#!/usr/bin/env python3
"""Read-only normalized characteristic on a fresh completed physical case."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

from downstream_compound_whole_semantic_bulk import generic_characteristic
from downstream_generic_ground_screen import checked_case
from downstream_parameter_optimum import as_strings


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selected-assembly',type=Path,required=True);ap.add_argument('--candidate-case',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();a=json.loads(args.selected_assembly.read_text())
    current=next(p for p in a['generic_characteristics'] if p['protected_centers']==0)
    assert as_strings(generic_characteristic(current['h'],current['roles'],0))==current
    case=checked_case(args.candidate_case);assert case['eligible'] and case['actual_histogram_audit']
    p=generic_characteristic(case['h'],case['roles'],0);audit=case['actual_histogram_audit']
    for k,boundary in (('middle','final_middle'),('joined','joined'),('data','stage3_data')):
        assert p['family_ranks'][k]==audit[boundary+'_copies']*audit[boundary+'_residual_rank']
    gain=p['saving']-Q(current['saving'])
    r=dict(status='PASS EXACT FRESH COMPLETED CANDIDATE COMPARISON; NO PROMOTION OR NEW KAPPA',
        generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256={n:sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in
            (Path(__file__).name,'downstream_compound_whole_semantic_bulk.py','downstream_generic_ground_screen.py')},
        inputs={str(q):sha256(q.read_bytes()).hexdigest() for q in (args.selected_assembly,args.candidate_case)},
        selected_normal_h=current['h'],selected_normal_roles=current['roles'],selected_normal_saving=current['saving'],
        candidate_actual_finite_producer=case,candidate_normalized_characteristic=p,
        exact_primitive_difference=gain,candidate_strictly_above_selected=gain>0,
        scope='Actual completed producer identity and full saved histogram, no hypothetical role reduction and no graph replay. Exact same normalized Taylor/log test. Independent finite promotion and complete parameter assembly remain separate.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(as_strings(r),indent=2,sort_keys=True)+'\n')
    print(r['status'],case['h'],case['roles'],p['saving'],r['candidate_strictly_above_selected'],flush=True)


if __name__=='__main__':main()
