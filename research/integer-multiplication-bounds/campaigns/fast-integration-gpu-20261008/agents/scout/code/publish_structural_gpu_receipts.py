#!/usr/bin/env python3
"""Publish completed structural GPU text while leaving raw binary arrays external."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-stems',nargs='+',required=True)
    ap.add_argument('--publication-id',required=True)
    ap.add_argument('--reuse-publication')
    args = ap.parse_args()
    own = Path(__file__).resolve().parent.parent
    repo = own.parents[5]
    derived = Path('/srv/ai/work/rad/integer-multiplication-bounds/fast-integration-gpu-20261008/derived/scout')
    evidence = own/'evidence'/args.publication_id
    compact = own/'gpu-parameter-results'/args.publication_id
    assert not evidence.exists() and not compact.exists()
    compact.mkdir(parents=True)
    rows = []
    for stem in args.run_stems:
        for device in (0,1):
            source = derived/f'{stem}-device{device}'
            completed = source/'summary.json'
            termination = source/'termination.json'
            assert completed.is_file() or termination.is_file(),source
            namespace = source.name
            reused = own/'evidence'/args.reuse_publication/namespace if args.reuse_publication else None
            destination = reused if reused is not None and reused.is_dir() else evidence/namespace
            if destination == evidence/namespace:
                subprocess.run([sys.executable,str(repo/'tools/archive_workspace.py'),'pack-text','--source',str(source),'--destination',str(destination)],check=True)
            subprocess.run([sys.executable,str(repo/'tools/archive_workspace.py'),'verify-text','--destination',str(destination),'--check-originals'],check=True)
            readable = compact/namespace;readable.mkdir()
            preserved = []
            # Hundreds of individual swap receipts belong in complete gzip
            # evidence. Copy only compact run metadata as readable JSON.
            for name in ('protocol.json','summary.json','termination.json','failure.json'):
                p = source/name
                if not p.exists():continue
                data = p.read_bytes()
                assert len(data) < 1024**2,(p,len(data))
                (readable/name).write_bytes(data)
                preserved.append({'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'readable_copy':str(readable/name)})
            files = list(destination.glob('*.gz'))
            rows.append({'run':namespace,'original_completed_text':str(source),
                         'archive_namespace':str(destination),'archive_manifest_sha256':hashlib.sha256((destination/'archive-manifest.jsonl.gz').read_bytes()).hexdigest(),
                         'gzip_files':len(files),'gzip_bytes':sum(p.stat().st_size for p in files),
                         'readable_metadata':preserved,
                         'omitted_from_Git':'Binary pivot/status arrays, CUDA caches and downloaded dependencies remain external. Complete text evidence includes per-order frequencies and controls, rather than only aggregate totals.'})
    result = {'created_utc':datetime.now(timezone.utc).isoformat(),'status':'COMPLETE STRUCTURAL GPU TEXT PUBLICATION; ALL ORIGINAL HASHES VERIFIED',
              'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'runs':rows,'total_gzip_bytes':sum(x['gzip_bytes'] for x in rows),
              'recovery':'Pinned readable generators and recorded input orders deterministically regenerate omitted arrays. Each complete source text is archived without splitting; originals remain unchanged.'}
    (compact/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'runs':len(rows),'gzip_bytes':result['total_gzip_bytes']}))


if __name__ == '__main__':
    main()
