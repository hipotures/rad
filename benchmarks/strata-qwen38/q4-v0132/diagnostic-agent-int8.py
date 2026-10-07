"""Single INT8 control after two incomplete K8V4 sessions; no engine changes."""
import json,time
import extended as e
import run as r
label='AGENT-127000-v0132-int8-control'
state=json.loads((r.ROOT/'STATUS.json').read_text());state['running']={'phase':'agent128 INT8 diagnostic','label':label};state['next_exact_action']='Finish uninterrupted diagnostic session; compare short-output behavior without claiming KV causality or production readiness.';r.c.save(r.ROOT/'STATUS.json',state)
e.agentic(127000,label_override=label,kv_override='int8')
result=json.loads((r.ROOT/'raw'/f'{label}-done.json').read_text())
assert len(result['runs'])==11
r.c.save(r.ROOT/'raw/phase-agent128-int8-control-terminal.json',{'status':'COMPLETE','ended':time.time(),'result':str(r.ROOT/'raw'/f'{label}-done.json'),'diagnostic_only':True,'scope':'KV-only config control with independent sampled outputs/nonce; not same-output controlledAB. FinalK8V4 agent128 remains failed.'})
print('INT8 diagnostic complete; manual comparison and remaining campaign required.',flush=True)
