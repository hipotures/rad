#!/usr/bin/env python3
"""Thin independently checked stage3 data-batch assembly extension.

Import the frozen two-family witness algebra, verify both exact old rows
and new Taylor inputs, and compose only the newly reviewed bit saving.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_batched_semantic_bulk_assembly import batch_witness, row_padding_certificate
from downstream_diagonal_batch_data_bound import data_extension
from downstream_gaussian import require
from downstream_parameter_optimum import as_strings
from downstream_promoted_complex_composition import parse_counts


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--two-family-assembly',type=Path,required=True)
    ap.add_argument('--data-certificate',type=Path,required=True)
    ap.add_argument('--data-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();require(not a.output.exists(),'Use a fresh output path')
    started=time.monotonic();source_dir=Path(__file__).parent
    old=json.loads(a.two_family_assembly.read_text())
    data=json.loads(a.data_certificate.read_text());review=json.loads(a.data_review.read_text())
    for name,expected in old['source_sha256'].items():
        require(sha(source_dir/name)==expected,'Frozen two-family source changed '+name)
    for name,expected in data['source_sha256'].items():
        require(sha(source_dir/name)==expected,'Data Taylor source changed '+name)
    require(review['status'].startswith('PASS') and
            sha(a.data_certificate) in review['inputs'].values(),
            'Independent data review is not terminal or tied to this input')
    require(review['physical_family']['disjoint_from_middle_and_joins'] and
            review['physical_family']['x_edge']=='stage3 X in->2' and
            review['physical_family']['y_edge']=='stage3 Y 0->1',
            'Data chronology or disjointness differs')
    oldp=old['bit_primitive_certificate']['witness'];regressions=[]
    for row in old['witnesses']:
        n,nc=parse_counts(row['bit_counts']),parse_counts(row['complex_counts'])
        actual=batch_witness(n,nc,row['mode'],row['prefix'],Q(row['previous_accepted_kappa']),oldp)
        for group in ('parameters','recurrence','margins','constraint_slacks','cutoff_log2_b'):
            require(as_strings(actual[group])==row[group],'Two-family exact regression differs '+group)
        require(as_strings(row_padding_certificate(actual))==row['compact_row_padding'],
                'Two-family row-padding regression differs')
        regressions.append(dict(mode=row['mode'],prefix=row['prefix'],kappa=row['parameters']['kappa'],unchanged=True))
    previous=max(Q(row['parameters']['kappa']) for row in old['witnesses'])
    nc=parse_counts(old['witnesses'][0]['complex_counts']);rows=[]
    for p in data['witnesses']:
        n=parse_counts(p['counts']);variant=p['variant']
        require(as_strings(data_extension(n['h'],n['side_roles'],variant))==p,
                'Data Taylor certificate regeneration differs')
        require(n==parse_counts(old['witnesses'][0]['bit_counts']),
                'Data extension finite counts differ from accepted two-family input')
        peer=next(r for r in review['rows'] if r['variant']==variant)
        require(Q(peer['saving'])==Q(p['saving']) and peer['strict_uniform_recurrence'] and
                peer['total_rank_conserved'] and Q(peer['strict_characteristic_gap'])>0,
                'Independent exact data characteristic differs')
        require(review['physical_family']['copies_each']==n['N'] and
                p['data_edge_count']==2*n['N'], 'Data physical multiplicity differs')
        for mode in ('conservative','tight'):
            for prefix in ('original','balanced'):
                row=batch_witness(n,nc,mode,prefix,previous,p);row['batch_variant']=variant
                row['compact_row_padding']=row_padding_certificate(row)
                row['native_bit_primitive']=dict(certificate_kind='THREE-FAMILY TAYLOR CHARACTERISTIC',
                    chosen_saving=Q(p['saving']),strict_taylor_gap=Q(p['strict_taylor_gap']),
                    maximum_child_rank=p['maximum_child_rank'],child_ratio=Q(1,n['h']),
                    child_width_relation=('r*floor(e/m)<e/h' if variant=='kernel-holes' else 'r*floor(e/m)<=e/h'),
                    depth='ceil(log_h e)',native_alphabet='Original fixed odd prime retained',
                    physical_data_edges='X stage3 in->2 and Y stage3 0->1, N copies each',
                    excluded_zero_data_edge='Y stage3 in->0')
                row['proof_obligations'].insert(0,'Independent three-family data projection, physical chronology, kernel holes and original-factor/tail batching transfer')
                row['additional_eventual_cutoffs'] += ['Fixed batched primitive base case and original odd-prime table',
                    'Retained fixed layout constant C in e<=C*p, after p>=C']
                rows.append(row)
    hashes=dict(old['source_sha256']);hashes.update(data['source_sha256']);hashes[Path(__file__).name]=sha(Path(__file__))
    result=dict(status='PASS STRICT CONDITIONAL THREE-FAMILY ASSEMBLY; INDEPENDENT FINAL ASSEMBLY REVIEW REQUIRED',
        campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
        campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
        generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
        original_reference=old['original_reference'],compact_reference=old['compact_reference'],
        input_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in (a.two_family_assembly,a.data_certificate,a.data_review)},
        odd_bit_finite_audit=old['odd_bit_finite_audit'],promoted_complex_audit=old['promoted_complex_audit'],
        previous_accepted_kappa=previous,two_family_regressions=regressions,
        data_primitive_certificate=data,independent_data_review_sha256=sha(a.data_review),
        witnesses=rows,elapsed_seconds=time.monotonic()-started,
        scope='Only the independently reviewed third data-edge family changes the declared bit saving; two-family historical source/results and all retained multiplication interfaces remain fixed')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in rows:print(result['status'],row['batch_variant'],row['mode'],row['prefix'],
                         row['parameters']['kappa'],row['cutoff_log2_b']['common'],flush=True)


if __name__=='__main__':main()
