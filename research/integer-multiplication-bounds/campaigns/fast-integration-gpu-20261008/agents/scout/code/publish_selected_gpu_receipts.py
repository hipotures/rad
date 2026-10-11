#!/usr/bin/env python3
"""Archive explicit completed GPU runs without copying binary execution arrays."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run-paths',type=Path,nargs='+',required=True)
    ap.add_argument('--publication-id',required=True)
    args=ap.parse_args()
    own=Path(__file__).resolve().parent.parent
    repo=next(x for x in own.parents if (x/'tools/archive_workspace.py').is_file())
    evidence=own/'evidence'/args.publication_id
    compact=own/'gpu-parameter-results'/args.publication_id
    assert not evidence.exists() and not compact.exists()
    assert len({x.name for x in args.run_paths})==len(args.run_paths)
    compact.mkdir(parents=True)
    rows=[]
    for source in args.run_paths:
        assert (source/'summary.json').is_file(),source
        destination=evidence/source.name
        for action in ('pack-text','verify-text'):
            command=[sys.executable,str(repo/'tools/archive_workspace.py'),action]
            if action=='pack-text':command+=['--source',str(source)]
            command+=['--destination',str(destination)]
            if action=='verify-text':command+=['--check-originals']
            subprocess.run(command,check=True)
        readable=compact/source.name;readable.mkdir()
        metadata=[]
        for name in ('protocol.json','summary.json','termination.json','failure.json'):
            p=source/name
            if not p.exists():continue
            data=p.read_bytes();assert len(data)<1024**2
            target=readable/name;target.write_bytes(data)
            metadata.append({'original':str(p),'readable_copy':str(target),
                             'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        files=list(destination.glob('*.gz'))
        assert files and all(x.stat().st_size<10485760 for x in files)
        manifest=destination/'archive-manifest.jsonl.gz'
        rows.append({'run':source.name,'original':str(source),'archive_namespace':str(destination),
                     'archive_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
                     'gzip_bytes':sum(x.stat().st_size for x in files),'gzip_files':len(files),
                     'readable_metadata':metadata,
                     'binary_policy':'Binary arrays remain external, bound by original summaries and deterministic pinned generators. No arrays or dependencies copied to Git.'})
    result={'utc':datetime.now(timezone.utc).isoformat(),
            'status':'PASS COMPLETE SELECTED GPU TEXT ARCHIVES; ORIGINAL HASHES VERIFIED',
            'publisher_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'runs':rows,'total_gzip_bytes':sum(x['gzip_bytes'] for x in rows),
            'originals_changed':False,'scope':'Explicit completed runs only; complete unsplit text gzip evidence and compact readable metadata. Large binary execution arrays are deterministically regenerable and described in the artifact manifest.'}
    (compact/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'runs':len(rows),'gzip_bytes':result['total_gzip_bytes']}))


if __name__=='__main__':
    main()
