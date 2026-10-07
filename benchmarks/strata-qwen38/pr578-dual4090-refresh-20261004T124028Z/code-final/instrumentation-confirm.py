import bench as b,run as r,json,statistics,shutil
R=b.R;st=json.loads((R/'auto-capacities.json').read_text());sets={a:[] for a in ['OFF','ON']}
for rep,arm in [(2,'ON'),(2,'OFF'),(3,'OFF'),(3,'ON')]:
 label=f'H-OPT-OVERHEAD-DIAG-{arm}-FRESH{rep}'
 c=b.cfg(label,'optimized','helper',primary=st['primary_cli_uniform_budget'],helper=st['helper'],opt=True,pcie=st['frozen_pcie_frac'])
 c['extra_env']={'STRATA_BENCH_CACHE_SNAPSHOT':'startup'} if arm=='ON' else {}
 if arm=='ON':c['required_initial_layout']=st
 b.save(R/'configs'/f'{label}.json',c);b.sweep(label,c)
for arm in ['OFF','ON']:
 for rep in [1,2,3]:
  label=f'H-OPT-STARTUP-DIAG-{arm}' if rep==1 else f'H-OPT-OVERHEAD-DIAG-{arm}-FRESH{rep}'
  rows=json.loads((R/'raw'/f'{label}-done.json').read_text())['runs'];assert len(rows)==3 and all(a['valid'] for a in rows)
  sets[arm].append({'server_replicate':rep,'label':label,'median_TG':statistics.median(a['tg_tps'] for a in rows),'rows':rows})
med={a:statistics.median(z['median_TG'] for z in rs) for a,rs in sets.items()};paired=[]
for x,y in zip(sets['OFF'],sets['ON']):
 for a,b in zip(x['rows'],y['rows']):paired.append({'server_replicate':x['server_replicate'],'input_ids_identical':a['input_ids_sha256']==b['input_ids_sha256'],'output_text_identical':a['output_text_sha256']==b['output_text_sha256'],'TG_ratio_ON_OFF':b['tg_tps']/a['tg_tps']})
loss=1-med['ON']/med['OFF'];result={'TG_median':med,'fresh_server_medians':{a:[z['median_TG'] for z in rs] for a,rs in sets.items()},'estimated_loss_fraction':loss,'within_1pct':loss<=.01,'scope':'Three independent fresh-server replicas per arm with alternating order; each median uses all three saved31400-token replay payloads after equal64-output warmup','paired_per_payload':paired,'raw_done_paths':[str(R/'raw'/f"{z['label']}-done.json") for rs in sets.values() for z in rs],'first_pair_preserved':'instrumentation-overhead-first-pair-preserved.json'}
(R/'instrumentation-overhead.json').write_text(json.dumps(result,indent=2)+'\n')
assert loss<=.01,'Repeated observed debug slowdown >1%; do not use it in headline runs'
