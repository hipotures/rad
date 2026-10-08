#!/usr/bin/env python3
"""Thin full assembly of the independently promoted enlarged clone program."""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_batched_semantic_bulk_assembly import batch_witness
from downstream_gaussian import require
from downstream_joined_block_characteristic import joined_block
from downstream_parameter_optimum import as_strings
from downstream_promoted_complex_composition import parse_counts
from downstream_uncapped_middle_semantic_bulk import uncapped_row_padding


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--previous-joined-assembly',type=Path,required=True)
    ap.add_argument('--descendant-characteristic',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    started=time.monotonic();source_dir=Path(__file__).parent
    old=json.loads(args.previous_joined_assembly.read_text())
    primitive=json.loads(args.descendant_characteristic.read_text())
    for document in (old,primitive):
        for name,digest in document['source_sha256'].items():
            require(sha(source_dir/name)==digest,'Frozen producer source differs '+name)
    for name,digest in primitive['independent_descendant_source_sha256'].items():
        require(sha(source_dir/name)==digest,'Independent changed-frame source differs '+name)
    for name,digest in old['independent_joined_source_sha256'].items():
        require(sha(source_dir/name)==digest,'Independent all-size joined source differs '+name)
    require(primitive['status'].startswith('PASS') and
            primitive['odd_bit_finite_audit']['status']=='INDEPENDENT FINITE PROMOTION PASS',
            'Changed-frame complete finite/all-size promotion absent')
    finite=primitive['odd_bit_finite_audit'];p=primitive['witness']
    n=parse_counts(p['counts']);nc=parse_counts(old['witnesses'][0]['complex_counts'])
    require(n['h']==finite['h']==51 and n['side_roles']==finite['roles']==485680 and
            nc['h']==28 and nc['R']==97586 and
            finite['actual_enlarged_frame_source_containment'] and finite['formal_core_equality_not_assumed'],
            'Pinned enlarged-frame finite/complex input differs')
    require(as_strings(joined_block(n['h'],n['side_roles'],'tensor-data'))==p,
            'Fresh changed-boundary characteristic regeneration differs')
    audit=primitive['actual_boundary_histogram_audit']
    require(audit['all_categories_reconstruct_actual_histogram'] and audit['no_identity_padding'] and
            audit['actual_full_rank_sum']==n['s'] and
            audit['grouped_rank']==p['middle_old_rank']+p['joined_old_rank']+p['data_old_rank'] and
            audit['other_actual_rank']==p['other_unchanged_rank'],
            'Actual changed histogram/family accounting absent')
    regressions=[]
    for row in old['witnesses']:
        oldn,oldnc=parse_counts(row['bit_counts']),parse_counts(row['complex_counts'])
        oldp=next(r for r in old['joined_characteristic_certificate']['witnesses']
                  if r['variant']=='tensor-data')
        actual=batch_witness(oldn,oldnc,row['mode'],row['prefix'],Q(row['previous_accepted_kappa']),oldp)
        for group in ('parameters','recurrence','margins','constraint_slacks','cutoff_log2_b'):
            require(as_strings(actual[group])==row[group],
                    'Accepted fixed-frame predecessor regression differs '+group)
        require(as_strings(uncapped_row_padding(actual))==row['compact_row_padding'],
                'Predecessor p^2600 row regression differs')
        regressions.append(dict(mode=row['mode'],prefix=row['prefix'],
                                kappa=row['parameters']['kappa'],unchanged=True))
    previous=max(Q(r['parameters']['kappa']) for r in old['witnesses'])
    rows=[]
    for mode in ('conservative','tight'):
        for prefix in ('original','balanced'):
            row=batch_witness(n,nc,mode,prefix,previous,p)
            row['batch_variant']='descendant-reflected-joined-block-tensor-data'
            row['compact_row_padding']=uncapped_row_padding(row)
            row['native_bit_primitive']=dict(
                certificate_kind='PROMOTED ENLARGED-CLONE BOUNDARY NEGATIVE-EXPONENTIAL TAYLOR',
                chosen_saving=Q(p['saving']),strict_taylor_gap=Q(p['strict_taylor_gap']),
                actual_histogram_sha256=audit['actual_histogram_sha256'],
                actual_grouped_rank=audit['grouped_rank'],other_actual_individual_rank=audit['other_actual_rank'],
                compiler_basis='Cycle(3,1,2)*(Q tensor Q tensor Q), Q=I-2J/51, applied to every actual assigned frame',
                enlarged_clone_frame='Existing positive first-consumer owner frame containing the formal source span; formal-core equality not required',
                middle='Unchanged endpoint matrix family, uniform full runs h^2*(h-2), h^2',
                data='Unchanged physical X stage3 incoming and Y stage3 0-to-1 data family, h-1 copies of h^2-2,1',
                joined='Unchanged shared-bank join matrix, h-2 isolated maximal runs h^2-2 plus remainder5096/156',
                internal='Every other actual changed-frame edge left individual; old internal frequencies are not substituted',
                maximum_child_rank=p['maximum_child_rank'],child_ratio=Q(49,51),
                depth='ceil(log_(51/49)e)<=26ceil(log2e)',
                row_divisor='W^depth<p^2600 after p>=C and log2p>=25; new smaller W remains below2^49',
                factor_table='New fixed reflected rational Bruhat table for the changed actual frame program',
                native_prime='A newly fixed admissible odd prime for the complete changed table, with its own eventual setup; no identity with the predecessor prime is assumed',
                bit_literal_guard=primitive['actual_bit_literal_guard'],
                complex_guard='Original h28 R97586 scalar network and semantic C0/C1 unchanged')
            row['proof_obligations'].insert(0,
                'Independent enlarged-clone source-span/owner/actual-target transfer plus full changed finite audit and unchanged grouped boundary families')
            row['additional_eventual_cutoffs'] += [
                'New fixed native table/admissible odd prime for the promoted enlarged actual frames',
                'Retained layout setup C for changed native calls: e<=C*p after p>=C',
                'Complete untouched row stock divisible by W^depth, certified below p^2600']
            rows.append(row)
    hashes=dict(old['source_sha256']);hashes.update(primitive['source_sha256'])
    hashes[Path(__file__).name]=sha(Path(__file__))
    result=dict(status='PASS STRICT CONDITIONAL DESCENDANT JOINED ASSEMBLY; INDEPENDENT FINAL ARITHMETIC REVIEW REQUIRED',
                campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
                generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
                original_reference=old['original_reference'],compact_reference=old['compact_reference'],
                input_files={str(q):dict(bytes=q.stat().st_size,sha256=sha(q)) for q in
                    (args.previous_joined_assembly,args.descendant_characteristic)},
                odd_bit_finite_audit=finite,promoted_complex_audit=old['promoted_complex_audit'],
                previous_fixed_frame_kappa=previous,fixed_frame_predecessor_regressions=regressions,
                descendant_characteristic_certificate=primitive,
                retained_independent_joined_review_sha256=old['independent_joined_review_sha256'],
                independent_joined_source_sha256=old['independent_joined_source_sha256'],
                witnesses=rows,elapsed_seconds=time.monotonic()-started,
                scope='Four exact complete rows for independently promoted delayed enlarged-clone actual frames. Fresh complete histogram and boundary multiplicities determine the characteristic; all other changed edges remain individual. New fixed table/prime/C qualifications are explicit. No accepted graph replay, old formal-core equality or unpromoted frontier candidate is used.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in rows:
        print(result['status'],row['mode'],row['prefix'],row['parameters']['kappa'],
              row['cutoff_log2_b']['common'],flush=True)


if __name__=='__main__':main()
