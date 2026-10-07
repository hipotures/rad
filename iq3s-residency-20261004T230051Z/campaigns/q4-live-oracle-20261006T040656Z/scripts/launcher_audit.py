"""Check every preserved shell entrypoint without adding inference repetitions."""
from pathlib import Path
import json,subprocess,time
C=Path(__file__).resolve().parents[1]
def main():
 rows=[];out=C/'tests/launcher-checks';out.mkdir(exist_ok=True)
 for path in sorted((C/'launchers').rglob('*.sh')):
  p=subprocess.run(['bash','-n',str(path)],capture_output=True,text=True,timeout=10)
  rows.append({'path':str(path),'test':'bash syntax','exit_code':p.returncode})
  assert p.returncode==0,p.stderr
 for profile in ['32k','128k','256k']:
  commands=[['bash',str(C/'launchers/control'/f'start-{profile}.sh'),'--check']]
  for mode in ['capture','replay-current','replay-full','replay-short']:
   commands.append(['bash',str(C/'launchers/experimental'/f'{mode}-{profile}.sh'),'--check'])
  commands.append(['bash',str(C/'launchers/experimental/validate-tape.sh'),'--profile',profile])
  for cmd in commands:
   label=Path(cmd[1]).stem+'-'+profile;start=time.monotonic()
   with (out/f'{label}.log').open('w') as f:
    p=subprocess.run(cmd,cwd=C,stdout=f,stderr=subprocess.STDOUT,timeout=90)
   rows.append({'command':cmd,'exit_code':p.returncode,'elapsed_s':time.monotonic()-start,'log':str(out/f'{label}.log'),'scope':'identity/config/tape check only; no server or new GPU inference'})
   print('LAUNCHER_CHECK',label,p.returncode,flush=True)
   assert p.returncode==0,label
 (out/'summary.json').write_text(json.dumps({'state':'PASS','rows':rows,'not_claimed':'No extra manual reproduction server was started. Exact execution backends were exercised by the retained capture, primary, overhead and independent runs. New-directory reproduction parent checks are static/config only.'},indent=2)+'\n')
if __name__=='__main__':main()
