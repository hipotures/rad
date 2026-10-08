#!/usr/bin/env python3
"""Complete tensor-data assembly with the reviewed joined-block moment.

This sharpens the estimate of existing reflected canonical pivot groups.
The role graph, native factor table, maximum child and tape schedule stay
those of the accepted reflected program. No proof-only S/R is executed.
"""
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
from downstream_householder_characteristic import householder
from downstream_joined_block_characteristic import joined_block
from downstream_parameter_optimum import as_strings
from downstream_promoted_complex_composition import parse_counts
from downstream_uncapped_middle_semantic_bulk import uncapped_row_padding


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--previous-householder-assembly',type=Path,required=True)
    ap.add_argument('--joined-characteristic',type=Path,required=True)
    ap.add_argument('--joined-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    started=time.monotonic();source_dir=Path(__file__).parent
    old=json.loads(args.previous_householder_assembly.read_text())
    primitive=json.loads(args.joined_characteristic.read_text())
    review=json.loads(args.joined_review.read_text())
    for document in (old,primitive):
        for name,digest in document['source_sha256'].items():
            require(sha(source_dir/name)==digest,'Frozen producer source differs '+name)
    for name,digest in review['source_sha256'].items():
        require(sha(source_dir/name)==digest,'Executed independent joined source differs '+name)
    require(review['status'].startswith('PASS') and
            review['same_actual_fixed_address_table'] and not review['new_runtime_adapter'] and
            review['retained_uncapped_row_degree']==2600,
            'Independent all-size joined/table/depth interface absent')
    finite=primitive['odd_bit_finite_audit']
    require(finite==old['odd_bit_finite_audit'] and
            review['finite_candidate_id']==finite['candidate_id'] and
            review['finite_compiled_sha256']==finite['compiled_sha256'],
            'Pinned complete reflected finite identity differs')
    require(all(r['original_and_transformed_canonical_profile_equal'] and
                r['all_spaced_kernel_holes_absent'] and
                len(r['known_maximal_diagonal_runs'])==r['h']-2
                for r in review['full_profile_cases']),
            'Independent full joined profiles or maximal runs failed')
    regressions=[]
    for row in old['witnesses']:
        n,nc=parse_counts(row['bit_counts']),parse_counts(row['complex_counts'])
        p=next(r for r in old['reflected_characteristic_certificate']['witnesses']
               if r['variant']=='tensor-data')
        require(as_strings(householder(n['h'],n['side_roles'],'tensor-data'))==p,
                'Historical reflected characteristic differs')
        actual=batch_witness(n,nc,row['mode'],row['prefix'],Q(row['previous_accepted_kappa']),p)
        for group in ('parameters','recurrence','margins','constraint_slacks','cutoff_log2_b'):
            require(as_strings(actual[group])==row[group],
                    'Reflected predecessor regression differs '+group)
        require(as_strings(uncapped_row_padding(actual))==row['compact_row_padding'],
                'Reflected p^2600 row regression differs')
        regressions.append(dict(mode=row['mode'],prefix=row['prefix'],
                                kappa=row['parameters']['kappa'],unchanged=True))
    previous=max(Q(r['parameters']['kappa']) for r in old['witnesses'])
    p=next(r for r in primitive['witnesses'] if r['variant']=='tensor-data')
    n=parse_counts(p['counts']);nc=parse_counts(old['witnesses'][0]['complex_counts'])
    require(n['h']==51 and n['side_roles']==500703 and nc['h']==28 and nc['R']==97586,
            'Historical complete finite inputs differ')
    require(as_strings(joined_block(n['h'],n['side_roles'],'tensor-data'))==p,
            'Exact sharpened joined characteristic regeneration differs')
    peer=review['row']
    for key in ('h','m','N','W','L','D','s'):
        require(peer['counts'][key]==n[key],'Independent count differs '+key)
    require(Q(peer['explicit_saving'])>=Q(p['saving']) and
            Q(peer['strict_independent_characteristic_gap'])>0 and
            peer['maximum_child']==p['maximum_child_rank'],
            'Independent stronger joined characteristic absent')
    require(peer['joined_known_diagonal_pivots']==p['isolated_joined_rank'] and
            peer['joined_known_diagonal_runs']==p['isolated_joined_runs'] and
            peer['joined_remainder_lower_pivots']==p['remaining_joined_diagonal_lower'] and
            peer['joined_remainder_upper_runs']==p['remaining_joined_run_upper'],
            'Independent isolated mass or Jensen remainder differs')
    for peer_key,own_key in (('middle_moment_lower','middle_rank_log_sum_lower'),
                            ('joined_moment_lower','joined_rank_log_sum_lower'),
                            ('data_moment_lower','data_rank_log_sum_lower')):
        require(Q(peer[peer_key])>=Q(p[own_key]),
                'Independent longer logarithm interval is weaker '+peer_key)
    rows=[]
    for mode in ('conservative','tight'):
        for prefix in ('original','balanced'):
            row=batch_witness(n,nc,mode,prefix,previous,p)
            row['batch_variant']='reflected-joined-block-tensor-data'
            row['compact_row_padding']=uncapped_row_padding(row)
            row['native_bit_primitive']=dict(
                certificate_kind='REVIEWED REFLECTED JOINED-BLOCK NEGATIVE-EXPONENTIAL TAYLOR',
                chosen_saving=Q(p['saving']),strict_taylor_gap=Q(p['strict_taylor_gap']),
                compiler_basis='Retained Cycle(3,1,2)*(Q tensor Q tensor Q), Q=I-2J/51',
                middle='Retained uniform full runs h^2*(h-2), h^2',
                data='Retained h-1 copies of h^2-2,1 per physical data edge',
                joined='h-2 isolated maximal runs h^2-2 plus Jensen remainder 5096/156',
                proof_only_lower_concentration='Used only to identify the original canonical profiles; no runtime S/R maps or new factor table',
                maximum_child_rank=p['maximum_child_rank'],child_ratio=Q(49,51),
                depth='ceil(log_(51/49)e)<=26ceil(log2e)',
                row_divisor='Retained W^depth<p^2600 after p>=C and log2p>=25',
                factor_table='Same newly fixed reflected rational table as the predecessor',
                native_prime='The same admissible odd prime for the reflected table; proof-only lower factors introduce no further exclusions',
                complex_guard='Original h28 R97586 network and semantic C0/C1 unchanged')
            row['proof_obligations'].insert(0,
                'Reviewed all-size reflected joined-block profile with h-2 isolated maximal runs and correct Jensen remainder')
            row['additional_eventual_cutoffs'] += [
                'Retained fixed reflected native table, admissible odd prime and descriptor constants',
                'Retained layout setup C for reflected calls: e<=C*p after p>=C',
                'Complete untouched row stock divisible by W^depth, certified below p^2600']
            rows.append(row)
    hashes=dict(old['source_sha256']);hashes.update(primitive['source_sha256'])
    hashes[Path(__file__).name]=sha(Path(__file__))
    result=dict(status='PASS STRICT CONDITIONAL JOINED-BLOCK ASSEMBLY; INDEPENDENT FINAL ARITHMETIC REVIEW REQUIRED',
                campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
                generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
                original_reference=old['original_reference'],compact_reference=old['compact_reference'],
                input_files={str(q):dict(bytes=q.stat().st_size,sha256=sha(q)) for q in
                    (args.previous_householder_assembly,args.joined_characteristic,args.joined_review)},
                odd_bit_finite_audit=finite,promoted_complex_audit=old['promoted_complex_audit'],
                previous_householder_kappa=previous,householder_predecessor_regressions=regressions,
                joined_characteristic_certificate=primitive,
                independent_joined_review_sha256=sha(args.joined_review),
                independent_joined_source_sha256=review['source_sha256'],
                witnesses=rows,elapsed_seconds=time.monotonic()-started,
                scope='Four exact tensor-data parameter rows for a sharper moment estimate of the already grouped reflected joined pivots. Graph, roles, table, native prime, maximum child, row degree, scalar precision, guard and fixed tapes remain the reviewed reflected program. Conditional original interfaces and separate eventual setup thresholds remain explicit.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in rows:
        print(result['status'],row['mode'],row['prefix'],row['parameters']['kappa'],
              row['cutoff_log2_b']['common'],flush=True)


if __name__=='__main__':main()
