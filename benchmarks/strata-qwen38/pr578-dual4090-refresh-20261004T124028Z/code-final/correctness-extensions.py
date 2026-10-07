import bench as b,run as r,json,copy
R=b.R;st=json.loads((R/'auto-capacities.json').read_text());out={}
for variant,opt in [('control',False),('optimized',True)]:
 label='CORRECT-EXT-'+variant.upper()
 c=b.cfg(label,variant,'helper',primary=st['primary_cli_uniform_budget'],helper=st['helper'],opt=opt,pcie=st['frozen_pcie_frac'])
 c['extra_env']={'STRATA_BENCH_CACHE_SNAPSHOT':'startup','STRATA_DBG_NAN':'1'};c['required_initial_layout']=st
 b.save(R/'configs'/f'{label}.json',c)
 rows=[]
 with r.Session(label,c) as session:
  layout=b.startup(session);b.save(R/'correctness'/f'{label}-layout.json',layout)
  for k in ['primary','helper','initial_resident_expert_count','initial_overlap','initial_primary_ids_SHA256','initial_helper_ids_SHA256']:assert layout[k]==st[k]
  for i in [5,6]:
   payload=json.loads((R/'raw'/f'CORRECT-H-OLD-case{i}-request.json').read_text());payload['max_tokens']=512
   a=b.request(session,payload,f'case{i}',kind='correctness',must256=False);assert a['valid'] and not a['non_finite_head_diagnostic']
   a['original_case']=i;b.save(R/'correctness'/f'{label}-case{i}.json',a);rows.append(a)
 out[variant]=rows
assert all(a['input_ids_sha256']==b['input_ids_sha256'] for a,b in zip(out['control'],out['optimized']))
(R/'correctness/extensions-summary.json').write_text(json.dumps({'budget':512,'same_inputs':True,'runs':out},indent=2)+'\n')
