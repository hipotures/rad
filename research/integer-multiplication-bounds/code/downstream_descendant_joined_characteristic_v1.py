#!/usr/bin/env python3
"""Reviewed boundary-family characteristic for enlarged delayed clones.

The actual changed rank histogram and both finite/all-size audits are
inputs. Internal old rank frequencies and formal-core equality are never
assumed. Only the unchanged boundary matrix families are grouped.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_gaussian import require
from downstream_joined_block_characteristic import joined_block
from downstream_parameter_optimum import as_strings


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def audit_boundary_histogram(counts,h,roles):
    v,m,N=counts['v'],counts['m'],counts['N']
    copies=(roles+h)*v*v
    categories=counts['categories']
    total={int(r):c for r,c in counts['rank_histogram'].items()}
    require(sum(r*c for r,c in total.items())==counts['s'],
            'Actual changed rank histogram sum differs')
    require(sum(total.values())==counts['edge_count'],
            'Actual changed zero/positive edge count differs')
    aggregate={}
    for category in categories.values():
        hist={int(r):c for r,c in category['rank_histogram'].items()}
        require(sum(r*c for r,c in hist.items())==category['rank_sum'] and
                sum(hist.values())==category['edge_count'],
                'Actual changed category count differs')
        for r,c in hist.items():aggregate[r]=aggregate.get(r,0)+c
    require(all(aggregate.get(r,0)==total.get(r,0) for r in set(aggregate)|set(total)),
            'Actual categories do not reconstruct the full histogram')
    side={int(r):c for r,c in categories['side_sources_shared_stage_join_and_sinks']['rank_histogram'].items()}
    centers={int(r):c for r,c in categories['centers_all_sources_three_returns_stage_join_and_sinks']['rank_histogram'].items()}
    require(side=={0:2*roles*v*v,m-2*h:roles*v*v,h*h-h:roles*v*v,m-h*h:roles*v*v},
            'Changed role endpoint or shared-join histogram differs')
    require(centers=={0:2*h*v*v,m-2*h:h*v*v,h*h-h:h*v*v,
                     m-h*h:h*v*v,h:9*h*v*v},
            'Actual centers or returns differ')
    require(side[m-2*h]+centers[m-2*h]==copies and
            side[m-h*h]+centers[m-h*h]==copies,
            'Joined or final-middle family multiplicity differs')
    data_rank=(h*h-1)*(h-1)
    for name in ('data_X_stage3','data_Y_stage3'):
        hist={int(r):c for r,c in categories[name]['rank_histogram'].items()}
        require(hist=={0:2*N,data_rank:N,h-1:N},
                'Actual chronological stage3 data histogram differs '+name)
    padding=categories['additional_identity_padding']
    require(padding['edge_count']==padding['rank_sum']==0,
            'Additional address padding cannot be ignored')
    grouped_rank=copies*(m-h*h)+copies*(m-2*h)+2*N*data_rank
    require(grouped_rank<counts['s'],'Grouped changed-frame families are not disjoint')
    return dict(actual_full_rank_sum=counts['s'],actual_full_edge_count=counts['edge_count'],
                all_categories_reconstruct_actual_histogram=True,
                final_middle_copies=copies,final_middle_residual_rank=m-h*h,
                joined_copies=copies,joined_residual_rank=m-2*h,
                stage3_data_copies=2*N,stage3_data_residual_rank=data_rank,
                grouped_rank=grouped_rank,
                other_actual_rank=counts['s']-grouped_rank,
                no_identity_padding=True,
                internal_rank_frequencies='Actual changed histogram retained and summed; all nonboundary families remain individual',
                actual_histogram_sha256=sha256(json.dumps(counts,sort_keys=True).encode()).hexdigest())


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--previous-joined-characteristic',type=Path,required=True)
    ap.add_argument('--descendant-promotion',type=Path,required=True)
    ap.add_argument('--descendant-transfer',type=Path,required=True)
    ap.add_argument('--descendant-producer',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    started=time.monotonic();source_dir=Path(__file__).parent
    old=json.loads(args.previous_joined_characteristic.read_text())
    promotion=json.loads(args.descendant_promotion.read_text())
    transfer=json.loads(args.descendant_transfer.read_text())
    raw=args.descendant_producer.read_bytes();producer=json.loads(raw)
    for document in (old,promotion,transfer):
        for name,digest in document['source_sha256'].items():
            require(sha(source_dir/name)==digest,'Pinned executed source differs '+name)
    require(promotion['status']=='PASS independent delayed first-consumer-frame clone finite witness' and
            transfer['status'].startswith('PASS') and
            transfer['actual_positive_and_zero_rank_histogram_retained'] and
            producer['status']=='Terminal exact descendant-frame clone witness PASS',
            'Changed-frame finite/all-size promotion absent')
    digest=sha256(raw).hexdigest()
    require(promotion['input_sha256'][str(args.descendant_producer)]==digest==
            transfer['input_sha256'][str(args.descendant_producer)],
            'Actual changed histogram input differs between independent audits')
    require(promotion['candidate_id']==transfer['candidate_id'],
            'Changed program candidate identity differs')
    full=promotion['full'];row=producer['rows'][0];h,roles=full['h'],full['roles']
    require((h,roles)==(51,485680) and row['h']==h and row['final']['roles']==roles and
            transfer['roles']==roles and transfer['chosen_clones']==full['clones']==16454,
            'Pinned enlarged clone candidate differs')
    require(full['every_actual_frame_contains_source_span'] and
            full['enlarged_frames_checked_against_first_consumer'] and
            full['frame_metadata']['clone_formal_core_equality_not_assumed'],
            'Actual enlarged frame/first-consumer premise absent')
    for key in ('all_global_coefficients_exact','all_additions_disjoint'):
        require(full['logical'][key],'Full changed scalar witness failed '+key)
    for key in ('every_gate_output_exact','every_physical_target_exact','cancellation_free_over_any_scalar_field'):
        require(full['physical'][key],'Full changed physical witness failed '+key)
    for key in ('all_input_frames_original_lines','all_output_frames_exact',
                'all_source_spans_contained_in_actual_frames','every_designated_target_orthogonal',
                'forward_and_reverse_complement_nesting'):
        require(full['rational_frames'][key],'Full actual rational frame witness failed '+key)
    dirty=promotion['small_control']['complete_invocation_dirty_basis']
    require({r['inverse'] for r in dirty}=={False,True} and
            all(r['exact_linear_map'] and r['input_basis_vectors']==4126 for r in dirty) and
            transfer['complete_small_dirty_basis_per_orientation']==4126,
            'Changed actual frame/complete dirty controls absent')
    p=joined_block(h,roles,'tensor-data');n=p['counts']
    for key in ('v','m','N','W','L','D','s'):
        require(full['exact_counts'][key]==transfer['counts'][key]==row['exact_counts'][key]==n[key],
                'Changed complete rank/count identity differs '+key)
    require(transfer['counts']['side_roles']==n['side_roles']==roles,
            'Changed physical role count differs')
    audit=audit_boundary_histogram(row['exact_counts'],h,roles)
    require(audit['grouped_rank']==p['middle_old_rank']+p['joined_old_rank']+p['data_old_rank'] and
            audit['other_actual_rank']==p['other_unchanged_rank'],
            'Characteristic boundary rank union differs from actual changed histogram')
    guard=full['literal_scalar_guard']
    require(guard['E']>guard['depth'] and guard['slack']==guard['E']-guard['depth'] and
            guard['G']==row['literal_scalar_guard']['G']==transfer['scalar_guard']['G'] and
            guard['E']==row['literal_scalar_guard']['E']==transfer['scalar_guard']['E'],
            'Actual changed literal scalar guard differs')
    regressions=[]
    for oldp in old['witnesses']:
        require(as_strings(joined_block(oldp['h'],oldp['roles'],oldp['variant']))==oldp,
                'Historical R500703 joined characteristic differs')
        regressions.append(dict(variant=oldp['variant'],saving=oldp['saving'],unchanged=True))
    predecessor=next(r for r in old['witnesses'] if r['variant']=='tensor-data')
    require(p['saving']>Q(predecessor['saving']),
            'No strict changed-frame boundary-characteristic improvement')
    hashes=dict(old['source_sha256']);hashes[Path(__file__).name]=sha(Path(__file__))
    finite=dict(status='INDEPENDENT FINITE PROMOTION PASS',h=h,roles=roles,
                candidate_id=promotion['candidate_id'],compiled_sha256=full['compiled_sha256'],
                path=str(args.descendant_promotion),sha256=sha(args.descendant_promotion),
                reference_commit=promotion['reference_commit'],counts=n,
                actual_enlarged_frame_source_containment=True,
                formal_core_equality_not_assumed=True,
                all_size_transfer_path=str(args.descendant_transfer),
                all_size_transfer_sha256=sha(args.descendant_transfer))
    result=dict(status='PASS STRICT DESCENDANT BOUNDARY CHARACTERISTIC WITH INDEPENDENT FINITE AND ALL-SIZE PROMOTION',
                campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
                generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
                input_files={str(q):dict(bytes=q.stat().st_size,sha256=sha(q)) for q in
                    (args.previous_joined_characteristic,args.descendant_promotion,
                     args.descendant_transfer,args.descendant_producer)},
                independent_descendant_source_sha256=dict(promotion['source_sha256'],**transfer['source_sha256']),
                odd_bit_finite_audit=finite,actual_boundary_histogram_audit=audit,
                actual_bit_literal_guard=guard,previous_joined_characteristic_regressions=regressions,
                witness=p,elapsed_seconds=time.monotonic()-started,
                scope='Changed delayed-clone actual frames/histogram independently promoted. Only unchanged complete middle/join/data boundaries are grouped in the accepted reflected basis; all changed internal edges remain individual. A new fixed rational table/prime/setup is required for the changed program. No old core equality, internal rank frequencies, graph replay or unpromoted frontier input is assumed.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],roles,p['saving'],p['saving_decimal_lower'],flush=True)


if __name__=='__main__':main()
