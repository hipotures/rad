"""Freeze provenance, models, payloads and counterbalanced orders before inference."""
import datetime, hashlib, json, os, pathlib, random, shutil, subprocess, sys, time
C=pathlib.Path(__file__).resolve().parents[1]
R=C.parents[1]
S=C/'source'
sys.path[:0]=[str(S),str(S/'tools')]
from serve.server import Service
from serve.frontend import ChatTemplate
import strata_tokenizer as ST

def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def hashjson(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def filehash(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(16*1024*1024),b''):h.update(b)
 return h.hexdigest()
def cmd(args,cwd=None):
 r=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=90)
 return {'command':args,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}

assert not (C/'protocol.json').exists(),'Frozen protocol already exists'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=S,text=True).strip()
assert not subprocess.check_output(['git','diff','v0.1.40','v0.1.40.1','--','src','include','CMakeLists.txt','cmake','third_party'],cwd=S)
inventory={}
for name,args in {
 'uname':['uname','-a'],'lscpu':['lscpu'],'memory':['free','-b'],'swap':['swapon','--show','--bytes'],
 'virtualization':['systemd-detect-virt'],'driver':['nvidia-smi','-q'],'topology':['nvidia-smi','topo','-m'],
 'p2p_read':['nvidia-smi','topo','-p2p','r'],'p2p_write':['nvidia-smi','topo','-p2p','w'],
 'cuda':['nvcc','--version'],'gcc':['g++','--version'],'cmake':['cmake','--version'],
 'python':[sys.executable,'--version'],'packages':['uv','pip','freeze','--python',sys.executable]
}.items():
 try:inventory[name]=cmd(args)
 except Exception as e:inventory[name]={'error':repr(e)}
