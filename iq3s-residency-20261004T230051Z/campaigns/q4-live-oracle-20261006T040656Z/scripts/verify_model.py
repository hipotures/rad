"""Reuse prior SHA256 verification and verify current size/mtime; optional payload rehash off timing path."""
from pathlib import Path
import json,hashlib,argparse
C=Path(__file__).resolve().parents[1]
def load(p):return json.loads(Path(p).read_text())
def verify(full=False):
 m=load(C/'git/reference-model.json');fresh_path=C/'git/model-full-aux-verified.json';fresh={x['path']:x for x in load(fresh_path)['files']} if fresh_path.exists() else {};assert m['quant']=='UD-Q4_K_XL' and m['revision']=='38bb39ee97821de2c9009abb7e93950eec396e66';rows=[]
 for s in m['shards']:
  p=Path(s['path']);st=p.stat();assert st.st_size==s['bytes'] and st.st_mtime_ns==s['mtime_ns'],str(p);rows.append(dict(s,current_bytes=st.st_size,current_mtime_ns=st.st_mtime_ns,verified_now='previous SHA256 + unchanged size/mtime'))
 for path,v in m['files'].items():
  p=Path(path);st=p.stat();assert st.st_size==v['bytes'],path
  if path in fresh:assert st.st_mtime_ns==fresh[path]['mtime_ns'],'Model auxiliary mtime changed: '+path
  if full or st.st_size<10*1024**2:
   h=hashlib.sha256()
   with p.open('rb') as f:
    while block:=f.read(8*1024**2):h.update(block)
   assert h.hexdigest()==v['sha256'],path
  rows.append({'path':path,'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'sha256':v['sha256'],'payload_sha_checked_now':full or st.st_size<10*1024**2})
 return {'state':'PASS','quant':m['quant'],'revision':m['revision'],'shards_payload_rehashed':False,'model_weights_changed':False,'files':rows,'verification_note':'111GB shards not rehashed or downloaded; prior verified SHA256 plus stable size/mtime. Pack/aux payload hashes verified separately outside timing.'}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--full-aux',action='store_true');a.add_argument('--out');v=a.parse_args();r=verify(v.full_aux);s=json.dumps(r,indent=2)+'\n';print(s)
 if v.out:Path(v.out).write_text(s)
