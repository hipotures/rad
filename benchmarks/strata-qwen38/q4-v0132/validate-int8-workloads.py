"""Long and 64K agent validation for the separately recorded INT8 candidate."""
import json,time,sys
import extended as e
import workloads as w
import run as r
import trace_acceptance
R=r.ROOT;source='FINAL-v0132-Q4-INT8-stability'
assert json.loads((R/'raw/phase-int8-final-matrix-terminal.json').read_text())['status']=='COMPLETE'
action=sys.argv[1]
if action=='long':
    label='LONG-INT8-v0132';assert not list((R/'raw').glob(label+'-*-request.json'))
    cfg=e.clone(label,source);cfg['env']=dict(cfg.get('env') or {},STRATA_TRACE='1');r.c.save(R/'configs'/f'{label}.json',cfg);rows=[]
    with r.Session(label,cfg) as session:
        session.request(8000,64,'smoke','smoke')
        for target,count,tag in [(63400,4096,'64K-4096-sampled'),(127000,4096,'128K-4096-sampled'),(127000,8192,'128K-8192-sampled')]:
            messages=w.exact(session.run,target,w.LONG_TASK)
            row=w.request(session,messages,count,tag,e.SAMPLE,kind='long_decode')
            row.update(requested_output=count,length_completed=row['generated_tokens']==count)
            row['acceptance_trace_file']=str(trace_acceptance.save(R,label+'-'+tag,row))
            r.c.save(R/'raw'/f'{label}-{tag}.json',row);rows.append(row)
    r.c.save(R/'raw/int8-long-decode-done.json',{'status':'OK','runs':rows,'scope':'Separate INT8 validation; upstream trace overhead included. Natural EOS respected and actual lengths independently required.'})
    assert all(x['length_completed'] for x in rows),'Preserve/review natural short output; no automatic retry'
    marker='phase-int8-long-terminal.json';result=R/'raw/int8-long-decode-done.json'
elif action=='agent64':
    label='AGENT-63400-v0132-int8-validation'
    e.agentic(63400,label_override=label,source_override=source)
    marker='phase-int8-agent64-terminal.json';result=R/'raw'/f'{label}-done.json'
else:raise ValueError(action)
r.c.save(R/'raw'/marker,{'status':'COMPLETE','ended':time.time(),'result':str(result),'candidate_config':str(R/'configs'/f'{source}.json')})
print('INT8 candidate '+action+' complete; independent review and production decision pending.',flush=True)
