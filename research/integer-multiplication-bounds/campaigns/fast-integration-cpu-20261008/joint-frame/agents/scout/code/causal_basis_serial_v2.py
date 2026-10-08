#!/usr/bin/env python3
"""Future-directed complements with an exact recorded causal retirement policy.

Reconstruct the exact tested root compiler from its public source, scheduling
source, and retired policy, and require its recorded SHA256 before changing
the sole retired-complement loop. This preserves the root mechanism and pays
the new complementary signals through the actual invertible synthesis word.
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
    for name in ['source_root','region_protocol','region_result','output','binary','other_profile','other_physical']:
        ap.add_argument('--'+name.replace('_','-'),required=True,type=Path)
    ap.add_argument('--h',required=True,type=int,choices=[23,25])
    ap.add_argument('--policies',default='pair,sum')
    args=ap.parse_args();assert __debug__;args.output.mkdir(parents=True,exist_ok=False)
    parent=json.loads(args.region_protocol.read_text());base_result=json.loads(args.region_result.read_text())
    assert parent['dimension']==args.h and parent['retired_policy'] in ['high-rank','sparse-first','dense-first','low-rank']
    assert len(parent['families'])==1 and parent['families'][0].get('target_lengths')==[]
    compiler=load_source(args.source_root.resolve())
    original=(args.source_root/'scripts/experiments/binary_frame_compiler.py').read_text()
    order_marker="order=sorted(range(len(blocks)),key=lambda g:(blocks[g]['rank'],min(blocks[g]['nodes'])))"
    assert original.count(order_marker)==1
    raw=original.replace(order_marker,'order=scheduled_order(blocks,uses,owner,SCHEDULE_POLICY)')
    assert raw.count('for s in sorted(retired):')==1
    retirement_keys={'high-rank':"-blocks[frames[s]]['rank'],s",'sparse-first':"-blocks[frames[s]]['rank'],slots[s].bit_count(),s",'dense-first':"-blocks[frames[s]]['rank'],-slots[s].bit_count(),s",'low-rank':"blocks[frames[s]]['rank'],s"}
    raw=raw.replace('for s in sorted(retired):','for s in sorted(retired,key=lambda s: ('+retirement_keys[parent['retired_policy']]+')):')
    assert sha256(raw.encode()).hexdigest()==parent['compiled_source_sha256']
    scheduling={};exec(compile(parent['scheduling_source'],'<frozen-causal-schedule>','exec'),scheduling)
    compiler.scheduled_order=scheduling['scheduled_order'];compiler.SCHEDULE_POLICY=parent['schedule']
    (args.output/'base_compiler.py').write_text(raw)
    (args.output/'causal_region_order.py').write_text(parent['scheduling_source'])
    old="   for i in range(len(ins)):\n    if independent(echelon,1<<i):rows.append(1<<i);labels.append(('retire',i));echelon=basis(rows)"
    assert raw.count(old)==1
    protocol=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),h=args.h,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        candidate_helper_sha256=sha256(Path(__file__).with_name('future_retirement_basis.py').read_bytes()).hexdigest(),
        base_compiler_sha256=sha256(raw.encode()).hexdigest(),
        region_protocol_sha256=sha256(args.region_protocol.read_bytes()).hexdigest(),
        base_result_sha256=sha256(args.region_result.read_bytes()).hexdigest(),
        base_word_sha256=base_result['word_sha256'],base_roles=base_result['compiled']['roles'],
        schedule=parent['schedule'],retired_policy=parent['retired_policy'],native_threads=1,policies=args.policies.split(','),scope=__doc__)
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
