#!/usr/bin/env python3
"""Freeze one completed-case snapshot for the final finite nomination.

No live worker is stopped or any physical graph replayed. The exact
normalized characteristic and two-center wholeC score rank completed
actual producer cases; nomination is not independent finite promotion.
"""
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_compound_whole_semantic_bulk import generic_characteristic
from downstream_generic_ground_screen import checked_case
from downstream_parameter_optimum import as_strings,compact_lower


def sha(p):return sha256(p.read_bytes()).hexdigest()


def score(a):
    h=Q(1,2**64);q=a*(1-2*h);epsilon=(1-h)/(1+q)
    return compact_lower(epsilon*q,places=40)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--cases',type=Path,required=True)
    ap.add_argument('--selected-assembly',type=Path,required=True);ap.add_argument('--checkpoint',type=Path,required=True)
    ap.add_argument('--case-list',type=Path,help='Immutable JSON path list for exact snapshot reproduction')
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists();t=time.monotonic()
    old=json.loads(args.selected_assembly.read_text());selected=next(p for p in old['generic_characteristics'] if p['protected_centers']==2)
    selected_score=score(Q(selected['saving']))
    assert selected_score==max(Q(r['parameters']['kappa']) for r in old['witnesses'])
    checkpoint_bytes=args.checkpoint.read_bytes();checkpoint=json.loads(checkpoint_bytes)
    files=(list(map(Path,json.loads(args.case_list.read_text()))) if args.case_list else list(sorted(args.cases.glob('*.json'))))
    records=[];unfinished=[];by_compile={}
    for path in files:
        try:row=json.loads(path.read_text())
        except json.JSONDecodeError:
            unfinished.append(dict(path=str(path),reason='Incomplete JSON at snapshot; left to its running producer'));continue
        if 'compiled_roles' not in row or 'final' not in row:
            unfinished.append(dict(path=str(path),reason='No completed physical result in this file'));continue
        case=checked_case(path);assert case['eligible'] and case['actual_histogram_audit']
        p0=generic_characteristic(case['h'],case['roles'],0);p2=generic_characteristic(case['h'],case['roles'],2)
        assert Q(1,10**6)>2*p2['saving']
        audit=case['actual_histogram_audit']
        for key,boundary in (('middle','final_middle'),('joined','joined'),('data','stage3_data')):
            assert p0['family_ranks'][key]==audit[boundary+'_copies']*audit[boundary+'_residual_rank']
        record=dict(h=case['h'],roles=case['roles'],candidate_id=case['candidate_id'],compiled_sha256=case['compiled_sha256'],
            source_case=case['source_case'],actual_normal_boundary_audit=audit,
            normal_saving=p0['saving'],two_center_saving=p2['saving'],two_center_strict_taylor_gap=p2['strict_taylor_gap'],
            prospective_tight_balanced_wholeC_score=score(p2['saving']),maximum_child=p2['maximum_child_rank'],
            exact_halving_depth=p2['depth_per_ceil_log2e'],actual_W_binary_upper_exponent=p2['W_binary_upper_exponent'],
            above_selected_score=score(p2['saving'])>selected_score,
            full_producer_only=True,independent_finite_promotion_required=True)
        records.append(record)
        if case['compiled_sha256'] not in by_compile:
            by_compile[case['compiled_sha256']]=(record,p0,p2)
    assert records
    ranking=sorted(by_compile.values(),key=lambda x:(-x[0]['prospective_tight_balanced_wholeC_score'],x[0]['source_case']['path']))
    best,p0,p2=ranking[0]
    result=dict(status='PASS EXACT COMPLETED-CASE CLOSING NOMINATION; NO FINITE PROMOTION OR NEW HEADLINE',
        generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256={n:sha(Path(__file__).with_name(n)) for n in
            (Path(__file__).name,'downstream_compound_whole_semantic_bulk.py','downstream_generic_ground_screen.py')},
        selected_assembly=dict(path=str(args.selected_assembly),sha256=sha(args.selected_assembly)),
        immutable_case_list=dict(path=str(args.case_list),sha256=sha(args.case_list)) if args.case_list else None,
        checkpoint_snapshot=dict(path=str(args.checkpoint),sha256=sha256(checkpoint_bytes).hexdigest(),content=checkpoint),
        selected_reference=dict(h=selected['h'],roles=selected['roles'],two_center_saving=selected['saving'],score=selected_score),
        completed_files_checked=len(records),unique_compiled_candidates=len(ranking),unfinished_at_snapshot=unfinished,
        records=records,ranked_candidate_ids=[x[0]['candidate_id'] for x in ranking],
        nomination=best,nomination_normal_primitive=p0,nomination_two_center_primitive=p2,
        score_formula='floor_1e-40[(1-h)*a2*(1-2h)/(1+a2*(1-2h))], h=2^-64; same fixed-half tight-balanced wholeC family',
        phase_leaf_feasible_for_every_completed_case=True,
        scope='Snapshot only of completed actual source files. Full saved histograms and all boundary categories audited. New normal/two-center characteristic uses the same exact normalized log/Taylor test. The score orders the declared family, not an accepted multiplication kappa. One selected final changed DAG must receive independent promotion, new table/setup/depth/product/guard verification and complete final arithmetic. Live workers and unfinished results remain untouched.',
        wall_seconds=time.monotonic()-t)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],best['h'],best['roles'],best['candidate_id'],best['source_case']['path'],best['two_center_saving'],best['prospective_tight_balanced_wholeC_score'],flush=True)


if __name__=='__main__':main()
