"""Completion is unproven until explicit artifacts, counts, invariants and process state pass."""
from pathlib import Path
import json,subprocess,hashlib,psutil,re,datetime,time
from owned import C
def main():
 checks=[]
 def check(name,ok,evidence):checks.append({'requirement':name,'state':'PASS' if ok else 'FAIL','evidence':evidence})
 def load(p):return json.loads(Path(p).read_text())
 required=['GOAL.md','STATUS.json','DECISIONS.md','ledger.jsonl','report.md','summary.csv','summary.json','phase-a/information-channel-map.md','phase-a/feature-query-audit.md','phase-a/protocol.json','phase-a/report.md','phase-b/report.md','phase-b/offline-summary.csv','phase-b/offline-summary.json','phase-c/report.md','phase-c/transfer-protocol.json','phase-c/independent-protocol.json','analysis/predictor-specification.md','git/oracle-decomposition-v2-identity.json','patches/information-v2.diff']
 check('Required English campaign artifacts',all((C/p).is_file() for p in required),required)
 s=load(C/'summary.json');rows=s['rows'];by={}
 for r in rows:by.setdefault((r['profile'],r['arm']),[]).append(r)
 expected={('32k',arm):3 for arm in ['current','FF','64F','F64','6464']}
 transfer=load(C/'phase-c/transfer-protocol.json')
 for profile,blocks in transfer['blocks'].items():
  for arm in set(sum(blocks,[])):expected[profile,arm]=sum(arm in b for b in blocks)
 check('Main decomposition and selected context transfer complete',all(len(by.get(k,[]))==n for k,n in expected.items()),{str(k):len(by.get(k,[])) for k in expected})
 check('No more than three unchanged measured attempts',all(len(v)<=3 for v in by.values()),{str(k):len(v) for k,v in by.items()})
 check('All headline requests valid with4096output and exact work/state/ownership',all(r['state']=='VALID' and r['recorded_output']==4096 and r['fidelity']=='PASS' and r['ownership']=='PASS' and r['initial_state']['match'] for r in rows),[r['label'] for r in rows])
 check('Independent role query budgets enforced',all((r['I']=='full' or r['queries']['incoming_max_visible']<=int(r['I'])) and (r['V']=='full' or r['queries']['victim_max_visible']<=int(r['V'])) for r in rows),'Per-request Q4_INFORMATION_END; inclusive endpoint tests')
 for p in [C/'tests/information-final-run/result.json',C/'tests/safety-v2-run/result.json',C/'tests/targeted-native/result.json']:
  check('Test '+p.parent.name,load(p)['exit_code']==0,str(p))
 check('No unknowns replaced by fabricated counter zero',all(r['local_entries']+r['CPU_entries']+r['mapped_entries']>0 for r in rows),'Unavailable selection reasons and secondary KV counters explicitly unknown; all-routed conservation in ownership audits')
 ident=load(C/'git/oracle-decomposition-v2-identity.json');check('Frozen binary source and clean worktree',hashlib.sha256(Path(ident['exe']).read_bytes()).hexdigest()==ident['binary_sha256'] and subprocess.check_output(['git','rev-parse','HEAD'],cwd=ident['source'],text=True,timeout=10).strip()==ident['source_sha'] and not subprocess.check_output(['git','status','--porcelain'],cwd=ident['source'],text=True,timeout=10).strip(),ident)
 old=load(C/'git/immutable-prior-anchors.json');check('Previous evidence anchor hashes/mtimes unchanged',all(Path(r['path']).stat().st_mtime_ns==r['mtime_ns'] and hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256'] for r in old),old)
 launch=load(C/'tests/launcher-checks.json');check('Retained replay launchers verified',launch['state']=='PASS' and len(launch['rows'])==18,str(C/'tests/launcher-checks.json'))
 ind=load(C/'phase-c/independent-summary.json');check('Independent previously-observed substantive task transfer retained',all(x['attempts']<=3 and x['valid']==x['attempts'] for x in ind['cells']),ind['description'])
 procs=[]
 for p in psutil.process_iter(['pid','cmdline','status']):
  try:
   cmd=p.info['cmdline'] or []
   scoped_binary=bool(cmd and Path(cmd[0]).is_relative_to(C/'builds'))
   scoped_script=any(Path(x).is_relative_to(C/'scripts') and Path(x).name in ['serve_capture.py','runner.py','batch.py','train.py','profiler.py'] for x in cmd if x.startswith('/'))
   if p.pid!=__import__('os').getpid() and p.info['status']!=psutil.STATUS_ZOMBIE and (scoped_binary or scoped_script):procs.append({'pid':p.pid,'command':cmd})
  except (psutil.NoSuchProcess,psutil.AccessDenied):pass
 compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],text=True,timeout=10).strip();gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,utilization.gpu,memory.used','--format=csv,noheader,nounits'],text=True,timeout=10)
 check('No owned research server/training/copier/profiler remains',not procs,procs);check('Both GPUs free of compute jobs',not compute,{'compute':compute,'GPU':gpu})
 d=load(C/'deadline.json');check('Absolute deadline respected',time.monotonic()<d['deadline_monotonic'],{'deadline':d,'observed_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_s':time.monotonic()-d['start_monotonic']})
 r={'state':'PASS' if all(x['state']=='PASS' for x in checks) else 'FAIL','checks':checks,'not_claimed':['Universal hardware-only benefit','Untouched holdout diversity from single tape replicas','Complete secondary-device KV DMA identity','Optimal scheduler/information-theoretic lower bound','All possible replay wrapper combinations live-benchmarked'],'observed':datetime.datetime.now(datetime.timezone.utc).isoformat()};(C/'analysis/final-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'state':r['state'],'failures':[x for x in checks if x['state']=='FAIL']},indent=2));assert r['state']=='PASS'
if __name__=='__main__':main()
