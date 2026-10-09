#!/usr/bin/env python3
"""Restore unchanged public mathematical inputs from full gzip evidence.

Existing files are verified, never replaced. Apache-2.0; OpenAI assistance.
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


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package', type=Path, required=True)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    need(not sys.flags.optimize, 'Optimized Python unsupported')
    need(args.output is None or not args.output.exists(), 'Fresh report path required')
    inputs = json.loads((args.package/'transfer-inputs.json').read_bytes())
    with gzip.open(args.archive/'archive-manifest.jsonl.gz', 'rt') as stream:
        records = {x['path']: x for line in stream if (x := json.loads(line)).get('status') == 'archived'}
    recovered = {}
    for name, item in inputs['files'].items():
        if not item['path'].startswith('inputs/'):
            continue
        relative = Path(item['path'])
        need(not relative.is_absolute() and '..' not in relative.parts, 'Unsafe input path')
        record = records[item['path']]
        need(record['original_sha256'] == item['sha256'] and record['original_bytes'] == item['bytes'],
             'Archived scientific input identity differs: '+name)
        compressed = (args.archive/(item['path']+'.gz')).read_bytes()
        need(sha256(compressed).hexdigest() == record['gzip_sha256'], 'Compressed input corruption')
        raw = gzip.decompress(compressed)
        need(len(raw) == item['bytes'] and sha256(raw).hexdigest() == item['sha256'], 'Decoded input corruption')
        target = args.package/relative
        existed = target.exists()
        if existed:
            need(target.read_bytes() == raw, 'Existing input differs; no overwrite: '+str(target))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as out:
                out.write(raw)
        recovered[name] = dict(path=item['path'], bytes=len(raw), sha256=item['sha256'], existing_verified=existed)
    need(len(recovered) == 3, 'Expected all three complete mathematical inputs')
    result = dict(status='PASS no-clobber recovery of original public mathematical input bytes',
        recovered=recovered, scientific_input_metadata_unchanged=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print('PASS exact no-clobber recovery of three portable mathematical inputs')


if __name__ == '__main__':
    main()
