#!/usr/bin/env python3
"""Compare the corrected carry-edge model to two COMPLETE physical profiles.

The ordinary no-reclamation compiler is a counterfactual needed to isolate
the additive model. The changed selected matching's full word/profile was
already reviewed independently. Neither reclaimed controller is inferred from
this comparison.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
from contextlib import redirect_stdout,redirect_stderr

from joint_match_components import load_source


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['source_root','costs','changed_uses','changed_profile','output','binary','other_profile','other_physical']:
        ap.add_argument('--'+name.replace('_','-'),required=True,type=Path)
    ap.add_argument('--h',required=True,type=int,choices=[23,25])
    args=ap.parse_args();assert __debug__;args.output.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();compiler=load_source(args.source_root.resolve())
    original=compiler.match;captured={}
    def record(blocks,uses,enabled):
        edges,chosen,right,stats=original(blocks,uses,enabled)
        owner={node:g for g,b in enumerate(blocks) for node in b['nodes']}
        captured.update(edges=edges,chosen=chosen,uses=uses,owner=owner)
        return edges,chosen,right,stats
    compiler.match=record
    with (args.output/'compile.log').open('w') as log,redirect_stdout(log),redirect_stderr(log):
        result,word=compiler.compile_(args.h,matching=True,reclaim=False,dirty=True)
    packed=(json.dumps(word,separators=(',',':'))+'\n').encode();(args.output/'word.json').write_bytes(packed)
    command=[sys.executable,'-B',str(Path(__file__).with_name('check_candidate_job.py')),
        '--word',str(args.output/'word.json'),'--h',str(args.h),'--output',str(args.output/'review'),
        '--binary',str(args.binary),'--other-profile',str(args.other_profile),'--other-physical',str(args.other_physical),
        '--inherited-certificate',str(args.source_root/'certificates/joint-dual-kappa.json'),
        '--assembly',str(args.source_root/'references/frame-compiler/pr48/research/copied-fixed/balanced_assembly.py')]
    with (args.output/'review.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    baseline=json.loads((args.output/'review/integer.profiles.json').read_text())
    changed=json.loads(args.changed_profile.read_text())
    assert baseline['h']==changed['h']==args.h and baseline['R']==changed['R']
    assert baseline['loss']==changed['loss'] and baseline['rank_sum']==changed['rank_sum']
    edges=captured['edges'];rows=json.loads(args.changed_uses.read_text());chosen=set()
    for row in rows:
        e=row['edge'];assert 0<=e<len(edges) and e not in chosen
        assert edges[e]==(row['block'],row['use'],row['input_index']);chosen.add(e)
    original=captured['chosen'];assert len(chosen)==len(original)
    table={}
    for line in args.costs.read_text().splitlines():
        row=json.loads(line);table[row['a'],row['b']]=row['blocks']
    predicted=Counter();difference=chosen^original
    for e in difference:
        sign=1 if e in chosen else -1;g,u,i=edges[e]
        value,target,_=captured['uses'][u];origin=captured['owner'][value]
        for a,b,coefficient in [(g+2,target+2,1),(g+2,1,-1),(0,origin+2,-1),(origin+2,target+2,-1)]:
            for t,n in enumerate(table[a,b]):predicted[t]+=sign*coefficient*n
    actual=[a-b for a,b in zip(changed['blocks'],baseline['blocks'])]
    modeled=[predicted[t] for t in range(args.h+1)]
    passed=actual==modeled
    receipt=dict(status='EXACT ADDITIVE PROFILE DIFFERENCE PASS' if passed else 'ADDITIVE PROFILE MODEL COUNTEREXAMPLE',
        recorded_utc=datetime.now(timezone.utc).isoformat(),h=args.h,roles=baseline['R'],
        selected_cardinality=len(chosen),changed_edges=len(difference),actual_profile_difference=actual,
        modeled_profile_difference=modeled,every_width_coefficient_equal=passed,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        original_selected_stream_sha256=sha256(('\n'.join('%d %d %d'%edges[e] for e in sorted(original))+'\n').encode()).hexdigest(),
        inputs={str(p):dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest()) for p in [args.changed_uses,args.changed_profile,args.costs]},
        baseline_profile_sha256=sha256((args.output/'review/integer.profiles.json').read_bytes()).hexdigest(),
        baseline_word_sha256=sha256(packed).hexdigest(),seconds=time.monotonic()-start,native_threads=1,
        model='Each continuation replaces cleanup at donor G plus the eliminated use clone born at origin F and raised F→H, with one G→H transition. Fixed cardinality leaves bank/exterior/denominator terms unchanged.',
        scope='Exact complete profile difference for this changed matching and ordinary no-reclamation counterpart. Does not prove a reclaimed additive model or global optimality of physical basis/producer choices.')
    (args.output/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['status','h','roles','changed_edges','every_width_coefficient_equal','seconds']}),flush=True)
    assert passed


if __name__=='__main__':main()
