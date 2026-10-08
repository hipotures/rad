#!/usr/bin/env python3
"""Run one sequential independent finite candidate review lane."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['word','output','binary','other_profile','other_physical','inherited_certificate','assembly']:
        ap.add_argument('--'+name.replace('_','-'),required=True,type=Path)
    ap.add_argument('--h',required=True,type=int,choices=[23,25])
    args=ap.parse_args();assert __debug__
    args.output.mkdir(parents=True,exist_ok=False)
    own=Path(__file__).resolve().parent
    commands=[
        [sys.executable,'-B',str(own/'check_pr58_word.py'),'--word',str(args.word),
         '--transitions',str(args.output/'transitions.bin'),'--output',str(args.output/'physical.json')],
        [sys.executable,'-B',str(own/'integer_crt_certificate.py'),'--binary',str(args.binary),
         '--transitions',str(args.output/'transitions.bin'),'--profiles',str(args.output/'integer.profiles.json'),
         '--output',str(args.output/'integer.certificate.json')]]
    pair=[None,None];phys=[None,None];index=(args.h-23)//2
    pair[index]=args.output/'integer.profiles.json';pair[1-index]=args.other_profile
    phys[index]=args.output/'physical.json';phys[1-index]=args.other_physical
    commands.append([sys.executable,'-B',str(own/'check_joint_moment.py'),
        '--profile23',str(pair[0]),'--profile25',str(pair[1]),
        '--physical23',str(phys[0]),'--physical25',str(phys[1]),
        '--inherited-certificate',str(args.inherited_certificate),'--assembly',str(args.assembly),
        '--output',str(args.output/'complete-moment.json')])
    protocol=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),commands=commands,
        word_sha256=sha256(args.word.read_bytes()).hexdigest(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),native_threads=1)
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    for i,command in enumerate(commands):
        with (args.output/f'step{i}.log').open('w') as log:
            subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    result=json.loads((args.output/'complete-moment.json').read_text())
    print(json.dumps({k:result[k] for k in ['status','saving','kappa']}),flush=True)


if __name__=='__main__':main()
