#!/usr/bin/env python3
"""Compose future-directed non-unit complements with the accepted acquires.

The exact accepted axis compiler source is hash-checked against its original
result and copied unchanged before the sole complement-row synthesis patch.
This distinguishes a negative under ordinary high-rank reclamation from the
same basis tested with future-horizon or guarded live-carrier reclamation.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
from future_retirement_basis import candidate_factory
from joint_match_components import load_source


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['source_root','compiler_source','compiler_receipt','output','binary','other_profile','other_physical']:
        ap.add_argument('--'+name.replace('_','-'),required=True,type=Path)
    ap.add_argument('--h',required=True,type=int,choices=[23,25])
    ap.add_argument('--policies',default='pair,sum,output,output-reverse')
    args=ap.parse_args();assert __debug__;args.output.mkdir(parents=True,exist_ok=False)
    compiler=load_source(args.source_root.resolve());base_receipt=json.loads(args.compiler_receipt.read_text())
    raw=args.compiler_source.read_text();digest=sha256(raw.encode()).hexdigest()
    assert base_receipt['h']==args.h and base_receipt['variant_compiler_sha256']==digest
    assert base_receipt['roles']=={23:30667,25:40324}[args.h]
    (args.output/'accepted_compiler_source.py').write_text(raw)
    old="   for i in range(len(ins)):\n    if independent(echelon,1<<i):rows.append(1<<i);labels.append(('retire',i));echelon=basis(rows)"
    assert raw.count(old)==1
    protocol=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),h=args.h,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        candidate_helper_sha256=sha256(Path(__file__).with_name('future_retirement_basis.py').read_bytes()).hexdigest(),
        accepted_compiler_sha256=digest,accepted_compiler_receipt_sha256=sha256(args.compiler_receipt.read_bytes()).hexdigest(),
        accepted_base_roles=base_receipt['roles'],native_threads=1,policies=args.policies.split(','),scope=__doc__)
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    seen={};summary=[]
    for policy in protocol['policies']:
        assert policy in ['pair','pair-reverse','sum','sum-reverse','output','output-reverse']
        start=time.monotonic();out=args.output/policy;out.mkdir()
        replacement="   for i,r in enumerate(future_candidates(b,g,blocks,uses,value_uses,order,contains,signal)):\n    if independent(echelon,r):rows.append(r);labels.append(('retire',i));echelon=basis(rows)"
        variant=raw.replace(old,replacement);(out/'variant_compiler.py').write_text(variant)
        exec(compile(variant,str(out/'variant_compiler.py'),'exec'),compiler.__dict__)
        compiler.graph=sys.modules['joint_dual_compiler'].producer.graph
        compiler.future_candidates=candidate_factory(policy)
        result,word=compiler.compile_(args.h,matching=True,reclaim=True,dirty=True)
        packed=(json.dumps(word,separators=(',',':'))+'\n').encode();word_digest=sha256(packed).hexdigest()
        (out/'word.json').write_bytes(packed)
        receipt=dict(policy=policy,h=args.h,word_sha256=word_digest,
            variant_compiler_sha256=sha256(variant.encode()).hexdigest(),compiled=result,
            duplicate_of=seen.get(word_digest),recorded_utc=datetime.now(timezone.utc).isoformat())
        (out/'compile.json').write_text(json.dumps(receipt,indent=2)+'\n')
        if word_digest not in seen:
            seen[word_digest]=policy
            command=[sys.executable,'-B',str(Path(__file__).with_name('check_candidate_job.py')),
                '--word',str(out/'word.json'),'--h',str(args.h),'--output',str(out/'review'),
                '--binary',str(args.binary),'--other-profile',str(args.other_profile),
                '--other-physical',str(args.other_physical),
                '--inherited-certificate',str(args.source_root/'certificates/joint-dual-kappa.json'),
                '--assembly',str(args.source_root/'references/frame-compiler/pr48/research/copied-fixed/balanced_assembly.py')]
            (out/'review-command.json').write_text(json.dumps(command,indent=2)+'\n')
            subprocess.run(command,check=True)
            moment=json.loads((out/'review/complete-moment.json').read_text())
            receipt.update(saving=moment['saving'],kappa=moment['kappa'])
        receipt.update(roles=result['roles'],seconds=time.monotonic()-start)
        summary.append(receipt);(args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps({k:receipt.get(k) for k in ['policy','roles','saving','duplicate_of','seconds']}),flush=True)


if __name__=='__main__':main()
