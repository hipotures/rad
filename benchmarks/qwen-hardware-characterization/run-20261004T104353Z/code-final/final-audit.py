#!/usr/bin/env python3
"""Independent final file/statistics/safety audit; performs no timed workload."""
import collections,hashlib,json,math,os,pathlib,subprocess,sys,time
R=pathlib.Path(sys.argv[1]).resolve();ROOT=R.parent;GIB=1<<30
issues=[];limits=[]
def read(n):return json.loads((R/n).read_text())
def check(condition,message):
 if not condition:issues.append(message)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while chunk:=f.read(1<<20):h.update(chunk)
 return h.hexdigest()
config=read('campaign_config.json');core=read('progress.json');follow=read('followup-progress.json');summary=read('summary.json');ledger=read('write-ledger.json')
check(core['status']=='MEASUREMENTS_COMPLETE','Core measurement phase not complete')
check(follow['status']=='MEASUREMENTS_COMPLETE','Follow-up measurement phase not complete')
check(not core.get('running') and not follow.get('running'),'Measurement still running')
check(sha(ROOT/'hwbench')==config['code_hash'],'Frozen core binary hash changed')
check(sha(ROOT/'campaign.py')==config['python_hash'],'Frozen supervisor hash changed')
check(sha(ROOT/'src/hwbench.cu')==config['source_hash'],'Frozen CUDA source hash changed')
rows=[json.loads(x) for x in (R/'results.jsonl').read_text().splitlines()];by=collections.defaultdict(list)
for x in rows:by[x['scenario_id'],x['repetition']].append(x)
for n in ['plan.json','followup-plan.json']:
 for c in read(n)['scenarios']:
  for rep in range(1,c['repeats']+1):
   rep=c.get('replacement_repetition',rep)
   check((c['id'],rep) in by,'Missing planned raw repetition: '+c['id']+' '+str(rep))
   valid=[x for x in by[c['id'],rep] if x['status']=='OK']
   terminals=by[c['id'],rep]
   for x in terminals:
    if x['status']=='OK':
     check(x.get('actual_measured_seconds',0)>=10,'Under-10-second useful measurement '+c['id'])
     marker=x.get('verification')
     if c.get('tool')=='launch_events':
      events=x.get('events',[])
      check(marker=='CUDA_CAPABILITY_PROBE_SUCCESS' and bool(events) and all(e.get('status')=='OK' for e in events) and len(events)==x.get('useful_work_count'),'Missing successful sustained CUDA initialization events '+c['id'])
     else:
      check(marker in ['PASS','CORPUS_SIGNATURE_CHECKED_OUTSIDE_TIMING','NOT_APPLICABLE'],'Missing native correctness marker '+c['id'])
    elif x['status'] in ['UNSUPPORTED','PROBE','SKIPPED_TIME_BUDGET']:limits.append({'scenario':c['id'],'repeat':rep,'status':x['status'],'reason':x.get('reason')})
    else:issues.append('Unexpected non-success: '+c['id']+' '+x['status'])
    if c.get('cpu_quota') and x['status']=='OK':
     samples=[json.loads(line) for line in pathlib.Path(x['telemetry']).read_text().splitlines()]
     scopes=[line['owned_scope'] for line in samples if line.get('owned_scope')]
     check(bool(scopes),'Actual cgroup monitor worker telemetry missing')
     check(all(line['cpu_max']==c['cpu_quota'] for line in scopes),'Actual cgroup quota differs from plan')
    for k in ['raw_stdout','raw_stderr','telemetry']:
     if c.get('tool')=='idle' and k in ['raw_stdout','raw_stderr']:
      check(not x.get('commands') and x.get('verification')=='NOT_APPLICABLE','Idle record unexpectedly has a worker '+c['id'])
      continue  # No child exists; its recorded planned stdout/stderr paths are intentionally absent.
     if k in x:check(pathlib.Path(x[k]).is_file() or (k in ['raw_stdout','raw_stderr'] and pathlib.Path(x[k]+'.0').is_file()),'Missing '+k+' '+c['id'])
check(ledger['reserved_logical_bytes']<=config['max_write_gib']*GIB,'Logical write reservation exceeded ceiling')
for e in ledger['entries']:
 if e.get('actual_logical_bytes') is not None:check(e['actual_logical_bytes']<=e['reservation_bytes'],'Observed writes exceeded reservation: '+e['id'])
