"""Restore retained text and exact journals to a new namespace without GPU work."""
import argparse,gzip,json,hashlib,subprocess,sys
from pathlib import Path
C=Path(__file__).resolve().parents[1]
def main():
    q=argparse.ArgumentParser();q.add_argument('--output',type=Path,required=True);a=q.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    archive=C/'evidence/requests-20261007T194914Z';files=0
    with gzip.open(archive/'archive-manifest.jsonl.gz','rt') as f:
        for line in f:
            x=json.loads(line)
            if x.get('status')!='archived' or x['path'].endswith('trace-export.jsonl'):continue
            rel=Path(x['path']);assert not rel.is_absolute() and '..' not in rel.parts
            dest=a.output/rel;dest.parent.mkdir(parents=True,exist_ok=True)
            data=gzip.decompress((archive/(x['path']+'.gz')).read_bytes());assert hashlib.sha256(data).hexdigest()==x['original_sha256'];dest.write_bytes(data);files+=1
    journals=C/'evidence/journals-20261007T194914Z'
    for point in sorted(journals.iterdir()):
        if not point.is_dir():continue
        temporary=a.output/(point.name+'-restored-journals')
        subprocess.run([sys.executable,str(C/'code/restore_trace.py'),'--input',*map(str,sorted(point.glob('*.jsonl.gz'))),'--output',str(temporary)],check=True,timeout=90)
        dest=a.output/point.name/'raw';dest.mkdir(exist_ok=True)
        for file in temporary.iterdir():file.rename(dest/file.name)
        temporary.rmdir();print('RESTORED_POINT',point.name,flush=True)
    print(json.dumps({'state':'PASS','text_files':files,'journal_original_SHA256_checked':True,'no_inference':True}))
if __name__=='__main__':main()
