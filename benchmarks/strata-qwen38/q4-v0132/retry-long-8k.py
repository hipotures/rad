"""One separately recorded retry after natural EOS; no engine or EOS policy changes."""
import json,time
import run as r
import workloads as w
import extended as e
import trace_acceptance
R=r.ROOT
old=json.loads((R/'raw/long-decode-done.json').read_text())
assert len(old['runs'])==3 and all(x['length_completed'] for x in old['runs'][:2])
assert old['runs'][2]['generated_tokens']==6324 and not old['runs'][2]['length_completed']
label='LONG-RETRY8K-v0132';tag='128K-8192-sampled'
assert not (R/'raw'/f'{label}-{tag}-request.json').exists(),'Preserve/review partial retry; never overwrite'
cfg=e.clone(label,'FINAL-v0132-Q4');cfg['env']=dict(cfg.get('env') or {},STRATA_TRACE='1');r.c.save(R/'configs'/f'{label}.json',cfg)
with r.Session(label,cfg) as s:
    s.request(8000,64,'smoke','smoke')
    messages=w.exact(s.run,127000,w.LONG_TASK)
    rec=w.request(s,messages,8192,tag,e.SAMPLE,kind='long_decode_retry')
    rec.update(requested_output=8192,length_completed=rec['generated_tokens']==8192,retry_reason='Prior natural EOS at6324; same task/sampling with new nonce. No ignore-EOS or engine changes.')
    rec['acceptance_trace_file']=str(trace_acceptance.save(R,label+'-'+tag,rec))
    r.c.save(R/'raw'/f'{label}-{tag}.json',rec)
assert rec['length_completed'],'One retry also ended early: preserve actual output and reassess, do not blindly retry'
result={'status':'OK','runs':old['runs'][:2]+[rec],'incomplete_attempts':[old['runs'][2]],'note':'First8K request natural EOS6324 preserved with all raw artifacts. One same-task sampled retry separately labeled. Trace overhead included; no EOS suppression. Both attempts remain reportable.'}
r.c.save(R/'raw/long-decode-done.json',result)
r.c.save(R/'raw/phase-long-terminal.json',{'status':'COMPLETE','ended':time.time(),'result':str(R/'raw/long-decode-done.json'),'retry':str(R/'raw'/f'{label}-{tag}.json')})
state=json.loads((R/'STATUS.json').read_text());state['running']=None;state['completed'].append('Long actual64K4K/128K4K/128K8K completed; naturalEOS first8K retained separately');state['pending']=[x for x in state['pending'] if not x.startswith('longdecode')];state['next_exact_action']='Validate long retry, then uninterrupted agentic sessions.';r.c.save(R/'STATUS.json',state)
