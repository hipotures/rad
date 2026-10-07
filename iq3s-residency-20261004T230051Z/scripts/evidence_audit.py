"""Capture present environment, inspect hardware cost ranges and preserve baseline resource accounting."""
import datetime, hashlib, json, pathlib, re, subprocess, time
ROOT=pathlib.Path(__file__).resolve().parents[1]
def save(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
env={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':{},'model_files':[],'frozen_base':'6f32ec070f23ced9f50e704d854d775da52591ab'}
for name,cmd in {
 'gpus':['nvidia-smi','--query-gpu=index,name,uuid,memory.total,driver_version,pci.bus_id,pcie.link.gen.max,pcie.link.width.max','--format=csv'],
 'topology':['nvidia-smi','topo','-m'], 'cuda':['/usr/local/cuda/bin/nvcc','--version'],
 'compiler':['c++','--version'],'kernel':['uname','-a'],'cpu':['lscpu'],'memory':['cat','/proc/meminfo'],
 'memlock':['bash','-c','ulimit -l'], 'affinity':['taskset','-pc',str(__import__('os').getpid())]}.items():
 r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=30);env['commands'][name]={'command':cmd,'returncode':r.returncode,'output':r.stdout}
cfg=json.loads((ROOT/'variants/control/32k.json').read_text())
for key in ['--native','--ple-gguf','--expert-profile']:
 p=pathlib.Path(cfg['args'][cfg['args'].index(key)+1]);st=p.stat();entry={'path':str(p),'size':st.st_size,'mtime_ns':st.st_mtime_ns,'kind':key}
 if st.st_size<1024**2:entry['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 env['model_files'].append(entry)
pack=pathlib.Path('/srv/ai/models/strata/packs/iq3_s')
for p in sorted(pack.glob('*.json')):
 env['model_files'].append({'path':str(p),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
save(ROOT/'git/environment.json',env)
model=json.loads((ROOT/'references/hardware/cost-model.json').read_text());envelope=json.loads((ROOT/'references/hardware/scheduler-envelope.json').read_text())
selected={k:v for k,v in model['paths'].items() if 'pinned' in k or 'round' in k or 'bridge' in k}
save(ROOT/'analysis/hardware-selected-costs.json',{'selected_paths':selected,'scheduler_envelope_top_level_keys':list(envelope),'reference':'references/hardware/cost-model.json','interpretation':'Isolated transfer costs within measured payload ranges only; no inference critical-path attribution'})
budgets={};summary=[]
for profile in ['32k','128k']:
 cell=ROOT/'experiments/E002-controls/v1'/profile
 data=json.loads((cell/'results.json').read_text());valid=[r for r in data['runs'] if r['state']=='VALID'];log=(cell/'logs/engine.log').read_text()
 main=re.search(r'expert cache (\d+) slots, ([\d.]+) GiB of VRAM',log);second=re.search(r'CUDA1 runs layers .*? expert cache (\d+) slots \(([\d.]+) GiB\)',log)
 budgets[profile]={'primary_slots':int(main[1]),'helper_or_stage1_slots':int(second[1]),'cache_gib_rounded':[float(main[2]),float(second[2])],'exact_byte_classes':'pending diagnostic cache layout snapshot','auto_sizing_frozen_by_invariant':True,'max_total_context':32768 if profile=='32k' else 131072,'source':str(cell/'logs/engine.log'),'rule':'CPU-only predictor state cannot increase VRAM; candidates must match per-profile physical capacities and byte classes, or charge any loss explicitly'}
 import statistics
 row={'variant':'control','profile':profile,'valid':len(valid),'attempted':len(data['runs']),'runs':[str(cell/'raw'/f'run{n}.json') for n in range(1,len(data['runs'])+1)]}
 for metric in ['actual_input_tokens','PP','TG','TTFT_s','wall_s','mtp_acceptance_pct','mtp_accepted_per_window','hit_rate_pct','cpu_fallback_entries','offloaded_entries']:
  vs=[r[metric] for r in valid if r.get(metric) is not None];row[metric]={'min':min(vs),'median':statistics.median(vs),'max':max(vs)} if vs else None
 summary.append(row)
save(ROOT/'analysis/control-budgets.json',budgets);save(ROOT/'experiments/E002-controls/summary.json',summary)
report='# E002: fresh CURRENT controls\n\n| Profile | Actual input range | PP median | TG min/median/max | TTFT median | Primary/stage1 slots |\n|---|---:|---:|---:|---:|---:|\n'
for r in summary:
 b=budgets[r['profile']];report+=f'| {r["profile"]} | {r["actual_input_tokens"]["min"]}–{r["actual_input_tokens"]["max"]} | {r["PP"]["median"]:.1f} | {r["TG"]["min"]:.1f}/{r["TG"]["median"]:.1f}/{r["TG"]["max"]:.1f} | {r["TTFT_s"]["median"]:.2f} | {b["primary_slots"]}/{b["helper_or_stage1_slots"]} |\n'
report+='\nAll six requests produced4096 tokens with zero reuse, using input+output+8 <= actual configured32768/131072. Serial-three cache history follows the predeclared protocol. First measured PP includes lazy graph capture; outliers are preserved. Smaller limits yield modest cache increases, not a free48GiB pool. Exact byte classes follow in the separate diagnostic experiment.\n\nNative suite:62 passed,2 skipped,4 environmental failures (missing Q2_0 PLE and experts.bin fixtures, unprivileged memlock). Python268 OK/7 skipped. These are not an all-tests-pass claim. No engine or weights were patched in this control. CMake4.3/Ninja1.13 differ from preserved build tooling; GCC15.2/CUDA13.4 and flags are recorded. Rebuilt control is the live comparator, not historical scores.\n\nClean shutdown by owned process group causes a frontend BrokenPipeError after all responses; server exit is cleanup, not an inference crash. No CUDA process remained.\n'
(ROOT/'experiments/E002-controls/report.md').write_text(report)
print(json.dumps(summary,indent=2),flush=True)
