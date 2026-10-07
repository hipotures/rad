import bench as b,run as r,workloads as w,json,copy,subprocess,hashlib,statistics,re,sys
from pathlib import Path
R=b.R;repo=Path('/srv/ai/strata-pr578-helper-priority')
def config(label,instrument=False,suffix=False):
 st=json.loads((R/'auto-capacities.json').read_text());c=b.cfg(label,'optimized','helper',primary=st['primary_cli_uniform_budget'],helper=st['helper'],opt=True,instrument=instrument,suffix=suffix)
 c.update(cwd=str(repo),exe=str(repo/'build-default/strata'),Strata_HEAD=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),build_variant='PR578-local-helper-priority-fix',local_algorithm_fix='optimized helper ownership before primary PCIe quota',local_algorithm_fix_commit='ec511d1',binary_sha256=hashlib.sha256((repo/'build-default/strata').read_bytes()).hexdigest())
 b.save(R/'configs'/f'{label}.json',c);return c
if __name__=='__main__':
 phase=sys.argv[1];b.warm=copy.deepcopy(b.warm);b.warm['max_tokens']=64
 if phase=='correctness':
  rows=b.battery('CORRECT-H-PRIORITY',config('CORRECT-H-PRIORITY',instrument=True))
  old=json.loads((R/'correctness/CORRECT-H-OPT-all.json').read_text());comparison=[]
  for i,(a,z) in enumerate(zip(old,rows)):
   assert a['input_ids_sha256']==z['input_ids_sha256'];text=z['text'];malformed=not text.strip() or '\ufffd' in text
   if i>=8:
    try:json.loads(text)
    except:malformed=True
   n=min(len(a['generated_token_ids']),len(z['generated_token_ids']));div=next((j for j in range(n) if a['generated_token_ids'][j]!=z['generated_token_ids'][j]),None)
   comparison.append({'case':i+1,'first_divergence_vs_originalPR':div,'malformed':malformed,'finish':z['finish_reasons'],'same_input_ids':True})
  log=(R/'logs/CORRECT-H-PRIORITY-engine.log').read_text();assert 'logits non-finite' not in log
  b.save(R/'correctness/helper-priority-summary.json',comparison)
  if any(x['malformed'] for x in comparison):raise RuntimeError('Correctness battery failure; do not speed benchmark')
 elif phase=='speed':
  assert (R/'correctness/helper-priority-summary.json').exists()
  b.sweep('H-PRIORITY',config('H-PRIORITY'))
 elif phase=='lookup-fixed':
  # Correct prior secondaryauto capacity drift; originalhelper same8586/11796already saved.
  st=json.loads((R/'auto-capacities.json').read_text());c=b.cfg('H-OPT-FIXED-LOOKUP-ON','optimized','helper',primary=st['primary_cli_uniform_budget'],helper=st['helper'],opt=True,instrument=False,suffix=True)
  b.sweep('H-OPT-FIXED-LOOKUP-ON',c)
 elif phase in ('steady','steady-old'):
  if phase=='steady':
   label='H-PRIORITY-STEADY2048';c=config(label)
  else:
   label='H-OLD-STEADY2048';st=json.loads((R/'auto-capacities.json').read_text());c=b.cfg(label,'control','helper',primary=st['primary_cli_uniform_budget'],helper=st['helper'],instrument=False)
  c['args']=r.setarg(c['args'],'--prompt-cache',0);rows=[]
  with r.Session(label,c) as s:
   st=b.startup(s);b.request(s,b.warm,'steady-warmup',kind='warmup');p=json.loads((R/'references/steady2048-request.json').read_text())
   for i in [1,2,3]:
    b.status('priority steady2048'+str(i));a=b.request(s,p,'steady-run'+str(i),kind='steady');a.update(context_label='steady2048',initial_layout=st);b.save(R/'raw'/f'{label}-steady-run{i}.json',a);rows.append(a)
  b.save(R/'raw'/f'{label}-done.json',{'label':label,'layout':st,'runs':rows})
 elif phase=='matrix':b.sweep('H-PRIORITY-FINAL',config('H-PRIORITY-FINAL'),contexts=('32K','64K','128K','256K'))
 else:raise ValueError(phase)