inventory.update(cpu_affinity=sorted(os.sched_getaffinity(0)),proc_meminfo=pathlib.Path('/proc/meminfo').read_text(),proc_swaps=pathlib.Path('/proc/swaps').read_text(),proc_stat=pathlib.Path('/proc/stat').read_text(),cpu_governors={str(p):p.read_text().strip() for p in pathlib.Path('/sys/devices/system/cpu').glob('cpu*/cpufreq/scaling_governor')},psi={str(p):p.read_text() for p in pathlib.Path('/proc/pressure').glob('*')},start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
inventory['pcie_sysfs']={str(p):p.read_text().strip() for bus in ['0000:01:00.0','0000:02:00.0'] for name in ['current_link_speed','current_link_width','max_link_speed','max_link_width'] if (p:=pathlib.Path('/sys/bus/pci/devices')/bus/name).exists()}
save(C/'provenance/environment-inventory.json',inventory)
save(C/'provenance/source.json',{'tag':'v0.1.40.1','sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=S,text=True).strip(),'v0.1.40_sha':subprocess.check_output(['git','rev-parse','v0.1.40'],cwd=S,text=True).strip(),'engine_diff_empty':True,'llama_ggml_pin':'3cf03257f219afbe7334045ff7c6a06ac68c627d','dependency_tarball_sha256':filehash(C/'provenance/llama-pinned.tar.gz'),'diff':subprocess.check_output(['git','diff','--stat','v0.1.40','v0.1.40.1'],cwd=S,text=True),'spin_default_evidence':{'file':'include/strata/kernels/cpu/pool.hpp','line':214,'text':'static constexpr std::chrono::milliseconds kSpinBeforeSleep{20};'},'spin_override_evidence':{'file':'src/kernels/cpu/pool.cpp','line':437,'text':'STRATA_POOL_SPIN_US -> chrono::microseconds(max(0, atoi(e)))'},'PR949_status':'closed, unmerged at start; no pool-tasks in released native source'})

configs={}
for regime,old in [('IQ3_S',R/'variants/pool-p0-default/32k.json'),('Q4',R/'campaigns/q4-pool-spin-20261005T184831Z/configs/default20ms-32k.json')]:
 cfg=json.loads(old.read_text())
 cfg={k:cfg[k] for k in ['args','tokenizer','model_name','lib_dirs','gpu','gpus_asked','layer_split','model_revision','model_family','env','parallel']}
 cfg.update(cwd=str(S),exe=str(C/'build/strata'),python=sys.executable,source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=S,text=True).strip(),release='v0.1.40.1',regime=regime,server_entrypoint=str(C/'scripts/serve_capture.py'))
 cfg['args'][cfg['args'].index('--pcie-frac')+1]='0.28'
 configs[regime]=cfg

# Full content hashes of every file consumed by the engine/tokenizer; native
# shards are checked once before and once after, with immutable stat checks per arm.
for regime,cfg in configs.items():
 paths=set()
 for opt in ['--native','--ple-gguf','--expert-profile']:
  paths.add(pathlib.Path(cfg['args'][cfg['args'].index(opt)+1]))
 # Include all shards referenced by a split GGUF, not just the CLI's first shard.
 native=pathlib.Path(cfg['args'][cfg['args'].index('--native')+1])
 paths.update(native.parent.glob('*.gguf'))
 for opt in ['--pack','--mtp']:
  folder=pathlib.Path(cfg['args'][cfg['args'].index(opt)+1])
  paths.update(p for p in folder.rglob('*') if p.is_file())
 frozen=C/'provenance'/f'model-{regime}.json'
 if frozen.exists():
  manifest=json.loads(frozen.read_text())
  for p,j in manifest['files'].items():
   st=pathlib.Path(p).stat();assert (st.st_size,st.st_mtime_ns,st.st_ino)==(j['size'],j['mtime_ns'],j['inode'])
  cfg['model_manifest']=str(frozen);continue
 manifest={'regime':regime,'model_revision':cfg['model_revision'],'model_family':cfg['model_family'],'files':{}}
 for p in sorted(paths):
  st=p.stat();print('MODEL HASH',regime,p,st.st_size,flush=True)
  manifest['files'][str(p)]={'resolved':str(p.resolve()),'size':st.st_size,'mtime_ns':st.st_mtime_ns,'inode':st.st_ino,'sha256':filehash(p)}
 save(C/'provenance'/f'model-{regime}.json',manifest)
 cfg['model_manifest']=str(C/'provenance'/f'model-{regime}.json')

old=json.loads((R/'experiments/E026-pool-generalization/workloads/manifest.json').read_text())
save(C/'workloads/original-manifest.json',old)
shutil.copytree(R/'experiments/E026-pool-generalization/workloads/sources',C/'workloads/sources',dirs_exist_ok=True)
manifest={'payloads':{},'families':old['families'],'policy':'Exact saved E026 payloads, variants 1/2/3; fourth family repetition uses variant1 again. Only model name changes for Q4. No outcome-based prompt selection.','tokenization':{},'warmup':'Exact saved4096input/64output payload; one per fresh server.'}
for regime,cfg in configs.items():
 voc=pathlib.Path(cfg['tokenizer']);vocab=json.loads((voc/'vocab.json').read_text());tokens=[None]*len(vocab)
 for s,i in vocab.items():tokens[i]=s
 tok=ST.Tokenizer(tokens,(voc/'merges.txt').read_text().split('\n'),json.loads((voc/'token_type.json').read_text()))
 svc=Service(None,tok,ChatTemplate(voc/'chat_template.jinja'),cfg['model_name'])
 for name,info in old['payloads'].items():
  p=json.loads(pathlib.Path(info['path']).read_text());p['model']=cfg['model_name']
  ids=svc.encode_prompt(p['messages'],None,{'enable_thinking':False})
  digest=hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest()
  assert digest==info['input_ids_sha256'],(regime,name,'CURRENT TOKENIZATION DRIFT')
  target=C/'workloads'/regime/f'{name}.json';save(target,p)
  idpath=C/'workloads'/regime/f'{name}-ids.json';idpath.write_text(json.dumps(ids,separators=(',',':')))
  key=f'{regime}/{name}';manifest['payloads'][key]={'path':str(target),'payload_sha256':hashjson(p),'input_ids_sha256':digest,'token_ids_path':str(idpath),'actual_input_tokens':len(ids),'family':info.get('family','warmup'),'profile':info.get('profile'),'max_tokens':p['max_tokens'],'source':info['path']}
  print('PAYLOAD',key,len(ids),digest,flush=True)
save(C/'workloads/manifest.json',manifest)

seed=92110020261006
cells=['IQ3_S-32k','Q4-32k','IQ3_S-128k','Q4-128k']
orders={}
for ci,cell in enumerate(cells):
 rng=random.Random(seed+ci);families=['code','math','prose']*4
 # Balance each family 2AB/2BA and first10 5AB/5BA, preserving fallback4/3/3.
 while True:
  per={f:rng.sample(['AB','AB','BA','BA'],4) for f in ['code','math','prose']}
  sequence=[per[f][i//3] for i,f in enumerate(families)]
  if sequence[:10].count('AB')==5:break
 pairs=[{'pair':i+1,'order':sequence[i],'family':f,'payload_variant':(i//3)%3+1,'replacement':False} for i,f in enumerate(families)]
 replacements=[{'slot':i+1,'order':['AB','BA'][i],'replacement':True,'family':'SAME_AS_INVALID_PAIR','payload_variant':'SAME_AS_INVALID_PAIR'} for i in range(2)]
 orders[cell]={'cell':cell,'seed':seed+ci,'pairs':pairs,'replacement_slots':replacements}
 save(C/'orders'/f'{cell}.json',orders[cell])
save(C/'orders/all.json',orders)
save(C/'configs-base.json',configs)
protocol={'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seed':seed,'cells':cells,'target_valid_pairs':12,'minimum_valid_pairs':10,'maximum_valid_pairs':12,'replacement_slots_per_cell':2,'fallback_family_allocation':{'code':4,'math':3,'prose':3},'target_family_allocation':{'code':4,'math':4,'prose':4},'measurement_schedule':'Round-robin cells at each pair number. First10 in all cells before final2. Adjacent arms, one fresh server per arm.','A':'STRATA_POOL_SPIN_US genuinely absent','B':'STRATA_POOL_SPIN_US=100','environment_policy':'Freeze parent environment once; remove all STRATA_ inherited variables then add only common DECODE_TIMING=1, SPLIT_TIMING=1 and CUDA_VISIBLE_DEVICES=0,1. Capture paths derived from config argv, never environment. Full native environment hashed per key and diffed; sole allowed difference spin.','timeouts_s':{'startup':600,'request':900,'arm_total':1800,'owned_shutdown':25},'objective_invalidations':['binary/source/model identity mismatch','input IDs mismatch','wrong resolved settings','warmup not64 or measured output not4096/length','missing required output capture, routing/MTP/timing evidence','server crash/error/restart','GPU conflict','capacity drift within pair','unexpected environment/command/affinity drift','timeout/system resource abort'], 'not_invalidation':['poor performance','output trajectory difference','CPU steal','temperature variation'],'statistics':{'unit':'A/B pair','primary':'median paired ratios B/A','permutation':'two-sided exact sign-flip of log TG ratios, statistic abs(mean log ratio); descriptive and exchangeability conditional on workload/order assumptions','bootstrap':'20000 paired resamples median ratio, seed921100, percentile95%; small sample and repeated fixed corpus limitations','families':'descriptive only; four pairs each','drift':'compare AB and BA, chronological and family results; no outcome-based exclusions'},'hardware_scope':'One physical dual4090/7950X3D16vCPU KVM machine; no cross-machine inference.','CPU_policy':'System busy excluding idle/iowait reported with separately measured steal. Native processCPU normalized to16vCPU plus unnormalized cores%. Decode boundaries first actual token through native DONE. GPU prefill/decode means use only1Hz samples wholly inside each phase. Telemetry samples never independent statistical N.','trajectory_policy':'Keep all protocol-valid divergences; first-divergence indices; repeated variant1 allows baseline repeat check without extra reruns.','no_tuning':True}
save(C/'protocol.json',protocol)
save(C/'invalid-pair-ledger.json',[])
print('PROTOCOL FROZEN',flush=True)
