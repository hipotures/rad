from lab import ROOT,load,save
import subprocess
base=ROOT/'experiments/E029-persistent-runtime';py=str(ROOT/'src/control/.venv/bin/python')
for role,enabled in [('off',False),('on',True)]:
 name='persistent-v1-fixed-'+role;overrides={'env':{'STRATA_POOL_SPIN_US':'100'},'experimental':enabled,'policy_version':'v1.1_validation_only_repair','safe_serve_only':True,'extra_explicit_GPU_bytes_per_device':320 if enabled else 0}
 if enabled:overrides['env']['STRATA_LAB_PERSISTENT']='1'
 file=base/(name+'-overrides.json');save(file,overrides)
 subprocess.run([py,'scripts/register_variant.py',name,'--source',str(ROOT/'src/persistent-runtime-v1-fixed'),'--binary',str(ROOT/'builds/persistent-runtime-v1-fixed/strata'),'--overrides',str(file)],cwd=ROOT,check=True)
 for profile in ['32k','128k']:
  file=ROOT/'variants'/name/(profile+'.json');cfg=load(file);cfg['server_entrypoint']=str(ROOT/'scripts/serve_capture.py');save(file,cfg)
