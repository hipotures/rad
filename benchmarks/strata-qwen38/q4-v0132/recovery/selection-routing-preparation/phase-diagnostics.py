"""Official opt-in prefill phase timings, separated from benchmark rankings."""
import run as r,json,copy,time,importlib.util,re
assert json.loads((r.ROOT/'raw/phase-iq3-terminal.json').read_text())['status']=='COMPLETE'
label='DIAGNOSTIC-FINAL-v0132';cfg=copy.deepcopy(json.loads((r.ROOT/'configs/FINAL-v0132-Q4.json').read_text()));cfg['env']=dict(cfg.get('env') or {},STRATA_PREFILL_TIMING='1');cfg['log']=str(r.ROOT/'logs'/f'{label}-engine.log');r.c.save(r.ROOT/'configs'/f'{label}.json',cfg)
assert not list((r.ROOT/'raw').glob(label+'-*-request.json')),'Partialdiagnostic attempt requires review'
s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']={'phase':'separate upstream timing diagnostics','candidate':label};s['next_exact_action']='One warmup per context and two diagnostic requests, then final offline plots/report/audit. Diagnostics excluded from performance selection.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2));rows=[]
with r.Session(label,cfg) as session:
 smoke=session.request(8000,64,'smoke','smoke');assert smoke['text'].strip()
 for target in [127000,259500]:
  session.request(target,256,f'{target}-warmup','warmup')  # same warm-request policy as final matrix; never selection eligible
  row=session.request(target,256,str(target));assert row['status']=='OK' and row['cache_reused_tokens']==0
  log=r.ROOT/'raw'/f'{label}-{target}-engine.log';text=log.read_text(errors='replace');lines=[x for x in text.splitlines() if x.startswith('strata prefill timing:')]
  assert lines,'Official prefill timing lines missing'
  row.update(diagnostic_only=True,selection_eligible=False,prefill_timing_lines=lines,timing_scope='GPU timeline includes host/copy wait gaps; multi-stage overlapping timeline must not be added as serialwallcost. Stage0/1 normal counters may be cumulative since engine start.');r.c.save(r.ROOT/'raw'/f'{label}-{target}.json',row);rows.append(row)
r.c.save(r.ROOT/'raw/diagnostic-summary.json',{'status':'COMPLETE','runs':rows,'source_evidence':str(r.ROOT/'evidence/prefill-diagnostic-source.json'),'ranking_eligible':False,'warmups':{'count':2,'policy':'One unique-prompt warmup before each diagnostic context; excluded from selection and reported diagnostic rows. Same warm-request policy as final matrix.'}})
r.c.save(r.ROOT/'raw/phase-diagnostics-terminal.json',{'status':'COMPLETE','ended':time.time()})
s=json.loads((r.ROOT/'STATUS.json').read_text());s['running']=None;s['completed'].append('Separate normal upstream prefill timing diagnostics128/256K, excluded from rankings');s['next_exact_action']='Assemble summaries/comparisons/plots and final20answerreport, independentlyaudit all requirements and preservation.';(r.ROOT/'STATUS.json').write_text(json.dumps(s,indent=2))
spec=importlib.util.spec_from_file_location('status_render',r.ROOT/'status-render.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.render()
