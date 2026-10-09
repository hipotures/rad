#!/usr/bin/env python3
"""Fetch a pinned GitHub source archive through gh into ignored sprint storage."""
import argparse, hashlib, json, subprocess, tarfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('repo');p.add_argument('sha');p.add_argument('label');a=p.parse_args()
s=Path(__file__).resolve().parents[1]; dest=s/'work/repos'/a.label
if dest.exists(): raise SystemExit(f'Refusing overwrite: {dest}')
archive=s/'work/inputs'/f'{a.label}.tar.gz'
with archive.open('xb') as f: subprocess.run(['gh','api',f'repos/{a.repo}/tarball/{a.sha}'],stdout=f,check=True,timeout=180)
with tarfile.open(archive,'r:gz') as tf:
 members=tf.getmembers();roots={m.name.split('/')[0] for m in members}
 if len(roots)!=1:raise ValueError('Unexpected archive roots')
 for m in members:
  q=Path(m.name)
  if q.is_absolute() or '..' in q.parts or m.issym() or m.islnk() or m.isdev(): raise ValueError(f'Unsafe entry {m.name}')
 dest.mkdir()
 for m in members:
  parts=Path(m.name).parts[1:]
  if not parts:continue
  m.name=str(Path(*parts));tf.extract(m,dest,filter='data')
manifest={'repository':a.repo,'revision':a.sha,'archive':str(archive.relative_to(s)),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,'directory':str(dest.relative_to(s))}
(s/'work/receipts'/f'source-{a.label}.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest))
