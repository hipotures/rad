"""Control adaptive placement versus static; same reviewed default topology/prefill."""
import run as r,json,copy,time
assert json.loads((r.ROOT/'raw/phase-prompt-modes-terminal.json').read_text())['status']=='COMPLETE'
policy=json.loads((r.ROOT/'raw/prefill-policy-reviewed.json').read_text());source=json.loads(r.Path(policy['config']).read_text());results=[]
for mode in ['adaptive','static']:
 label=f'PLACEMENT-{mode}-v0132';cfg=copy.deepcopy(source);cfg['args']=r.setarg(cfg['args'],'--max-context',65536);cfg['environment_overrides']={}
 if mode=='static':cfg['args']=r.setarg(cfg['args'],'--adapt-every',0)
 cfg['log']=str(r.ROOT/'logs'/f'{label}-engine.log');r.c.save(r.ROOT/'configs'/f'{label}.json',cfg)
 s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']={'phase':'adaptive/static','candidate':label};s['next_exact_action']='Finish adaptive/static warmup+3 control. Then upstream calibrator and sequential CPU/PCIe/min-p.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2));(r.ROOT/'STATUS.md').write_text('# v0.1.32 IN_PROGRESS\n\nRunning: '+json.dumps(s['running'])+'\n\nNext: '+s['next_exact_action']+'\n\nFull state: STATUS.json.\n')
 res=r.candidate(label,cfg,3,True);assert res['status']=='OK' and len(res['runs'])==3
 for i in range(1,4):
  row=json.loads((r.ROOT/'raw'/f'{label}-run{i}.json').read_text());assert row['generated_tokens']==256 and row['cache_reused_tokens']==0 and abs(row['actual_prompt_tokens']-63400)<=8 and not row['abort']
 results.append(res)
r.c.save(r.ROOT/'raw/placement-comparison.json',{'status':'COMPLETE','results':results,'TG_adaptive_vs_static_delta_pct':100*(results[0]['median_tg']/results[1]['median_tg']-1)})
r.c.save(r.ROOT/'raw/phase-placement-terminal.json',{'status':'COMPLETE','ended':time.time()})
s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']=None;s['completed'].append('Default adaptive/static best split: warmup+3 each actual64K');s['pending']=[x for x in s['pending'] if not x.startswith('adaptive/static')];s['next_exact_action']='Run upstream calibrator, then separate workers/PCIe/min-p screens and final combined confirmation.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2));(r.ROOT/'STATUS.md').write_text('# v0.1.32 IN_PROGRESS\n\nAdaptive/static COMPLETE.\n\nNext: '+s['next_exact_action']+'\n\nFull state: STATUS.json.\n')

import importlib.util
_spec=importlib.util.spec_from_file_location('status_render',Path(__file__).resolve().parent/'status-render.py' if 'Path' in globals() else r.ROOT/'status-render.py');_module=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_module);_module.render()
