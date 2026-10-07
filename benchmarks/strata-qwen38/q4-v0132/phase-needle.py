from final_identity import require_phase, final_config_path, final_config_name, long_summary_path, phase_terminal_path, selection
"""Upstream needle method, with actual tokenizer sizing instead of character estimate."""
import run as r,workloads as w,json,copy,random,importlib.util,time,hashlib
require_phase('final-matrix')
path=r.c.REPO/'tools/needle_bench.py';spec=importlib.util.spec_from_file_location('needle_upstream',path);u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
label='NEEDLE-FINAL-v0132';cfg=copy.deepcopy(json.loads((final_config_path()).read_text()));cfg['log']=str(r.ROOT/'logs'/f'{label}-engine.log');r.c.save(r.ROOT/'configs'/f'{label}.json',cfg)
assert not list((r.ROOT/'raw').glob(label+'-*-request.json')),'Partialneedle attempt must be preserved/reviewed'
s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']={'phase':'upstream needle','candidate':label};s['next_exact_action']='Nine tokenizer-sized upstream needle requests at32/128/256K depths10/50/90; then review raw recall without quality judge.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2))
rnd=random.Random(7);rows=[]
with r.Session(label,cfg) as session:
 session.request(8000,64,'smoke','smoke')
 for target in [31400,127000,259500]:
  text=u.haystack(target*12)
  for depth in [10,50,90]:
   word=f'{rnd.choice(u.WORDS)}-{rnd.choice(u.WORDS)}-{rnd.randint(100,999)}'
   def make(n):
    body=text[:n];cut=int(len(body)*depth/100);cut=body.rfind('\n',0,cut)+1 or cut
    prompt=body[:cut]+f'\nThe secret code word for this text is: {word}. Remember it.\n'+body[cut:]+'\n\nWhat is the secret code word mentioned in the text above? Reply with the code word only.'
    return [{'role':'user','content':prompt}]
   lo,hi=0,len(text);best=None
   while lo<=hi:
    mid=(lo+hi)//2;msg=make(mid);n=session.run.count(msg)
    if n<=target:best=(msg,n);lo=mid+1
    else:hi=mid-1
   assert best and target-8<=best[1]<=target
   tag=f'{target}-depth{depth}';rec=w.request(session,best[0],40,tag,{'temperature':0,'chat_template_kwargs':{'enable_thinking':False}},reuse=True,kind='needle')
   assert rec['status']=='OK' and rec['actual_prompt_tokens']==rec['actual_prompt_tokens_tokenizer'] and abs(rec['actual_prompt_tokens']-target)<=8
   rows.append({'target':target,'depth':depth,'word':word,'found':word in rec['text'],'actual_prompt_tokens':rec['actual_prompt_tokens'],'answer':rec['text'],'wall_s':rec['total_wall_s'],'request':str(r.ROOT/'raw'/f'{label}-{tag}-request.json'),'cache_reused_tokens':rec['cache_reused_tokens']})
   r.c.save(r.ROOT/'quality/needle-progress.json',rows)
r.c.save(r.ROOT/'raw/needle-summary.json',{'status':'COMPLETE','results':rows,'source':str(path),'source_SHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'methodology':'Upstream haystack, words, seed7, depths10/50/90, question, greedy and max40 retained. External adaptation verifies actual prompt count instead of estimated characters. Common streaming API for telemetry. Recall membership is a mechanical upstream check, no LLM judge. Reuse reported separately, not throughput matrix.'})
r.c.save(r.ROOT/'raw/phase-needle-terminal.json',{'status':'COMPLETE','ended':time.time(),'requests':len(rows)})
s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']=None;s['completed'].append('Upstream needle actual32/128/256K depths10/50/90 completed');s['pending']=[x for x in s['pending'] if not x.startswith('upstreamneedle')];s['next_exact_action']='Finish IQ3 controls if pending, then diagnostics/comparison/plots/report/completion audit.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2))
spec=importlib.util.spec_from_file_location('status_render',r.ROOT/'status-render.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.render()
