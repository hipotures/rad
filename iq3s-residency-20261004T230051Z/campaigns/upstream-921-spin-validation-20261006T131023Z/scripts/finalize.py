"""Record completed lifecycle and hash all campaign evidence after the full audit."""
import datetime,hashlib,json,os,pathlib,subprocess,time
C=pathlib.Path(__file__).resolve().parents[1]
def read(n):return json.loads((C/n).read_text())
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(8*1024*1024):h.update(b)
 return h.hexdigest()
a=read('reproducibility-audit.json');assert a['state']=='PASS' and all(a['checks'].values())
for name,key in [('report.md','report_sha256'),('github-issue-921-comment.md','comment_sha256'),('summary.json','summary_sha256'),('tables.md','tables_sha256')]:assert digest(C/name)==a[key]
assert read('metrics-audit.json')['state']=='PASS'
g=read('statistics-regeneration-audit.json');assert g['state']=='PASS' and all(g['byte_identical'].values())
pairs=[p for v in a['details'].values() for p in v['pairs']]
for key in ['outputs_identical','warmup_output_identical','warmup_graph_messages_identical','measured_graph_messages_identical']:assert all(p[key] for p in pairs)
assert len(pairs)==48 and all(v['valid_pairs']==12 for v in a['details'].values())
q=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],capture_output=True,text=True,timeout=15,check=True)
assert not q.stdout.strip(),q.stdout
(C/'provenance'/'end-state-gpu-processes.txt').write_text('No GPU compute processes.\n'+q.stdout)
t=read('timing.json');now=time.monotonic();assert now<t['deadline_monotonic']
finished=datetime.datetime.now(datetime.timezone.utc).isoformat()
s={'state':'COMPLETE','finished_utc':finished,'finished_monotonic':now,'elapsed_seconds':now-t['start_monotonic'],'elapsed_hours':(now-t['start_monotonic'])/3600,'start_utc':t['start_utc'],'absolute_deadline_utc':t['deadline_utc'],'measurements_completed_utc':read('STATUS.json')['updated_utc'],'valid_pairs_by_cell':{k:v['valid_pairs'] for k,v in a['details'].items()},'valid_pairs':48,'valid_measured_requests':96,'total_attempted_measured_requests':97,'invalid_entire_pairs':1,'replacement_pairs':1,'TG_B_wins':47,'paired_output_ID_identity':48,'audits':{'full_reproducibility':'PASS','statistics_byte_identical_regeneration':'PASS','independent_clocks_ticks_medians':'PASS'},'decision_label':read('interpretation.json')['decision_label'],'owned_processes_stopped':True,'no_gpu_compute_jobs':True,'source_clean':True,'github_comment_posted':False,'push':False,'PR_created':False}
(C/'STATUS.json').write_text(json.dumps(s,indent=2)+'\n')
(C/'STATUS.md').write_text('# Campaign complete\n\nCompleted '+finished+'; elapsed %.3f hours (maximum eight).\n\n'%s['elapsed_hours']+'48 valid interleaved pairs, 12 per cell; 96 valid measured requests. One objectively invalid pair and its replacement are preserved. Full source/binary/model/protocol audit and independent metric checks passed. Statistical regeneration reproduced all seven files byte for byte. All paired input/output IDs, MTP/routing counters, capacities, warmup outputs and observed graph messages match. Owned processes are stopped; no GPU compute jobs remain. Source is clean. No comment posted, push or PR.\n\nDecision: `'+s['decision_label']+'` within the tested hardware/workload scope.\n\nSee report.md, github-issue-921-comment.md, pairs.csv, reproduce.md and reproducibility-audit.json. artifact-manifest.json hashes the final evidence.\n')
files={}
for root,dirs,names in os.walk(C):
 if pathlib.Path(root)==C:dirs[:]=[d for d in dirs if d not in {'source','build','dependency','replays'}]
 for name in names:
  p=pathlib.Path(root)/name
  if p.is_symlink() or name=='artifact-manifest.json' or '__pycache__' in p.parts:continue
  files[str(p.relative_to(C))]={'sha256':digest(p),'bytes':p.stat().st_size}
for name in ['build/strata','build/CMakeCache.txt','build/compile_commands.json']:
 p=C/name;files[name]={'sha256':digest(p),'bytes':p.stat().st_size}
manifest={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'COMPLETE','scope':'All campaign evidence outside source/build/dependency/replays, plus frozen binary and build configuration; complete upstream and external model identities are separately verified in reproducibility-audit.json and provenance.','files':files}
(C/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'state':'COMPLETE','elapsed_hours':s['elapsed_hours'],'hashed_artifacts':len(files),'pairs':48,'requests':96,'audit':'PASS'},indent=2))
