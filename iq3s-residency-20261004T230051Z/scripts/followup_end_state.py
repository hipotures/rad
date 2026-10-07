"""Read-only provenance/end-state audit, limited cleanup of explicitly owned process groups."""
import datetime,hashlib,pathlib,subprocess,psutil
from lab import ROOT,load,save,owned_stop
campaign=pathlib.Path(load(ROOT/'active-campaign.json')['path'])
# This script runs only after every driver completed, never in the middle of a request.
assert load(ROOT/'experiments/E029-persistent-runtime/v2-fixed-pipeline/command.json')['returncode']==0
assert load(ROOT/'experiments/E029-persistent-runtime/postmatrix-diagnostic-fixed-driver/command.json')['returncode']==0
variants=['p1-baseline','p1-pool-default','persistent-signal-v1','persistent-v1-fixed-off','persistent-v1-fixed-on','persistent-v2-off','persistent-v2-on','persistent-v2-diagnostic']
identities=[];stopped=[]
for name in variants:
 path=ROOT/'variants'/name;cfg=load(path/'32k.json');source=pathlib.Path(cfg['cwd']);binary=pathlib.Path(cfg['exe'])
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip();status=subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True);sha=hashlib.sha256(binary.read_bytes()).hexdigest();assert head==cfg['source_sha'] and not status and sha==cfg['binary_sha256']
 for file in ['start-32k.sh','start-128k.sh','stop.sh','reproduce.sh']:subprocess.run(['bash','-n',str(path/file)],check=True,stdout=subprocess.DEVNULL)
 own=path/'owned-process.json'
 if own.exists():
  record=load(own)
  if psutil.pid_exists(record['pid']):
   process=psutil.Process(record['pid'])
   if abs(process.create_time()-record['create_time'])<.1:owned_stop(record['pid'],record['create_time']);stopped.append(record)
 identities.append({'variant':name,'source':str(source),'source_SHA':head,'git_status':status,'binary':str(binary),'binary_SHA256':sha,'shell_syntax':'PASS','configs':[str(path/(p+'.json')) for p in ['32k','128k']]})
prior=load(ROOT/'git/final-provenance.json');models=[]
for old in prior['model']:
 path=pathlib.Path(old['path']);st=path.stat();same=st.st_size==old['size'] and st.st_mtime_ns==old['mtime_ns'];assert same,(str(path),old,st)
 row=dict(old);row['size_mtime_unchanged']=same
 if st.st_size<16*1024*1024:row['current_SHA256']=hashlib.sha256(path.read_bytes()).hexdigest()
 models.append(row)
profile=pathlib.Path('/srv/ai/strata/data/expert-profile.bin');assert hashlib.sha256(profile.read_bytes()).hexdigest()=='8f59b4aa8873209dff11c11e37bcda9529a1335b724a1afeea37bf6388975baf'
archived=[]
for row in load(campaign/'previous-root-manifest.json'):
 path=campaign/'previous-root'/row['path'];sha=hashlib.sha256(path.read_bytes()).hexdigest();assert sha==row['sha256'];archived.append({'path':str(path),'sha256':sha,'state':'PASS'})
control_status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT/'src/control',text=True);assert not control_status
apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],text=True).strip();assert not apps,apps
owned=[]
for process in psutil.process_iter(['pid','cmdline','status','cwd']):
 try:
  args=' '.join(process.info['cmdline'] or [])
  is_owned=str(ROOT) in args or str(process.info['cwd'] or '').startswith(str(ROOT))
  if is_owned and process.info['status']!='zombie' and (('strata --serve' in args) or ('serve_capture.py' in args) or ('train_' in args) or ('pool_stress' in args) or ('nsys profile' in args)):owned.append({'pid':process.pid,'args':args})
 except psutil.Error:pass
assert not owned,owned
now=datetime.datetime.now(datetime.timezone.utc);deadline=load(campaign/'deadline.json');elapsed=now.timestamp()-deadline['start_epoch'];assert now.timestamp()<deadline['deadline_epoch']
result={'state':'PASS_IDLE_OWNED_PROCESSES','updated_UTC':now.isoformat(),'elapsed_wall_s':elapsed,'deadline_UTC':deadline['deadline_utc'],'remaining_upperbound_s':deadline['deadline_epoch']-now.timestamp(),'GPUcomputeapps':apps,'owned_Strata_training_profiling':owned,'cleanup':stopped,'variant_identities':identities,'model_metadata':models,'model_SHA256_manifest':prior['model_SHA256_manifest'],'profile_SHA256':hashlib.sha256(profile.read_bytes()).hexdigest(),'previous_archive_checks':archived,'control_git_status':control_status,'no_push_or_PR':True,'scope':'Largeweights existingSHAmanifest plusunchangedsize/mtime; no rereadhash of54GBGGUF. ExactliveGPU/RAMbyteaudit separate. Owneddriversalreadycompleted; PIDcreateidentityguardscleanup.'}
save(campaign/'end-state.json',result);print(result['state'],'elapsed_h',elapsed/3600,flush=True)
