"""Pin primary decision-model references via gh; no model checkpoint downloads."""
import base64, hashlib, json, subprocess, shutil
from pathlib import Path
C=Path(__file__).resolve().parents[1];R=C.parents[1]
def gh(endpoint):return json.loads(subprocess.check_output(['gh','api',endpoint],timeout=60))
out=C/'sources';out.mkdir(exist_ok=True)
records=[]
for repo,revision,selected in [('Zefan-Cai/Open-Jev','bd4118882f733574a3250a4b65fe4d884130c08b',None),('rkinas/basal','c3cab778b8cac8f1cc40ddfc982c5c809570c1e7',None)]:
 folder=out/repo.replace('/','-');folder.mkdir(exist_ok=True)
 meta=gh('repos/'+repo);tree=gh(f'repos/{repo}/git/trees/{revision}?recursive=1')
 (folder/'metadata.json').write_text(json.dumps({'repository':repo,'revision':revision,'license':meta.get('license')},indent=2)+'\n')
 (folder/'tree.json').write_text(json.dumps(tree,indent=2)+'\n')
 paths=[x['path'] for x in tree['tree'] if x['type']=='blob' and x.get('size',0)<150000]
 chosen=[p for p in paths if p in ['README.md','LICENSE','LICENSE.txt','pyproject.toml'] or (p.endswith('.py') and any(t in p.lower() for t in ['model.py','predictor.py','calibration.py','scoring.py','decision.py']))][:14]
 for p in chosen:
  local=R/'sources/open-jev'/p
  if repo=='Zefan-Cai/Open-Jev' and local.exists():data=local.read_bytes()
  else:data=base64.b64decode(gh(f'repos/{repo}/contents/{p}?ref={revision}')['content'])
  dest=folder/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  records.append({'repository':repo,'revision':revision,'path':p,'saved':str(dest.relative_to(C)),'sha256':hashlib.sha256(data).hexdigest(),'license':meta.get('license',{}).get('spdx_id'),'executed':False,'weights_downloaded':False})
for name in ['fate-v1.html','specmd-v1.html']:
 p=R/'sources'/name;dest=out/name;shutil.copy2(p,dest)
 records.append({'name':name,'saved':str(dest.relative_to(C)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'origin':'Previously pinned primary arXiv v1; reread original HTML'})
(out/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
print('PRIMARY_SOURCES',len(records),flush=True)
