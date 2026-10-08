#!/usr/bin/env python3
"""Causal region order plus fully guarded live donors and paid complements.

The tested nested/live compiler is hash-checked unchanged, then receives the
root's exact causal schedule. Requested/carry rows retain their meanings.
Every borrowed donor must still fit the current frame and every actual
unconsumed future-use frame, under the new order. Whole words, profiles and
moments are rechecked; composition is not inferred from separate successes.
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
    for name in ['source_root','region_protocol','live_source','live_receipt','output','binary','other_profile','other_physical']:
        ap.add_argument('--'+name.replace('_','-'),required=True,type=Path)
    ap.add_argument('--h',required=True,type=int,choices=[23,25])
    ap.add_argument('--policies',default='unit,sum,pair,output')
    args=ap.parse_args();assert __debug__;args.output.mkdir(parents=True,exist_ok=False)
    parent=json.loads(args.region_protocol.read_text());live=json.loads(args.live_receipt.read_text())
    assert parent['dimension']==args.h and parent['retired_policy']=='high-rank'
    assert len(parent['families'])==1 and parent['families'][0].get('target_lengths')==[]
    compiler=load_source(args.source_root.resolve());raw=args.live_source.read_text()
    assert sha256(raw.encode()).hexdigest()==live['variant_compiler_sha256']
    assert live['h']==25 and live['roles']==40324
    (args.output/'original_guarded_live.py').write_text(raw)
    order_marker="order=sorted(range(len(blocks)),key=lambda g:(blocks[g]['rank'],min(blocks[g]['nodes'])))"
    assert raw.count(order_marker)==1
    raw=raw.replace(order_marker,'order=scheduled_order(blocks,uses,owner,SCHEDULE_POLICY)')
    scheduling={};exec(compile(parent['scheduling_source'],'<frozen-causal-schedule>','exec'),scheduling)
    compiler.scheduled_order=scheduling['scheduled_order'];compiler.SCHEDULE_POLICY=parent['schedule']
    (args.output/'base_compiler.py').write_text(raw)
    (args.output/'causal_region_order.py').write_text(parent['scheduling_source'])
    old="   for i in range(len(ins)):\n    if independent(echelon,1<<i):rows.append(1<<i);labels.append(('retire',i));echelon=basis(rows)"
    assert raw.count(old)==1
    protocol=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),h=args.h,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        candidate_helper_sha256=sha256(Path(__file__).with_name('future_retirement_basis.py').read_bytes()).hexdigest(),
        original_live_compiler_sha256=live['variant_compiler_sha256'],
        composite_base_compiler_sha256=sha256(raw.encode()).hexdigest(),
        region_protocol_sha256=sha256(args.region_protocol.read_bytes()).hexdigest(),
        live_receipt_sha256=sha256(args.live_receipt.read_bytes()).hexdigest(),
        schedule=parent['schedule'],native_threads=1,policies=args.policies.split(','),scope=__doc__)
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    seen={};summary=[]
    for policy in protocol['policies']:
        assert policy in ['unit','pair','pair-reverse','sum','sum-reverse','output','output-reverse']
        start=time.monotonic();out=args.output/policy;out.mkdir()
        replacement="   for i,r in enumerate(future_candidates(b,g,blocks,uses,value_uses,order,contains,signal)):\n    if independent(echelon,r):rows.append(r);labels.append(('retire',i));echelon=basis(rows)"
        variant=raw if policy=='unit' else raw.replace(old,replacement)
        (out/'variant_compiler.py').write_text(variant)
        exec(compile(variant,str(out/'variant_compiler.py'),'exec'),compiler.__dict__)
        compiler.graph=sys.modules['joint_dual_compiler'].producer.graph
        if policy!='unit':compiler.future_candidates=candidate_factory(policy)
        result,word=compiler.compile_(args.h,matching=True,reclaim=True,dirty=True)
        packed=(json.dumps(word,separators=(',',':'))+'\n').encode();digest=sha256(packed).hexdigest()
        (out/'word.json').write_bytes(packed)
        receipt=dict(policy=policy,h=args.h,word_sha256=digest,
            variant_compiler_sha256=sha256(variant.encode()).hexdigest(),compiled=result,
            duplicate_of=seen.get(digest),recorded_utc=datetime.now(timezone.utc).isoformat())
        (out/'compile.json').write_text(json.dumps(receipt,indent=2)+'\n')
        if digest not in seen:
            seen[digest]=policy
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
