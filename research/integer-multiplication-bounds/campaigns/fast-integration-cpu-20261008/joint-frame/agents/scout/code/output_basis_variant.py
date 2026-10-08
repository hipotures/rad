#!/usr/bin/env python3
"""Change the independent requested-output basis order, then fully review.

The source graph and requested output span remain fixed. Choosing a different
independent requested-output basis changes actual retired physical signals and XOR synthesis.
Any saving is accepted only after a fresh complete word/profile calculation.
"""
import argparse
from datetime import datetime,timezone
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
    ap.add_argument('--completion',choices=['reverse-output'],default='reverse-output')
    args=ap.parse_args();assert __debug__;args.output.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();compiler=load_source(args.source_root.resolve())
    raw=(args.source_root/'scripts/experiments/binary_frame_compiler.py').read_text()
    old="   for x in outvalues:\n    r=b['coeff'][x]"
    assert raw.count(old)==1
    variant=raw.replace(old,"   for x in reversed(outvalues):\n    r=b['coeff'][x]")
    old_retire='for s in sorted(retired):';assert variant.count(old_retire)==1
    variant=variant.replace(old_retire,"for s in sorted(retired,key=lambda s: (-blocks[frames[s]]['rank'],s)):")
    (args.output/'variant_compiler.py').write_text(variant)
    exec(compile(variant,str(args.output/'variant_compiler.py'),'exec'),compiler.__dict__)
    compiler.graph=sys.modules['joint_dual_compiler'].producer.graph
    result,word=compiler.compile_(args.h,matching=True,reclaim=True,dirty=True)
    packed=(json.dumps(word,separators=(',',':'))+'\n').encode()
    (args.output/'word.json').write_bytes(packed)
    receipt=dict(status='CHANGED UNIT COMPLETION FINITE COMPILE; INDEPENDENT REVIEW FOLLOWS',
        recorded_utc=datetime.now(timezone.utc).isoformat(),h=args.h,completion=args.completion,
        base_compiler_sha256=sha256(raw.encode()).hexdigest(),variant_compiler_sha256=sha256(variant.encode()).hexdigest(),
        wrapper_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),word_sha256=sha256(packed).hexdigest(),
        compiled=result,seconds=time.monotonic()-start,native_threads=1,
        scope='Changed physical invertible basis completion; high-rank retirement is inherited from the reviewed layout candidate. Fullword/frame profiles and all-size framing semantics are separate obligations.')
    (args.output/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
    command=[sys.executable,'-B',str(Path(__file__).with_name('check_candidate_job.py')),
        '--word',str(args.output/'word.json'),'--h',str(args.h),'--output',str(args.output/'review'),
        '--binary',str(args.binary),'--other-profile',str(args.other_profile),'--other-physical',str(args.other_physical),
        '--inherited-certificate',str(args.source_root/'certificates/joint-dual-kappa.json'),
        '--assembly',str(args.source_root/'references/frame-compiler/pr48/research/copied-fixed/balanced_assembly.py')]
    subprocess.run(command,check=True)
    print(json.dumps(dict(status='CHANGED UNIT COMPLETION AND FULL REVIEW PASS',h=args.h,
        roles=result['roles'],completion=args.completion,seconds=time.monotonic()-start)),flush=True)


if __name__=='__main__':main()
