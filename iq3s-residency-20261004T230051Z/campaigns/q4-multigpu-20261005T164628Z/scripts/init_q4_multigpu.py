"""Create a separate frozen Q4 campaign. Does not change production launchers."""
import copy, datetime, hashlib, json, pathlib, subprocess, sys
from lab import ROOT, load, save, hashjson
SRC=ROOT/'src/control';sys.path[:0]=[str(SRC),str(SRC/'tools')]
import strata_tokenizer as ST
from serve.frontend import ChatTemplate
from serve.server import Service, engine_args

stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
C=ROOT/'campaigns'/('q4-multigpu-'+stamp);C.mkdir()
for d in ['configs','raw','logs','telemetry','inputs/token-ids','analysis','git','scripts','launchers','exploratory']:(C/d).mkdir(parents=True,exist_ok=True)
expected='eca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d'
exe=(ROOT/'builds/control/strata').resolve();assert hashlib.sha256(exe.read_bytes()).hexdigest()==expected
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=SRC,text=True).strip();assert head=='6f32ec070f23ced9f50e704d854d775da52591ab'
old=load(ROOT/'variants/ud-q4-k-xl/128k.json');pack=pathlib.Path('/srv/ai/models/strata/packs/ud-q4_k_xl-v0132')
manifest=load(old['model_manifest']);shards=[]
for x in manifest:
 p=pathlib.Path('/srv/ai/models/strata/models/UD-Q4_K_XL')/x['file'];st=p.stat();assert st.st_size==x['bytes'] and x['sha256']==x['actual_sha256']
 shards.append({'path':str(p),'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'previous_verified_sha256':x['actual_sha256'],'verification':'previous SHA256 manifest plus current size/mtime; no redownload'})
small={}
for p in [pack/'dense.bin',pack/'index.txt',pack/'native_experts.txt',pack/'compat-bf16.json',pack/'conversions.json',*sorted((pack/'tokenizer').iterdir()),pathlib.Path('/srv/ai/strata/data/expert-profile.bin')]:
 if p.is_file():small[str(p)]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
mtp=pathlib.Path('/srv/ai/models/strata/mtp/rt')
for p in sorted(mtp.rglob('*')):
 if p.is_file():small[str(p)]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
native=[]
for line in (pack/'native_experts.txt').read_text().splitlines():
 if not line or line.startswith('#'):continue
 t=line.split();native.append({'layer':int(t[0]),'gate_up_ggml_type':int(t[1]),'down_ggml_type':int(t[2]),'expert_blob_bytes':int(t[4]),'experts':512})
save(C/'git/model.json',{'quant':'UD-Q4_K_XL','revision':'38bb39ee97821de2c9009abb7e93950eec396e66','family':'unsloth/Qwen3.8-Flash-Next-GGUF','shards':shards,'previous_manifest':old['model_manifest'],'pack':str(pack),'files':small,'native_layers':native,'arena_bytes':sum(x['expert_blob_bytes']*512 for x in native),'routed_experts':24576,'experts_bin':False})
commands={'version':[str(exe),'--version'],'help':[str(exe),'--help'],'git-status':['git','status','--porcelain'],'build':['cat',str(ROOT/'builds/control/CMakeCache.txt')],'compiler':['c++','--version'],'CUDA':['/usr/local/cuda/bin/nvcc','--version'],'GPU':['nvidia-smi','-q'],'topology':['nvidia-smi','topo','-m'],'CPU':['lscpu'],'kernel':['uname','-a'],'RAM':['cat','/proc/meminfo'],'processes':['ps','-eo','pid,ppid,pgid,etime,args']}
records={}
for name,cmd in commands.items():
 r=subprocess.run(cmd,cwd=SRC,capture_output=True,text=True);(C/'git'/f'{name}.txt').write_text(r.stdout+r.stderr);records[name]={'command':cmd,'exit_code':r.returncode,'path':str(C/'git'/f'{name}.txt')}
save(C/'git/environment.json',{'source_sha':head,'binary_sha256':expected,'binary_realpath':str(exe),'version':'0.1.39','version_note':'--version unsupported; startup/API version must be checked','source_status':subprocess.check_output(['git','status','--porcelain'],cwd=SRC,text=True),'records':records,'old_Q4':'INVALID_AS_CURRENT_CONTROL','source_modified':False,'rebuilt':False})
base=load(ROOT/'variants/p1-baseline/128k.json')
base.update(exe=str(exe),cwd=str(SRC),tokenizer=str(pack/'tokenizer'),model_name='qwen3.8-flash-next-ud-q4_k_xl',source_sha=head,Strata_HEAD=head,Strata_version='0.1.39',binary_sha256=expected,model_revision='38bb39ee97821de2c9009abb7e93950eec396e66',model_family='unsloth/Qwen3.8-Flash-Next-GGUF',build_variant='frozen-current-p1-Q4',port=18134,host='127.0.0.1',parallel=1)
base['env']={'CUDA_VISIBLE_DEVICES':'0,1','STRATA_POOL_SPIN_US':'100','STRATA_SPLIT_TIMING':'1','STRATA_DECODE_TIMING':'1'}
base['args']=['--pack',str(pack),'--native',shards[0]['path'],'--ple-gguf',shards[1]['path'],'--expert-profile','/srv/ai/strata/data/expert-profile.bin','--mtp',str(mtp),'--expert-cache','auto','--prefill','auto','--pool-workers','15','--pcie-frac','0.28','--spec','4','--spec-min-p','0.5','--kv','int8','--kv-resident','32768','--suffix-draft','0','--prompt-cache','0','--max-context','131072']
base['gpu']=[0,1];base['layer_split']='auto';base['model_manifest']=str(C/'git/model.json');base['server_entrypoint']=str(ROOT/'scripts/serve_capture.py')
base['inference_provenance']='CURRENT P1 common settings, Q4 model only; architecture selection separate exploratory phase'
save(C/'configs/base.json',base)
VOC=pack/'tokenizer';v=load(VOC/'vocab.json');tokens=[None]*len(v)
for s,i in v.items():tokens[i]=s
svc=Service.__new__(Service);svc.tok=ST.Tokenizer(tokens,(VOC/'merges.txt').read_text().split('\n'),load(VOC/'token_type.json'));svc.template=ChatTemplate(VOC/'chat_template.jinja');svc.effort_end=False
def encode(p):return svc.encode_prompt(p['messages'],None,{'enable_thinking':False})
manifest={'payloads':{},'profiles':{},'reserve':256,'engine_reserve':8,'output':4096,'policy':'Existing sustained repository-maintenance workload; input IDs frozen once with current Q4 service tokenizer. Preserve source prefix at complete line boundaries.'}
oldmanifest=load(ROOT/'workloads/manifest.json')
def store(name,p,source,extra=None):
 p['model']=base['model_name'];ids=encode(p);digest=hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest();ip=C/'inputs/token-ids'/f'{digest}.json';ip.write_text(json.dumps(ids,separators=(',',':')));path=C/'inputs'/f'{name}.json';save(path,p)
 manifest['payloads'][name]={'path':str(path),'payload_sha256':hashjson(p),'messages_sha256':hashjson(p['messages']),'input_ids_sha256':digest,'token_ids_path':str(ip),'actual_input_tokens':len(ids),'source_payload':str(source),**(extra or {})}
 print('INPUT',name,len(ids),digest,flush=True)
for profile,limit in [('32k',32768),('128k',131072),('256k',262144)]:
 manifest['profiles'][profile]={'max_total_context':limit,'input_ceiling':limit-4096-256,'output':4096}
 for n in range(1,4):
  if profile!='256k':source=pathlib.Path(oldmanifest['payloads'][f'{profile}-run{n}']['path']);p=load(source)
  else:
   source=pathlib.Path(f'/srv/ai/benchmarks/strata-qwen38/results/raw/IQ3_S-256K-{n}-request.json');p=load(source)
   task=load(ROOT/'workloads/128k-run1.json')['messages'][-1]['content'].rsplit('\n\nTask:',1)[1]
   body=p['messages'][-1]['content'];body=body.rsplit('\n\nTask:',1)[0] if '\n\nTask:' in body else body
   p.update(max_tokens=4096,temperature=0,stream=True,stream_options={'include_usage':True},reasoning_effort='none')
   p['model']=base['model_name'];ends=[0]+[i+1 for i,c in enumerate(body) if c=='\n'];lo,hi=0,len(ends)-1;best=0
   while lo<=hi:
    m=(lo+hi)//2;p['messages'][-1]['content']=body[:ends[m]]+'\n\nTask:'+task
    if len(encode(p))<=limit-4096-256:best=m;lo=m+1
    else:hi=m-1
   p['messages'][-1]['content']=body[:ends[best]]+'\n\nTask:'+task
  p['model']=base['model_name'];count=len(encode(p));assert limit-4096-400<=count<=limit-4096-8,(profile,count)
  store(f'{profile}-run{n}',p,source,{'profile':profile,'max_total_context':limit,'total_requested':count+4096})
store('warmup',load(ROOT/'workloads/warmup.json'),ROOT/'workloads/warmup.json',{'output':64})
save(C/'inputs/manifest.json',manifest)
save(C/'protocol.json',{'strategies':['layer-split','original-helper','optimized-helper'],'contexts':[32768,131072,262144],'final_valid_per_cell':3,'final_requests':27,'warmup':'one identical saved 64-output request per fresh server/cell','restart':'one fresh server per cell, then 3 serial unique saved payloads; cache adaptation retained within cell','output':4096,'no_concurrency':True,'no_lookup_or_reuse':True,'screening':'Layer auto at32K/.28, then autoK-2,autoK+2/.28 and autoK/.37; one warmup + one exploratory4096 per point. Freeze K/pcie before final matrix. No Cartesian sweep.','helper_fairness':'Both helpers auto-size with same unmodified allocator/profile/model/KV; require identical initial capacities for original vs optimized per profile; preserve mismatch and fix explicit sizing if necessary.','invalids':'Preserve all failures/early stops. No favorable-result retries. Correct deterministic workload only if systematic failure before final freeze. Never more than3valid final per unchanged point.','ranking':'No winner until all27 valid final requests complete; PP/TG/wall separately.','timing':'Same existing lightweight frontend token-ID capture and1Hz sampler/dmon, noPSS, noenginepatch.'})
save(C/'STATUS.json',{'state':'PREPARING','completed':['GPU idle check','source/binary/model provenance','frozen common config and payloads'],'running':None,'pending':['bounded layer check','helper smoke/capacity fairness','final27matrix','analysis','launchers','cleanup'],'next_exact_action':'start current Q4 layer auto32K, identical warmup, one4096 exploratory'})
(C/'STATUS.md').write_text('# Q4 current multi-GPU campaign\n\nPREPARING. Frozen runtime0.1.39; no winner selected. See STATUS.json and protocol.json.\n')
(C/'report.md').write_text('# Q4 dual4090 controlled campaign\n\nIN PROGRESS. Historical0.1.32 is INVALID_AS_CURRENT_CONTROL. No winner before27 valid final requests.\n')
print('CAMPAIGN',C,flush=True)
