#!/usr/bin/env python3
"""Fetch immutable public PR54, PR53 and PR51 snapshots outside the checkout.

Public constructions: Chafik Boukhalfa (#54), Avi Eisenberg (#53), and
RaD / hipotures (#51), with all upstream NOTICE and assistance credits.
This acquisition helper is not a mathematical verifier.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import io
import json
from pathlib import Path
import subprocess
import tarfile

REPOSITORY='CrocSwap/integer-mult-bounds'
URL='https://github.com/'+REPOSITORY+'.git'
PINS={54:'84eb0b067741dc2690da837743fda06d133da865',
      53:'3ffd4021995c959ac02d12920e0279ae97dd03c7',
      51:'ee552125fb82c1664740fcc6c5eb97cad74d6bbd'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args()
    assert not args.work.exists(),'Each acquisition needs a fresh external directory.'
    args.work.mkdir(parents=True)
    metadata={}
    for number in PINS:
        raw=subprocess.check_output(['gh','api',f'repos/{REPOSITORY}/pulls/{number}'])
        metadata[number]=json.loads(raw)
        (args.work/f'pr-{number}.json').write_bytes(raw)
    bare=args.work/'objects.git'
    subprocess.run(['git','init','--bare','--quiet',str(bare)],check=True)
    git=['git','--git-dir',str(bare)]
    subprocess.run(git+['fetch','--quiet',URL,
        *[f'refs/pull/{n}/head:refs/sources/pr{n}'for n in PINS]],check=True)
    manifest=dict(utc=datetime.now(timezone.utc).isoformat(),upstream=URL,
                  helper_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),sources=[])
    for number,pin in PINS.items():
        exists=subprocess.run(git+['cat-file','-e',pin+'^{commit}'],capture_output=True)
        if exists.returncode:
            subprocess.run(git+['fetch','--quiet',URL,pin],check=True)
        resolved=subprocess.check_output(git+['rev-parse','--verify',pin+'^{commit}'],text=True).strip()
        assert resolved==pin
        destination=args.work/f'pr{number}-{pin}'
        destination.mkdir()
        archive=subprocess.check_output(git+['archive',pin])
        with tarfile.open(fileobj=io.BytesIO(archive)) as container:
            container.extractall(destination,filter='data')
        records=[]
        for path in sorted(destination.rglob('*')):
            if path.is_file():
                assert not path.is_symlink()
                records.append(dict(path=str(path.relative_to(destination)),bytes=path.stat().st_size,
                                    sha256=sha256(path.read_bytes()).hexdigest()))
                path.chmod(0o444)
        for path in sorted(destination.rglob('*'),reverse=True):
            if path.is_dir():path.chmod(0o555)
        destination.chmod(0o555)
        source=dict(pr=number,pinned_commit=pin,current_pr_head=metadata[number]['head']['sha'],
                    snapshot=str(destination),archive_sha256=sha256(archive).hexdigest(),
                    files=records,immutable=True)
        manifest['sources'].append(source)
        print(json.dumps({k:source[k]for k in ['pr','pinned_commit','current_pr_head','snapshot']}),flush=True)
    (args.work/'snapshot-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
