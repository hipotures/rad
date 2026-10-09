#!/usr/bin/env python3
"""Decode immutable PR165 finite inputs, checking all package source pins.

RaD; GPT-6.1 Sol assistance. Apache-2.0. Export only: graph/closure/word
regeneration and signed/reflected certification are separate commands.
"""
import argparse
from datetime import datetime,timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if sys.flags.optimize:raise ValueError('assertion-disabled execution rejected')
    selected=a.source/'research/paired-cube-plateau-162/selected/complex'
    pins=json.loads((selected/'result.json').read_text())['pins']
    a.output.mkdir(parents=True,exist_ok=False);outpins={}
    for name,digest in pins.items():
        compressed=(selected/name).read_bytes()
        if sha256(compressed).hexdigest()!=digest:raise ValueError('source pin: '+name)
        raw=gzip.decompress(compressed);json.loads(raw)
        out=a.output/name.removesuffix('.gz');out.write_bytes(raw);out.chmod(0o444)
        outpins[out.name]=dict(compressed_sha256=digest,sha256=sha256(raw).hexdigest(),bytes=len(raw))
    protocol=dict(started_utc=datetime.now(timezone.utc).isoformat(),source_root=str(a.source.resolve()),
                  source_head='7518fed2688baf25c7c32bae32674f3334b517da',input_pins=outpins,
                  source_pin_file_sha256=sha256((selected/'result.json').read_bytes()).hexdigest(),
                  driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Immutable pin-checked finite input export; no source or historical search regeneration claim.')
    with (a.output/'protocol.json').open('x') as stream:
        json.dump(protocol,stream,indent=2);stream.write('\n')
    print('PASS immutable PR165 decoded input export; %d files' % len(outpins))


if __name__=='__main__':main()
