#!/usr/bin/env python3
"""Recover a declared transfer closure from source caches and complete evidence.

No original derived work files are read. Download pinned source tarballs into
the manifest's source-cache layout first. Apache-2.0; OpenAI assistance.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys

sys.dont_write_bytecode = True


def need(condition, message):
    if not condition:
        raise ValueError(message)


def relative(value):
    path = Path(value)
    need(not path.is_absolute() and '..' not in path.parts, 'Nonrelative recovery path')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sprint', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--source-cache', type=Path, required=True)
    parser.add_argument('--group', default='lifetime_fused')
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    need(not sys.flags.optimize, 'Optimized execution unsupported')
    need(not args.output_root.exists() and not args.report.exists(), 'Fresh output paths required')
    manifest_raw = args.manifest.read_bytes()
    manifest = json.loads(manifest_raw)
    records = manifest['groups'][args.group]
    args.output_root.mkdir(parents=True)
    recovered = {}
    kinds = {}
    for name, pin in records.items():
        recovery = pin['recovery']
        kind = recovery['kind']
        if kind == 'repository_file':
            raw = (args.sprint/relative(recovery['path'])).read_bytes()
        elif kind == 'downloaded_source':
            source = manifest['source_snapshots'][recovery['snapshot']]
            path = args.source_cache/relative(source['source_root'])/relative(recovery['relative_path'])
            raw = path.read_bytes()
        elif kind == 'gzip':
            compressed = (args.sprint/relative(recovery['path'])).read_bytes()
            need(sha256(compressed).hexdigest() == recovery['sha256'], 'Evidence corruption: '+name)
            raw = gzip.decompress(compressed)
            need(len(raw) == recovery['decoded_bytes'], 'Incomplete gzip evidence: '+name)
        else:
            raise ValueError('Unsupported recovery kind: '+kind)
        need(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'],
             'Recovered source/input corruption: '+name)
        output = args.output_root/relative(pin['path'])
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            need(output.read_bytes() == raw, 'Inconsistent duplicate target: '+name)
        else:
            output.write_bytes(raw)
        recovered[name] = dict(path=pin['path'], bytes=len(raw), sha256=pin['sha256'], recovery_kind=kind)
        kinds[kind] = kinds.get(kind, 0)+1
    result = dict(status='PASS complete declared byte recovery without original derived work',
        group=args.group, manifest_sha256=sha256(manifest_raw).hexdigest(), records=len(records),
        unique_files=len({p['path'] for p in records.values()}), recovery_kinds=kinds,
        recovered=recovered, scope='Pinned source-cache bytes and committed readable/gzip evidence only. '
            'This checks recoverability and byte identities; the associated mathematical and finite gates are separate.')
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('PASS recovery '+args.group+': '+str(len(records))+' records, '+str(result['unique_files'])+' files')


if __name__ == '__main__':
    main()
