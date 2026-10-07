"""Hash/verify retained immutable artifacts after GPU inference stops; progress remains mutable."""
import argparse,datetime,hashlib,json,pathlib,subprocess,time
C=pathlib.Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--verify',action='store_true');v=a.parse_args()
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,timeout=8).strip(),'GPU conflict; no heavy hashing during inference'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(8*1024**2):h.update(b)
 return h.hexdigest()
last=time.monotonic();out=[]
if v.verify:
 m=json.loads((C/'artifact-manifest.json').read_text());files=m['files']
 for i,x in enumerate(files):
  p=C/x['relative_path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],x['relative_path']
  if time.monotonic()-last>=20:print('ARTIFACT VERIFY HEARTBEAT',i+1,'/',len(files),flush=True);last=time.monotonic()
 r={'state':'PASS','verified_files':len(files),'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()};(C/'artifact-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('ARTIFACT VERIFY PASS',len(files),flush=True)
else:
 skipped={'artifact-manifest.json','artifact-verification.json','progress.json','progress.jsonl','STATUS.md','progress.json.tmp'}
 for p in sorted(C.rglob('*')):
  if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts or p.name in skipped:continue
  out.append({'relative_path':str(p.relative_to(C)),'bytes':p.stat().st_size,'sha256':sha(p)})
  if time.monotonic()-last>=20:print('ARTIFACT HASH HEARTBEAT',len(out),flush=True);last=time.monotonic()
 (C/'artifact-manifest.json').write_text(json.dumps({'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'All observed campaign files except this manifest,verification report,bytecode and mutable lifecycle progress/STATUS; original binary/model provenance remains in separate exact identity manifests','files':out},indent=2)+'\n');print('ARTIFACT MANIFEST WRITTEN',len(out),'files',flush=True)
