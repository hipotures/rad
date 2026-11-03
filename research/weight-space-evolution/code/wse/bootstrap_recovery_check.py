"""Recover every archived parent patch in a fresh registry and compare tensor hashes without changing production."""
import gzip
import json
import os
from pathlib import Path
import shutil
import uuid

from . import patch, registry
from .bootstrap_broker import GOLD
from .bootstrap_patch_archive import recover
from .bootstrap_prepare import TOPIC
from .tensors import sha256_array


def main():
    if os.environ.get('WSE_WORK_ROOT'):raise RuntimeError('unset work override')
    original=registry.gold_dir(GOLD)
    if not registry.verify(GOLD):raise RuntimeError('original Gold invalid')
    man=registry.manifest(GOLD)
    archives=TOPIC/'evidence/20261103T-phaseD-bootstrap-parent-provenance/patch-exports'
    root=TOPIC/'work/tmp'/('bootstrap-recovery-'+uuid.uuid4().hex)
    gold=root/'gold'/GOLD;gold.mkdir(parents=True)
    shutil.copyfile(original/'gold_manifest.json',gold/'gold_manifest.json')
    os.link(original/man['file'],gold/man['file'])
    (gold/'gold_manifest.json').chmod(0o400);gold.chmod(0o500)
    inputs=root/'inputs';inputs.mkdir()
    records={}
    for source in sorted(archives.glob('*.json.gz')):
        p=inputs/source.stem;p.write_bytes(gzip.decompress(source.read_bytes()))
        records[json.loads(p.read_text())['patch']['patch_id']]=p
    if len(records)!=46:raise RuntimeError('unexpected archived population')
    os.environ['WSE_WORK_ROOT']=str(root)
    recovered=[]
    try:
        while records:
            ready=[pid for pid,p in records.items() if json.loads(p.read_text())['patch']['parent_id'] in [None]+recovered]
            if not ready:raise RuntimeError('missing ancestor or cycle')
            for pid in ready:
                path=records.pop(pid)
                if recover(path)!=pid:raise RuntimeError('recovery identity mismatch')
                rec=patch.load_patch(pid);names=[t['name'] for t in rec['tensors']]
                values=patch.materialize(GOLD,pid,names)
                if not all(sha256_array(values[t['name']][1])==t['edited_sha256'] for t in rec['tensors']):
                    raise RuntimeError('recovered tensor checksum differs')
                recovered.append(pid)
        if not registry.verify(GOLD):raise RuntimeError('recovery Gold changed')
    finally:
        os.environ.pop('WSE_WORK_ROOT',None)
    if not registry.verify(GOLD):raise RuntimeError('production Gold changed')
    result={'recovered_patches':len(recovered),'patch_ids':recovered,'all_patch_ids_match':True,
            'all_tensor_hashes_match':True,'original_gold_unchanged':True,
            'method':'fresh isolated registry with read-only hard link to immutable Gold; every archive decompressed and reconstructed',
            'temporary_registry':str(root.relative_to(TOPIC))}
    out=TOPIC/'runs/20261103T-phaseD-bootstrap-execution/results/recovery_check.json'
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