excluded=read('exclusions.json')['excluded'];excluded_paths={x['raw_stdout'] for x in excluded}
for s in summary['scenarios']:
 rec=[x for x in rows if x['scenario_id']==s['scenario_id'] and x['status']=='OK' and x.get('raw_stdout') not in excluded_paths]
 # Deduplicate exact successful software identities, matching the analyzer.
 d={(x['repetition'],x.get('software_identity')):x for x in rec};rec=list(d.values())
 check(len(rec)==s['independent_repetitions'],'Summary count mismatch: '+s['scenario_id'])
 metric=s['rate_metric'];values=[x.get(metric,x.get('useful_work_count',0)/x['actual_measured_seconds']) for x in rec]
 if values:check(math.isclose(sum(values)/len(values),s['rates']['mean'],rel_tol=1e-9,abs_tol=1e-12),'Summary rate mean mismatch: '+s['scenario_id'])
 check(not excluded_paths.intersection(s['raw_records']),'Excluded contaminated run included')
 for evidence in s.get('fio_write_crc_readbacks',[]):check(evidence['status']=='PASS','Independent fio CRC readback failed/missing')
 reserve=max(16*GIB,.15*read('inventory.json')['initial_snapshot']['memory']['MemTotal'])
 if s.get('MemAvailable_min_bytes') is not None:check(s['MemAvailable_min_bytes']>=reserve,'Observed RAM reserve crossed: '+s['scenario_id'])
 for observation in s.get('per_repeat_system_observation',[]):
  for d,g in observation.get('GPU',{}).items():
   if g.get('temperature_C'):check(g['temperature_C']['max']<80,'GPU thermal abort threshold reached: '+s['scenario_id']+' GPU'+d)
for path in ['report.md','summary.csv','summary.json','cost-model.json','scheduler-envelope.json','sources.json','inventory.json','inventory.txt','plan.json','campaign_config.json','normalized-results.jsonl','final-code-manifest.json']:
 check((R/path).is_file() and (R/path).stat().st_size>0,'Missing deliverable '+path)
for plot in ['transfer-size-throughput-latency.png','interference-envelope.png','isolated-versus-concurrent.png','storage-gpu-pipeline.png','storage-paths.png','burst-compute-power-cpu.png']:
 check((R/'plots'/plot).is_file(),'Missing required plot '+plot)
corpora=[]
for storage in config['scratch']:
 m=read('scratch-'+storage+'-manifest.json');p=pathlib.Path(m['path']);st=p.stat()
 check(st.st_size==m['size'] and st.st_ino==m['inode'],'Corpus size/inode changed '+storage)
 check(m.get('verification_after',{}).get('status')=='PASS','Missing post-core corpus signatures '+storage)
 v=os.statvfs(p.parent);avail=v.f_bavail*v.f_frsize;fsreserve=max(32*GIB,.15*v.f_blocks*v.f_frsize)
 check(avail>=fsreserve,'Filesystem available reserve crossed at audit '+storage)
 corpora.append({'storage':storage,'path':str(p),'allocated_bytes':st.st_blocks*512,'free_bytes_at_audit':avail,'required_free_reserve_bytes':fsreserve})
# Require no surviving campaign-owned GPU worker. Do not kill any process here.
p=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],capture_output=True,text=True)
check(p.returncode==0,'GPU process query failed')
check(not any(str(ROOT) in line for line in p.stdout.splitlines()),'Hardware campaign CUDA process still alive')
output={'status':'PASS' if not issues else 'FAIL','captured_UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'issues':issues,'limitations_and_nonperformance_records':limits,'all_raw_records':len(rows),'valid_performance_repetitions':summary['valid_performance_repetitions'],'summary_scenarios':len(summary['scenarios']),'logical_write_reservation_bytes':ledger['reserved_logical_bytes'],'corpus_and_free_space':corpora,'GPU_process_query':p.stdout,'unavailable':'Physical SSD counters/host cache state; physical DRAM topology; no PSS polling','final_elapsed_seconds':time.time()-config['created_wall']}
p=R/'final-audit.json';temp=p.with_suffix('.json.tmp');temp.write_text(json.dumps(output,indent=2)+'\n');os.replace(temp,p)
print(json.dumps(output,indent=2));raise SystemExit(0 if not issues else 1)
