"""Archive inspected primary sources and local evidence without executing vendor code."""
import hashlib, json, pathlib, shutil, subprocess, urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
REFS={
 'threeway':pathlib.Path('/srv/ai/benchmarks/strata-qwen38/threeway-32k-128k-longdecode-20261004T212330Z'),
 'refresh':pathlib.Path('/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z'),
 'helper':pathlib.Path('/srv/ai/benchmarks/strata-qwen38/pr578-dual4090'),
 'hardware':pathlib.Path('/srv/ai/benchmarks/qwen-hardware-characterization/run-20261004T104353Z')}
record=json.loads((ROOT/'sources.json').read_text())
for name,path in REFS.items():
 dest=ROOT/'references'/name;dest.mkdir(exist_ok=True)
 files=['report.md','summary.json','summary.csv']
 if name=='hardware':files+=['cost-model.json','scheduler-envelope.json','inventory.json','final-code-manifest.json','followup-source-manifest.json']
 if name=='threeway':files+=['configs/CURRENT.json','git/CURRENT.json','git/CURRENT-preserved-control-configure-command.json','git/CURRENT-preserved-control-build-command.json','git/IQ3_S-SHA256SUMS','tokenization.json','analysis/token-comparison.json']
 if name=='refresh':files+=['git/ggml-source.json','git/dependency-review.json','expert-io-provenance.json']
 for f in files:
  src=path/f
  if not src.exists():continue
  out=dest/f;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out)
  record['local_references'].append({'source':str(src),'copy':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})

def gh(endpoint):
 return json.loads(subprocess.check_output(['gh','api',endpoint],timeout=60))
repo='Zefan-Cai/Open-Jev';rev='bd4118882f733574a3250a4b65fe4d884130c08b'
meta=gh('repos/'+repo)
tree=gh(f'repos/{repo}/git/trees/{rev}?recursive=1')
dest=ROOT/'sources/open-jev';dest.mkdir(exist_ok=True)
(dest/'metadata.json').write_text(json.dumps({k:meta.get(k) for k in ['full_name','default_branch','license','html_url']},indent=2))
(dest/'tree.json').write_text(json.dumps(tree,indent=2))
import base64
for x in tree['tree']:
 p=x['path']
 if x['type']!='blob' or x.get('size',0)>500000:continue
 if p in ['README.md','LICENSE','jev/model.py'] or (p.endswith('.py') and any(s in p.lower() for s in ['calibrat','train','score'])):
  obj=gh(f'repos/{repo}/contents/{p}?ref={rev}')
  data=base64.b64decode(obj['content']);out=dest/p;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
  record['downloads'].append({'url':f'https://github.com/{repo}/blob/{rev}/{p}','revision':rev,'license':'MIT','path':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'executed':False})
record['external_sources'].append({'name':'Open-Jev','url':'https://github.com/'+repo,'revision':rev,'license':'MIT','use':'Inspect scalar candidate head and calibration; no backbone/model download, no vendor code executed'})
for name,url,license in [
 ('open-jev-story','https://zefan-cai.github.io/open-jev/story/','Project text; no license inferred'),
 ('fate-v1','https://arxiv.org/html/2502.12224v1','See saved arXiv article license'),
 ('specmd-v1','https://arxiv.org/html/2602.03921v1','CC BY 4.0')]:
 with urllib.request.urlopen(url,timeout=60) as r:data=r.read()
 out=ROOT/'sources'/f'{name}.html';out.write_bytes(data)
 record['external_sources'].append({'name':name,'url':url,'license':license,'path':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest()})
(ROOT/'sources.json').write_text(json.dumps(record,indent=2)+'\n')
print('Archived local evidence and primary sources; vendor code not executed',flush=True)
