#!/usr/bin/env python3
"""Dual-root actual projectors; output is separate from the original basis run."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,time
from run_positive_profiles import run


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--binary',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--baseline-binary',type=Path);a=ap.parse_args()
    assert not a.work.exists() and not a.output.exists();a.work.mkdir(parents=True);configs=json.loads(a.input.read_text());rows=[];begin=time.monotonic()
    for config in configs:
        case=config['case_id'];work=a.work/case;witness=Path(config['witness']);profiled=a.work/f'{case}-complete.json'
        run(witness,a.binary,config['basis'],work,profiled)
        retained=json.loads(profiled.read_text());basis=config['basis']
        retained['configuration'].update(basis='I+J/3' if basis=='negative-transpose' else 'I-10/[9(h+1)]J',
                    dual_root_of='I-4/[3(h+3)]J' if basis=='negative-transpose' else 'I+J',
                    data_certificate='Identical source coordinate products; same old basis source/data family')
        retained['provenance']['authored_source_sha256']=sha256(Path(__file__).with_name('positive_transpose_profiles.cpp').read_bytes()).hexdigest()
        final=a.work/f'{case}-retained.json';final.write_text(json.dumps(retained,indent=2)+'\n')
        original=json.loads(witness.read_text())
        if basis=='fixed-transpose':
            assert a.baseline_binary
            baseline_file=a.work/f'{case}-fixed-baseline.json'
            run(witness,a.baseline_binary,'fixed',a.work/f'{case}-fixed-baseline',baseline_file)
            original=json.loads(baseline_file.read_text())
        new=retained['copied_blocks'];old=original.get('copied_blocks')
        if old is None:
            old=original['fixed_profile']['blocks'][:];h=original['producer']['h'];old[1]+=h;old[h]-=h
        phi=retained['local_phi']['value'];baseline=original.get('local_phi')
        if isinstance(baseline,dict):baseline=baseline.get('value')
        if baseline is None:
            import math
            baseline=sum(n*t*math.expm1(4e-5*math.log(575/t)) for t,n in enumerate(old) if t and n)
        row=dict(case_id=case,h=retained['producer']['h'],basis=basis,reference_basis='fixed' if basis=='fixed-transpose' else 'negative',R=retained['producer']['R'],local_phi=phi,
                    baseline_local_phi=baseline,unchanged_width_histogram=new==old,improvement=baseline-phi,
                    profile=retained['fixed_profile'],retained_witness=str(final))
        rows.append(row);(a.work/'status.json').write_text(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),completed=len(rows),total=len(configs),last=row),indent=2)+'\n')
        print(json.dumps({k:row[k] for k in ('case_id','h','basis','R','local_phi','unchanged_width_histogram','improvement')}),flush=True)
    result=dict(status='COMPLETE EXACT DUAL-ROOT LOCAL DISCRIMINATORS',rows=rows,elapsed_seconds=time.monotonic()-begin,
                completed_utc=datetime.now(timezone.utc).isoformat(),input_sha256=sha256(a.input.read_bytes()).hexdigest(),
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    a.output.write_text(json.dumps(result,indent=2)+'\n')
