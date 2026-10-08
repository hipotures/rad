#!/usr/bin/env python3
"""Preserve complete UTF-8 inputs of a completed frozen profile-pool check."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

CAMPAIGN=Path(__file__).resolve().parents[3]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run',action='append',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    assert not args.output.exists()
    files={}
    runs=[]
    for directory in args.run:
        directory=directory.resolve()
        runs.append(str(directory.relative_to(CAMPAIGN)))
        paths=[directory/'protocol.json',directory/'result.json']
        protocol=json.loads(paths[0].read_text())
        paths.append(CAMPAIGN/protocol['geometry_certificate']['path'])
        for ids in protocol['input_files']:
            for identity in ids:
                path=CAMPAIGN/identity['path']
                raw=path.read_bytes()
                assert len(raw)==identity['bytes'] and hashlib.sha256(raw).hexdigest()==identity['sha256']
                paths.append(path)
        for path in paths:
            raw=path.read_bytes()
            files[str(path.resolve().relative_to(CAMPAIGN))]=dict(
                path=str(path.resolve().relative_to(CAMPAIGN)),bytes=len(raw),
                sha256=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf-8'))
    output=dict(format='complete-frozen-profile-pools-v1',
                recorded_utc=datetime.now(timezone.utc).isoformat(),
                capture_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                runs=runs,files=[files[key] for key in sorted(files)],
                scope='Complete original UTF-8 profile, protocol, result and actual-geometry bytes. This bundle supports moment replay; it does not contain producer binaries or replay the matrix-profile construction.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(dict(files=len(files),bytes=args.output.stat().st_size)))


if __name__=='__main__':main()
