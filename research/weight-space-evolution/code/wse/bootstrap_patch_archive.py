"""Lossless JSON evidence export/recovery of candidate lineage deltas, including BF16 bit patterns."""
import argparse
import json
from pathlib import Path

import numpy as np

from . import patch


def export(pid, destination):
    rec=patch.load_patch(pid)
    with np.load(patch.patches_dir()/pid/'delta.npz',allow_pickle=False) as z:
        arrays={k:{'dtype':str(z[k].dtype),'values':z[k].tolist()} for k in z.files}
    body={'schema':'wse-lossless-patch-1','patch':rec,'arrays':arrays}
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    p=destination/(pid+'.json')
    text=json.dumps(body,separators=(',',':'))
    if p.exists() and p.read_text()!=text:raise ValueError('refusing changed evidence export')
    if not p.exists():p.write_text(text)
    return p


def recover(path):
    body=json.loads(Path(path).read_text());rec=body['patch'];names=[t['name'] for t in rec['tensors']]
    proposed={n:a.copy() for n,(_,a) in patch.materialize(rec['gold_id'],rec['parent_id'],names).items()}
    for t in rec['tensors']:
        arrays=body['arrays'];key=t['key']
        idx=np.asarray(arrays[key+'_idx']['values'],dtype=arrays[key+'_idx']['dtype'])
        val=np.asarray(arrays[key+'_val']['values'],dtype=arrays[key+'_val']['dtype'])
        proposed[t['name']].reshape(-1)[idx]=val
    rebuilt=patch.create(rec['gold_id'],proposed,rec['policy'],rec['meta'],rec['parent_id'])
    if rebuilt['patch_id']!=rec['patch_id']:raise ValueError('recovered patch identity mismatch')
    return rebuilt['patch_id']


def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='command',required=True)
    e=sp.add_parser('export');e.add_argument('--out',required=True);e.add_argument('patch_id')
    r=sp.add_parser('recover');r.add_argument('path')
    a=ap.parse_args()
    if a.command=='export':
        for pid in patch.lineage(a.patch_id):print(export(pid,a.out))
    else:print(recover(a.path))


if __name__=='__main__':main()
