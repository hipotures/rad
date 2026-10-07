from lab import ROOT,save,load
import subprocess
base=ROOT/'experiments/E029-persistent-runtime';py=str(ROOT/'src/control/.venv/bin/python')
for role,enabled in [('off',False),('on',True)]:
 name='persistent-v2-'+role;env={'STRATA_POOL_SPIN_US':'100'}
 if enabled:env['STRATA_LAB_PERSISTENT']='1'
 p=base/(name+'-overrides.json');save(p,{'env':env,'experimental':enabled,'safe_serve_only':True,'policy_version':'P2v2 predeclaredhorizon64/budget64MiB','extra_explicit_GPU_bytes_per_device':320 if enabled else 0,'mapped_CPU_bytes_per_device':1664 if enabled else 0,'math':'True experts, immutable original weights; alteredCPU/GPUpathcanrounddifferently.','posttiming_byteaudit_default':'OFF'})
 subprocess.run([py,'scripts/register_variant.py',name,'--source',str(ROOT/'src/persistent-runtime-v2-fixed'),'--binary',str(ROOT/'builds/persistent-runtime-v2-fixed/strata'),'--overrides',str(p)],cwd=ROOT,check=True)
 for profile in ['32k','128k']:
  file=ROOT/'variants'/name/(profile+'.json');cfg=load(file);cfg['server_entrypoint']=str(ROOT/'scripts/serve_capture.py');save(file,cfg)
