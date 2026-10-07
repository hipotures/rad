"""Complete typed text export of retained binary journals; originals are untouched."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from trace_io import P,H,read_gpu
from inspect_oracle import E,L,N
D=np.dtype([(f,'<i4') for f in ['generation','first_use','last_use','distinct_uses','evicted_at','released_at','expiry','reason']])
def value(x):
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 return x

def export(p):
 dest=p/'raw/trace-export.jsonl';assert not dest.exists();prefix=p/'raw/oracle';sources=[]
 with dest.open('x') as f:
  def emit(v):f.write(json.dumps(v,separators=(',',':'))+'\n')
  emit({'type':'schema','version':2,'request':p.name,'meaning':'Complete original field values; chronologies use timestamps/logical IDs, never vector position. Padding fields are included where present.'})
  for kind,suffix,dtype in [('admission','-admissions.bin',E),('layer','-layers.bin',L),('native','-native.bin',N),('lifecycle','-lifecycle.bin',D),('publication','-publication-trace.bin',P),('producer','-producer-trace.bin',H)]:
   source=Path(str(prefix)+suffix)
   if not source.exists():continue
   data=np.fromfile(source,dtype);sha=hashlib.file_digest(source.open('rb'),'sha256').hexdigest();sources.append({'path':str(source),'sha256':sha,'bytes':source.stat().st_size,'rows':len(data),'type':kind})
   emit({'type':'source','record_type':kind,'path':str(source),'sha256':sha,'bytes':source.stat().st_size,'dtype':dtype.descr})
   for row in data:emit({'type':kind,**{name:value(row[name]) for name in dtype.names}})
  for d in [0,1]:
   source=Path(str(prefix)+f'-gpu{d}-trace.bin');g=read_gpu(source);sha=hashlib.file_digest(source.open('rb'),'sha256').hexdigest();sources.append({'path':str(source),'sha256':sha,'bytes':source.stat().st_size,'type':f'gpu{d}'})
   emit({'type':'gpu_header','device':d,'header':g['header'].tolist(),'source':str(source),'sha256':sha})
   for kind,records in enumerate(g['rows']):
    for row in records:emit({'type':'gpu','device':d,'kind':kind,**{name:value(row[name]) for name in records.dtype.names}})
  emit({'type':'end','source_files':len(sources)})
 (p/'trace-export-manifest.json').write_text(json.dumps({'path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.file_digest(dest.open('rb'),'sha256').hexdigest(),'sources':sources,'omitted':['Original full tape and numerical activation observations; external hashed artifacts, fidelity summaries retain sampled activation checks.'],'recovery':'Typed journal/GPU field values recoverable from this complete text; original tape not recoverable from a hash.'},indent=2)+'\n')
 print('EXPORTED',p.name,dest.stat().st_size,flush=True)
if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('--raw-root',required=True,type=Path);args=q.parse_args()
 for p in sorted(args.raw_root.iterdir()):
  if (p/'episode.json').exists():export(p)
