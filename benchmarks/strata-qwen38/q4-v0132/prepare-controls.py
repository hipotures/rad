"""Isolated immutable-runtime controls; never writes originalcampaign orengine."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys,uuid
R=Path(__file__).resolve().parent;OLD=R.parent/'q4-max-sweep'
selection=json.loads((R/'raw/topology-selection.json').read_text());winner=selection['winner'];base=json.loads((R/'configs'/f'{winner}.json').read_text())
def hashfile(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(16<<20),b''):h.update(b)
 return h.hexdigest()
# Run this preparation only BETWEEN engine candidates;1.4GBhashscan outside timedrequests.
import psutil
for p in psutil.process_iter(['cmdline']):
 assert not any(x.endswith('/engine/strata') or x.endswith('/build-default/strata') for x in (p.info['cmdline'] or []))
oldpack=Path('/srv/ai/models/strata/packs/ud-q4_k_xl');newpack=Path('/srv/ai/models/strata/packs/ud-q4_k_xl-v0132')
assert hashfile(oldpack/'dense.bin')==hashfile(newpack/'dense.bin')
mtp_hashes={}
for f in Path('/srv/ai/models/strata/mtp/rt').glob('*'):
 if f.is_file():
  other=Path('/srv/ai/models/strata-v0132/mtp/rt')/f.name
  assert other.exists() and hashfile(f)==hashfile(other),f
  mtp_hashes[f.name]=hashfile(f)
oldintegrity=json.loads((OLD/'V0131-CHECKPOINT.json').read_text());assert hashfile('/srv/ai/strata/engine/strata')==oldintegrity['version']['engine_sha256']
for version,repo,head,variant in [('v0131','/srv/ai/strata','9259cad4cfa3543cd3b8decab5962672b968c649','v0131-preserved'),('v0132','/srv/ai/strata-v0.1.32','c499bd102e7a4135c0de389dcfe38c399759ccc8','default')]:
 out=R/'controls'/version;out.mkdir(parents=True,exist_ok=True)
 for sub in ['configs','logs','raw','telemetry']: (out/sub).mkdir(exist_ok=True)
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==head
 for name in ['campaign.py','telemetry.py','workloads.py','strata-bench.upstream.py']:
  text=(R/name).read_text()
  if name=='campaign.py':text=text.replace("REPO = Path('/srv/ai/strata-v0.1.32')",f"REPO = Path('{repo}')")
  (out/name).write_text(text)
 cfg=json.loads(json.dumps(base));cfg.update(exe=repo+('/engine/strata' if version=='v0131' else '/build-default/strata'),cwd=repo,port=18086,log=str(out/'logs/control-engine.log'))
 a=cfg['args'];a[a.index('--max-context')+1]='262144'
 for key,val in {'--pack':str(oldpack if version=='v0131' else newpack),'--mtp':'/srv/ai/models/strata/mtp/rt' if version=='v0131' else '/srv/ai/models/strata-v0132/mtp/rt','--expert-profile':repo+'/data/expert-profile.bin'}.items():a[a.index(key)+1]=val
 cfg['tokenizer']=str((oldpack if version=='v0131' else newpack)/'tokenizer')
 (out/'configs/resident-baseline-seed.json').write_text(json.dumps(cfg,indent=2))
 text=(R/'run.py').read_text().replace("'c499bd102e7a4135c0de389dcfe38c399759ccc8'",repr(head)).replace("Strata_version='0.1.32'",f"Strata_version='{'0.1.31' if version=='v0131' else '0.1.32'}'").replace("build_variant='default'",f"build_variant='{variant}'").replace('18085','18086')
 (out/'run.py').write_text(text)
 (out/'control.py').write_text('''import run as r,json,time,uuid,copy
from pathlib import Path
label='PP-CONTROL';cfg=copy.deepcopy(r.SEED);r.c.save(r.ROOT/'configs'/f'{label}.json',cfg)
plan=json.loads((r.ROOT.parent.parent/'controls-request-plan.json').read_text());rows=[]
with r.Session(label,cfg) as s:
 s.request(8000,64,'smoke','smoke')
 for cell in plan['cells']:
  target=cell['target']
  messages,count,_=s.run.exact_prompt(target,cell['warmup_nonce']);import workloads as w
  warm=w.request(s,messages,256,f'{target}-warmup',kind='warmup');assert warm['generated_tokens']==256
  for i,nonce in enumerate(cell['nonces'],1):
   messages,count,_=s.run.exact_prompt(target,nonce);rec=w.request(s,messages,256,f'{target}-run{i}',kind='controlled_version_AB')
   assert rec['actual_prompt_tokens']==rec['actual_prompt_tokens_tokenizer'] and abs(rec['actual_prompt_tokens']-target)<=8 and rec['generated_tokens']==256 and rec['cache_reused_tokens']==0
   rows.append(rec)
r.c.save(r.ROOT/'raw/control-done.json',{'status':'COMPLETE','runs':rows,'plan':str(r.ROOT.parent.parent/'controls-request-plan.json'),'note':'Samepairedmessages andsettings, frozenoldcodecorpus. Ownversion-specific directory; preservedoldengine only, no originalcampaignrestart.'})
print('ControlledPP matrix COMPLETE',flush=True)
''')
plan={'max_context':262144,'output':256,'zero_reuse':True,'cells':[{'target':target,'n':n,'warmup_nonce':uuid.uuid4().hex,'nonces':[uuid.uuid4().hex for _ in range(n)]} for target,n in [(8000,2),(16000,2),(31400,3),(63400,3),(127000,3),(259500,3)]],'source_topology':winner,'layer_split':base['layer_split'],'pairing':'SameAPI messages perpair acrossversions, allnoncesuniquewithin each runtime. Warmups separate; greedy. Restartsbetweenversions only.'}
(R/'controls-request-plan.json').write_text(json.dumps(plan,indent=2))
(R/'raw/controls-preparation.json').write_text(json.dumps({'status':'READY','winner':winner,'dense_pack_byteidentity':True,'MTP_runtime_files_SHA256':mtp_hashes,'old_binary_identity_matches_checkpoint':True,'separate_version_directories':True},indent=2))
print('Versioncontrols prepared. No engine started.',flush=True)
