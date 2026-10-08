#!/usr/bin/env python3
"""Retired complements directed by actual compatible future consumers.

Unlike unstructured non-unit completion, candidate rows are drawn from input
signals delivered to the same future region, or from exact future requested
scalar forms representable in the current incoming span. These are only
basis choices: the original producer DAG and matching edges are unchanged,
all XORs are synthesized and every dirty row is verified independently.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
import time
from joint_match_components import load_source


def candidate_factory(policy):
    context={}
    def candidates(b,g,blocks,uses,value_uses,order,contains,signal):
        if context.get('blocks') is not blocks:
            context.clear();context.update(blocks=blocks,place={q:i for i,q in enumerate(order)})
        place=context['place'];by_target=defaultdict(list)
        for i,y in enumerate(b['inputs']):
            for u in value_uses[y]:
                _,target,terminal=uses[u]
                if terminal is None and place[target]>place[g] and contains(b['frame'],blocks[target]['frame']):
                    by_target[target].append(i)
        targets=sorted(by_target,key=lambda target:(place[target],target))
        if policy.endswith('reverse'):targets.reverse()
        rows=[]
        if policy.startswith('pair'):
            for target in targets:
                rows.extend((1<<i)^(1<<j) for i,j in combinations(sorted(set(by_target[target])),2))
        elif policy.startswith('sum'):
            for target in targets:
                row=sum(1<<i for i in set(by_target[target]))
                if row.bit_count()>1:rows.append(row)
        elif policy.startswith('output'):
            # Incoming scalar source forms may themselves be dependent. A
            # deterministic representation still defines a literal physical
            # row; its independence is checked against all requested/carry
            # rows before use, so no quotient or clean scratch is assumed.
            echelon={}
            for i,y in enumerate(b['inputs']):
                row=signal[y];expression=1<<i
                while row:
                    p=row.bit_length()-1
                    if p not in echelon:echelon[p]=(row,expression);break
                    old,e=echelon[p];row^=old;expression^=e
            for target in targets:
                for x in blocks[target]['outvalues']:
                    row=signal[x];expression=0
                    while row:
                        p=row.bit_length()-1
                        if p not in echelon:break
                        old,e=echelon[p];row^=old;expression^=e
                    if not row and expression:rows.append(expression)
        else:raise ValueError(policy)
        seen=set();answer=[]
        for row in rows:
            if row not in seen:seen.add(row);answer.append(row)
        return answer+[1<<i for i in range(len(b['inputs']))]
    return candidates


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['source_root','output','binary','other_profile','other_physical']:
        ap.add_argument('--'+name.replace('_','-'),required=True,type=Path)
    ap.add_argument('--h',required=True,type=int,choices=[23,25])
    ap.add_argument('--policies',default='pair,pair-reverse,sum,sum-reverse,output,output-reverse')
    args=ap.parse_args();assert __debug__
    args.output.mkdir(parents=True,exist_ok=False);compiler=load_source(args.source_root.resolve())
    raw=(args.source_root/'scripts/experiments/binary_frame_compiler.py').read_text()
    old="   for i in range(len(ins)):\n    if independent(echelon,1<<i):rows.append(1<<i);labels.append(('retire',i));echelon=basis(rows)"
    assert raw.count(old)==1
    protocol=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),h=args.h,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        base_compiler_sha256=sha256(raw.encode()).hexdigest(),native_threads=1,
        policies=args.policies.split(','),scope=__doc__)
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    seen={};summary=[]
    for policy in protocol['policies']:
        start=time.monotonic();out=args.output/policy;out.mkdir()
        replacement="   for i,r in enumerate(future_candidates(b,g,blocks,uses,value_uses,order,contains,signal)):\n    if independent(echelon,r):rows.append(r);labels.append(('retire',i));echelon=basis(rows)"
        variant=raw.replace(old,replacement)
        assert variant.count('for s in sorted(retired):')==1
        variant=variant.replace('for s in sorted(retired):',"for s in sorted(retired,key=lambda s:(-blocks[frames[s]]['rank'],s)):")
        (out/'variant_compiler.py').write_text(variant)
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
