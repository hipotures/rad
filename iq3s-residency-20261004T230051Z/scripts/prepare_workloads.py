"""Freeze service-rendered workloads trimmed deterministically at complete line boundaries."""
import bisect, copy, hashlib, json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
SRC=ROOT/'src/control'
sys.path[:0]=[str(SRC),str(SRC/'tools')]
import strata_tokenizer as ST
from serve.frontend import ChatTemplate
from serve.server import Service
OLD=pathlib.Path('/srv/ai/benchmarks/strata-qwen38/threeway-32k-128k-longdecode-20261004T212330Z')
VOC=pathlib.Path('/srv/ai/models/strata/packs/iq3_s/tokenizer')
vocab=json.loads((VOC/'vocab.json').read_text());tokens=[None]*len(vocab)
for s,i in vocab.items():tokens[i]=s
svc=Service.__new__(Service);svc.tok=ST.Tokenizer(tokens,(VOC/'merges.txt').read_text().split('\n'),json.loads((VOC/'token_type.json').read_text()));svc.template=ChatTemplate(VOC/'chat_template.jinja');svc.effort_end=False
def encode(p):return svc.encode_prompt(p['messages'],None,{'enable_thinking':False})
def sha(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
manifest={'runtime_reserve_tokens':8,'additional_safety_tokens':248,'output_tokens':4096,'trim_policy':'Preserve original system/nonce and final long-output task. Trim repository source to the largest complete line prefix within limit-output-256. No RoPE/admission changes.','profiles':{},'payloads':{}}
idsdir=ROOT/'workloads/token-ids';idsdir.mkdir(exist_ok=True)
def save(name,p,details):
 ids=encode(p);path=ROOT/'workloads'/f'{name}.json'
 if path.exists():raise RuntimeError('Refuse overwrite frozen payload: '+str(path))
 path.write_text(json.dumps(p,indent=2,ensure_ascii=False)+'\n')
 h=hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest()
 (idsdir/f'{h}.json').write_text(json.dumps(ids,separators=(',',':')))
 manifest['payloads'][name]={'path':str(path),'payload_sha256':sha(p),'messages_sha256':sha(p['messages']),'input_ids_sha256':h,'token_ids_path':str(idsdir/f'{h}.json'),'actual_input_tokens':len(ids),**details}
 print(name,len(ids),flush=True)
for profile,limit in [('32k',32768),('128k',131072)]:
 ceiling=limit-4096-256
 manifest['profiles'][profile]={'max_total_context':limit,'input_ceiling':ceiling,'required_service_slack':8,'fixed_output':4096}
 for n in range(1,4):
  source=OLD/'payloads'/f'{profile.upper()}-long-run{n}.json'
  # Historical filenames use upper-case K, lower-case is converted explicitly.
  source=OLD/'payloads'/f'{"32K" if profile=="32k" else "128K"}-long-run{n}.json'
  p=json.loads(source.read_text());original=p['messages'][-1]['content']
  body,task=original.rsplit('\n\nTask:',1)
  endings=[0]+[i+1 for i,c in enumerate(body) if c=='\n']
  lo,hi=0,len(endings)-1;best=None
  while lo<=hi:
   mid=(lo+hi)//2;q=copy.deepcopy(p);q['messages'][-1]['content']=body[:endings[mid]]+'\n\nTask:'+task
   count=len(encode(q))
   if count<=ceiling:best=(q,endings[mid],count);lo=mid+1
   else:hi=mid-1
  assert best and best[2]+4096+8<=limit
  p,chars,count=best
  save(f'{profile}-run{n}',p,{'profile':profile,'source_payload':str(source),'source_payload_file_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'retained_source_characters':chars,'removed_source_characters':len(body)-chars,'trim_boundary':'complete source line','total_requested_tokens':count+4096,'admission_verified_offline':True})
warm=json.loads((OLD/'payloads/warmup.json').read_text());save('warmup',warm,{'fixed_output':64,'source_payload':str(OLD/'payloads/warmup.json')})
# Independent episodes: distinct task/domain documents, not nonce variants of benchmark corpus.
episodes=[
 ('dev-code','Implement a Python dependency graph with topological sorting, cycle reporting, incremental edge updates and tests. Explain the full design and write the implementation and many edge cases.','development'),
 ('dev-math','Develop an elementary derivation of finite-state Markov hitting times, then solve six different examples step by step, verifying each with recurrence equations and Python simulation code.','development'),
 ('cal-prose','Write a detailed engineering handbook for incident response in a fictional water-treatment control service. Include communication, failure analysis, recovery and worked incident narratives.','calibration'),
 ('hold-code','Design a transactional inventory ledger in SQLite and Python. Specify schema, idempotency, concurrent updates, audit invariants, migration, rollback, and a complete tested reference implementation.','holdout'),
 ('hold-structured','Produce a structured test catalog as valid JSON with 80 cases for a datetime parser. Each case needs input, expected interpretation, boundary rationale and a test stub.','holdout'),
 ('hold-math','Give a detailed derivation and reference Python implementation for exact rational polynomial interpolation, including error cases, independent examples and property tests.','holdout')]
for name,task,split in episodes:
 p={'model':'qwen3.8-flash-next-iq3_s','messages':[{'role':'system','content':'You are a careful technical assistant. No tools are available. Complete the requested work directly.'},{'role':'user','content':task}], 'max_tokens':1024,'stream':True,'stream_options':{'include_usage':True},'temperature':0,'reasoning_effort':'none'}
 save(name,p,{'profile':'32k','split':split,'episode':name,'independent_document':True,'purpose':'bounded causal predictor trace; natural EOS allowed'})
(ROOT/'workloads/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
