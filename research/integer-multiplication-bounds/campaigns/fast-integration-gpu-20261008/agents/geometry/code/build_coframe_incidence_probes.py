#!/usr/bin/env python3
"""Build DISCOVERY matrix-cost probes, explicitly not physical networks."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import struct

from verify_complemented_source_edge_frames import independent_normal_classes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    configs = []
    manifests = []
    for h,common,vertices,bases in [(23,20,[21,22,0,1],['beta:1:15','beta:-1:12']),
                                  (25,23,[24,0,1,2],['beta:7:207','beta:-1:15'])]:
        edges = list(combinations(vertices,2))
        frames = [(0,0,(0,)*h),(h,0,(0,)*h)]
        lookup = {}
        by_mask = {}
        for mask in range(1 << len(edges)):
            selected = [edge for i,edge in enumerate(edges) if mask >> i & 1]
            normals,symbols,components = independent_normal_classes(h,common,selected)
            frame = (h-1-len(normals),(1 << 63)|(1 << common),tuple(symbols))
            if frame not in lookup:
                lookup[frame] = len(frames)
                frames.append(frame)
            by_mask[mask] = lookup[frame]
        transitions = Counter()
        for low,a in by_mask.items():
            for high,b in by_mask.items():
                if low & high == low and frames[b][0]>frames[a][0]:
                    transitions[a,b] = 1
        for edge in edges:
            forced = (1 << common)|sum(1 << i for i in edge)
            frame = (1,forced,tuple(int(forced >> i & 1) for i in range(h)))
            fid = len(frames)
            frames.append(frame)
            for mask,b in by_mask.items():
                if mask >> edges.index(edge) & 1 and frames[b][0]>1:
                    transitions[fid,b] = 1
        mass = sum((frames[b][0]-frames[a][0])*count for (a,b),count in transitions.items())
        data = bytearray(b'RADCOF01')
        data.extend(struct.pack('<6I2Q',h,0,0,len(frames),len(transitions),0,mass,0))
        for rank,forced,symbols in frames:
            data.extend(struct.pack('<QI',forced,rank))
            data.extend(struct.pack(f'<{h}b',*symbols))
        for (a,b),count in sorted(transitions.items()):
            data.extend(struct.pack('<2Iq',a,b,count))
        binary = args.work/f'h{h}-coframe-incidence-probe.bin'
        binary.write_bytes(data)
        manifests.append(dict(h=h,common=common,vertices=vertices,
            input_binary_sha256=sha256(data).hexdigest(),frames=len(frames),
            transitions=len(transitions),probe_rank_mass=mass,
            physical_network=False,role_denominator=None,
            scope='All exact nested incidence-span pairs on four outside vertices '
                  'plus every included rank-one source injection. Matrix costs only.'))
        for basis in bases:
            configs.append(dict(case_id=f'h{h}-incidence-probe-{basis.replace(":","-")}',
                                transitions=str(binary),basis=basis))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(configs,indent=2)+'\n')
    (args.work/'manifest.json').write_text(json.dumps(dict(
        classification='DISCOVERY MATRIX PROBE, NOT A PHYSICAL NETWORK',
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        inputs=manifests),indent=2)+'\n')
    print(json.dumps(manifests),flush=True)


if __name__ == '__main__':
    main()
