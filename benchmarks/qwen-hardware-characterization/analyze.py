#!/usr/bin/env python3
"""Reproduce tables, conservative scheduler bounds and plots from retained native records."""
import collections,csv,datetime,hashlib,json,math,os,pathlib,re,statistics,sys
R=pathlib.Path(sys.argv[1]).resolve()
os.environ["MPLCONFIGDIR"]=str(R/"plot-cache")
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
GIB=1<<30;MIB=1<<20

def put(name,obj):(R/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def stats(x):
 x=[float(v) for v in x if v is not None and math.isfinite(float(v))]
 if not x:return None
 mean=statistics.mean(x);sd=statistics.stdev(x) if len(x)>1 else 0
 return {'n':len(x),'mean':mean,'median':statistics.median(x),'stddev':sd,'cv_percent':100*sd/abs(mean) if mean else None,'min':min(x),'max':max(x)}
def number(x):return f'{x:.3f}' if isinstance(x,(int,float)) else 'UNAVAILABLE'
def argv(case,key,default=None):
 a=case.get('args',[])
 try:return a[a.index(key)+1]
 except (ValueError,IndexError):return default

OWNED_ROWS=None

def actual_fio_telemetry(record, primary_rows):
 global OWNED_ROWS
 if record['case'].get('tool')!='fio':return None
 if OWNED_ROWS is None:
  path=R/'samples/owned-worker-1hz.jsonl'
  OWNED_ROWS=[json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
 commands=record.get('commands',[])
 filename=next((x.split('=',1)[1] for cmd in commands for x in cmd if x.startswith('--filename=')),None)
 if not filename or not primary_rows:return None
 lo,hi=primary_rows[0]['monotonic'],primary_rows[-1]['monotonic']
 actual=[x for x in OWNED_ROWS if lo<=x['monotonic']<=hi and x.get('phase')!='postwrite_verification' and pathlib.Path(x['executable']).name=='fio' and any(f['path']==filename for f in x.get('files',[]))]
 if not actual:return None
 bypid=collections.defaultdict(list)
 for x in actual:bypid[x['pid']].append(x)
 cpu=[]
 for samples in bypid.values():
  for a,b in zip(samples,samples[1:]):
   dt=b['monotonic']-a['monotonic']
   if dt>0:cpu.append(100*(b['user_ticks']+b['system_ticks']-a['user_ticks']-a['system_ticks'])/os.sysconf('SC_CLK_TCK')/dt)
 return {'CPU_percent_one_core_100':stats(cpu),'rss_bytes_peak':max(x['rss_bytes'] for x in actual),'sample_count':len(actual),'scope':'actual native fio worker; excludes independent post-write CRC verifier; includes setup/warmup/measurement','native_PIDs':list(bypid)}

def fio_verification(record):
 if not record['case'].get('write') or record['case'].get('tool')!='fio':return None
 flat=[x for cmd in record.get('commands',[]) for x in cmd]
 filename=next((x.split('=',1)[1] for x in flat if x.startswith('--filename=')),None)
 job=next((x.split('=',1)[1] for x in flat if x.startswith('--name=')),None)
 if not filename or not job:return {'status':'MISSING_COMMAND_EVIDENCE'}
 d=pathlib.Path(filename).parent
 evidence={'scope':'readback outside timed write','rusage_path':str(d/(job+'.rusage.json')),'verification_path':str(d/(job+'.postverify.json'))}
 try:
  evidence['rusage']=json.loads(pathlib.Path(evidence['rusage_path']).read_text())
  v=json.loads(pathlib.Path(evidence['verification_path']).read_text())
  evidence['status']='PASS' if all(j['error']==0 and j['read']['io_bytes']==256*MIB for j in v['jobs']) else 'FAIL'
  evidence['full_readback_bytes']=sum(j['read']['io_bytes'] for j in v['jobs'])
 except (OSError,ValueError):evidence['status']='MISSING_READBACK_EVIDENCE'
 return evidence

def telemetry(record):
 p=pathlib.Path(record.get('telemetry',''))
 if not p.is_file():return {}
 rows=[json.loads(x) for x in p.read_text().splitlines()]
 if len(rows)<2:return {}
 cpu=[];steal=[];process_cpu=[]
 for x,y in zip(rows,rows[1:]):
  ticks=[b-a for a,b in zip(x['cpu_ticks'],y['cpu_ticks'])];total=sum(ticks[:8]);dt=y['monotonic']-x['monotonic']
  if total:cpu.append(100*(total-ticks[3]-ticks[4]-ticks[7])/total);steal.append(100*ticks[7]/total)
  before={z['pid']:z for z in x['processes']};active=[z for z in y['processes'] if z['pid'] in before]
  process_cpu.append(100*sum(z['user_ticks']+z['system_ticks']-before[z['pid']]['user_ticks']-before[z['pid']]['system_ticks'] for z in active)/os.sysconf('SC_CLK_TCK')/dt)
 out={'scope':'whole process observation including setup/warmup/measurement/teardown; no PSS polling','system_CPU_percent':stats(cpu),'CPU_steal_percent':stats(steal),'process_CPU_percent_one_core_100':stats(process_cpu),'rss_bytes_peak':max((sum(p['rss_bytes'] for p in x['processes']) for x in rows),default=0),'MemAvailable_min_bytes':min(x['memory']['MemAvailable'] for x in rows),'GPU':{}}
 actual=actual_fio_telemetry(record,rows)
 if actual:
  out['actual_fio_worker']=actual;out['process_CPU_percent_one_core_100']=actual['CPU_percent_one_core_100'];out['rss_bytes_peak']=actual['rss_bytes_peak']
 for d in [0,1]:
  g=[g for x in rows for g in x['gpu'] if g['index']==d]
  out['GPU'][str(d)]={key:stats([x.get(key) for x in g]) for key in ['utilization_gpu_percent','utilization_memory_percent','power_W','temperature_C','sm_clock_MHz','memory_clock_MHz','vram_used_MiB','pcie_generation','pcie_width']}
 pcie=R/'samples'/(pathlib.Path(record.get('raw_stdout','')).name.split('.stdout')[0]+'-pcie.txt')
 if pcie.exists():
  parsed=[]
  for line in pcie.read_text().splitlines():
   if line.startswith('#'):continue
   f=line.split()
   if len(f)==3 and f[0].isdigit():
    try:parsed.append({'GPU':int(f[0]),'RX_MB_s':float(f[1]),'TX_MB_s':float(f[2])})
    except ValueError:pass
  out['PCIe']={str(d):{k:stats([x[k] for x in parsed if x['GPU']==d]) for k in ['RX_MB_s','TX_MB_s']} for d in [0,1]}
  out['PCIe_scope']='nvidia-smi dmon, whole observation; units exactly as raw header, not physical SSD I/O'
 return out

allrows=[json.loads(x) for x in (R/'results.jsonl').read_text().splitlines()];exclusions=json.loads((R/'exclusions.json').read_text()) if (R/'exclusions.json').exists() else {'excluded':[]};excluded_paths={x.get('raw_stdout') for x in exclusions['excluded']}
rows=[];invalid=[]
for record in allrows:
 if record.get('raw_stdout') in excluded_paths:invalid.append({**record,'analysis_status':'EXCLUDED_BUILD_BACKGROUND'});continue
 if record['status']!='OK':invalid.append(record);continue
 if record.get('actual_measured_seconds',0)<10:invalid.append({**record,'analysis_status':'INVALID_SHORT_WINDOW'});continue
 rows.append(record)
# A resumed success replaces no prior success of a different executable. Dedup exact identities only.
unique={}
for x in rows:unique[(x['scenario_id'],x['repetition'],x.get('software_identity'))]=x
rows=list(unique.values());groups=collections.defaultdict(list)
for x in rows:groups[x['scenario_id']].append(x)
summary=[]
for id,items in groups.items():
 first=items[0];case=first['case'];metric='work_rate' if argv(case,'--mode') in ['gemm','combined','monitor','controller'] else 'bandwidth_GB_s'
 rates=[x.get(metric,x.get('useful_work_count',0)/x['actual_measured_seconds']) for x in items]
 durations=[x['actual_measured_seconds'] for x in items];total_bytes=sum(x.get('completed_logical_bytes',0) for x in items)
 tel=[telemetry(x) for x in items]
 diagnostics=[]
 for rec in items:
  stderr=pathlib.Path(rec.get('raw_stderr',''))
  if stderr.is_file():
   for label,data in re.findall(r'(PIPELINE_DIAGNOSTICS|STORE_DIAGNOSTICS|MONITOR_DIAGNOSTICS) (\{.*\})',stderr.read_text()):diagnostics.append({'repetition':rec['repetition'],'label':label,'data':json.loads(data)})
 entry={'scenario_id':id,'family':case.get('family'),'case':case,'rate_metric':metric,'rates':stats(rates),'bandwidth_GB_s':stats([x.get('bandwidth_GB_s') for x in items]),'aggregate_payload_GB_s':total_bytes/sum(durations)/1e9,'actual_durations_seconds':durations,'independent_repetitions':len(items),'software_identities':sorted(set(x.get('software_identity','') for x in items)),'latency_per_repeat':[{k:x.get(k) for k in ['latency_sample_count','latency_sample_unit','latency_p50_ms','latency_p95_ms','latency_p99_ms','fio_latency']} for x in items],'actual_warmup_seconds':0 if case.get('tool')=='idle' else case.get('warmup'),'observation_conditions':{'direction':argv(case,'--direction'),'device':argv(case,'--device'),'memory_kind':argv(case,'--kind'),'buffers':int(argv(case,'--buffers','1')),'threads':int(argv(case,'--threads','1')),'payload_bytes':int(argv(case,'--bytes','0')),'GPU_UUIDs':'inventory.json, gpus query','timing':'host completion, bounded batch; events only on one device','buffer_scope':'warm reusable buffers; not all operations exercise physical DRAM','stream_scope':'one stream per ring buffer, or explicit scenario workers'},'latency_note':'native bounded-batch reservoir quantiles and/or fio histograms; per-repeat p99 is not pooled','CPU_seconds':stats([x.get('cpu_seconds') for x in items]),'traffic_achieved_GB_s':stats([x.get('traffic_completed_bytes',0)/x['actual_measured_seconds']/1e9 for x in items]) if any(x.get('traffic_completed_bytes') for x in items) else None,'system_CPU_percent':stats([x.get('system_CPU_percent',{}).get('mean') for x in tel]),'process_CPU_percent_one_core_100':stats([x.get('process_CPU_percent_one_core_100',{}).get('mean') for x in tel]),'MemAvailable_min_bytes':min((x['MemAvailable_min_bytes'] for x in tel if 'MemAvailable_min_bytes' in x),default=None),'rss_bytes_peak':max((x.get('rss_bytes_peak',0) for x in tel),default=0),'gpu':{str(d):{key:stats([x.get('GPU',{}).get(str(d),{}).get(key,{}).get('mean') if x.get('GPU',{}).get(str(d),{}).get(key) else None for x in tel]) for key in ['utilization_gpu_percent','power_W','temperature_C','vram_used_MiB']} for d in [0,1]},'diagnostics':diagnostics,'fio_write_crc_readbacks':[fio_verification(x) for x in items if fio_verification(x) is not None],'per_repeat_system_observation':tel,'raw_records':[x.get('raw_stdout') for x in items],'complete_default_repetition_set':len(items)>=3}
 summary.append(entry)
byid={x['scenario_id']:x for x in summary}
interference=[]
pairs=collections.defaultdict(dict)
for x in rows:
 c=x['case']
 if c.get('pair'):pairs[c['pair']].setdefault(c['arm'],{})[x['repetition']]=x
for id,arms in pairs.items():
 if 'A' not in arms or 'B' not in arms:continue
 values=[]
 for rep in sorted(set(arms['A'])&set(arms['B'])):
  a,b=arms['A'][rep],arms['B'][rep];av=a.get('work_rate',a.get('completed_logical_bytes',0)/a['actual_measured_seconds']);bv=b.get('work_rate',b.get('completed_logical_bytes',0)/b['actual_measured_seconds']);loss=1-bv/av if av else None
  ap=a.get('latency_p99_ms');bp=b.get('latency_p99_ms');achieved=b.get('traffic_completed_bytes',0)/b['actual_measured_seconds']
  values.append({'repetition':rep,'A_rate':av,'B_rate':bv,'loss_fraction':loss,'latency_p99_increase_fraction':bp/ap-1 if ap and bp else None,'achieved_bytes_s':achieved,'burst_bytes':b['case'].get('burst_bytes',0),'raw_A':a.get('raw_stdout'),'raw_B':b.get('raw_stdout'),'same_binary':a.get('software_identity')==b.get('software_identity'),'combined_CPU_bytes_A':a.get('combined_cpu_useful_bytes'),'combined_CPU_bytes_B':b.get('combined_cpu_useful_bytes')})
 interference.append({'pair':id,'observations':values,'loss':stats([x['loss_fraction'] for x in values]),'achieved_bytes_s':stats([x['achieved_bytes_s'] for x in values]),'latency_p99_increase':stats([x['latency_p99_increase_fraction'] for x in values]),'independent_pairs':len(values),'baseline_rate_variability':stats([x['A_rate'] for x in values]),'loaded_rate_variability':stats([x['B_rate'] for x in values])})
thresholds={}
for limit in [.02,.05,.10]:
 candidates=[p for p in interference if len(p['observations'])>=3 and all(x['same_binary'] for x in p['observations']) and p['achieved_bytes_s']['mean']>0 and p['loss']['max']<=limit and p['baseline_rate_variability']['cv_percent']<=5 and p['loaded_rate_variability']['cv_percent']<=5]
 thresholds[str(limit)]={'supported_cases':[{'pair':p['pair'],'achieved_bytes_s_median':p['achieved_bytes_s']['median'],'worst_observed_loss_fraction':p['loss']['max'],'largest_measured_burst_bytes':max(x['burst_bytes'] for x in p['observations']),'independent_pairs':p['independent_pairs']} for p in candidates],'unsupported_reason':None if candidates else 'No tested stable point meets threshold in every paired observation (minimum3); no extrapolation.'}
cost_paths=collections.defaultdict(list)
for x in summary:
 c=x['case'];mode=argv(c,'--mode');size=argv(c,'--bytes')
 if mode not in ['transfer','bridge'] or size is None or '--both' in c.get('args',[]) or c.get('concurrent_device'):continue
 latency=[v['latency_p50_ms'] for v in x['latency_per_repeat'] if v.get('latency_p50_ms') is not None]
 key='|'.join([mode,argv(c,'--device','0'),argv(c,'--kind','pinned'),argv(c,'--direction','h2d'),argv(c,'--op','copy'),argv(c,'--buffers','1')])
 cost_paths[key].append({'scenario_id':x['scenario_id'],'payload_bytes':int(size),'latency_p50_ms_median':statistics.median(latency) if latency else None,'throughput_GB_s':x['bandwidth_GB_s'],'independent_repetitions':x['independent_repetitions'],'measured_seconds':x['actual_durations_seconds']})
cost={}
for path,points in cost_paths.items():
 points.sort(key=lambda x:x['payload_bytes']);fit=None
 usable=[p for p in points if p['latency_p50_ms_median'] is not None]
 if len(usable)>=3:
  sizes=np.array([p['payload_bytes'] for p in usable],dtype=float);lat=np.array([p['latency_p50_ms_median']/1000 for p in usable]);coef=np.polyfit(sizes,lat,1);pred=np.polyval(coef,sizes);residual=abs(pred-lat)/np.maximum(lat,1e-12)
  if coef[0]>0 and coef[1]>=0 and max(residual)<=.15:fit={'fixed_overhead_seconds':float(coef[1]),'effective_bytes_s':float(1/coef[0]),'max_relative_residual':float(max(residual)),'method':'unweighted least-squares to median repetition p50 bounded-batch service time; three support sizes, not a universal bandwidth'}
 cost[path]={'lookup':points,'fit':fit,'interpolation_payload_range':[points[0]['payload_bytes'],points[-1]['payload_bytes']],'extrapolation':'UNSUPPORTED','conditions':'visible VM path; exact mode/kind/device/buffers; warm reusable buffers; host synchronized completion'}
put('cost-model.json',{'paths':cost,'physical_media_service_time':'UNAVAILABLE: host/device caches not controlled or visible','cross_device_timing':'host monotonic, no event subtraction across devices'})
put('scheduler-envelope.json',{'thresholds':thresholds,'criteria_scope':'observed surrogate useful-work loss, worst of at least three pairs; baseline and loaded repetition CV must each be <=5%; not a production guarantee or LLM token loss','paired_observations':interference,'unstable_pairs_excluded_from_supported_budgets':[{'pair':p['pair'],'baseline_CV_percent':p['baseline_rate_variability']['cv_percent'],'loaded_CV_percent':p['loaded_rate_variability']['cv_percent'],'reason':'CV>5%; retain observed loss/rates but do not infer a safe budget from unstable baselines'} for p in interference if p['baseline_rate_variability']['cv_percent']>5 or p['loaded_rate_variability']['cv_percent']>5],'burst_tail_uncertainty':'Only a few 30-second cadence events per minute; correlated native latency samples are not independent burst replications','inclusive_eviction':'see immutable-store-inclusive: immutable host backing preserved, clean GPU copy needs no D2H; simulated exchange is a separate case','activation_handoff':'see bridge-roundtrip-activation and size-specific host bridge lookup in cost-model.json','limitations':['No extrapolation from isolated peak to safe background budget','No model routing trace or predictor evaluated','No physical SSD attribution through VM and host caches','CPU quota is a per-scope scheduler limit, not a DRAM bandwidth cap']})
put('summary.json',{'run':str(R),'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scenarios':summary,'interference':interference,'nonperformance_or_excluded':invalid,'all_raw_records':len(allrows),'valid_performance_repetitions':len(rows),'statistics':'arithmetic repetition means/medians/sample sd/CV; aggregate payload is completed bytes divided by summed measured time; no pooled p99 claims'})
columns=['scenario_id','family','rate_metric','repetitions','mean','median','stddev','cv_percent','min','max','aggregate_payload_GB_s','durations_seconds','MemAvailable_min_GiB','rss_peak_GiB']
with open(R/'summary.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
 for x in summary:w.writerow({'scenario_id':x['scenario_id'],'family':x['family'],'rate_metric':x['rate_metric'],'repetitions':x['independent_repetitions'],**{k:x['rates'][k] for k in ['mean','median','stddev','cv_percent','min','max']},'aggregate_payload_GB_s':x['aggregate_payload_GB_s'],'durations_seconds':json.dumps(x['actual_durations_seconds']),'MemAvailable_min_GiB':x['MemAvailable_min_bytes']/GIB if x['MemAvailable_min_bytes'] else None,'rss_peak_GiB':x['rss_bytes_peak']/GIB})

plots=R/'plots';plots.mkdir(exist_ok=True)
fig,ax=plt.subplots(1,2,figsize=(12,4))
for d in [0,1]:
 for direction in ['h2d','d2h']:
  points=[x for x in summary if x['family']=='D' and argv(x['case'],'--mode')=='transfer' and argv(x['case'],'--device','0')==str(d) and argv(x['case'],'--direction','h2d')==direction and argv(x['case'],'--kind','pinned')=='pinned' and argv(x['case'],'--buffers','1')=='1' and '--both' not in x['case'].get('args',[])]
  points.sort(key=lambda x:int(argv(x['case'],'--bytes')))
  if points:
   xx=[int(argv(x['case'],'--bytes')) for x in points];ax[0].plot(xx,[x['bandwidth_GB_s']['median'] for x in points],'-o',label=f'GPU{d} {direction} pinned')
   yy=[statistics.median([p['latency_p50_ms'] for p in x['latency_per_repeat'] if p.get('latency_p50_ms') is not None]) for x in points];ax[1].plot(xx,yy,'-o',label=f'GPU{d} {direction} p50 batch')
for a in ax:a.set_xscale('log');a.set_xlabel('Payload bytes');a.grid(alpha=.3);a.legend(fontsize=7)
ax[0].set_ylabel('Completed logical GB/s');ax[1].set_ylabel('Completed-batch latency ms');ax[1].set_yscale('log');fig.tight_layout();fig.savefig(plots/'transfer-size-throughput-latency.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4))
for workload in ['gemm','dispatch','cpu']:
 pts=[p for p in interference if p['pair'].startswith(workload+'-') and p['achieved_bytes_s']['mean']>0];pts.sort(key=lambda p:p['achieved_bytes_s']['median'])
 if pts:ax.errorbar([p['achieved_bytes_s']['median']/GIB for p in pts],[100*p['loss']['mean'] for p in pts],yerr=[100*p['loss']['stddev'] for p in pts],fmt='-o',label=workload)
ax.axhline(0,color='k',lw=.5);ax.set_xlabel('Achieved H2D GiB/s');ax.set_ylabel('Useful-work loss % (paired mean ± SD)');ax.legend();ax.grid(alpha=.3);fig.tight_layout();fig.savefig(plots/'interference-envelope.png',dpi=160);plt.close(fig)
labels=['gpu0-h2d-pinned-67108864','gpu1-h2d-pinned-67108864','both-h2d','gpu0-d2h-pinned-67108864','gpu1-d2h-pinned-67108864','both-d2h','both-mixed','gpu0-bidirectional']
chosen=[byid[x] for x in labels if x in byid];fig,ax=plt.subplots(figsize=(11,4));ax.bar(range(len(chosen)),[x['bandwidth_GB_s']['median'] for x in chosen]);ax.set_xticks(range(len(chosen)),[x['scenario_id'] for x in chosen],rotation=35,ha='right');ax.set_ylabel('Completed total payload GB/s');ax.set_title('Isolated and simultaneous paths (aggregate for both/bidirectional)');fig.tight_layout();fig.savefig(plots/'isolated-versus-concurrent.png',dpi=160);plt.close(fig)
chosen=[x for x in summary if '-pipeline-' in x['scenario_id'] and 'stage-diagnostic' not in x['scenario_id']];fig,ax=plt.subplots(figsize=(12,4));ax.bar(range(len(chosen)),[x['bandwidth_GB_s']['median'] for x in chosen]);ax.set_xticks(range(len(chosen)),[x['scenario_id'] for x in chosen],rotation=45,ha='right');ax.set_ylabel('Delivered file payload GB/s');ax.set_title('Real file → RAM → GPU pipelines; warm/host-cache state unproven');fig.tight_layout();fig.savefig(plots/'storage-gpu-pipeline.png',dpi=160);plt.close(fig)
chosen=[x for x in summary if x['family']=='F' and x['bandwidth_GB_s']];fig,ax=plt.subplots(figsize=(13,5));ax.bar(range(len(chosen)),[x['bandwidth_GB_s']['median'] for x in chosen]);ax.set_xticks(range(len(chosen)),[x['scenario_id'] for x in chosen],rotation=70,ha='right',fontsize=7);ax.set_ylabel('Guest logical GB/s');fig.tight_layout();fig.savefig(plots/'storage-paths.png',dpi=160);plt.close(fig)
# Boundary-instrumented diagnostic is a separate binary cohort, not a headline A/B.
reps=[x for x in rows if x['scenario_id']=='burst-timeseries-diagnostic']
if reps:
 rec=reps[0];tr=[json.loads(x) for x in pathlib.Path(rec['telemetry']).read_text().splitlines()]
 text=pathlib.Path(rec['raw_stderr']).read_text()
 phases=[json.loads(x) for x in re.findall(r'PHASE_MONOTONIC (\{.*\})',text)]
 origin=next(x['time'] for x in phases if x['phase']=='measure');finish=next(x['time'] for x in phases if x['phase']=='drain')
 tr=[x for x in tr if origin-1<=x['monotonic']<=finish+1]
 bursts=[json.loads(x) for x in re.findall(r'BURST_MONOTONIC (\{.*\})',text)]
 fig,ax=plt.subplots(3,1,figsize=(11,8),sharex=True)
 for d in [0,1]:
  pts=[(x['monotonic']-origin,g['power_W']) for x in tr for g in x['gpu'] if g['index']==d and g['power_W'] is not None]
  ax[0].plot([p[0] for p in pts],[p[1] for p in pts],label=f'GPU{d} power')
 ax[0].set_ylabel('W');ax[0].legend()
 times=[];busy=[]
 for x,y in zip(tr,tr[1:]):
  delta=[b-a for a,b in zip(x['cpu_ticks'],y['cpu_ticks'])];total=sum(delta[:8]);times.append(y['monotonic']-origin);busy.append(100*(total-delta[3]-delta[4]-delta[7])/total if total else 0)
 ax[1].plot(times,busy);ax[1].set_ylabel('System CPU %')
 points=re.findall(r'phase=measure elapsed=([0-9.]+).*?work=([0-9]+)',text)
 if points:
  elapsed=[0]+[float(x[0]) for x in points];counts=[0]+[int(x[1]) for x in points]
  rates=[(counts[i]-counts[i-1])/(elapsed[i]-elapsed[i-1])/1e12 for i in range(1,len(elapsed))]
  ax[2].plot(elapsed[1:],rates,'-o',label='useful FP32 TFLOP/s over successive ~5s windows')
 ax[2].set_ylabel('TFLOP/s');ax[2].set_xlabel('Seconds after native measurement boundary');ax[2].legend()
 for i,event in enumerate(bursts):
  if event['event']=='start' and event.get('phase')==1:
   stop=next((b['time'] for b in bursts[i+1:] if b['event']=='end'),finish)
   for a in ax:a.axvspan(event['time']-origin,stop-origin,color='orange',alpha=.25)
 for a in ax:a.grid(alpha=.3)
 fig.suptitle('Actual 30-second H2D bursts (orange), aligned native monotonic clocks; diagnostic cohort')
 fig.tight_layout();fig.savefig(plots/'burst-compute-power-cpu.png',dpi=160);plt.close(fig)
 put('burst-aligned-evidence.json',{'raw_record':rec['raw_stdout'],'measurement_start_monotonic':origin,'measurement_end_monotonic':finish,'events':bursts,'native_phases':phases})

# Report generated as a transparent evidence map, including incomplete/unsupported items.
inv=json.loads((R/'inventory.json').read_text());ledger=json.loads((R/'write-ledger.json').read_text());progress=json.loads((R/'progress.json').read_text());follow=json.loads((R/'followup-progress.json').read_text()) if (R/'followup-progress.json').exists() else {}
lines=['# VM hardware and MoE residency data-movement study','','## Environment and limits','',f"Two RTX 4090 GPUs, CUDA 13.4, driver 615.71.09; guest CPU/RAM/affinity and topology are recorded in inventory.json. Guest-visible MemTotal: {inv['initial_snapshot']['memory']['MemTotal']/GIB:.2f} GiB; affinity allows {len(inv['affinity'])} CPUs. No physical host DRAM channel/CCD topology is inferred.",'','Two deliberately separate storage paths are tested: /srv/ai through virtiofs, and /home/user/DEV/test20261001_1 through ext4 on virtual /dev/sdb. Host SSD identity, host cache state, physical media bandwidth and write amplification are not observable. Buffered and guest-direct measurements must not be called physical SSD speeds. First pass is after preparation and fdatasync, not a cold-media guarantee.','',f"Core status: {progress['status']}; follow-up status: {follow.get('status','UNAVAILABLE')}. {len(rows)} valid sustained performance repetitions from {len(allrows)} raw records. Default headline windows are 60 seconds × 3 after 15 seconds warmup; supporting windows are 20 seconds × 3. Raw failures/probes/exclusions remain intact.",'','Direct CUDA P2P is unsupported in both directions, verified by capability probes. It is not represented as zero bandwidth. All peer bridge results are explicit pinned-host staging, with both logical delivered bytes and two transfer legs counted.','','## Path and size matrix','','| Scenario | Mechanism / rate unit | Mean | Median | Min / max | CV % | Repeats | Measured seconds |','|---|---|---:|---:|---:|---:|---:|---|']
for x in summary:
 if x['family'] in ['B','C','D','E','F','G']:
  s=x['rates'];lines.append(f"| {x['scenario_id']} | {x['rate_metric']} | {s['mean']:.3f} | {s['median']:.3f} | {s['min']:.3f} / {s['max']:.3f} | {number(s['cv_percent'])} | {s['n']} | {', '.join(f'{v:.2f}' for v in x['actual_durations_seconds'])} |")
lines+=['','Native latency p50/p95/p99 and sample counts are in summary.json by repetition, with raw bounded-batch sampling semantics. fio latency histograms and achieved queue depth are retained in native output. No averaged p99 is presented as a pooled p99. CPU read/copy/triad useful payload differs from estimated read+write traffic. cuBLAS uses FP32 pedantic math; small GEMMs are cache/dispatch-sensitive surrogates, not DRAM bandwidth or LLM tokens/s.','','## Concurrent paths and optimizations','','See isolated-versus-concurrent.png and per-worker native paths in raw records. Simultaneous two-worker GPU cases use separate actual measurement windows; do not interpret their aggregate as the sum of isolated peaks or a perfectly synchronized common interval. Grouped both-GPU copies have equal completed payload counts by construction. Reusable pinned buffers, explicit pageable-to-pinned staging, double/triple buffering, modest reader concurrency, scattered mapped-host access, and immutable segmented versus contiguous promotion are scoped reversible comparisons. Changes in mechanism and buffer count are explicit in each case.','','## Interference envelope','','| Pair | Baseline / loaded useful rate (mean) | Achieved H2D GiB/s | Useful-work loss mean % | Loss min / max % | p99 latency increase mean % | Independent pairs |','|---|---:|---:|---:|---:|---:|---:|']
for p in interference:
 obs=p['observations'];lines.append(f"| {p['pair']} | {statistics.mean(x['A_rate'] for x in obs):.3g} / {statistics.mean(x['B_rate'] for x in obs):.3g} | {p['achieved_bytes_s']['mean']/GIB:.3f} | {100*p['loss']['mean']:.2f} | {100*p['loss']['min']:.2f} / {100*p['loss']['max']:.2f} | {number(100*p['latency_p99_increase']['mean'] if p['latency_p99_increase'] else None)} | {len(obs)} |")
lines+=['','A/B order alternates by repetition. Negative losses are preserved as observed improvements. Rate pacing is completion-based and conservative; use achieved, not requested traffic rates. The 30-second burst case has only a few events per repetition, so three repetitions do not establish robust burst-tail guarantees. Native five-second cumulative useful-work logs accompany approximately 1 Hz RSS/CPU/GPU/PCIe telemetry. Telemetry aggregate scope includes setup and warmup; it is not claimed as pure measured-phase utilization. No PSS polling occurs.','','## Memory, storage safety and visibility','','| Check | Evidence / result |','|---|---|',f"| Logical write budget | {ledger['reserved_logical_bytes']/GIB:.3f} GiB conservatively reserved across preparation/warmup/tests and earlier preserved preflight, ceiling 512 GiB. Actual traced write totals are stored per ledger entry; unobserved probe writes remain conservatively charged. |",f"| Minimum observed MemAvailable | {min((x['MemAvailable_min_bytes'] for x in summary if x['MemAvailable_min_bytes']),default=0)/GIB:.3f} GiB; per-request RSS peaks in summary. |",'| Host allocation ceiling | Buffers remain below min(64 GiB,50% initial available); host available reserve max(16 GiB,15% total), GPU reserve 3 GiB each, free-space reserve max(32 GiB,15% capacity). |','| Corpus | 16 GiB seeded non-sparse corpus per path; exclusively created and fdatasync completed; allocated size and pre/post sampled signatures in manifests. |','| Physical counters | Guest logical I/O and process counters available; host media identity/cache and physical write amplification unavailable. |','| Pinning | CUDA pin/register operations tested; ulimit is recorded, and is not assumed to be an exact CUDA allocation ceiling. |','| Optional infrastructure | No driver/VM/mount/power changes; no raw device writes, global cache drops or model changes. A delegated user-owned cgroup CPU quota is tested in a transient scope (25000/100000, one-quarter of one core), without changing foreign/global limits. GDS not exercised; installed files alone do not establish a direct supported path. |','','## Scheduler implications','','Threshold cases in scheduler-envelope.json require all three paired repetitions to meet the stated 2%,5%,10% compute-loss limit. These are measured surrogate bounds, not guaranteed production budgets. cost-model.json separates each device/mechanism/buffer count, provides measured lookup ranges, and only accepts a fixed-overhead+bytes/bandwidth fit when residuals support it. Extrapolation is unsupported. Inclusive immutable host backing makes clean GPU eviction unnecessary to read back; the exchange control is separate. Remote per-layer execution must pay the measured explicit-host handoff/round-trip cost without P2P. These data cannot decide the best Qwen runtime or train a predictor.','','## Direct answers','','1. Per-workload bottlenecks must be read from CPU thread scaling, GPU FP32/local-memory rates, mapped access, and paired transfer loss rather than power/utilization alone. Physical host memory-controller and SSD attribution are unavailable.','2. Supported low-disruption achieved rates are the threshold cases in scheduler-envelope.json; no untested higher budget is approved.','3. Burst versus smooth throughput/p99 observations are paired in the envelope; limited burst-event counts prevent strong tail claims.','4. Both-GPU grouped and independent-worker cases measure the actual aggregate path; isolated peak sums are not used as simultaneous capacity.','5. Direct P2P is unsupported; bridge and round-trip size cases supply explicit staged latency and throughput.','6. Storage path suitability is characterized by random expert-sized tail/throughput and real pipelines, with host cache/physical device state hidden. These are not cold SSD guarantees.','7. Layer-split activation handoff versus remote expert movement can be compared by measured payload sizes/service ranges. Actual model compute/routing and speculative acceptance are not measured here.','8. After attachment/bare-metal changes, rerun inventory, loaded PCIe/P2P, guest-direct/buffered storage and real pipelines, then interference at the observed knee; expose physical counters/health where possible.','9. The next measurement that most reduces residency uncertainty is a controlled existing-model routing/miss trace replay with measured promotion budgets and paired token latency, using immutable weights and the same tokens—not another isolated peak copy test.','','## Exclusions, failures and reproducibility','','Earlier preflight run is preserved separately and not pooled across changed orchestrator hashes. One RAM repetition conservatively overlapping a follow-up compiler build is excluded by exact raw path and replaced after core execution. All raw requests and stderr remain. The separate follow-up binary implements actual immutable segmented backing, completion-gated publication, clean eviction and simulated noninclusive exchange, plus decaying rolling counts/ranked-plan drift monitoring. Its hash/cohort is explicit; comparisons are made within each binary.','']
for x in invalid:lines.append(f"- {x['scenario_id']} repetition {x['repetition']}: {x.get('analysis_status',x['status'])}; {x.get('reason','retained nonperformance record')}")
lines+=['','Plots: transfer-size-throughput-latency.png, interference-envelope.png, isolated-versus-concurrent.png, storage-gpu-pipeline.png, storage-paths.png, burst-compute-power-cpu.png.','','Artifacts: inventory.json/txt, campaign_config.json, plan.json, followup-plan.json, progress.json, followup-progress.json, raw/, samples/, results.jsonl, summary.csv/json, cost-model.json, scheduler-envelope.json, sources.json and code/. Reproduce with run_campaign.sh; exact per-case commands are retained for narrow diagnostics.','']
(R/'report.md').write_text('\n'.join(lines))
print(json.dumps({'valid_repetitions':len(rows),'raw_records':len(allrows),'scenarios':len(summary),'report':str(R/'report.md')}))
