"""Recover binary journal bytes from a complete plain/gzip text export, without inference."""
import argparse,gzip,json,hashlib
from pathlib import Path
import numpy as np
from trace_io import P,H,G
from inspect_oracle import E,L,N
D=np.dtype([(f,'<i4') for f in ['generation','first_use','last_use','distinct_uses','evicted_at','released_at','expiry','reason']])
T={'admission':E,'layer':L,'native':N,'lifecycle':D,'publication':P,'producer':H}
def main():
 q=argparse.ArgumentParser();q.add_argument('--input',required=True,type=Path,nargs='+');q.add_argument('--output',required=True,type=Path);a=q.parse_args();a.output.mkdir(parents=True,exist_ok=False);handles={};gpu={};expected={}
 def lines():
  for path in a.input:
   with gzip.open(path,'rt') if path.suffix=='.gz' else path.open() as reader:
    yield from reader
 for line in lines():
  x=json.loads(line);kind=x['type']
  if kind=='source':
   k=x['record_type'];name=Path(x['path']).name;handles[k]=(a.output/name).open('xb');expected[name]=x['sha256']
  elif kind in T:
   dtype=T[kind];row=np.zeros(1,dtype)
   for f in dtype.names:row[f]=x[f]
   handles[kind].write(row.tobytes())
  elif kind=='gpu_header':
   d=x['device'];gpu[d]={'header':x['header'],'name':Path(x['source']).name,'rows':[[] for _ in range(11)]};expected[gpu[d]['name']]=x['sha256']
  elif kind=='gpu':gpu[x['device']]['rows'][x['kind']].append(tuple(x[k] for k in G.names))
 for f in handles.values():f.close()
 for g in gpu.values():
  with (a.output/g['name']).open('xb') as f:
   f.write(np.array(g['header'],'<u8').tobytes())
   for records in g['rows']:f.write(np.array(records,dtype=G).tobytes())
 for name,sha in expected.items():assert hashlib.file_digest((a.output/name).open('rb'),'sha256').hexdigest()==sha,('Binary journal recovery mismatch',name)
 print(json.dumps({'state':'PASS','files_restored_exact_SHA256':len(expected),'no_inference':True}))
if __name__=='__main__':main()
