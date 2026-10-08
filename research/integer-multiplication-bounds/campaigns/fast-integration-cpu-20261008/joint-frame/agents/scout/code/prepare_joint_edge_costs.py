#!/usr/bin/env python3
"""Certify all exact frame increments needed by actual joint carry edges."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import struct
import subprocess
import sys
import time

from joint_match_components import load_source,components


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root',required=True,type=Path)
    ap.add_argument('--h',required=True,type=int,choices=[23,25])
    ap.add_argument('--binary',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args();assert __debug__;args.output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();compiler=load_source(args.source_root.resolve())
    c,blocks,uses,value_uses,owner,signal,order,contains=compiler.build(args.h)
    edges,groups=components(blocks,uses)
    frame_rows=[(0,0,0),(0,0,args.h)]+[(b['frame'][0],b['frame'][1],b['rank']) for b in blocks]
    pairs=set()
    for g,u,i in edges:
        value,target,_=uses[u];origin=owner[value]
        assert blocks[target]['rank']>blocks[g]['rank']
        assert blocks[g]['rank']>blocks[origin]['rank']
        pairs.update([(g+2,target+2),(g+2,1),(0,origin+2),(origin+2,target+2)])
    ordered=sorted(pairs);mass=sum(frame_rows[b][2]-frame_rows[a][2] for a,b in ordered)
    binary=args.output/'frame-cost-input.bin'
    with binary.open('wb') as stream:
        stream.write(struct.pack('<6I2Q',args.h,comb(args.h,3),0,len(frame_rows),len(ordered),0,mass,mass))
        for frame in frame_rows:stream.write(struct.pack('<2QI',*frame))
        for a,b in ordered:stream.write(struct.pack('<2Iq',a,b,1))
    edge_identity=('\n'.join('%d %d %d'%edge for edge in edges)+'\n').encode()
    protocol=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),h=args.h,
        edges=len(edges),components=len(groups),distinct_frame_increments=len(pairs),
        edge_stream_sha256=sha256(edge_identity).hexdigest(),binary_sha256=sha256(binary.read_bytes()).hexdigest(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source_root=str(args.source_root),native_threads=1,
        model_version=2,
        model='Fixed-cardinality no-reclamation edge internal cost: C(P_target-P_donor)-C(I-P_donor)-C(P_origin)-C(P_target-P_origin). The removed use clone starts at the original value owner frame, not the consumer frame. The fixed role/exterior/denominator term is constant at fixed matching cardinality. Reclamation alters the controller nonlinearly and requires complete physical/profile acceptance.')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    command=[sys.executable,'-B',str(Path(__file__).with_name('integer_crt_certificate.py')),
        '--binary',str(args.binary),'--transitions',str(binary),
        '--profiles',str(args.output/'combined-profile.json'),
        '--dump',str(args.output/'exact-frame-costs.jsonl'),
        '--output',str(args.output/'crt-certificate.json')]
    with (args.output/'profile.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    print(json.dumps(dict(status='EXACT ALL-CORNER JOINT EDGE FRAME COST TABLE PASS',h=args.h,
        edges=len(edges),frame_increments=len(pairs),seconds=time.monotonic()-started)),flush=True)


if __name__=='__main__':main()
