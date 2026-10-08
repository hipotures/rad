#!/usr/bin/env python3
"""Serial exact requested-output basis variants, one native worker.

Change the independent requested row order while preserving its span, all
matching incidences, UNIT completion, and high-rank retirement. A word hash
is used only to skip an identical finite word; every new word gets the full
independent dirty replay, twelve-prime profile and complete moment.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time

from joint_match_components import load_source


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['source_root','output','binary','other_profile','other_physical']:
        ap.add_argument('--'+name.replace('_','-'),required=True,type=Path)
    ap.add_argument('--h',required=True,type=int,choices=[23,25])
    ap.add_argument('--policies',default='sparse,dense,pivot-low,pivot-high,rotate1,rotate2,rotate3,zigzag')
    args=ap.parse_args();assert __debug__
    args.output.mkdir(parents=True,exist_ok=False)
    compiler=load_source(args.source_root.resolve())
    raw=(args.source_root/'scripts/experiments/binary_frame_compiler.py').read_text()
    old="   for x in outvalues:\n    r=b['coeff'][x]"
    assert raw.count(old)==1
    expressions={
        'sparse':"sorted(outvalues,key=lambda x:(b['coeff'][x].bit_count(),x))",
        'dense':"sorted(outvalues,key=lambda x:(-b['coeff'][x].bit_count(),x))",
        'pivot-low':"sorted(outvalues,key=lambda x:((b['coeff'][x]&-b['coeff'][x]).bit_length(),x))",
        'pivot-high':"sorted(outvalues,key=lambda x:(-b['coeff'][x].bit_length(),x))",
        'rotate1':"outvalues[1:]+outvalues[:1]",
        'rotate2':"outvalues[2:]+outvalues[:2]",
        'rotate3':"outvalues[3:]+outvalues[:3]",
        'zigzag':"outvalues[::2]+outvalues[1::2]",
    }
    seen={};summary=[]
    protocol=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),h=args.h,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        base_compiler_sha256=sha256(raw.encode()).hexdigest(),native_threads=1,
        policies=args.policies.split(','),scope='Requested output basis order only; scalar graph, matching, UNIT completion and high-rank retirement fixed.')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    for policy in protocol['policies']:
        assert policy in expressions
        start=time.monotonic();out=args.output/policy;out.mkdir()
        variant=raw.replace(old,"   for x in "+expressions[policy]+":\n    r=b['coeff'][x]")
        assert variant.count('for s in sorted(retired):')==1
        variant=variant.replace('for s in sorted(retired):',"for s in sorted(retired,key=lambda s:(-blocks[frames[s]]['rank'],s)):")
        (out/'variant_compiler.py').write_text(variant)
        exec(compile(variant,str(out/'variant_compiler.py'),'exec'),compiler.__dict__)
        compiler.graph=sys.modules['joint_dual_compiler'].producer.graph
        result,word=compiler.compile_(args.h,matching=True,reclaim=True,dirty=True)
        packed=(json.dumps(word,separators=(',',':'))+'\n').encode()
        digest=sha256(packed).hexdigest();(out/'word.json').write_bytes(packed)
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
        summary.append(receipt)
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps({k:receipt.get(k) for k in ['policy','roles','saving','duplicate_of','seconds']}),flush=True)


if __name__=='__main__':main()
