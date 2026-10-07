"""After all inference stops, verify and snapshot compatible historical tapes."""
import hashlib,json,pathlib,shutil,time,subprocess
C=pathlib.Path(__file__).resolve().parents[1];R=C.parents[1];P=R/'campaigns/q4-live-oracle-20261006T040656Z'
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,timeout=8).strip(),'No heavy hashing/copying during GPU inference'
out=[];d=C/'extended';d.mkdir(exist_ok=True)
for name in ['capture-32k-v3','capture-128k-v3','capture-256k-v3','independent-code4-capture-v3']:
 p=P/'tapes'/(name+'.bin');proof=P/'phase-a'/(name+'-fidelity.json')
 if not p.exists() or not proof.exists():continue
 j=json.loads(proof.read_text());assert j['state']=='PASS';expected=j['tape']['tape_sha256'];h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(8*1024**2):h.update(b)
 assert h.hexdigest()==expected,(name,'historical tape changed')
 dest=d/p.name;shutil.copyfile(p,dest)
 for suffix in ['.initial-state.bin']:
  src=pathlib.Path(str(p)+suffix)
  if src.exists():shutil.copyfile(src,str(dest)+suffix)
 out.append({'name':name,'origin':str(p),'snapshot':str(dest),'tape_sha256':expected,'bytes':p.stat().st_size,'validation':str(proof),'validation_state':'PASS','source_SHA':'117bc89b3bacbf263379c336557e6c8aa07aff5e','binary_SHA':'30a31432b5aff51bcd4340900c13cad0c8487a832bfdb22d05f9157b88d5bdb3','trace_type':'FULL_REPLAY_TAPE','protocol':'Original fixed4096/64 warmup,natural record/native cache; original output budget retained','extended_256K':'256k' in name,'prior_evaluation_exposure':True,'core_replacement':False,'reason':'Compatible validated existing capture,not a new independent natural core task; original wrapper/input IDs differ'})
(C/'provenance/compatible-existing-tapes.json').write_text(json.dumps({'items':out,'new_GPU_recordings':0,'note':'Immutable verified snapshots of already-existing natural recordings; original files unchanged; future replay must check hashes'},indent=2)+'\n');print('EXISTING TAPES VERIFIED/SNAPSHOTTED',len(out),flush=True)
